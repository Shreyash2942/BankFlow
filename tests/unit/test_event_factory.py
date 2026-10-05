"""Mapping and serialization checks for the Day 8 event factory."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import SecretStr

from bankflow.messaging import (
    EventFactoryError,
    balance_viewed_event,
    deserialize_event,
    event_from_authentication_result,
    event_from_transaction_result,
    serialize_event,
    session_ended_event,
    withdrawal_requested_event,
)
from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.account import AccountBalance
from bankflow.schemas.authentication import (
    AuthenticationOutcome,
    AuthenticationResult,
    AuthenticationSession,
)
from bankflow.schemas.events import AuthenticationEventPayload, EventType, TransactionEventPayload
from bankflow.schemas.transaction import TransactionResult, WithdrawalRequest

NOW = datetime(2026, 10, 5, 16, 0, tzinfo=UTC)


@pytest.fixture
def authentication() -> AuthenticationSession:
    return AuthenticationSession(
        customer_id=uuid4(),
        account_id=uuid4(),
        card_id=uuid4(),
    )


def _result(**updates) -> TransactionResult:
    values = {
        "transaction_id": uuid4(),
        "transaction_type": TransactionType.WITHDRAWAL,
        "status": TransactionStatus.COMPLETED,
        "amount": Decimal("25.00"),
        "balance_before": Decimal("100.00"),
        "balance_after": Decimal("75.00"),
        "account_status": AccountStatus.ACTIVE,
    }
    values.update(updates)
    return TransactionResult(**values)


def test_factory_maps_completed_declined_and_closed_transaction_results(authentication):
    completed = event_from_transaction_result(
        EventType.WITHDRAWAL_COMPLETED,
        _result(),
        authentication,
        currency="USD",
        occurred_at=NOW,
    )
    declined = event_from_transaction_result(
        EventType.WITHDRAWAL_DECLINED,
        _result(
            status=TransactionStatus.DECLINED,
            balance_after=Decimal("100.00"),
            decline_reason="insufficient_funds",
        ),
        authentication,
        currency="USD",
        occurred_at=NOW,
    )
    closed = event_from_transaction_result(
        EventType.ACCOUNT_CLOSED,
        _result(balance_after=Decimal("0.00"), account_status=AccountStatus.CLOSED),
        authentication,
        currency="USD",
        occurred_at=NOW,
    )

    assert isinstance(completed.payload, TransactionEventPayload)
    assert completed.payload.customer_id == authentication.customer_id
    assert declined.payload.decline_reason == "insufficient_funds"
    assert closed.payload.account_status is AccountStatus.CLOSED


def test_transaction_factory_rejects_an_event_type_result_mismatch(authentication):
    with pytest.raises(EventFactoryError, match="does not match"):
        event_from_transaction_result(
            EventType.DEPOSIT_COMPLETED,
            _result(),
            authentication,
            currency="USD",
        )


def test_balance_and_requested_withdrawal_factories_use_exact_snapshots(authentication):
    transaction_id = uuid4()
    viewed = balance_viewed_event(
        AccountBalance(
            account_id=authentication.account_id,
            transaction_id=transaction_id,
            balance=Decimal("100.00"),
            currency="USD",
            status=AccountStatus.ACTIVE,
            version=1,
        ),
        authentication,
        occurred_at=NOW,
    )
    requested = withdrawal_requested_event(
        uuid4(),
        WithdrawalRequest(amount=Decimal("40.00")),
        authentication,
        balance_before=Decimal("100.00"),
        currency="USD",
        account_status=AccountStatus.ACTIVE,
        occurred_at=NOW,
    )

    assert viewed.event_type is EventType.BALANCE_VIEWED
    assert viewed.payload.transaction_id == transaction_id
    assert viewed.payload.amount == Decimal("0.00")
    assert requested.event_type is EventType.WITHDRAWAL_REQUESTED
    assert requested.payload.status is TransactionStatus.PENDING
    assert requested.payload.balance_before == requested.payload.balance_after


def test_authentication_factory_omits_session_secret_and_handles_unknown_card(authentication):
    session_secret = "opaque-session-secret-that-must-not-appear"
    succeeded = event_from_authentication_result(
        AuthenticationResult(
            authenticated=True,
            outcome=AuthenticationOutcome.AUTHENTICATED,
            session_token=SecretStr(session_secret),
            expires_in_seconds=900,
        ),
        authentication=authentication,
        occurred_at=NOW,
    )
    failed = event_from_authentication_result(
        AuthenticationResult(
            authenticated=False,
            outcome=AuthenticationOutcome.INVALID_CREDENTIALS,
            remaining_attempts=None,
        ),
        occurred_at=NOW,
    )

    assert isinstance(succeeded.payload, AuthenticationEventPayload)
    assert succeeded.event_type is EventType.AUTHENTICATION_SUCCEEDED
    assert failed.event_type is EventType.AUTHENTICATION_FAILED
    assert failed.payload.card_id is None
    assert session_secret not in serialize_event(succeeded).decode("utf-8")


def test_authentication_factory_requires_subjects_for_success_and_lock():
    for result in (
        AuthenticationResult(
            authenticated=True,
            outcome=AuthenticationOutcome.AUTHENTICATED,
            session_token=SecretStr("session-secret"),
            expires_in_seconds=900,
        ),
        AuthenticationResult(
            authenticated=False,
            outcome=AuthenticationOutcome.CARD_LOCKED,
            remaining_attempts=0,
        ),
    ):
        with pytest.raises(EventFactoryError, match="subject|does not match"):
            event_from_authentication_result(result)


def test_authentication_factory_rejects_inconsistent_service_results(authentication):
    inconsistent = AuthenticationResult(
        authenticated=False,
        outcome=AuthenticationOutcome.AUTHENTICATED,
        session_token=SecretStr("unexpected-session-secret"),
        expires_in_seconds=900,
    )
    missing_session = AuthenticationResult(
        authenticated=True,
        outcome=AuthenticationOutcome.AUTHENTICATED,
        expires_in_seconds=900,
    )

    with pytest.raises(EventFactoryError, match="flags and outcome"):
        event_from_authentication_result(inconsistent, authentication=authentication)
    with pytest.raises(EventFactoryError, match="session state"):
        event_from_authentication_result(missing_session, authentication=authentication)


def test_session_end_and_utf8_serialization_round_trip(authentication):
    event = session_ended_event(authentication, occurred_at=NOW)

    encoded = serialize_event(event)
    decoded = deserialize_event(encoded)

    assert decoded == event
    assert event.event_type is EventType.SESSION_ENDED
    assert event.payload.card_id == authentication.card_id
    assert isinstance(encoded, bytes)
