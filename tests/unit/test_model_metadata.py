from decimal import Decimal

from sqlalchemy import Enum, Numeric

from bankflow.database.base import Base
from bankflow.models import Account, Card, Transaction


def test_day3_tables_are_registered_in_application_schema():
    assert {
        "bankflow.customers",
        "bankflow.accounts",
        "bankflow.cards",
        "bankflow.transactions",
        "bankflow.audit_events",
    }.issubset(Base.metadata.tables)


def test_money_columns_are_fixed_precision_decimal():
    for column in (
        Account.__table__.c.balance,
        Transaction.__table__.c.amount,
        Transaction.__table__.c.balance_before,
        Transaction.__table__.c.balance_after,
    ):
        assert isinstance(column.type, Numeric)
        assert (column.type.precision, column.type.scale, column.type.asdecimal) == (18, 2, True)
        assert column.type.python_type is Decimal


def test_status_enums_use_named_varchar_constraints():
    for column in (
        Account.__table__.c.account_type,
        Account.__table__.c.status,
        Card.__table__.c.status,
        Transaction.__table__.c.transaction_type,
        Transaction.__table__.c.status,
    ):
        assert isinstance(column.type, Enum)
        assert column.type.native_enum is False
        assert column.type.create_constraint is True
        assert column.type.name
