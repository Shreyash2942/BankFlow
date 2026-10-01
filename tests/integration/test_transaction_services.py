"""Live Day 6 service checks against the isolated PostgreSQL database."""

import os
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text

from bankflow.database.session import create_session_factory, session_scope
from bankflow.models import (
    Account,
    AccountStatus,
    AccountType,
    AuditEvent,
    Card,
    Customer,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from bankflow.repositories import RepositoryWriteError, TransactionRepository
from bankflow.schemas import (
    AuthenticationSession,
    DepositRequest,
    TransactionHistoryQuery,
    WithdrawalRequest,
)
from bankflow.services import (
    AccountAuthorizationError,
    AccountService,
    AccountUnavailableError,
    BalanceLimitExceededError,
    TransactionService,
)
from bankflow.services.transaction_service import MAX_MONEY
from bankflow.utils import hash_pin

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1", reason="database tests require opt-in"
    ),
]


def _create_account_graph(factory, *, balance: Decimal = Decimal("100.00")):
    customer_id, account_id, card_id = uuid4(), uuid4(), uuid4()
    with session_scope(factory) as session:
        customer = Customer(
            id=customer_id,
            full_name="Transaction Service Customer",
            email=f"{customer_id}@bankflow.example",
        )
        account = Account(
            id=account_id,
            customer=customer,
            account_number=f"BF-TXN-{account_id.hex[:16]}",
            account_type=AccountType.CHECKING,
            balance=balance,
        )
        card = Card(
            id=card_id,
            account=account,
            card_token=f"transaction-{card_id}",
            last_four="6001",
            pin_hash=hash_pin("2468"),
            expiry_month=12,
            expiry_year=2035,
        )
        session.add_all([customer, account, card])
    authentication = AuthenticationSession(
        customer_id=customer_id, account_id=account_id, card_id=card_id
    )
    return customer_id, account_id, card_id, authentication


def _delete_account_graph(database_engine, customer_id: UUID):
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM bankflow.audit_events WHERE customer_id=:customer "
                "OR account_id IN (SELECT id FROM bankflow.accounts WHERE customer_id=:customer)"
            ),
            {"customer": customer_id},
        )
        connection.execute(
            text(
                "DELETE FROM bankflow.transactions WHERE account_id IN "
                "(SELECT id FROM bankflow.accounts WHERE customer_id=:customer)"
            ),
            {"customer": customer_id},
        )
        connection.execute(
            text(
                "DELETE FROM bankflow.cards WHERE account_id IN "
                "(SELECT id FROM bankflow.accounts WHERE customer_id=:customer)"
            ),
            {"customer": customer_id},
        )
        connection.execute(
            text("DELETE FROM bankflow.accounts WHERE customer_id=:customer"),
            {"customer": customer_id},
        )
        connection.execute(
            text("DELETE FROM bankflow.customers WHERE id=:customer"),
            {"customer": customer_id},
        )


def test_balance_withdrawal_decline_deposit_and_history_workflow(
    migrated_database, database_engine
):
    factory = create_session_factory(database_engine)
    customer_id, account_id, _, authentication = _create_account_graph(factory)
    try:
        with session_scope(factory) as session:
            inquiry = AccountService(session).inquire_balance(authentication)
        assert inquiry.balance == Decimal("100.00")

        with session_scope(factory) as session:
            withdrawal = TransactionService(session).withdraw(
                authentication, WithdrawalRequest(amount=Decimal("25.00"))
            )
        assert withdrawal.status is TransactionStatus.COMPLETED
        assert withdrawal.balance_before == Decimal("100.00")
        assert withdrawal.balance_after == Decimal("75.00")

        with session_scope(factory) as session:
            declined = TransactionService(session).withdraw(
                authentication, WithdrawalRequest(amount=Decimal("100.00"))
            )
        assert declined.status is TransactionStatus.DECLINED
        assert declined.decline_reason == "insufficient_funds"
        assert declined.balance_before == declined.balance_after == Decimal("75.00")

        with session_scope(factory) as session:
            deposit = TransactionService(session).deposit(
                authentication, DepositRequest(amount=Decimal("10.00"))
            )
        assert deposit.status is TransactionStatus.COMPLETED
        assert deposit.balance_after == Decimal("85.00")

        with factory() as session:
            history = TransactionService(session).history(
                authentication, TransactionHistoryQuery(limit=10)
            )
            account = session.get(Account, account_id)
            events = list(
                session.scalars(
                    select(AuditEvent)
                    .where(AuditEvent.account_id == account_id)
                    .order_by(AuditEvent.created_at, AuditEvent.id)
                )
            )
        assert account.balance == Decimal("85.00")
        assert account.version == 3
        assert [item.transaction_type for item in history.items] == [
            TransactionType.DEPOSIT,
            TransactionType.WITHDRAWAL,
            TransactionType.WITHDRAWAL,
            TransactionType.BALANCE_INQUIRY,
        ]
        assert [item.status for item in history.items] == [
            TransactionStatus.COMPLETED,
            TransactionStatus.DECLINED,
            TransactionStatus.COMPLETED,
            TransactionStatus.COMPLETED,
        ]
        assert {event.event_type for event in events} == {
            "balance.viewed",
            "withdrawal.completed",
            "withdrawal.declined",
            "deposit.completed",
        }
        assert all(event.transaction_id is not None for event in events)
    finally:
        _delete_account_graph(database_engine, customer_id)


