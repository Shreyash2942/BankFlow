"""Contract checks for versioned and secret-free BankFlow events."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.events import (
    CURRENT_EVENT_SCHEMA_VERSION,
    EVENT_SOURCE,
    PROHIBITED_EVENT_FIELDS,
    AuthenticationEventOutcome,
    AuthenticationEventPayload,
    BankFlowEvent,
    EventType,
    TransactionEventPayload,
)


def _transaction_payload(**updates) -> TransactionEventPayload:
    values = {
        "transaction_id": uuid4(),
        "customer_id": uuid4(),
        "account_id": uuid4(),
        "card_id": uuid4(),
        "transaction_type": TransactionType.WITHDRAWAL,
        "status": TransactionStatus.COMPLETED,
        "amount": Decimal("25.00"),
        "balance_before": Decimal("100.00"),
        "balance_after": Decimal("75.00"),
        "currency": "USD",
        "account_status": AccountStatus.ACTIVE,
    }
    values.update(updates)
    return TransactionEventPayload(**values)


def _event(payload=None, **updates) -> BankFlowEvent:
    values = {
        "event_id": uuid4(),
        "event_type": EventType.WITHDRAWAL_COMPLETED,
        "occurred_at": datetime(2026, 10, 5, 12, 30, tzinfo=UTC),
        "payload": payload or _transaction_payload(),
    }
    values.update(updates)
    return BankFlowEvent(**values)


def _schema_property_names(value: object) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for nested in value.values():
            names.update(_schema_property_names(nested))
    elif isinstance(value, list):
        for nested in value:
            names.update(_schema_property_names(nested))
    return names


def test_transaction_event_round_trip_preserves_exact_money_and_utc_timestamp():
    event = _event()

    encoded = event.model_dump_json(exclude_none=True)
    decoded = BankFlowEvent.model_validate_json(encoded)
    document = json.loads(encoded)

    assert decoded == event
    assert decoded.occurred_at.tzinfo is UTC
    assert document["schema_version"] == CURRENT_EVENT_SCHEMA_VERSION == 1
    assert document["source"] == EVENT_SOURCE == "bankflow.application"
    assert document["payload"]["amount"] == "25.00"
    assert document["payload"]["balance_after"] == "75.00"


def test_atm_identifier_is_an_optional_backward_compatible_field():
    legacy_event = _event()
    assert legacy_event.payload.atm_id is None
    assert "atm_id" not in json.loads(legacy_event.model_dump_json(exclude_none=True))["payload"]

    synthetic_event = _event(payload=_transaction_payload(atm_id="ATM-0007"))
    assert synthetic_event.payload.atm_id == "ATM-0007"

    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        _transaction_payload(atm_id="terminal-7")


def test_event_timestamp_must_be_aware_and_event_id_must_be_uuid4():
    with pytest.raises(ValidationError, match="timezone"):
        _event(occurred_at=datetime(2026, 10, 5, 12, 30))

    with pytest.raises(ValidationError, match="version 4"):
        _event(event_id="11111111-1111-1111-8111-111111111111")


def test_schema_version_source_and_unknown_fields_are_closed_contracts():
    event = _event()
    document = event.model_dump(mode="json")

    for field, value in (
        ("schema_version", 2),
        ("source", "another.application"),
        ("unexpected", "value"),
    ):
        invalid = {**document, field: value}
        with pytest.raises(ValidationError):
            BankFlowEvent.model_validate(invalid)


@pytest.mark.parametrize(
    ("event_type", "payload_updates"),
    [
        (EventType.WITHDRAWAL_DECLINED, {}),
        (
            EventType.WITHDRAWAL_COMPLETED,
            {"transaction_type": TransactionType.DEPOSIT},
        ),
        (
            EventType.ACCOUNT_CLOSED,
            {"account_status": AccountStatus.ACTIVE},
        ),
    ],
)
def test_transaction_payload_must_match_event_type(event_type, payload_updates):
    with pytest.raises(ValidationError, match="does not match|closed account"):
        _event(event_type=event_type, payload=_transaction_payload(**payload_updates))


def test_transaction_payload_enforces_money_and_decline_shape():
    with pytest.raises(ValidationError, match="positive"):
        _transaction_payload(amount=Decimal("0.00"))
    with pytest.raises(ValidationError, match="decimal places"):
        _transaction_payload(amount=Decimal("1.001"))
    with pytest.raises(ValidationError, match="decline reason"):
        _transaction_payload(status=TransactionStatus.DECLINED)
    with pytest.raises(ValidationError, match="Only declined"):
        _transaction_payload(decline_reason="insufficient_funds")


def test_authentication_events_allow_unknown_cards_but_require_complete_known_subjects():
    unknown_card = AuthenticationEventPayload(
        outcome=AuthenticationEventOutcome.INVALID_CREDENTIALS,
        remaining_attempts=None,
    )
    event = _event(
        event_type=EventType.AUTHENTICATION_FAILED,
        payload=unknown_card,
    )
    assert event.payload.card_id is None

    with pytest.raises(ValidationError, match="all present or all absent"):
        AuthenticationEventPayload(
            card_id=uuid4(),
            outcome=AuthenticationEventOutcome.INVALID_CREDENTIALS,
        )
    with pytest.raises(ValidationError, match="requires subject identifiers"):
        _event(
            event_type=EventType.CARD_LOCKED,
            payload=AuthenticationEventPayload(outcome=AuthenticationEventOutcome.CARD_LOCKED),
        )


def test_event_type_rejects_the_wrong_payload_family_or_outcome():
    authentication = AuthenticationEventPayload(
        customer_id=uuid4(),
        account_id=uuid4(),
        card_id=uuid4(),
        outcome=AuthenticationEventOutcome.AUTHENTICATED,
    )
    with pytest.raises(ValidationError, match="does not accept an authentication"):
        _event(event_type=EventType.DEPOSIT_COMPLETED, payload=authentication)
    with pytest.raises(ValidationError, match="does not match"):
        _event(event_type=EventType.CARD_LOCKED, payload=authentication)


def test_generated_schema_and_validation_exclude_prohibited_sensitive_fields():
    property_names = _schema_property_names(BankFlowEvent.model_json_schema())
    assert property_names.isdisjoint(PROHIBITED_EVENT_FIELDS)

    document = _event().model_dump(mode="json")
    document["payload"]["pin"] = "2468"
    with pytest.raises(ValidationError) as captured:
        BankFlowEvent.model_validate(document)
    assert "2468" not in str(captured.value)
