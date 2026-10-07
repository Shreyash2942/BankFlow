"""Synchronous, acknowledged Kafka publication for committed application events."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from confluent_kafka import KafkaError, KafkaException, Message, Producer

from bankflow.config.settings import Settings
from bankflow.messaging.event_factory import serialize_event
from bankflow.schemas.events import (
    AuthenticationEventPayload,
    BankFlowEvent,
    TransactionEventPayload,
)

LOGGER = logging.getLogger(__name__)


class EventPublicationError(RuntimeError):
    """A validated event could not be acknowledged by its transport."""


class KafkaUnavailableError(EventPublicationError):
    """The broker did not acknowledge an event within the configured bound."""


class KafkaDeliveryError(EventPublicationError):
    """Kafka invoked the delivery callback with a terminal error."""


class EventPublisher(Protocol):
    """Application boundary implemented by Kafka and lightweight test doubles."""

    def publish(self, event: BankFlowEvent) -> "DeliveryReceipt": ...


@dataclass(frozen=True)
class DeliveryReceipt:
    event_id: UUID
    topic: str
    partition: int
    offset: int


def producer_config(settings: Settings) -> dict[str, object]:
    """Return reliability-oriented librdkafka settings without secret-bearing values."""

    timeout_ms = settings.kafka_delivery_timeout_seconds * 1000
    return {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "client.id": settings.kafka_client_id,
        "acks": "all",
        "enable.idempotence": True,
        "compression.type": "gzip",
        "max.in.flight.requests.per.connection": 5,
        "message.timeout.ms": timeout_ms,
        "socket.timeout.ms": timeout_ms,
    }


def _partition_key(event: BankFlowEvent) -> bytes:
    payload = event.payload
    if isinstance(payload, TransactionEventPayload):
        aggregate_id = payload.transaction_id
    elif isinstance(payload, AuthenticationEventPayload) and payload.card_id is not None:
        aggregate_id = payload.card_id
    else:
        aggregate_id = event.event_id
    return str(aggregate_id).encode("ascii")


class KafkaEventProducer:
    """Publish one event and wait for its delivery callback before returning."""

    def __init__(
        self,
        client: Producer,
        *,
        topic: str,
        delivery_timeout_seconds: int,
    ) -> None:
        if not topic.strip():
            raise ValueError("Kafka topic must not be blank.")
        if delivery_timeout_seconds < 1:
            raise ValueError("Kafka delivery timeout must be positive.")
        self._client = client
        self._topic = topic
        self._delivery_timeout_seconds = delivery_timeout_seconds

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        client_factory: Callable[[dict[str, object]], Producer] = Producer,
    ) -> "KafkaEventProducer":
        return cls(
            client_factory(producer_config(settings)),
            topic=settings.kafka_transaction_topic,
            delivery_timeout_seconds=settings.kafka_delivery_timeout_seconds,
        )

    def publish(self, event: BankFlowEvent) -> DeliveryReceipt:
        delivery_error: KafkaError | None = None
        delivered_message: Message | None = None

        def on_delivery(error: KafkaError | None, message: Message) -> None:
            nonlocal delivery_error, delivered_message
            delivery_error = error
            delivered_message = message
            if error is None:
                LOGGER.info(
                    "Kafka delivered event %s to %s[%s] at offset %s",
                    event.event_id,
                    message.topic(),
                    message.partition(),
                    message.offset(),
                )
            else:
                LOGGER.error("Kafka delivery failed for event %s: %s", event.event_id, error)

        try:
            self._client.produce(
                topic=self._topic,
                key=_partition_key(event),
                value=serialize_event(event),
                headers={
                    "event_type": event.event_type.value,
                    "schema_version": str(event.schema_version),
                    "source": event.source,
                },
                on_delivery=on_delivery,
            )
        except (BufferError, KafkaException) as exc:
            raise KafkaUnavailableError("Kafka could not accept the event for delivery.") from exc

        remaining = self._client.flush(self._delivery_timeout_seconds)
        if remaining:
            raise KafkaUnavailableError(
                "Kafka did not acknowledge the event before the delivery timeout."
            )
        if delivery_error is not None:
            raise KafkaDeliveryError("Kafka rejected the event during delivery.")
        if delivered_message is None:
            raise KafkaUnavailableError("Kafka completed without a delivery acknowledgement.")

        return DeliveryReceipt(
            event_id=event.event_id,
            topic=delivered_message.topic(),
            partition=delivered_message.partition(),
            offset=delivered_message.offset(),
        )

    def close(self) -> int:
        """Drain queued callbacks and return the number of undelivered messages."""

        return self._client.flush(self._delivery_timeout_seconds)
