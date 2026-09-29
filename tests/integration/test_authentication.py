"""Live PostgreSQL and Redis checks for the Day 5 authentication contract."""

import json
import os
import time
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text

from bankflow.cache import AuthenticationStateStore, check_redis_health, create_redis_client
from bankflow.database.session import create_session_factory, session_scope
from bankflow.models import Account, AccountType, AuditEvent, Card, CardStatus, Customer
from bankflow.schemas import AuthenticationOutcome, AuthenticationRequest, AuthenticationSession
from bankflow.services import AuthenticationService
from bankflow.utils import hash_pin

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1",
        reason="database and Redis tests require opt-in",
    ),
]

_CORRECT_PIN = "2468"
_WRONG_PIN = "1357"


@pytest.fixture
def authentication_state(database_settings):
    if database_settings.redis_db != 1:
        pytest.fail("Authentication integration tests require dedicated Redis database 1.")
    client = create_redis_client(database_settings)
    health = check_redis_health(client)
    if not health.healthy:
        pytest.fail(health.message)
    prefix = f"bankflow:test:authentication:{uuid4()}"
    state = AuthenticationStateStore(client, prefix=prefix)
    yield client, state, prefix
    keys = list(client.scan_iter(match=f"{prefix}:*"))
    if keys:
        client.delete(*keys)
    client.close()


def _create_card_graph(factory):
    customer_id, account_id, card_id = uuid4(), uuid4(), uuid4()
    card_token = f"auth-{card_id}"
    with session_scope(factory) as session:
        customer = Customer(
            id=customer_id,
            full_name="Authentication Test Customer",
            email=f"{customer_id}@bankflow.example",
        )
        account = Account(
            id=account_id,
            customer=customer,
            account_number=f"BF-AUTH-{account_id.hex[:16]}",
            account_type=AccountType.CHECKING,
            balance=Decimal("100.00"),
        )
        session.add(
            Card(
                id=card_id,
                account=account,
                card_token=card_token,
                last_four="1001",
                pin_hash=hash_pin(_CORRECT_PIN),
                expiry_month=12,
                expiry_year=2035,
            )
        )
    return customer_id, account_id, card_id, card_token


def _delete_card_graph(database_engine, customer_id: UUID):
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM bankflow.audit_events WHERE customer_id=:customer "
                "OR account_id IN (SELECT id FROM bankflow.accounts WHERE customer_id=:customer)"
            ),
            {"customer": customer_id},
        )
        connection.execute(
            text(
                "DELETE FROM bankflow.cards WHERE account_id IN "
                "(SELECT id FROM bankflow.accounts WHERE customer_id=:customer)"
            ),
            {"customer": customer_id},
        )
        connection.execute(
            text("DELETE FROM bankflow.accounts WHERE customer_id=:customer"),
            {"customer": customer_id},
        )
        connection.execute(
            text("DELETE FROM bankflow.customers WHERE id=:customer"),
            {"customer": customer_id},
        )


def _authenticate(factory, state, card_token, pin, *, session_ttl=60):
    with session_scope(factory) as session:
        return AuthenticationService(
            session,
            state,
            max_attempts=3,
            attempt_ttl_seconds=60,
            session_ttl_seconds=session_ttl,
        ).authenticate(AuthenticationRequest(card_token=card_token, pin=pin))


def test_wrong_pin_locks_on_third_attempt_and_locked_card_stays_denied(
    migrated_database, database_engine, authentication_state
):
    _, state, _ = authentication_state
    factory = create_session_factory(database_engine)
    customer_id, _, card_id, card_token = _create_card_graph(factory)
    try:
        results = [_authenticate(factory, state, card_token, _WRONG_PIN) for _ in range(3)]

        assert [result.remaining_attempts for result in results] == [2, 1, 0]
        assert [result.outcome for result in results] == [
            AuthenticationOutcome.INVALID_CREDENTIALS,
            AuthenticationOutcome.INVALID_CREDENTIALS,
            AuthenticationOutcome.CARD_LOCKED,
        ]
        denied = _authenticate(factory, state, card_token, _CORRECT_PIN)
        assert not denied.authenticated
        assert denied.outcome is AuthenticationOutcome.CARD_LOCKED

        with factory() as session:
            card = session.get(Card, card_id)
            events = list(
                session.scalars(
                    select(AuditEvent)
                    .where(AuditEvent.card_id == card_id)
                    .order_by(AuditEvent.created_at, AuditEvent.id)
                )
            )
            assert card.status is CardStatus.LOCKED
            assert card.locked_at is not None
            assert [event.event_type for event in events] == [
                "authentication.denied",
                "authentication.denied",
                "authentication.card_locked",
                "authentication.denied",
            ]
            serialized_details = json.dumps([event.details for event in events])
            assert _CORRECT_PIN not in serialized_details
            assert _WRONG_PIN not in serialized_details
            assert card_token not in serialized_details
        assert state.get_failed_attempts(card_id) == 3
    finally:
        _delete_card_graph(database_engine, customer_id)


def test_correct_pin_creates_session_and_resets_failed_attempts(
    migrated_database, database_engine, authentication_state
):
    _, state, _ = authentication_state
    factory = create_session_factory(database_engine)
    customer_id, account_id, card_id, card_token = _create_card_graph(factory)
    try:
        _authenticate(factory, state, card_token, _WRONG_PIN)
        _authenticate(factory, state, card_token, _WRONG_PIN)
        result = _authenticate(factory, state, card_token, _CORRECT_PIN)

        assert result.authenticated
        assert result.outcome is AuthenticationOutcome.AUTHENTICATED
        assert result.expires_in_seconds == 60
        token = result.session_token.get_secret_value()
        assert state.get_failed_attempts(card_id) == 0
        assert state.get_session(token) == AuthenticationSession(
            card_id=card_id, account_id=account_id, customer_id=customer_id
        )
        assert 0 < state.get_session_ttl(token) <= 60

        with factory() as session:
            events = list(session.scalars(select(AuditEvent).where(AuditEvent.card_id == card_id)))
            serialized_details = json.dumps([event.details for event in events])
            assert token not in serialized_details
            assert _CORRECT_PIN not in serialized_details
            assert card_token not in serialized_details
            assert any(event.event_type == "authentication.succeeded" for event in events)
    finally:
        _delete_card_graph(database_engine, customer_id)


def test_authentication_session_expires(authentication_state):
    _, state, _ = authentication_state
    expected = AuthenticationSession(card_id=uuid4(), account_id=uuid4(), customer_id=uuid4())
    token = state.create_session(expected, ttl_seconds=1)

    assert state.get_session(token) == expected
    deadline = time.monotonic() + 3
    while state.get_session(token) is not None and time.monotonic() < deadline:
        time.sleep(0.05)
    assert state.get_session(token) is None
