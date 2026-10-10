"""Append-only validated Kafka events for operational analytics and replay audits."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from bankflow.database.base import Base


class ConsumedEvent(Base):
    __tablename__ = "consumed_events"
    __table_args__ = (
        UniqueConstraint(
            "topic",
            "partition",
            "offset",
            name="uq_consumed_events_kafka_position",
        ),
        Index("ix_consumed_events_type_occurred_at", "event_type", "occurred_at"),
        Index("ix_consumed_events_consumed_at", "consumed_at"),
    )

    event_id: Mapped[UUID] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    topic: Mapped[str] = mapped_column(String(249), nullable=False)
    partition: Mapped[int] = mapped_column(Integer, nullable=False)
    offset: Mapped[int] = mapped_column(BigInteger, nullable=False)
    consumer_group: Mapped[str] = mapped_column(String(255), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
