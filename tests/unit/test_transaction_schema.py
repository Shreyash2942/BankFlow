"""Transaction inputs accept exact positive cents and reject unsafe money."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from bankflow.schemas import DepositRequest, TransactionHistoryQuery, WithdrawalRequest


@pytest.mark.parametrize("schema", [WithdrawalRequest, DepositRequest])
def test_transaction_amount_accepts_positive_decimal_cents(schema):
    assert schema(amount=Decimal("123.45")).amount == Decimal("123.45")


@pytest.mark.parametrize("schema", [WithdrawalRequest, DepositRequest])
@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-0.01"),
        Decimal("0.001"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("10000000000000000.00"),
        10.0,
        "10.00",
    ],
)
def test_transaction_amount_rejects_nonpositive_imprecise_or_non_decimal_values(schema, amount):
    with pytest.raises(ValidationError):
        schema(amount=amount)


@pytest.mark.parametrize(
    "values",
    [{"limit": 0}, {"limit": 501}, {"offset": -1}],
)
def test_transaction_history_query_enforces_repository_bounds(values):
    with pytest.raises(ValidationError):
        TransactionHistoryQuery(**values)
