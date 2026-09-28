"""Persistent customer account and exact available balance."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bankflow.database.base import Base
from bankflow.models.common import TimestampMixin, checked_enum
from bankflow.models.enums import AccountStatus, AccountType

if TYPE_CHECKING:
    from bankflow.models.audit_event import AuditEvent
    from bankflow.models.card import Card
    from bankflow.models.customer import Customer
    from bankflow.models.transaction import Transaction


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="balance_nonnegative"),
        CheckConstraint("version >= 1", name="version_positive"),
        CheckConstraint(
            "char_length(currency) = 3 AND currency = upper(currency)",
            name="currency_iso_style",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("bankflow.customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    account_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    account_type: Mapped[AccountType] = mapped_column(
        checked_enum(AccountType, "account_type"), nullable=False
    )
    status: Mapped[AccountStatus] = mapped_column(
        checked_enum(AccountStatus, "account_status"),
        default=AccountStatus.ACTIVE,
        server_default=AccountStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2, asdecimal=True),
        default=Decimal("0.00"),
        server_default=text("0.00"),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="USD", server_default="USD", nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, default=1, server_default=text("1"), nullable=False
    )

    __mapper_args__ = {"version_id_col": version}

    customer: Mapped[Customer] = relationship(back_populates="accounts")
    cards: Mapped[list[Card]] = relationship(back_populates="account", passive_deletes=True)
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="account", passive_deletes=True
    )
    audit_events: Mapped[list[AuditEvent]] = relationship(
        back_populates="account", passive_deletes=True
    )
