"""Deterministic consumer configuration, validation, and offset tests."""

import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from confluent_kafka import KafkaError, KafkaException
from sqlalchemy.exc import SQLAlchemyError

from bankflow.config.settings import Settings
from bankflow.messaging.consumer import (
    ConsumeStatus,
    EventPersistenceError,
    KafkaConsumerError,
    KafkaEventConsumer,
    StructuredJsonFormatter,
    consumer_config,
)
from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.events import BankFlowEvent, EventType, TransactionEventPayload


class FakeMessage:
    def __init__(self, value: bytes, *, error: KafkaError | None = None, offset: int = 8) -> None:
        self._value = value
        self._error = error
        self._offset = offset

    def value(self) -> bytes:
        return self._value

    def error(self) -> KafkaError | None:
        return self._error

    def topic(self) -> str:
        return "bankflow.transaction.events"

    def partition(self) -> int:
        return 1

    def offset(self) -> int:
        return self._offset


class FakeConsumer:
    def __init__(
        self, messages=None, *, poll_error=None, commit_error=None, operation_log=None
    ) -> None:
        self.messages = list(messages or [])
        self.poll_error = poll_error
        self.commit_error = commit_error
        self.operation_log = operation_log
        self.subscriptions: list[list[str]] = []
        self.commits: list[FakeMessage] = []
        self.poll_timeouts: list[float] = []
        self.closed = False

    def subscribe(self, topics: list[str]) -> None:
        self.subscriptions.append(topics)

    def poll(self, timeout: float):
        self.poll_timeouts.append(timeout)
        if self.poll_error is not None:
            raise self.poll_error
        return self.messages.pop(0) if self.messages else None

    def commit(self, *, message, asynchronous: bool):
        assert asynchronous is False
        if self.commit_error is not None:
            raise self.commit_error
        if self.operation_log is not None:
            self.operation_log.append("commit")
        self.commits.append(message)

    def close(self) -> None:
        self.closed = True


class FakeStore:
    def __init__(
        self, *, persisted: bool = True, error: Exception | None = None, operation_log=None
    ) -> None:
        self.persisted = persisted
        self.error = error
        self.operation_log = operation_log
        self.calls = []

    def persist(self, event, metadata) -> bool:
        if self.error is not None:
            raise self.error
        if self.operation_log is not None:
            self.operation_log.append("persist")
        self.calls.append((event, metadata))
        return self.persisted


def _event() -> BankFlowEvent:
    return BankFlowEvent(
        event_id=uuid4(),
        event_type=EventType.DEPOSIT_COMPLETED,
        occurred_at=datetime(2026, 10, 9, 12, 0, tzinfo=UTC),
        payload=TransactionEventPayload(
            transaction_id=uuid4(),
            customer_id=uuid4(),
            account_id=uuid4(),
            card_id=uuid4(),
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=Decimal("12.50"),
            balance_before=Decimal("10.00"),
            balance_after=Decimal("22.50"),
            currency="USD",
            account_status=AccountStatus.ACTIVE,
        ),
    )


def _consumer(client: FakeConsumer, store: FakeStore) -> KafkaEventConsumer:
    return KafkaEventConsumer(
        client,
        store,
        topic="bankflow.transaction.events",
        poll_timeout_seconds=2.5,
    )


def test_consumer_configuration_uses_manual_commits_and_read_committed_messages():
    settings = Settings(postgres_password="test-only")

    assert consumer_config(settings) == {
        "bootstrap.servers": "127.0.0.1:9093",
        "group.id": "bankflow-operational-v1",
        "client.id": "bankflow-operational-consumer-v1",
        "enable.auto.commit": False,
        "enable.auto.offset.store": False,
        "auto.offset.reset": "earliest",
        "isolation.level": "read_committed",
    }


@pytest.mark.parametrize(
    ("persisted", "expected"),
    [(True, ConsumeStatus.PERSISTED), (False, ConsumeStatus.DUPLICATE)],
)
def test_valid_events_are_persisted_or_deduplicated_before_offset_commit(persisted, expected):
    event = _event()
    message = FakeMessage(event.model_dump_json().encode())
    operations = []
    client = FakeConsumer([message], operation_log=operations)
    store = FakeStore(persisted=persisted, operation_log=operations)
    consumer = _consumer(client, store)

    result = consumer.consume_once()

    assert result is not None and result.status is expected
    assert result.event_id == event.event_id
    assert len(store.calls) == 1
    assert store.calls[0][1].offset == 8
    assert client.commits == [message]
    assert client.subscriptions == [["bankflow.transaction.events"]]
    assert client.poll_timeouts == [2.5]
    assert operations == ["persist", "commit"]


def test_invalid_event_is_logged_without_payload_and_committed(caplog):
    submitted = b'{"pin":"2468","schema_version":999}'
    message = FakeMessage(submitted)
    client = FakeConsumer([message])
    store = FakeStore()

    with caplog.at_level(logging.WARNING):
        result = _consumer(client, store).consume_once()

    assert result is not None and result.status is ConsumeStatus.INVALID
    assert store.calls == []
    assert client.commits == [message]
    assert "2468" not in caplog.text
    assert caplog.records[-1].consume_status == "invalid"


def test_persistence_failure_does_not_commit_offset():
    message = FakeMessage(_event().model_dump_json().encode())
    client = FakeConsumer([message])
    consumer = _consumer(client, FakeStore(error=SQLAlchemyError("database unavailable")))

    with pytest.raises(EventPersistenceError, match="persistence"):
        consumer.consume_once()

    assert client.commits == []


def test_broker_poll_and_commit_failures_have_stable_errors():
    poll_client = FakeConsumer(poll_error=KafkaException(KafkaError(KafkaError._ALL_BROKERS_DOWN)))
    with pytest.raises(KafkaConsumerError, match="polling"):
        _consumer(poll_client, FakeStore()).consume_once()

    message = FakeMessage(_event().model_dump_json().encode())
    commit_client = FakeConsumer(
        [message], commit_error=KafkaException(KafkaError(KafkaError._TIMED_OUT))
    )
    with pytest.raises(KafkaConsumerError, match="commit"):
        _consumer(commit_client, FakeStore()).consume_once()


def test_graceful_shutdown_closes_consumer_without_polling():
    client = FakeConsumer()
    consumer = _consumer(client, FakeStore())
    consumer.request_shutdown()

    assert consumer.run() == 0
    assert client.subscriptions == [["bankflow.transaction.events"]]
    assert client.poll_timeouts == []
    assert client.closed is True


def test_structured_formatter_emits_selected_fields_without_payload():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "processed", (), None)
    record.event_id = str(uuid4())
    record.event_type = "deposit.completed"
    record.payload = {"pin": "must-not-appear"}

    document = json.loads(StructuredJsonFormatter().format(record))

    assert document["event_id"] == record.event_id
    assert document["event_type"] == "deposit.completed"
    assert "payload" not in document
