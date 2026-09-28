"""Fictional card token and one-way PIN credential."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bankflow.database.base import Base
from bankflow.models.common import TimestampMixin, checked_enum
from bankflow.models.enums import CardStatus

if TYPE_CHECKING:
    from bankflow.models.account import Account
    from bankflow.models.audit_event import AuditEvent
    from bankflow.models.transaction import Transaction


class Card(TimestampMixin, Base):
    __tablename__ = "cards"
    __table_args__ = (
        CheckConstraint("last_four ~ '^[0-9]{4}$'", name="last_four_digits"),
        CheckConstraint("expiry_month BETWEEN 1 AND 12", name="expiry_month_range"),
        CheckConstraint("expiry_year BETWEEN 2000 AND 9999", name="expiry_year_range"),
        CheckConstraint("char_length(pin_hash) >= 32", name="pin_hash_present"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("bankflow.accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    card_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    last_four: Mapped[str] = mapped_column(String(4), nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[CardStatus] = mapped_column(
        checked_enum(CardStatus, "card_status"),
        default=CardStatus.ACTIVE,
        server_default=CardStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    expiry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year: Mapped[int] = mapped_column(Integer, nullable=False)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    account: Mapped[Account] = relationship(back_populates="cards")
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="card", passive_deletes=True
    )
    audit_events: Mapped[list[AuditEvent]] = relationship(
        back_populates="card", passive_deletes=True
    )
