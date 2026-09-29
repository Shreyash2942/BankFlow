"""Card lookup queries for later authentication services."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from bankflow.models import Card
from bankflow.repositories.exceptions import RepositoryNotFoundError


class CardRepository:
    """Read fictional card credentials without owning a transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, card_id: UUID) -> Card | None:
        return self._session.get(Card, card_id)

    def require_by_id(self, card_id: UUID) -> Card:
        card = self.get_by_id(card_id)
        if card is None:
            raise RepositoryNotFoundError("Card", card_id)
        return card

    def get_by_token(self, card_token: str, *, for_update: bool = False) -> Card | None:
        statement = select(Card).where(Card.card_token == card_token)
        if for_update:
            statement = statement.with_for_update()
        return self._session.scalars(statement).one_or_none()

    def list_for_account(self, account_id: UUID) -> list[Card]:
        statement = (
            select(Card).where(Card.account_id == account_id).order_by(Card.created_at, Card.id)
        )
        return list(self._session.scalars(statement))
