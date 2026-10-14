"""Thin application runtime used by Streamlit pages."""

import logging
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from redis import Redis
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from bankflow.analytics import AnalyticsSnapshot, load_analytics_snapshot
from bankflow.cache.redis_client import AuthenticationStateStore, create_redis_client
from bankflow.config.settings import Settings, load_settings
from bankflow.database.connection import create_database_engine
from bankflow.database.session import create_session_factory, session_scope
from bankflow.demo import DEMO_CARD_ID
from bankflow.messaging import (
    EventPublicationError,
    EventPublisher,
    KafkaEventProducer,
    balance_viewed_event,
    event_from_authentication_result,
    event_from_transaction_result,
    session_ended_event,
    withdrawal_requested_event,
)
from bankflow.models import (
    Account,
    AccountStatus,
    AccountType,
    Card,
    CardStatus,
    TransactionStatus,
)
from bankflow.repositories import CardRepository
from bankflow.schemas.account import AccountBalance
from bankflow.schemas.authentication import (
    AuthenticationRequest,
    AuthenticationResult,
    AuthenticationSession,
)
from bankflow.schemas.events import BankFlowEvent, EventType
from bankflow.schemas.transaction import (
    DepositRequest,
    TransactionHistory,
    TransactionHistoryQuery,
    TransactionResult,
    WithdrawalRequest,
)
from bankflow.services import (
    AccountService,
    AuthenticationService,
    DemoResetResult,
    DemoService,
    TransactionService,
)

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DemoCardOption:
    card_id: UUID
    card_token: str = field(repr=False)
    last_four: str = ""
    account_type: AccountType = AccountType.CHECKING
    card_status: CardStatus = CardStatus.ACTIVE

    @property
    def label(self) -> str:
        return f"{self.account_type.value.title()} •••• {self.last_four}"


@dataclass(frozen=True)
class AccountSummary:
    customer_name: str
    account_id: UUID
    account_type: AccountType
    account_status: AccountStatus
    card_last_four: str
    balance: Decimal
    currency: str


