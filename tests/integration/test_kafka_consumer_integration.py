"""Live Kafka-to-PostgreSQL consumer, deduplication, and invalid-message test."""

import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from confluent_kafka import Producer
from sqlalchemy.orm import Session

from bankflow.database.session import create_session_factory
from bankflow.messaging import (
    ConsumeStatus,
    KafkaEventConsumer,
    KafkaEventProducer,
    producer_config,
)
from bankflow.models import (
    AccountStatus,
    ConsumedEvent,
    TransactionStatus,
    TransactionType,
)
from bankflow.schemas.events import BankFlowEvent, EventType, TransactionEventPayload

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1" or os.getenv("BANKFLOW_RUN_KAFKA_TESTS") != "1",
        reason="live consumer test requires PostgreSQL and Kafka opt-ins",
    ),
]


def _event() -> BankFlowEvent:
    return BankFlowEvent(
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
            amount=Decimal("7.25"),
            balance_before=Decimal("30.00"),
            balance_after=Decimal("37.25"),
            currency="USD",
            account_status=AccountStatus.ACTIVE,
        ),
    )


def _next_result(consumer: KafkaEventConsumer):
    for _ in range(20):
        result = consumer.consume_once()
        if result is not None:
            return result
    pytest.fail("Kafka consumer did not receive the expected message.")


def test_live_consumer_persists_deduplicates_and_skips_invalid_message(
    migrated_database, database_engine, kafka_test_settings
):
    settings = kafka_test_settings
    event = _event()
    producer = KafkaEventProducer.from_settings(settings)
    consumer = KafkaEventConsumer.from_settings(settings, create_session_factory(database_engine))
    raw_producer = Producer(producer_config(settings))
    try:
        producer.publish(event)
        first = _next_result(consumer)
        assert first.status is ConsumeStatus.PERSISTED

        producer.publish(event)
        duplicate = _next_result(consumer)
        assert duplicate.status is ConsumeStatus.DUPLICATE

        raw_producer.produce(settings.kafka_transaction_topic, value=b'{"schema_version":999}')
        assert raw_producer.flush(5) == 0
        invalid = _next_result(consumer)
        assert invalid.status is ConsumeStatus.INVALID

        with Session(database_engine) as session:
            stored = session.get(ConsumedEvent, event.event_id)
            assert stored is not None
            assert stored.payload["amount"] == "7.25"
            assert stored.consumer_group == settings.kafka_consumer_group
    finally:
        consumer.close()
        producer.close()
        raw_producer.flush(1)
        with database_engine.begin() as connection:
            connection.execute(
                ConsumedEvent.__table__.delete().where(ConsumedEvent.event_id == event.event_id)
            )
