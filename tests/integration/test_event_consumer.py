"""PostgreSQL event-store persistence and deduplication coverage."""

import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from bankflow.database.session import create_session_factory
from bankflow.messaging import KafkaMessageMetadata, PostgresEventStore
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
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1",
        reason="event-store tests require PostgreSQL opt-in",
    ),
]


def _event() -> BankFlowEvent:
    return BankFlowEvent(
        event_id=uuid4(),
        event_type=EventType.WITHDRAWAL_COMPLETED,
        occurred_at=datetime(2026, 10, 9, 15, 30, tzinfo=UTC),
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


def test_event_store_persists_exact_payload_and_deduplicates_event_id(
    migrated_database, database_engine
):
    event = _event()
    metadata = KafkaMessageMetadata("bankflow.test.events", 2, 17)
    store = PostgresEventStore(
        create_session_factory(database_engine), consumer_group="bankflow-test-consumer"
    )
    try:
        assert store.persist(event, metadata) is True
        assert store.persist(event, KafkaMessageMetadata(metadata.topic, 2, 18)) is False

        with Session(database_engine) as session:
            stored = session.get(ConsumedEvent, event.event_id)
            assert stored is not None
            assert stored.event_type == EventType.WITHDRAWAL_COMPLETED.value
            assert stored.payload["amount"] == "25.00"
            assert stored.payload["balance_after"] == "75.00"
            assert (stored.topic, stored.partition, stored.offset) == (
                "bankflow.test.events",
                2,
                17,
            )
            assert stored.consumer_group == "bankflow-test-consumer"
            assert stored.consumed_at.tzinfo is not None
    finally:
        with database_engine.begin() as connection:
            connection.execute(
                ConsumedEvent.__table__.delete().where(ConsumedEvent.event_id == event.event_id)
            )


def test_event_store_deduplicates_kafka_position(migrated_database, database_engine):
    first, second = _event(), _event()
    metadata = KafkaMessageMetadata("bankflow.test.events", 3, 22)
    store = PostgresEventStore(
        create_session_factory(database_engine), consumer_group="bankflow-test-consumer"
    )
    try:
        assert store.persist(first, metadata) is True
        assert store.persist(second, metadata) is False
        with Session(database_engine) as session:
            assert session.get(ConsumedEvent, first.event_id) is not None
            assert session.get(ConsumedEvent, second.event_id) is None
    finally:
        with database_engine.begin() as connection:
            connection.execute(
                ConsumedEvent.__table__.delete().where(
                    ConsumedEvent.event_id.in_([first.event_id, second.event_id])
                )
            )
