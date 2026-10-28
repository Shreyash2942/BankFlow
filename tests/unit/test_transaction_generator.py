"""Deterministic coverage for the Day 15 synthetic event generator."""

import json
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from bankflow.messaging import serialize_event
from bankflow.models import TransactionStatus, TransactionType
from bankflow.schemas.events import AuthenticationEventPayload, EventType, TransactionEventPayload
from bankflow.synthetic import (
    SyntheticEventGenerator,
    SyntheticGeneratorConfig,
    publish_generated_events,
    validate_generated_events,
)
from scripts.transaction_generator import main


class FakePublisher:
    def __init__(self) -> None:
        self.events = []

    def publish(self, event):
        self.events.append(event)


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


def _events(*, seed: int = 42, count: int = 40):
    config = SyntheticGeneratorConfig(
        customer_count=8,
        atm_count=4,
        seed=seed,
        start_time=datetime(2026, 10, 27, 12, 0, tzinfo=UTC),
    )
    return list(SyntheticEventGenerator(config).iter_events(count))


def test_seed_reproduces_identifiers_timestamps_amounts_and_event_order():
    first = [serialize_event(event) for event in _events(seed=2942)]
    second = [serialize_event(event) for event in _events(seed=2942)]
    different = [serialize_event(event) for event in _events(seed=2943)]

    assert first == second
    assert first != different


def test_synthetic_population_has_unique_customer_account_and_card_identifiers():
    generator = SyntheticEventGenerator(
        SyntheticGeneratorConfig(customer_count=250, atm_count=10, seed=15)
    )

    assert len({profile.customer_id for profile in generator.profiles}) == 250
    assert len({profile.account_id for profile in generator.profiles}) == 250
    assert len({profile.card_id for profile in generator.profiles}) == 250


def test_generator_covers_transaction_authentication_and_decline_scenarios():
    events = _events()
    report = validate_generated_events(events)

    assert report.event_count == 40
    assert set(report.event_type_counts) == {
        event_type.value for event_type in EventType if event_type is not EventType.ACCOUNT_CLOSED
    }
    assert len({event.event_id for event in events}) == 40
    assert all(
        event.payload.atm_id in {"ATM-0001", "ATM-0002", "ATM-0003", "ATM-0004"} for event in events
    )
    assert any(isinstance(event.payload, TransactionEventPayload) for event in events)
    assert any(isinstance(event.payload, AuthenticationEventPayload) for event in events)


def test_high_volume_stream_preserves_schema_and_nonnegative_balances():
    config = SyntheticGeneratorConfig(customer_count=100, atm_count=10, seed=15)

    report = validate_generated_events(SyntheticEventGenerator(config).iter_events(10_000))

    assert report.event_count == 10_000


def test_transaction_balances_and_requested_completion_pair_are_consistent():
    events = _events(count=20)
    requested = events[3]
    completed = events[4]

    assert requested.event_type is EventType.WITHDRAWAL_REQUESTED
    assert completed.event_type is EventType.WITHDRAWAL_COMPLETED
    assert requested.payload.transaction_id == completed.payload.transaction_id
    assert requested.payload.atm_id == completed.payload.atm_id

    for event in events:
        payload = event.payload
        if not isinstance(payload, TransactionEventPayload):
            continue
        if payload.transaction_type is TransactionType.DEPOSIT:
            assert payload.balance_after == payload.balance_before + payload.amount
        elif payload.status is TransactionStatus.COMPLETED:
            if payload.transaction_type is TransactionType.WITHDRAWAL:
                assert payload.balance_after == payload.balance_before - payload.amount
            else:
                assert payload.amount == Decimal("0.00")
                assert payload.balance_after == payload.balance_before
        else:
            assert payload.balance_after == payload.balance_before


def test_unknown_card_failures_omit_subjects_but_keep_atm_provenance():
    event = _events(count=15)[14]

    assert event.event_type is EventType.AUTHENTICATION_FAILED
    assert isinstance(event.payload, AuthenticationEventPayload)
    assert event.payload.customer_id is None
    assert event.payload.account_id is None
    assert event.payload.card_id is None
    assert event.payload.atm_id == "ATM-0003"


def test_publisher_applies_configured_rate_and_validates_each_event():
    events = _events(count=3)
    publisher = FakePublisher()
    clock = FakeClock()

    report = publish_generated_events(
        events,
        publisher,
        rate_per_second=2,
        clock=clock,
        sleep=clock.sleep,
    )

    assert publisher.events == events
    assert clock.sleeps == [0.5, 0.5, 0.5]
    assert report.event_count == 3
    assert report.elapsed_seconds == 1.5
    assert report.achieved_rate == 2.0


@pytest.mark.parametrize(
    "config",
    [
        {"customer_count": 0},
        {"atm_count": 0},
        {"timestamp_step_milliseconds": 0},
        {"start_time": datetime(2026, 1, 1)},
    ],
)
def test_generator_configuration_rejects_invalid_bounds(config):
    with pytest.raises(ValueError):
        SyntheticGeneratorConfig(**config)

    with pytest.raises(ValueError, match="count"):
        list(SyntheticEventGenerator().iter_events(-1))


def test_cli_dry_run_validates_without_loading_kafka_settings(capsys):
    result = main(
        [
            "--count",
            "20",
            "--seed",
            "15",
            "--customers",
            "5",
            "--atms",
            "2",
            "--dry-run",
            "--env-file",
            "does-not-exist.env",
        ]
    )

    document = json.loads(capsys.readouterr().out)
    assert result == 0
    assert document["mode"] == "dry-run"
    assert document["event_count"] == 20
    assert document["event_types"]["withdrawal.declined"] == 2
