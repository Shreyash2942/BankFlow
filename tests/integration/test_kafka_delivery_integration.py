"""Live Kafka acknowledgement and round-trip smoke test."""

import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from confluent_kafka import Consumer

from bankflow.config.settings import load_settings
from bankflow.messaging import KafkaEventProducer, deserialize_event
from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.events import BankFlowEvent, EventType, TransactionEventPayload

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_KAFKA_TESTS") != "1",
        reason="Live Kafka test requires explicit opt-in",
    ),
]


def test_live_producer_receives_ack_and_event_round_trips():
    settings = load_settings(".env.test")
    producer = KafkaEventProducer.from_settings(settings)
    event = BankFlowEvent(
        event_id=uuid4(),
        event_type=EventType.DEPOSIT_COMPLETED,
        occurred_at=datetime.now(UTC),
        payload=TransactionEventPayload(
            transaction_id=uuid4(),
            customer_id=uuid4(),
            account_id=uuid4(),
            card_id=uuid4(),
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=Decimal("10.25"),
            balance_before=Decimal("40.00"),
            balance_after=Decimal("50.25"),
            currency="USD",
            account_status=AccountStatus.ACTIVE,
        ),
    )

    receipt = producer.publish(event)
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": f"bankflow-day9-test-{uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    try:
        consumer.subscribe([settings.kafka_transaction_topic])
        received = None
        for _ in range(20):
            message = consumer.poll(0.5)
            if message is None or message.error():
                continue
            candidate = deserialize_event(message.value())
            if candidate.event_id == event.event_id:
                received = candidate
                break
    finally:
        consumer.close()
        producer.close()

    assert receipt.topic == settings.kafka_transaction_topic
    assert receipt.partition >= 0
    assert receipt.offset >= 0
    assert received == event
