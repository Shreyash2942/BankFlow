"""Live Day 4 repository checks, gated by BANKFLOW_RUN_DB_TESTS=1."""

import os
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from bankflow.database.session import create_session_factory, session_scope
from bankflow.models import (
    Account,
    AccountType,
    Card,
    Customer,
    TransactionStatus,
    TransactionType,
)
from bankflow.repositories import (
    AccountRepository,
    CardRepository,
    ConcurrentUpdateError,
    CustomerRepository,
    InvalidRepositoryQueryError,
    RepositoryNotFoundError,
    RepositoryWriteError,
    TransactionRepository,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1", reason="database tests require opt-in"
    ),
]


def _create_customer_graph(factory, *, two_accounts: bool = False):
    customer_id, first_account_id, first_card_id = uuid4(), uuid4(), uuid4()
    second_account_id = uuid4() if two_accounts else None
    second_card_id = uuid4() if two_accounts else None
    with session_scope(factory) as session:
        customer = Customer(
            id=customer_id,
            full_name="Repository Test Customer",
            email=f"{customer_id}@bankflow.example",
        )
        first_account = Account(
            id=first_account_id,
            customer=customer,
            account_number=f"BF-B-{first_account_id.hex[:16]}",
            account_type=AccountType.CHECKING,
            balance=Decimal("100.00"),
        )
        first_card = Card(
            id=first_card_id,
            account=first_account,
            card_token=f"repository-{first_card_id}",
            last_four="4101",
            pin_hash="scrypt$repository$" + "x" * 40,
            expiry_month=12,
            expiry_year=2035,
        )
        session.add_all([customer, first_account, first_card])
        if second_account_id is not None and second_card_id is not None:
            second_account = Account(
                id=second_account_id,
                customer=customer,
                account_number=f"BF-A-{second_account_id.hex[:16]}",
                account_type=AccountType.SAVINGS,
                balance=Decimal("25.00"),
            )
            second_card = Card(
                id=second_card_id,
                account=second_account,
                card_token=f"repository-{second_card_id}",
                last_four="4102",
                pin_hash="scrypt$repository$" + "y" * 40,
                expiry_month=11,
                expiry_year=2035,
            )
            session.add_all([second_account, second_card])
    return customer_id, first_account_id, first_card_id, second_account_id, second_card_id


def _delete_customer_graph(database_engine, customer_id: UUID):
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


def test_customer_account_and_card_lookups(migrated_database, database_engine):
    factory = create_session_factory(database_engine)
    ids = _create_customer_graph(factory, two_accounts=True)
    customer_id, first_account_id, first_card_id, second_account_id, second_card_id = ids
    try:
        with factory() as session:
            customers = CustomerRepository(session)
            accounts = AccountRepository(session)
            cards = CardRepository(session)

            customer = customers.require_by_id(customer_id)
            assert customers.get_by_email(customer.email).id == customer_id
            assert accounts.get_by_id(first_account_id).balance == Decimal("100.00")
            assert (
                accounts.get_by_account_number(f"BF-A-{second_account_id.hex[:16]}").id
                == second_account_id
            )
            assert [account.id for account in accounts.list_for_customer(customer_id)] == [
                second_account_id,
                first_account_id,
            ]
            assert cards.get_by_token(f"repository-{first_card_id}").id == first_card_id
            assert cards.require_by_id(second_card_id).account_id == second_account_id
            assert [card.id for card in cards.list_for_account(first_account_id)] == [first_card_id]
            with pytest.raises(RepositoryNotFoundError, match="Customer"):
                customers.require_by_id(uuid4())
            with pytest.raises(RepositoryNotFoundError, match="Card"):
                cards.require_by_id(uuid4())
    finally:
        _delete_customer_graph(database_engine, customer_id)


