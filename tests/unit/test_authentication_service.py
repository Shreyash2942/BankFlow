"""Authentication fails closed when temporary security state is unavailable."""

from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from bankflow.models import Account, AccountType, Card, CardStatus, Customer
from bankflow.schemas import AuthenticationRequest
from bankflow.services import AuthenticationService, AuthenticationStateUnavailableError
from bankflow.utils import hash_pin


class UnavailableStateStore:
    def increment_failed_attempts(self, card_id, *, ttl_seconds):
        raise RedisConnectionError("driver detail containing submitted value 1357")


class CardLookup:
    def __init__(self, card):
        self.card = card

    def get_by_token(self, card_token, *, for_update):
        assert for_update
        return self.card


def test_redis_failure_denies_authentication_without_exposing_input():
    customer = Customer(
        id=uuid4(), full_name="Unit Test Customer", email=f"{uuid4()}@bankflow.example"
    )
    account = Account(
        id=uuid4(),
        customer=customer,
        account_number=f"BF-UNIT-{uuid4().hex[:16]}",
        account_type=AccountType.CHECKING,
        balance=Decimal("10.00"),
    )
    card = Card(
        id=uuid4(),
        account=account,
        card_token=f"unit-{uuid4()}",
        last_four="1001",
        pin_hash=hash_pin("2468"),
        status=CardStatus.ACTIVE,
        expiry_month=12,
        expiry_year=2035,
    )
    service = AuthenticationService(MagicMock(), UnavailableStateStore())
    service._cards = CardLookup(card)

    with pytest.raises(AuthenticationStateUnavailableError) as exc_info:
        service.authenticate(AuthenticationRequest(card_token=card.card_token, pin="1357"))

    assert "1357" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None
