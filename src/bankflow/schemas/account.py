"""Account-operation responses exposed by the service layer."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from bankflow.models import AccountStatus


class AccountBalance(BaseModel):
    """A consistent balance snapshot and its persisted inquiry transaction."""

    model_config = ConfigDict(frozen=True)

    account_id: UUID
    transaction_id: UUID
    balance: Decimal
    currency: str
    status: AccountStatus
    version: int
