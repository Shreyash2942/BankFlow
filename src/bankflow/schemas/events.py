"""Versioned, secret-free contracts for BankFlow application events."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from bankflow.models import AccountStatus, TransactionStatus, TransactionType

CURRENT_EVENT_SCHEMA_VERSION = 1
EVENT_SOURCE = "bankflow.application"
PROHIBITED_EVENT_FIELDS = frozenset(
    {
        "card_token",
        "database_password",
        "password",
        "pin",
        "pin_hash",
        "redis_password",
        "session_token",
    }
)

CurrencyCode = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"),
]
NonNegativeMoney = Annotated[
    Decimal,
    Field(strict=True, ge=0, max_digits=18, decimal_places=2, allow_inf_nan=False),
]
DeclineReason = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)
]
AtmIdentifier = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^ATM-[A-Z0-9]{4,12}$"),
]


class EventType(StrEnum):
    AUTHENTICATION_SUCCEEDED = "authentication.succeeded"
    AUTHENTICATION_FAILED = "authentication.failed"
    CARD_LOCKED = "card.locked"
    BALANCE_VIEWED = "balance.viewed"
    WITHDRAWAL_REQUESTED = "withdrawal.requested"
    WITHDRAWAL_COMPLETED = "withdrawal.completed"
    WITHDRAWAL_DECLINED = "withdrawal.declined"
    DEPOSIT_COMPLETED = "deposit.completed"
    ACCOUNT_CLOSED = "account.closed"
    SESSION_ENDED = "session.ended"


class AuthenticationEventOutcome(StrEnum):
    AUTHENTICATED = "authenticated"
    INVALID_CREDENTIALS = "invalid_credentials"
    CARD_LOCKED = "card_locked"
    CARD_UNAVAILABLE = "card_unavailable"
    SESSION_ENDED = "session_ended"


class TransactionEventPayload(BaseModel):
    """Exact financial result without customer names or credential material."""

    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)

    kind: Literal["transaction"] = "transaction"
    transaction_id: UUID
    customer_id: UUID
    account_id: UUID
    card_id: UUID | None = None
    transaction_type: TransactionType
    status: TransactionStatus
    amount: NonNegativeMoney
    balance_before: NonNegativeMoney
    balance_after: NonNegativeMoney
    currency: CurrencyCode
    account_status: AccountStatus
    decline_reason: DeclineReason | None = None
    atm_id: AtmIdentifier | None = None

    @model_validator(mode="after")
    def validate_financial_shape(self) -> Self:
        if self.transaction_type is TransactionType.BALANCE_INQUIRY:
            if self.amount != 0:
                raise ValueError("Balance-inquiry event amounts must be zero.")
        elif self.amount <= 0:
            raise ValueError("Balance-changing event amounts must be positive.")

        if self.status is TransactionStatus.DECLINED:
            if self.decline_reason is None:
                raise ValueError("Declined transaction events require a decline reason.")
        elif self.decline_reason is not None:
            raise ValueError("Only declined transaction events may include a decline reason.")
        return self


class AuthenticationEventPayload(BaseModel):
    """Authentication outcome containing identifiers only when the card is known."""

    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)

    kind: Literal["authentication"] = "authentication"
    customer_id: UUID | None = None
    account_id: UUID | None = None
    card_id: UUID | None = None
    outcome: AuthenticationEventOutcome
    remaining_attempts: int | None = Field(default=None, ge=0, le=10)
    atm_id: AtmIdentifier | None = None

    @model_validator(mode="after")
    def keep_subject_identifiers_complete(self) -> Self:
        identifiers = (self.customer_id, self.account_id, self.card_id)
        if any(value is not None for value in identifiers) and not all(
            value is not None for value in identifiers
        ):
            raise ValueError(
                "Authentication subject identifiers must be all present or all absent."
            )
        return self


EventPayload = Annotated[
    TransactionEventPayload | AuthenticationEventPayload,
    Field(discriminator="kind"),
]

_TRANSACTION_EVENT_SHAPES = {
    EventType.BALANCE_VIEWED: (TransactionType.BALANCE_INQUIRY, TransactionStatus.COMPLETED),
    EventType.WITHDRAWAL_REQUESTED: (TransactionType.WITHDRAWAL, TransactionStatus.PENDING),
    EventType.WITHDRAWAL_COMPLETED: (TransactionType.WITHDRAWAL, TransactionStatus.COMPLETED),
    EventType.WITHDRAWAL_DECLINED: (TransactionType.WITHDRAWAL, TransactionStatus.DECLINED),
    EventType.DEPOSIT_COMPLETED: (TransactionType.DEPOSIT, TransactionStatus.COMPLETED),
    EventType.ACCOUNT_CLOSED: (TransactionType.WITHDRAWAL, TransactionStatus.COMPLETED),
}
_AUTHENTICATION_EVENT_OUTCOMES = {
    EventType.AUTHENTICATION_SUCCEEDED: {AuthenticationEventOutcome.AUTHENTICATED},
    EventType.AUTHENTICATION_FAILED: {
        AuthenticationEventOutcome.INVALID_CREDENTIALS,
        AuthenticationEventOutcome.CARD_UNAVAILABLE,
    },
    EventType.CARD_LOCKED: {AuthenticationEventOutcome.CARD_LOCKED},
    EventType.SESSION_ENDED: {AuthenticationEventOutcome.SESSION_ENDED},
}


class BankFlowEvent(BaseModel):
    """Canonical schema-version-1 envelope consumed by all BankFlow event topics."""

    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)

    event_id: UUID4
    event_type: EventType
    schema_version: Literal[1] = CURRENT_EVENT_SCHEMA_VERSION
    occurred_at: AwareDatetime
    source: Literal["bankflow.application"] = EVENT_SOURCE
    payload: EventPayload

    @field_validator("occurred_at")
    @classmethod
    def normalize_timestamp_to_utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_event_type_matches_payload(self) -> Self:
        if isinstance(self.payload, TransactionEventPayload):
            expected = _TRANSACTION_EVENT_SHAPES.get(self.event_type)
            if expected is None:
                raise ValueError("The event type does not accept a transaction payload.")
            actual = (self.payload.transaction_type, self.payload.status)
            if actual != expected:
                raise ValueError("The transaction payload does not match the event type.")
            if (
                self.event_type is EventType.ACCOUNT_CLOSED
                and self.payload.account_status is not AccountStatus.CLOSED
            ):
                raise ValueError("Account-closed events require a closed account status.")
        else:
            allowed = _AUTHENTICATION_EVENT_OUTCOMES.get(self.event_type)
            if allowed is None:
                raise ValueError("The event type does not accept an authentication payload.")
            if self.payload.outcome not in allowed:
                raise ValueError("The authentication payload does not match the event type.")
            if (
                self.event_type
                in {
                    EventType.AUTHENTICATION_SUCCEEDED,
                    EventType.CARD_LOCKED,
                    EventType.SESSION_ENDED,
                }
                and self.payload.card_id is None
            ):
                raise ValueError("This authentication event requires subject identifiers.")
        return self
