"""Immutable financial intent and its resulting account balances."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bankflow.database.base import Base
from bankflow.models.common import TimestampMixin, checked_enum
from bankflow.models.enums import TransactionStatus, TransactionType

if TYPE_CHECKING:
    from bankflow.models.account import Account
    from bankflow.models.audit_event import AuditEvent
    from bankflow.models.card import Card


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "amount > 0 OR (transaction_type = 'balance_inquiry' AND amount = 0)",
            name="amount_matches_type",
        ),
        CheckConstraint("balance_before >= 0", name="balance_before_nonnegative"),
        CheckConstraint("balance_after >= 0", name="balance_after_nonnegative"),
        Index("ix_transactions_account_created_at", "account_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("bankflow.accounts.id", ondelete="RESTRICT"), nullable=False
    )
    card_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bankflow.cards.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        checked_enum(TransactionType, "transaction_type"), nullable=False, index=True
    )
    status: Mapped[TransactionStatus] = mapped_column(
        checked_enum(TransactionStatus, "transaction_status"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    balance_before: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    decline_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    account: Mapped[Account] = relationship(back_populates="transactions")
    card: Mapped[Card | None] = relationship(back_populates="transactions")
    audit_events: Mapped[list[AuditEvent]] = relationship(
        back_populates="transaction", passive_deletes=True
    )
