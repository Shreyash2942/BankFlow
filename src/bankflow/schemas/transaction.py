"""Exact-money request and response contracts for banking transactions."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from bankflow.models import AccountStatus, TransactionStatus, TransactionType

PositiveMoney = Annotated[
    Decimal,
    Field(strict=True, gt=0, max_digits=18, decimal_places=2, allow_inf_nan=False),
]


class WithdrawalRequest(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True, extra="forbid")

    amount: PositiveMoney


class DepositRequest(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True, extra="forbid")

    amount: PositiveMoney


class TransactionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    transaction_id: UUID
    transaction_type: TransactionType
    status: TransactionStatus
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    account_status: AccountStatus
    decline_reason: str | None = None


class TransactionHistoryQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class TransactionHistoryItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    transaction_id: UUID
    transaction_type: TransactionType
    status: TransactionStatus
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    decline_reason: str | None
    created_at: datetime


class TransactionHistory(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_id: UUID
    limit: int
    offset: int
    items: tuple[TransactionHistoryItem, ...]
