"""Create and serialize schema-version-1 events from application-service results."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import ValidationError

from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.account import AccountBalance
from bankflow.schemas.authentication import (
    AuthenticationOutcome,
    AuthenticationResult,
    AuthenticationSession,
)
from bankflow.schemas.events import (
    AuthenticationEventOutcome,
    AuthenticationEventPayload,
    BankFlowEvent,
    EventType,
    TransactionEventPayload,
)
from bankflow.schemas.transaction import TransactionResult, WithdrawalRequest


class EventFactoryError(ValueError):
    """Application data cannot form the requested canonical event."""


def _envelope(
    event_type: EventType,
    payload: TransactionEventPayload | AuthenticationEventPayload,
    *,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    try:
        return BankFlowEvent(
            event_id=event_id or uuid4(),
            event_type=event_type,
            occurred_at=occurred_at or datetime.now(UTC),
            payload=payload,
        )
    except ValidationError as exc:
        raise EventFactoryError(
            "Application data does not match the requested event type."
        ) from exc


def event_from_transaction_result(
    event_type: EventType,
    result: TransactionResult,
    authentication: AuthenticationSession,
    *,
    currency: str,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    """Map a committed or declined transaction result without adding broker I/O."""
    payload = TransactionEventPayload(
        transaction_id=result.transaction_id,
        customer_id=authentication.customer_id,
        account_id=authentication.account_id,
        card_id=authentication.card_id,
        transaction_type=result.transaction_type,
        status=result.status,
        amount=result.amount,
        balance_before=result.balance_before,
        balance_after=result.balance_after,
        currency=currency,
        account_status=result.account_status,
        decline_reason=result.decline_reason,
    )
    return _envelope(event_type, payload, event_id=event_id, occurred_at=occurred_at)


def balance_viewed_event(
    balance: AccountBalance,
    authentication: AuthenticationSession,
    *,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    payload = TransactionEventPayload(
        transaction_id=balance.transaction_id,
        customer_id=authentication.customer_id,
        account_id=authentication.account_id,
        card_id=authentication.card_id,
        transaction_type=TransactionType.BALANCE_INQUIRY,
        status=TransactionStatus.COMPLETED,
        amount=Decimal("0.00"),
        balance_before=balance.balance,
        balance_after=balance.balance,
        currency=balance.currency,
        account_status=balance.status,
    )
    return _envelope(
        EventType.BALANCE_VIEWED,
        payload,
        event_id=event_id,
        occurred_at=occurred_at,
    )


def withdrawal_requested_event(
    transaction_id: UUID,
    request: WithdrawalRequest,
    authentication: AuthenticationSession,
    *,
    balance_before: Decimal,
    currency: str,
    account_status: AccountStatus,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    payload = TransactionEventPayload(
        transaction_id=transaction_id,
        customer_id=authentication.customer_id,
        account_id=authentication.account_id,
        card_id=authentication.card_id,
        transaction_type=TransactionType.WITHDRAWAL,
        status=TransactionStatus.PENDING,
        amount=request.amount,
        balance_before=balance_before,
        balance_after=balance_before,
        currency=currency,
        account_status=account_status,
    )
    return _envelope(
        EventType.WITHDRAWAL_REQUESTED,
        payload,
        event_id=event_id,
        occurred_at=occurred_at,
    )


def event_from_authentication_result(
    result: AuthenticationResult,
    *,
    authentication: AuthenticationSession | None = None,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    authenticated_outcome = result.outcome is AuthenticationOutcome.AUTHENTICATED
    if result.authenticated is not authenticated_outcome:
        raise EventFactoryError("Authentication result flags and outcome disagree.")
    has_session_token = result.session_token is not None
    if authenticated_outcome != has_session_token:
        raise EventFactoryError("Authentication result session state is inconsistent.")
    event_type = {
        AuthenticationOutcome.AUTHENTICATED: EventType.AUTHENTICATION_SUCCEEDED,
        AuthenticationOutcome.INVALID_CREDENTIALS: EventType.AUTHENTICATION_FAILED,
        AuthenticationOutcome.CARD_LOCKED: EventType.CARD_LOCKED,
        AuthenticationOutcome.CARD_UNAVAILABLE: EventType.AUTHENTICATION_FAILED,
    }[result.outcome]
    if authenticated_outcome and authentication is None:
        raise EventFactoryError("Authenticated events require subject identifiers.")
    payload = AuthenticationEventPayload(
        customer_id=authentication.customer_id if authentication else None,
        account_id=authentication.account_id if authentication else None,
        card_id=authentication.card_id if authentication else None,
        outcome=AuthenticationEventOutcome(result.outcome.value),
        remaining_attempts=result.remaining_attempts,
    )
    return _envelope(event_type, payload, event_id=event_id, occurred_at=occurred_at)


def session_ended_event(
    authentication: AuthenticationSession,
    *,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> BankFlowEvent:
    payload = AuthenticationEventPayload(
        customer_id=authentication.customer_id,
        account_id=authentication.account_id,
        card_id=authentication.card_id,
        outcome=AuthenticationEventOutcome.SESSION_ENDED,
    )
    return _envelope(
        EventType.SESSION_ENDED,
        payload,
        event_id=event_id,
        occurred_at=occurred_at,
    )


def serialize_event(event: BankFlowEvent) -> bytes:
    """Return compact UTF-8 JSON; Decimal values remain exact JSON strings."""
    return event.model_dump_json(exclude_none=True).encode("utf-8")


def deserialize_event(value: bytes | str) -> BankFlowEvent:
    """Validate a complete envelope before a consumer accepts it."""
    return BankFlowEvent.model_validate_json(value)