def test_account_balance_update_uses_decimal_lock_and_version(migrated_database, database_engine):
    factory = create_session_factory(database_engine)
    customer_id, account_id, *_ = _create_customer_graph(factory)
    try:
        with session_scope(factory) as session:
            updated = AccountRepository(session).update_balance(
                account_id, Decimal("75.25"), expected_version=1
            )
            assert updated.balance == Decimal("75.25")
            assert updated.version == 2

        with factory() as session:
            repository = AccountRepository(session)
            assert repository.require_by_id(account_id).balance == Decimal("75.25")
            with pytest.raises(ConcurrentUpdateError, match="expected version 1"):
                repository.update_balance(account_id, Decimal("60.00"), expected_version=1)
            with pytest.raises(InvalidRepositoryQueryError, match="Decimal"):
                repository.update_balance(account_id, 50.0)  # type: ignore[arg-type]
            with pytest.raises(RepositoryNotFoundError, match="Account"):
                repository.update_balance(uuid4(), Decimal("1.00"))
    finally:
        _delete_customer_graph(database_engine, customer_id)


def test_transaction_creation_history_order_and_transaction_ownership(
    migrated_database, database_engine
):
    factory = create_session_factory(database_engine)
    customer_id, account_id, card_id, *_ = _create_customer_graph(factory)
    transaction_ids = [uuid4() for _ in range(3)]
    expected_history = sorted(transaction_ids, reverse=True)
    rolled_back_id = uuid4()
    try:
        with session_scope(factory) as session:
            repository = TransactionRepository(session)
            repository.create(
                transaction_id=transaction_ids[0],
                account_id=account_id,
                card_id=card_id,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.COMPLETED,
                amount=Decimal("10.00"),
                balance_before=Decimal("100.00"),
                balance_after=Decimal("110.00"),
            )
            repository.create(
                transaction_id=transaction_ids[1],
                account_id=account_id,
                card_id=card_id,
                transaction_type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.COMPLETED,
                amount=Decimal("5.00"),
                balance_before=Decimal("110.00"),
                balance_after=Decimal("105.00"),
            )
            repository.create(
                transaction_id=transaction_ids[2],
                account_id=account_id,
                card_id=card_id,
                transaction_type=TransactionType.BALANCE_INQUIRY,
                status=TransactionStatus.COMPLETED,
                amount=Decimal("0.00"),
                balance_before=Decimal("105.00"),
                balance_after=Decimal("105.00"),
            )

        with factory() as session:
            repository = TransactionRepository(session)
            assert [row.id for row in repository.list_for_account(account_id, limit=2)] == [
                expected_history[0],
                expected_history[1],
            ]
            assert [
                row.id for row in repository.list_for_account(account_id, limit=2, offset=1)
            ] == [expected_history[1], expected_history[2]]
            assert repository.require_by_id(transaction_ids[0]).amount == Decimal("10.00")
            with pytest.raises(InvalidRepositoryQueryError, match="between 1 and 500"):
                repository.list_for_account(account_id, limit=0)
            with pytest.raises(InvalidRepositoryQueryError, match="negative"):
                repository.list_for_account(account_id, offset=-1)

        with pytest.raises(RepositoryWriteError, match="could not be created"):
            with session_scope(factory) as session:
                TransactionRepository(session).create(
                    account_id=account_id,
                    card_id=card_id,
                    transaction_type=TransactionType.WITHDRAWAL,
                    status=TransactionStatus.DECLINED,
                    amount=Decimal("0.00"),
                    balance_before=Decimal("105.00"),
                    balance_after=Decimal("105.00"),
                )

        with factory() as session:
            repository = TransactionRepository(session)
            repository.create(
                transaction_id=rolled_back_id,
                account_id=account_id,
                card_id=card_id,
                transaction_type=TransactionType.BALANCE_INQUIRY,
                status=TransactionStatus.COMPLETED,
                amount=Decimal("0.00"),
                balance_before=Decimal("105.00"),
                balance_after=Decimal("105.00"),
            )
            session.rollback()
        with factory() as session:
            assert TransactionRepository(session).get_by_id(rolled_back_id) is None
    finally:
        _delete_customer_graph(database_engine, customer_id)
