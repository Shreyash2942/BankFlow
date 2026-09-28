"""Transaction creation and deterministic account-history queries."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from bankflow.models import Transaction, TransactionStatus, TransactionType
from bankflow.repositories.exceptions import (
    InvalidRepositoryQueryError,
    RepositoryNotFoundError,
    RepositoryWriteError,
)

MAX_HISTORY_PAGE_SIZE = 500


class TransactionRepository:
    """Persist transactions without committing the caller's unit of work."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        return self._session.get(Transaction, transaction_id)

    def require_by_id(self, transaction_id: UUID) -> Transaction:
        transaction = self.get_by_id(transaction_id)
        if transaction is None:
            raise RepositoryNotFoundError("Transaction", transaction_id)
        return transaction

    def list_for_account(
        self, account_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Transaction]:
        if not 1 <= limit <= MAX_HISTORY_PAGE_SIZE:
            raise InvalidRepositoryQueryError(
                f"Transaction history limit must be between 1 and {MAX_HISTORY_PAGE_SIZE}."
            )
        if offset < 0:
            raise InvalidRepositoryQueryError("Transaction history offset cannot be negative.")
        statement = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.scalars(statement))

    def create(
        self,
        *,
        account_id: UUID,
        card_id: UUID | None,
        transaction_type: TransactionType,
        status: TransactionStatus,
        amount: Decimal,
        balance_before: Decimal,
        balance_after: Decimal,
        decline_reason: str | None = None,
        transaction_id: UUID | None = None,
    ) -> Transaction:
        if not all(isinstance(value, Decimal) for value in (amount, balance_before, balance_after)):
            raise InvalidRepositoryQueryError(
                "Transaction money values must be supplied as Decimal."
            )
        values = {
            "account_id": account_id,
            "card_id": card_id,
            "transaction_type": transaction_type,
            "status": status,
            "amount": amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "decline_reason": decline_reason,
        }
        if transaction_id is not None:
            values["id"] = transaction_id
        transaction = Transaction(**values)
        self._session.add(transaction)
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise RepositoryWriteError("The transaction record could not be created.") from exc
        return transaction
