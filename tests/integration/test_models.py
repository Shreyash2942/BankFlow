"""Live Day 3 persistence checks, gated by BANKFLOW_RUN_DB_TESTS=1."""

import os
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from bankflow.database.session import create_session_factory, session_scope
from bankflow.models import (
    Account,
    AccountType,
    AuditEvent,
    Card,
    Customer,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from scripts.seed_database import (
    DEMO_ACCOUNT_ID,
    DEMO_CARD_ID,
    DEMO_CUSTOMER_ID,
    seed_demo_data,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1", reason="database tests require opt-in"
    ),
]


def _delete_graph(database_engine, customer_id, account_id, card_id, transaction_id=None):
    with database_engine.begin() as connection:
        if transaction_id is not None:
            connection.execute(
                text("DELETE FROM bankflow.audit_events WHERE transaction_id=:id"),
                {"id": transaction_id},
            )
            connection.execute(
                text("DELETE FROM bankflow.transactions WHERE id=:id"), {"id": transaction_id}
            )
        connection.execute(
            text(
                "DELETE FROM bankflow.audit_events "
                "WHERE customer_id=:customer OR account_id=:account OR card_id=:card"
            ),
            {"customer": customer_id, "account": account_id, "card": card_id},
        )
        connection.execute(text("DELETE FROM bankflow.cards WHERE id=:id"), {"id": card_id})
        connection.execute(text("DELETE FROM bankflow.accounts WHERE id=:id"), {"id": account_id})
        connection.execute(text("DELETE FROM bankflow.customers WHERE id=:id"), {"id": customer_id})


def test_tables_relationships_timestamps_and_decimal_round_trip(migrated_database, database_engine):
    assert {
        "customers",
        "accounts",
        "cards",
        "transactions",
        "audit_events",
    }.issubset(inspect(database_engine).get_table_names(schema="bankflow"))

    customer_id, account_id, card_id, transaction_id = (uuid4() for _ in range(4))
    factory = create_session_factory(database_engine)
    try:
        with session_scope(factory) as session:
            customer = Customer(
                id=customer_id,
                full_name="Relationship Test Customer",
                email=f"{customer_id}@bankflow.example",
            )
            account = Account(
                id=account_id,
                customer=customer,
                account_number=f"BF-{account_id.hex[:20]}",
                account_type=AccountType.CHECKING,
                balance=Decimal("100.00"),
            )
            card = Card(
                id=card_id,
                account=account,
                card_token=f"test-{card_id}",
                last_four="4242",
                pin_hash="scrypt$fixture$" + "x" * 40,
                expiry_month=12,
                expiry_year=2035,
            )
            transaction = Transaction(
                id=transaction_id,
                account=account,
                card=card,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.COMPLETED,
                amount=Decimal("0.01"),
                balance_before=Decimal("100.00"),
                balance_after=Decimal("100.01"),
            )
            session.add_all(
                [
                    customer,
                    account,
                    card,
                    transaction,
                    AuditEvent(
                        event_type="test.deposit",
                        outcome="completed",
                        customer=customer,
                        account=account,
                        card=card,
                        transaction=transaction,
                        details={"fixture": True},
                    ),
                ]
            )

        with factory() as session:
            stored = session.scalar(
                select(Customer)
                .where(Customer.id == customer_id)
                .options(
                    selectinload(Customer.accounts)
                    .selectinload(Account.transactions)
                    .selectinload(Transaction.card)
                )
            )
            assert stored is not None
            stored_account = stored.accounts[0]
            stored_transaction = stored_account.transactions[0]
            assert stored_account.balance == Decimal("100.00")
            assert stored_transaction.amount == Decimal("0.01")
            assert stored_transaction.balance_after == Decimal("100.01")
            assert stored_transaction.card.last_four == "4242"
            assert stored.created_at.tzinfo is not None
            assert stored.updated_at.tzinfo is not None
    finally:
        _delete_graph(database_engine, customer_id, account_id, card_id, transaction_id)


def test_database_rejects_negative_balance_and_zero_withdrawal(migrated_database, database_engine):
    factory = create_session_factory(database_engine)
    customer_id, account_id = uuid4(), uuid4()
    with pytest.raises(IntegrityError):
        with session_scope(factory) as session:
            session.add(
                Account(
                    id=account_id,
                    customer=Customer(
                        id=customer_id,
                        full_name="Invalid Balance",
                        email=f"{customer_id}@bankflow.example",
                    ),
                    account_number=f"BF-{account_id.hex[:20]}",
                    account_type=AccountType.CHECKING,
                    balance=Decimal("-0.01"),
                )
            )

    customer_id, account_id, transaction_id = uuid4(), uuid4(), uuid4()
    try:
        with session_scope(factory) as session:
            session.add(
                Account(
                    id=account_id,
                    customer=Customer(
                        id=customer_id,
                        full_name="Invalid Transaction",
                        email=f"{customer_id}@bankflow.example",
                    ),
                    account_number=f"BF-{account_id.hex[:20]}",
                    account_type=AccountType.CHECKING,
                    balance=Decimal("10.00"),
                )
            )
        with pytest.raises(IntegrityError):
            with session_scope(factory) as session:
                session.add(
                    Transaction(
                        id=transaction_id,
                        account_id=account_id,
                        transaction_type=TransactionType.WITHDRAWAL,
                        status=TransactionStatus.DECLINED,
                        amount=Decimal("0.00"),
                        balance_before=Decimal("10.00"),
                        balance_after=Decimal("10.00"),
                    )
                )
    finally:
        with database_engine.begin() as connection:
            connection.execute(
                text("DELETE FROM bankflow.transactions WHERE id=:id"), {"id": transaction_id}
            )
            connection.execute(
                text("DELETE FROM bankflow.accounts WHERE id=:id"), {"id": account_id}
            )
            connection.execute(
                text("DELETE FROM bankflow.customers WHERE id=:id"), {"id": customer_id}
            )


def test_demo_seed_is_complete_idempotent_and_never_stores_plain_pin(
    migrated_database, database_engine
):
    _delete_graph(database_engine, DEMO_CUSTOMER_ID, DEMO_ACCOUNT_ID, DEMO_CARD_ID)
    factory = create_session_factory(database_engine)
    try:
        with session_scope(factory) as session:
            first = seed_demo_data(session)
        with session_scope(factory) as session:
            second = seed_demo_data(session)
        assert first.created is True
        assert second.created is False
        with factory() as session:
            account = session.get(Account, DEMO_ACCOUNT_ID)
            card = session.get(Card, DEMO_CARD_ID)
            assert account.balance == Decimal("500.00")
            assert account.customer_id == DEMO_CUSTOMER_ID
            assert card.account_id == DEMO_ACCOUNT_ID
            assert card.pin_hash.startswith("scrypt$")
            assert "2468" not in card.pin_hash
    finally:
        _delete_graph(database_engine, DEMO_CUSTOMER_ID, DEMO_ACCOUNT_ID, DEMO_CARD_ID)
