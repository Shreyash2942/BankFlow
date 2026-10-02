"""Atomic reset for the one fixed, fictional BankFlow demo graph."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from bankflow.demo import (
    DEMO_ACCOUNT_ID,
    DEMO_CARD_ID,
    DEMO_CARD_TOKEN,
    DEMO_CUSTOMER_ID,
    DEMO_STARTING_BALANCE,
)
from bankflow.models import (
    Account,
    AccountStatus,
    AuditEvent,
    Card,
    CardStatus,
    Transaction,
)


class DemoDataUnavailableError(RuntimeError):
    """The fixed identifiers do not resolve to the expected demo graph."""


@dataclass(frozen=True)
class DemoResetResult:
    account_id: UUID
    card_id: UUID
    balance: Decimal
    removed_transactions: int


class DemoService:
    """Manage demo-only state inside a caller-owned database transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def reset(self) -> DemoResetResult:
        account = self._session.get(Account, DEMO_ACCOUNT_ID, with_for_update=True)
        card = self._session.get(Card, DEMO_CARD_ID, with_for_update=True)
        if (
            account is None
            or card is None
            or account.customer_id != DEMO_CUSTOMER_ID
            or card.account_id != account.id
            or card.card_token != DEMO_CARD_TOKEN
        ):
            raise DemoDataUnavailableError(
                "The fixed fictional demo graph is missing or conflicts with stored data."
            )

        previous_balance = account.balance
        previous_account_status = account.status.value
        previous_card_status = card.status.value
        removal = self._session.execute(
            delete(Transaction).where(Transaction.account_id == DEMO_ACCOUNT_ID)
        )

        account.balance = DEMO_STARTING_BALANCE
        account.status = AccountStatus.ACTIVE
        card.status = CardStatus.ACTIVE
        card.locked_at = None
        self._session.add(
            AuditEvent(
                event_type="demo.reset",
                outcome="completed",
                customer_id=DEMO_CUSTOMER_ID,
                account_id=DEMO_ACCOUNT_ID,
                card_id=DEMO_CARD_ID,
                details={
                    "previous_balance": str(previous_balance),
                    "previous_account_status": previous_account_status,
                    "previous_card_status": previous_card_status,
                    "starting_balance": str(DEMO_STARTING_BALANCE),
                    "removed_transactions": removal.rowcount,
                    "fictional": True,
                },
            )
        )
        self._session.flush()
        return DemoResetResult(
            account_id=account.id,
            card_id=card.id,
            balance=account.balance,
            removed_transactions=removal.rowcount,
        )
