"""Thin application runtime used by Streamlit pages."""

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from redis import Redis
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from bankflow.cache.redis_client import AuthenticationStateStore, create_redis_client
from bankflow.config.settings import Settings, load_settings
from bankflow.database.connection import create_database_engine
from bankflow.database.session import create_session_factory, session_scope
from bankflow.demo import DEMO_CARD_ID
from bankflow.models import Account, AccountStatus, AccountType, Card, CardStatus
from bankflow.schemas.account import AccountBalance
from bankflow.schemas.authentication import (
    AuthenticationRequest,
    AuthenticationResult,
    AuthenticationSession,
)
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
    ) -> None:
        self.settings = settings
        self._engine = engine
        self._sessions = session_factory
        self._redis = redis_client
        self._state = state_store

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
        )

    def close(self) -> None:
        self._redis.close()
        self._engine.dispose()

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
            return AuthenticationService.from_settings(
                session, self._state, self.settings
            ).authenticate(request)

    def resolve_session(self, token: str) -> AuthenticationSession | None:
        return self._state.get_session(token)

    def end_session(self, token: str) -> None:
        self._state.delete_session(token)

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
            return AccountService(session).inquire_balance(authentication)

    def withdraw(
        self, authentication: AuthenticationSession, request: WithdrawalRequest
    ) -> TransactionResult:
        with session_scope(self._sessions) as session:
            return TransactionService.from_settings(session, self.settings).withdraw(
                authentication, request
            )

    def deposit(
        self, authentication: AuthenticationSession, request: DepositRequest
    ) -> TransactionResult:
        with session_scope(self._sessions) as session:
            return TransactionService.from_settings(session, self.settings).deposit(
                authentication, request
            )

    def history(
        self, authentication: AuthenticationSession, *, limit: int = 100, offset: int = 0
    ) -> TransactionHistory:
        query = TransactionHistoryQuery(limit=limit, offset=offset)
        with session_scope(self._sessions) as session:
            return TransactionService.from_settings(session, self.settings).history(
                authentication, query
            )

    def reset_demo(self, *, session_token: str | None = None) -> DemoResetResult:
        with session_scope(self._sessions) as session:
            result = DemoService(session).reset()
        self._state.clear_failed_attempts(result.card_id)
        if session_token:
            self._state.delete_session(session_token)
        return result
