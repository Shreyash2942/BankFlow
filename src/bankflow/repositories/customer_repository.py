"""Customer persistence queries."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from bankflow.models import Customer
from bankflow.repositories.exceptions import RepositoryNotFoundError


class CustomerRepository:
    """Read customers without owning the surrounding transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, customer_id: UUID) -> Customer | None:
        return self._session.get(Customer, customer_id)

    def require_by_id(self, customer_id: UUID) -> Customer:
        customer = self.get_by_id(customer_id)
        if customer is None:
            raise RepositoryNotFoundError("Customer", customer_id)
        return customer

    def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return self._session.scalars(statement).one_or_none()