class BankFlowRuntime:
    """Own shared clients and open a fresh database transaction per UI action."""

    def __init__(
        self,
        settings: Settings,
        engine: Engine,
        session_factory: sessionmaker[Session],
        redis_client: Redis,
        state_store: AuthenticationStateStore,
        event_publisher: EventPublisher,
    ) -> None:
        self.settings = settings
        self._engine = engine
        self._sessions = session_factory
        self._redis = redis_client
        self._state = state_store
        self._events = event_publisher

    @classmethod
    def from_env(cls, env_file: str | Path = ".env") -> "BankFlowRuntime":
        settings = load_settings(env_file)
        engine = create_database_engine(settings)
        redis_client = create_redis_client(settings)
        return cls(
            settings,
            engine,
            create_session_factory(engine),
            redis_client,
            AuthenticationStateStore(redis_client),
            KafkaEventProducer.from_settings(settings),
        )

    def close(self) -> None:
        if isinstance(self._events, KafkaEventProducer):
            undelivered = self._events.close()
            if undelivered:
                LOGGER.warning("Kafka producer closed with %s undelivered event(s)", undelivered)
        self._redis.close()
        self._engine.dispose()

    def _publish(self, *events: BankFlowEvent) -> None:
        """Publish committed facts without changing an already completed operation."""

        for event in events:
            try:
                self._events.publish(event)
            except EventPublicationError as exc:
                LOGGER.warning(
                    "Committed operation event %s was not delivered: %s", event.event_id, exc
                )
                break
            except Exception:
                LOGGER.exception("Unexpected event publication failure for %s", event.event_id)
                break

    @staticmethod
    def _authentication_subject(session: Session, card_token: str) -> AuthenticationSession | None:
        card = CardRepository(session).get_by_token(card_token)
        if card is None:
            return None
        account = session.get(Account, card.account_id)
        if account is None:
            return None
        return AuthenticationSession(
            card_id=card.id,
            account_id=account.id,
            customer_id=account.customer_id,
        )

    def list_demo_cards(self) -> tuple[DemoCardOption, ...]:
        with session_scope(self._sessions) as session:
            statement = (
                select(Card).options(joinedload(Card.account)).where(Card.id == DEMO_CARD_ID)
            )
            cards = session.scalars(statement).all()
            return tuple(
                DemoCardOption(
                    card_id=card.id,
                    card_token=card.card_token,
                    last_four=card.last_four,
                    account_type=card.account.account_type,
                    card_status=card.status,
                )
                for card in cards
            )

    def authenticate(self, card_token: str, pin: str) -> AuthenticationResult:
        request = AuthenticationRequest(card_token=card_token, pin=pin)
        with session_scope(self._sessions) as session:
            result = AuthenticationService.from_settings(
                session, self._state, self.settings
            ).authenticate(request)
            authentication = self._authentication_subject(session, card_token)
        self._publish(event_from_authentication_result(result, authentication=authentication))
        return result

    def resolve_session(self, token: str) -> AuthenticationSession | None:
        return self._state.get_session(token)

    def end_session(self, token: str) -> None:
        authentication = self._state.get_session(token)
        self._state.delete_session(token)
        if authentication is not None:
            self._publish(session_ended_event(authentication))

    def account_summary(self, authentication: AuthenticationSession) -> AccountSummary:
        with session_scope(self._sessions) as session:
            account = AccountService(session).require_authorized_account(
                authentication, for_update=False, require_active=False
            )
            statement = (
                select(Card)
                .options(joinedload(Card.account).joinedload(Account.customer))
                .where(Card.id == authentication.card_id)
            )
            card = session.scalars(statement).one()
            return AccountSummary(
                customer_name=card.account.customer.full_name,
                account_id=account.id,
                account_type=account.account_type,
                account_status=account.status,
                card_last_four=card.last_four,
                balance=account.balance,
                currency=account.currency,
            )

    def inquire_balance(self, authentication: AuthenticationSession) -> AccountBalance:
        with session_scope(self._sessions) as session:
            result = AccountService(session).inquire_balance(authentication)
        self._publish(balance_viewed_event(result, authentication))
        return result

    def withdraw(
        self, authentication: AuthenticationSession, request: WithdrawalRequest
    ) -> TransactionResult:
        with session_scope(self._sessions) as session:
            result = TransactionService.from_settings(session, self.settings).withdraw(
                authentication, request
            )
            account = session.get(Account, authentication.account_id)
            if account is None:
                raise RuntimeError("The committed withdrawal account could not be loaded.")
            currency = account.currency
        terminal_type = (
            EventType.WITHDRAWAL_COMPLETED
            if result.status is TransactionStatus.COMPLETED
            else EventType.WITHDRAWAL_DECLINED
        )
        events = [
            withdrawal_requested_event(
                result.transaction_id,
                request,
                authentication,
                balance_before=result.balance_before,
                currency=currency,
                account_status=AccountStatus.ACTIVE,
            ),
            event_from_transaction_result(
                terminal_type,
                result,
                authentication,
                currency=currency,
            ),
        ]
        if result.account_status is AccountStatus.CLOSED:
            events.append(
                event_from_transaction_result(
                    EventType.ACCOUNT_CLOSED,
                    result,
                    authentication,
                    currency=currency,
                )
            )
        self._publish(*events)
        return result

    def deposit(
        self, authentication: AuthenticationSession, request: DepositRequest
    ) -> TransactionResult:
        with session_scope(self._sessions) as session:
            result = TransactionService.from_settings(session, self.settings).deposit(
                authentication, request
            )
            account = session.get(Account, authentication.account_id)
            if account is None:
                raise RuntimeError("The committed deposit account could not be loaded.")
            currency = account.currency
        self._publish(
            event_from_transaction_result(
                EventType.DEPOSIT_COMPLETED,
                result,
                authentication,
                currency=currency,
            )
        )
        return result

    def history(
        self, authentication: AuthenticationSession, *, limit: int = 100, offset: int = 0
    ) -> TransactionHistory:
        query = TransactionHistoryQuery(limit=limit, offset=offset)
        with session_scope(self._sessions) as session:
            return TransactionService.from_settings(session, self.settings).history(
                authentication, query
            )

    def analytics_snapshot(self, *, start_date: date | None = None) -> AnalyticsSnapshot:
        return load_analytics_snapshot(self._engine, start_date=start_date)

    def reset_demo(self, *, session_token: str | None = None) -> DemoResetResult:
        with session_scope(self._sessions) as session:
            result = DemoService(session).reset()
        self._state.clear_failed_attempts(result.card_id)
        if session_token:
            self._state.delete_session(session_token)
        return result
