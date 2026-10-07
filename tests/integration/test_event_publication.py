"""Post-commit event publication coverage through the application runtime."""

import os
from decimal import Decimal

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from bankflow.cache import AuthenticationStateStore, create_redis_client
from bankflow.database.session import create_session_factory, session_scope
from bankflow.demo import DEMO_ACCOUNT_ID, DEMO_CARD_ID, DEMO_CUSTOMER_ID, DEMO_PIN
from bankflow.messaging import DeliveryReceipt, KafkaUnavailableError
from bankflow.models import Account, Transaction
from bankflow.schemas.events import BankFlowEvent, EventType, TransactionEventPayload
from bankflow.schemas.transaction import DepositRequest, WithdrawalRequest
from bankflow.ui.runtime import BankFlowRuntime
from scripts.seed_database import seed_demo_data

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1",
        reason="Post-commit publication tests require PostgreSQL and Redis opt-in",
    ),
]


def _delete_demo_graph(database_engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM bankflow.audit_events "
                "WHERE customer_id=:customer OR account_id=:account OR card_id=:card"
            ),
            {
                "customer": DEMO_CUSTOMER_ID,
                "account": DEMO_ACCOUNT_ID,
                "card": DEMO_CARD_ID,
            },
        )
        connection.execute(
            text("DELETE FROM bankflow.transactions WHERE account_id=:account"),
            {"account": DEMO_ACCOUNT_ID},
        )
        connection.execute(
            text("DELETE FROM bankflow.cards WHERE id=:card"), {"card": DEMO_CARD_ID}
        )
        connection.execute(
            text("DELETE FROM bankflow.accounts WHERE id=:account"),
            {"account": DEMO_ACCOUNT_ID},
        )
        connection.execute(
            text("DELETE FROM bankflow.customers WHERE id=:customer"),
            {"customer": DEMO_CUSTOMER_ID},
        )


class RecordingPublisher:
    def __init__(self, database_engine) -> None:
        self.database_engine = database_engine
        self.events: list[BankFlowEvent] = []

    def publish(self, event: BankFlowEvent) -> DeliveryReceipt:
        if isinstance(event.payload, TransactionEventPayload):
            with Session(self.database_engine) as session:
                assert session.get(Transaction, event.payload.transaction_id) is not None
        self.events.append(event)
        return DeliveryReceipt(event.event_id, "test", 0, len(self.events) - 1)


class UnavailablePublisher:
    def publish(self, event: BankFlowEvent) -> DeliveryReceipt:
        raise KafkaUnavailableError("test broker unavailable")


@pytest.fixture
def runtime_factory(migrated_database, database_engine, database_settings):
    _delete_demo_graph(database_engine)
    sessions = create_session_factory(database_engine)
    with session_scope(sessions) as session:
        seed_demo_data(session)
    redis_client = create_redis_client(database_settings)
    keys = list(redis_client.scan_iter(match="bankflow:auth:*"))
    if keys:
        redis_client.delete(*keys)

    runtimes: list[BankFlowRuntime] = []

    def factory(publisher) -> BankFlowRuntime:
        runtime = BankFlowRuntime(
            database_settings,
            database_engine,
            sessions,
            redis_client,
            AuthenticationStateStore(redis_client),
            publisher,
        )
        runtimes.append(runtime)
        return runtime

    yield factory

    keys = list(redis_client.scan_iter(match="bankflow:auth:*"))
    if keys:
        redis_client.delete(*keys)
    redis_client.close()
    _delete_demo_graph(database_engine)


def _authentication(runtime: BankFlowRuntime):
    card = runtime.list_demo_cards()[0]
    result = runtime.authenticate(card.card_token, DEMO_PIN)
    assert result.session_token is not None
    authentication = runtime.resolve_session(result.session_token.get_secret_value())
    assert authentication is not None
    return card, result, authentication


def test_runtime_publishes_complete_lifecycle_only_after_database_commit(
    runtime_factory, database_engine
):
    publisher = RecordingPublisher(database_engine)
    runtime = runtime_factory(publisher)
    _, result, authentication = _authentication(runtime)

    runtime.inquire_balance(authentication)
    runtime.withdraw(authentication, WithdrawalRequest(amount=Decimal("600.00")))
    runtime.deposit(authentication, DepositRequest(amount=Decimal("50.00")))
    runtime.reset_demo()
    runtime.withdraw(authentication, WithdrawalRequest(amount=Decimal("500.00")))
    runtime.end_session(result.session_token.get_secret_value())

    assert [event.event_type for event in publisher.events] == [
        EventType.AUTHENTICATION_SUCCEEDED,
        EventType.BALANCE_VIEWED,
        EventType.WITHDRAWAL_REQUESTED,
        EventType.WITHDRAWAL_DECLINED,
        EventType.DEPOSIT_COMPLETED,
        EventType.WITHDRAWAL_REQUESTED,
        EventType.WITHDRAWAL_COMPLETED,
        EventType.ACCOUNT_CLOSED,
        EventType.SESSION_ENDED,
    ]


def test_runtime_publishes_failed_authentication_and_card_lock(runtime_factory, database_engine):
    publisher = RecordingPublisher(database_engine)
    runtime = runtime_factory(publisher)
    card = runtime.list_demo_cards()[0]

    runtime.authenticate(card.card_token, "0000")
    runtime.authenticate(card.card_token, "0000")
    runtime.authenticate(card.card_token, "0000")

    assert [event.event_type for event in publisher.events] == [
        EventType.AUTHENTICATION_FAILED,
        EventType.AUTHENTICATION_FAILED,
        EventType.CARD_LOCKED,
    ]
    assert all(event.payload.card_id == DEMO_CARD_ID for event in publisher.events)


def test_kafka_unavailable_does_not_reverse_a_committed_withdrawal(
    runtime_factory, database_engine
):
    runtime = runtime_factory(UnavailablePublisher())
    _, _, authentication = _authentication(runtime)

    result = runtime.withdraw(authentication, WithdrawalRequest(amount=Decimal("100.00")))

    with Session(database_engine) as session:
        account = session.get(Account, DEMO_ACCOUNT_ID)
        transaction = session.scalar(
            select(Transaction).where(Transaction.id == result.transaction_id)
        )
    assert result.balance_after == Decimal("400.00")
    assert account is not None and account.balance == Decimal("400.00")
    assert transaction is not None
