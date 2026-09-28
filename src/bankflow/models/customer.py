"""Customer profile for fictional BankFlow users."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bankflow.database.base import Base
from bankflow.models.common import TimestampMixin, checked_enum
from bankflow.models.enums import CustomerStatus

if TYPE_CHECKING:
    from bankflow.models.account import Account
    from bankflow.models.audit_event import AuditEvent


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        CheckConstraint("char_length(trim(full_name)) > 0", name="full_name_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    status: Mapped[CustomerStatus] = mapped_column(
        checked_enum(CustomerStatus, "customer_status"),
        default=CustomerStatus.ACTIVE,
        server_default=CustomerStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    accounts: Mapped[list[Account]] = relationship(back_populates="customer", passive_deletes=True)
    audit_events: Mapped[list[AuditEvent]] = relationship(
        back_populates="customer", passive_deletes=True
    )
