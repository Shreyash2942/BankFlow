"""Stable database values shared by domain models and later service layers."""

from enum import StrEnum


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class CardStatus(StrEnum):
    ACTIVE = "active"
    LOCKED = "locked"
    EXPIRED = "expired"
    INACTIVE = "inactive"


class TransactionType(StrEnum):
    BALANCE_INQUIRY = "balance_inquiry"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"


class TransactionStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    DECLINED = "declined"
    FAILED = "failed"
