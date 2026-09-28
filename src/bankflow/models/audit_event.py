"""Append-oriented operational audit record with secret-free structured details."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bankflow.database.base import Base
from bankflow.models.common import TimestampMixin

if TYPE_CHECKING:
    from bankflow.models.account import Account
    from bankflow.models.card import Card
    from bankflow.models.customer import Customer
    from bankflow.models.transaction import Transaction


class AuditEvent(TimestampMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_events_type_created_at", "event_type", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)
    customer_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bankflow.customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bankflow.accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    card_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bankflow.cards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    transaction_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bankflow.transactions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )

    customer: Mapped[Customer | None] = relationship(back_populates="audit_events")
    account: Mapped[Account | None] = relationship(back_populates="audit_events")
    card: Mapped[Card | None] = relationship(back_populates="audit_events")
    transaction: Mapped[Transaction | None] = relationship(back_populates="audit_events")
