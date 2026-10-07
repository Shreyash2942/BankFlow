"""Deterministic coverage for Kafka producer configuration and delivery outcomes."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from confluent_kafka import KafkaError

from bankflow.config.settings import Settings
from bankflow.messaging.producer import (
    KafkaDeliveryError,
    KafkaEventProducer,
    KafkaUnavailableError,
    producer_config,
)
from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.events import BankFlowEvent, EventType, TransactionEventPayload


class FakeMessage:
    def topic(self) -> str:
        return "bankflow.transaction.events"

    def partition(self) -> int:
        return 2

    def offset(self) -> int:
        return 41


class FakeProducer:
    def __init__(
        self,
        *,
        delivery_error: KafkaError | None = None,
        remaining: int = 0,
        produce_error: Exception | None = None,
    ) -> None:
        self.delivery_error = delivery_error
        self.remaining = remaining
        self.produce_error = produce_error
        self.produced: dict[str, object] | None = None
        self.flush_timeouts: list[int] = []

    def produce(self, **kwargs) -> None:
        if self.produce_error is not None:
            raise self.produce_error
        self.produced = kwargs
        kwargs["on_delivery"](self.delivery_error, FakeMessage())

    def flush(self, timeout: int) -> int:
        self.flush_timeouts.append(timeout)
        return self.remaining


def _event() -> BankFlowEvent:
    return BankFlowEvent(
        event_id=uuid4(),
        event_type=EventType.WITHDRAWAL_COMPLETED,
        occurred_at=datetime(2026, 10, 6, 12, 0, tzinfo=UTC),
        payload=TransactionEventPayload(
            transaction_id=uuid4(),
            customer_id=uuid4(),
            account_id=uuid4(),
            card_id=uuid4(),
            transaction_type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            amount=Decimal("25.00"),
            balance_before=Decimal("100.00"),
            balance_after=Decimal("75.00"),
            currency="USD",
            account_status=AccountStatus.ACTIVE,
        ),
    )


def test_producer_configuration_enables_acknowledged_idempotent_delivery():
    settings = Settings(postgres_password="test-only", kafka_delivery_timeout_seconds=7)

    config = producer_config(settings)

    assert config == {
        "bootstrap.servers": "127.0.0.1:9093",
        "client.id": "bankflow-application-v1",
        "acks": "all",
        "enable.idempotence": True,
        "compression.type": "gzip",
        "max.in.flight.requests.per.connection": 5,
        "message.timeout.ms": 7000,
        "socket.timeout.ms": 7000,
    }


def test_publish_serializes_contract_uses_aggregate_key_and_returns_receipt():
    client = FakeProducer()
    producer = KafkaEventProducer(
        client, topic="bankflow.transaction.events", delivery_timeout_seconds=3
    )
    event = _event()

    receipt = producer.publish(event)

    assert client.produced is not None
    assert client.produced["topic"] == "bankflow.transaction.events"
    assert client.produced["key"] == str(event.payload.transaction_id).encode("ascii")
    document = json.loads(client.produced["value"])
    assert document["event_id"] == str(event.event_id)
    assert document["payload"]["amount"] == "25.00"
    assert client.produced["headers"] == {
        "event_type": "withdrawal.completed",
        "schema_version": "1",
        "source": "bankflow.application",
    }
    assert client.flush_timeouts == [3]
    assert receipt.event_id == event.event_id
    assert (receipt.topic, receipt.partition, receipt.offset) == (
        "bankflow.transaction.events",
        2,
        41,
    )


def test_delivery_callback_error_is_exposed_without_payload_details():
    error = KafkaError(KafkaError._MSG_TIMED_OUT)
    producer = KafkaEventProducer(
        FakeProducer(delivery_error=error),
        topic="bankflow.transaction.events",
        delivery_timeout_seconds=2,
    )

    with pytest.raises(KafkaDeliveryError, match="rejected"):
        producer.publish(_event())


@pytest.mark.parametrize(
    "client",
    [
        FakeProducer(remaining=1),
        FakeProducer(produce_error=BufferError("queue full")),
    ],
)
def test_unavailable_or_full_broker_queue_has_a_stable_error(client):
    producer = KafkaEventProducer(
        client, topic="bankflow.transaction.events", delivery_timeout_seconds=2
    )

    with pytest.raises(KafkaUnavailableError, match="Kafka"):
        producer.publish(_event())


def test_producer_rejects_blank_topics_and_invalid_timeouts():
    with pytest.raises(ValueError, match="topic"):
        KafkaEventProducer(FakeProducer(), topic=" ", delivery_timeout_seconds=2)
    with pytest.raises(ValueError, match="timeout"):
        KafkaEventProducer(
            FakeProducer(), topic="bankflow.transaction.events", delivery_timeout_seconds=0
        )
