"""Account lookups and exact-balance persistence."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from bankflow.models import Account
from bankflow.repositories.exceptions import (
    ConcurrentUpdateError,
    InvalidRepositoryQueryError,
    RepositoryNotFoundError,
    RepositoryWriteError,
)


class AccountRepository:
    """Persist account state while the caller owns commit and rollback."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, account_id: UUID, *, for_update: bool = False) -> Account | None:
        return self._session.get(Account, account_id, with_for_update=for_update)

    def require_by_id(self, account_id: UUID, *, for_update: bool = False) -> Account:
        account = self.get_by_id(account_id, for_update=for_update)
        if account is None:
            raise RepositoryNotFoundError("Account", account_id)
        return account

    def get_by_account_number(self, account_number: str) -> Account | None:
        statement = select(Account).where(Account.account_number == account_number)
        return self._session.scalars(statement).one_or_none()

    def list_for_customer(self, customer_id: UUID) -> list[Account]:
        statement = (
            select(Account)
            .where(Account.customer_id == customer_id)
            .order_by(Account.account_number.asc())
        )
        return list(self._session.scalars(statement))

    def update_balance(
        self,
        account_id: UUID,
        new_balance: Decimal,
        *,
        expected_version: int | None = None,
    ) -> Account:
        if not isinstance(new_balance, Decimal):
            raise InvalidRepositoryQueryError("Account balances must be supplied as Decimal.")
        account = self.require_by_id(account_id, for_update=True)
        if expected_version is not None and account.version != expected_version:
            raise ConcurrentUpdateError(
                f"Account {account_id} is at version {account.version}, "
                f"not expected version {expected_version}."
            )
        account.balance = new_balance
        try:
            self._session.flush()
        except StaleDataError as exc:
            raise ConcurrentUpdateError(f"Account {account_id} changed concurrently.") from exc
        except IntegrityError as exc:
            raise RepositoryWriteError(
                f"The balance update for account {account_id} failed."
            ) from exc
        return account
