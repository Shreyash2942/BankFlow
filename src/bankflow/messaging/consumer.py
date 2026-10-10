"""Validated Kafka consumption with transactional event-store persistence."""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from threading import Event
from typing import Protocol
from uuid import UUID

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from bankflow.config.settings import Settings
from bankflow.database.session import session_scope
from bankflow.messaging.event_factory import deserialize_event
from bankflow.models import ConsumedEvent
from bankflow.schemas.events import BankFlowEvent

LOGGER = logging.getLogger(__name__)


class KafkaConsumerError(RuntimeError):
    """A Kafka message could not be polled or committed safely."""


class EventPersistenceError(RuntimeError):
    """A validated event could not be committed to the event store."""


class ConsumeStatus(StrEnum):
    PERSISTED = "persisted"
    DUPLICATE = "duplicate"
    INVALID = "invalid"


@dataclass(frozen=True)
class KafkaMessageMetadata:
    topic: str
    partition: int
    offset: int


@dataclass(frozen=True)
class ConsumeResult:
    status: ConsumeStatus
    metadata: KafkaMessageMetadata
    event_id: UUID | None = None


class EventStore(Protocol):
    def persist(self, event: BankFlowEvent, metadata: KafkaMessageMetadata) -> bool: ...


class PostgresEventStore:
    """Persist validated envelopes once by event ID or Kafka position."""

    def __init__(self, sessions: sessionmaker[Session], *, consumer_group: str) -> None:
        self._sessions = sessions
        self._consumer_group = consumer_group

    def persist(self, event: BankFlowEvent, metadata: KafkaMessageMetadata) -> bool:
        payload = json.loads(event.payload.model_dump_json(exclude_none=True))
        statement = (
            insert(ConsumedEvent)
            .values(
                event_id=event.event_id,
                event_type=event.event_type.value,
                schema_version=event.schema_version,
                occurred_at=event.occurred_at,
                source=event.source,
                payload=payload,
                topic=metadata.topic,
                partition=metadata.partition,
                offset=metadata.offset,
                consumer_group=self._consumer_group,
            )
            .on_conflict_do_nothing()
            .returning(ConsumedEvent.event_id)
        )
        with session_scope(self._sessions) as session:
            return session.execute(statement).scalar_one_or_none() is not None


def consumer_config(settings: Settings) -> dict[str, object]:
    """Return manual-commit configuration for the operational consumer group."""

    return {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": settings.kafka_consumer_group,
        "client.id": settings.kafka_consumer_client_id,
        "enable.auto.commit": False,
        "enable.auto.offset.store": False,
        "auto.offset.reset": "earliest",
        "isolation.level": "read_committed",
    }


class KafkaEventConsumer:
    """Consume, validate, persist, and synchronously commit one message at a time."""

    def __init__(
        self,
        client: Consumer,
        event_store: EventStore,
        *,
        topic: str,
        poll_timeout_seconds: float,
    ) -> None:
        if not topic.strip():
            raise ValueError("Kafka topic must not be blank.")
        if poll_timeout_seconds <= 0:
            raise ValueError("Kafka poll timeout must be positive.")
        self._client = client
        self._event_store = event_store
        self._topic = topic
        self._poll_timeout_seconds = poll_timeout_seconds
        self._shutdown = Event()
        self._started = False
        self._closed = False

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        sessions: sessionmaker[Session],
        *,
        client_factory: Callable[[dict[str, object]], Consumer] = Consumer,
    ) -> "KafkaEventConsumer":
        return cls(
            client_factory(consumer_config(settings)),
            PostgresEventStore(sessions, consumer_group=settings.kafka_consumer_group),
            topic=settings.kafka_transaction_topic,
            poll_timeout_seconds=settings.kafka_consumer_poll_timeout_seconds,
        )

    def start(self) -> None:
        if self._closed:
            raise KafkaConsumerError("A closed Kafka consumer cannot be restarted.")
        if not self._started:
            try:
                self._client.subscribe([self._topic])
            except KafkaException as exc:
                raise KafkaConsumerError("Kafka topic subscription failed.") from exc
            self._started = True
            LOGGER.info("Kafka consumer subscribed", extra={"topic": self._topic})

    def request_shutdown(self) -> None:
        self._shutdown.set()

    def consume_once(self) -> ConsumeResult | None:
        if not self._started:
            self.start()
        try:
            message = self._client.poll(self._poll_timeout_seconds)
        except KafkaException as exc:
            raise KafkaConsumerError("Kafka polling failed.") from exc
        if message is None:
            return None

        error = message.error()
        if error is not None:
            if error.code() == KafkaError._PARTITION_EOF:
                return None
            raise KafkaConsumerError(f"Kafka polling failed with broker code {error.code()}.")

        metadata = KafkaMessageMetadata(
            topic=message.topic(),
            partition=message.partition(),
            offset=message.offset(),
        )
        try:
            event = deserialize_event(message.value())
        except ValidationError, ValueError, TypeError:
            LOGGER.warning(
                "Kafka event rejected by schema validation",
                extra={
                    "consume_status": ConsumeStatus.INVALID.value,
                    "topic": metadata.topic,
                    "partition": metadata.partition,
                    "offset": metadata.offset,
                },
            )
            self._commit(message)
            return ConsumeResult(ConsumeStatus.INVALID, metadata)

        try:
            persisted = self._event_store.persist(event, metadata)
        except SQLAlchemyError as exc:
            raise EventPersistenceError("Validated Kafka event persistence failed.") from exc

        status = ConsumeStatus.PERSISTED if persisted else ConsumeStatus.DUPLICATE
        LOGGER.info(
            "Kafka event processed",
            extra={
                "consume_status": status.value,
                "event_id": str(event.event_id),
                "event_type": event.event_type.value,
                "topic": metadata.topic,
                "partition": metadata.partition,
                "offset": metadata.offset,
            },
        )
        self._commit(message)
        return ConsumeResult(status, metadata, event.event_id)

    def run(self) -> int:
        processed = 0
        self.start()
        try:
            while not self._shutdown.is_set():
                if self.consume_once() is not None:
                    processed += 1
        finally:
            self.close()
        return processed

    def _commit(self, message: Message) -> None:
        try:
            self._client.commit(message=message, asynchronous=False)
        except KafkaException as exc:
            raise KafkaConsumerError("Kafka offset commit failed.") from exc

    def close(self) -> None:
        if not self._closed:
            self._client.close()
            self._closed = True
            LOGGER.info("Kafka consumer closed", extra={"topic": self._topic})


class StructuredJsonFormatter(logging.Formatter):
    """Emit stable JSON records without serializing event payloads."""

    _FIELDS = (
        "consume_status",
        "event_id",
        "event_type",
        "topic",
        "partition",
        "offset",
    )

    def format(self, record: logging.LogRecord) -> str:
        document: dict[str, object] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in self._FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                document[field] = value
        return json.dumps(document, separators=(",", ":"))