@pytest.mark.parametrize(
    ("auto_close", "expected_status"),
    [(True, AccountStatus.CLOSED), (False, AccountStatus.ACTIVE)],
)
def test_zero_balance_rule_is_configurable(
    migrated_database, database_engine, auto_close, expected_status
):
    factory = create_session_factory(database_engine)
    customer_id, account_id, _, authentication = _create_account_graph(factory)
    try:
        with session_scope(factory) as session:
            result = TransactionService(session, auto_close_zero_balance=auto_close).withdraw(
                authentication, WithdrawalRequest(amount=Decimal("100.00"))
            )
        assert result.balance_after == Decimal("0.00")
        assert result.account_status is expected_status

        with factory() as session:
            account = session.get(Account, account_id)
            event_types = set(
                session.scalars(
                    select(AuditEvent.event_type).where(AuditEvent.account_id == account_id)
                )
            )
        assert account.status is expected_status
        assert ("account.closed" in event_types) is auto_close

        if auto_close:
            with pytest.raises(AccountUnavailableError, match="closed"):
                with session_scope(factory) as session:
                    TransactionService(session).deposit(
                        authentication, DepositRequest(amount=Decimal("1.00"))
                    )
    finally:
        _delete_account_graph(database_engine, customer_id)


def test_transaction_failure_rolls_back_balance_and_history(
    migrated_database, database_engine, monkeypatch
):
    factory = create_session_factory(database_engine)
    customer_id, account_id, _, authentication = _create_account_graph(factory)

    def reject_transaction(*args, **kwargs):
        raise RepositoryWriteError("Injected transaction failure.")

    monkeypatch.setattr(TransactionRepository, "create", reject_transaction)
    try:
        with pytest.raises(RepositoryWriteError, match="Injected"):
            with session_scope(factory) as session:
                TransactionService(session).withdraw(
                    authentication, WithdrawalRequest(amount=Decimal("25.00"))
                )

        with factory() as session:
            account = session.get(Account, account_id)
            transaction_count = len(
                list(
                    session.scalars(select(Transaction).where(Transaction.account_id == account_id))
                )
            )
            audit_count = len(
                list(session.scalars(select(AuditEvent).where(AuditEvent.account_id == account_id)))
            )
        assert account.balance == Decimal("100.00")
        assert account.version == 1
        assert transaction_count == 0
        assert audit_count == 0
    finally:
        _delete_account_graph(database_engine, customer_id)


def test_authentication_subjects_must_match_the_account_graph(migrated_database, database_engine):
    factory = create_session_factory(database_engine)
    customer_id, account_id, _, authentication = _create_account_graph(factory)
    unauthorized = authentication.model_copy(update={"customer_id": uuid4()})
    try:
        with pytest.raises(AccountAuthorizationError, match="not authorized"):
            with session_scope(factory) as session:
                TransactionService(session).withdraw(
                    unauthorized, WithdrawalRequest(amount=Decimal("1.00"))
                )
        with factory() as session:
            account = session.get(Account, account_id)
            assert account.balance == Decimal("100.00")
            assert not list(
                session.scalars(select(Transaction).where(Transaction.account_id == account_id))
            )
    finally:
        _delete_account_graph(database_engine, customer_id)


def test_deposit_rejects_balance_overflow_without_partial_write(migrated_database, database_engine):
    factory = create_session_factory(database_engine)
    customer_id, account_id, _, authentication = _create_account_graph(factory, balance=MAX_MONEY)
    try:
        with pytest.raises(BalanceLimitExceededError, match="supported balance limit"):
            with session_scope(factory) as session:
                TransactionService(session).deposit(
                    authentication, DepositRequest(amount=Decimal("0.01"))
                )
        with factory() as session:
            account = session.get(Account, account_id)
            assert account.balance == MAX_MONEY
            assert account.version == 1
            assert not list(
                session.scalars(select(Transaction).where(Transaction.account_id == account_id))
            )
    finally:
        _delete_account_graph(database_engine, customer_id)
