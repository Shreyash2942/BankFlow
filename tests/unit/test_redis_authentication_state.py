"""Redis authentication state uses expiring keys without embedding session tokens."""

from contextlib import AbstractContextManager
from uuid import uuid4

from bankflow.cache import AuthenticationStateStore
from bankflow.schemas import AuthenticationSession


class FakePipeline(AbstractContextManager):
    def __init__(self, client):
        self.client = client
        self.operations = []

    def __exit__(self, *args):
        return None

    def incr(self, key):
        self.operations.append(("incr", key, None))
        return self

    def expire(self, key, ttl):
        self.operations.append(("expire", key, ttl))
        return self

    def execute(self):
        results = []
        for operation, key, value in self.operations:
            if operation == "incr":
                self.client.values[key] = int(self.client.values.get(key, 0)) + 1
                results.append(self.client.values[key])
            else:
                self.client.ttls[key] = value
                results.append(True)
        return results


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.ttls = {}

    def pipeline(self, *, transaction):
        assert transaction is True
        return FakePipeline(self)

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, *, ex):
        self.values[key] = value
        self.ttls[key] = ex

    def delete(self, key):
        self.values.pop(key, None)
        self.ttls.pop(key, None)

    def ttl(self, key):
        return self.ttls.get(key, -2)


def test_failed_attempt_counter_expires_and_clears():
    client = FakeRedis()
    state = AuthenticationStateStore(client, prefix="bankflow:test")
    card_id = uuid4()

    assert state.increment_failed_attempts(card_id, ttl_seconds=60) == 1
    assert state.increment_failed_attempts(card_id, ttl_seconds=60) == 2
    assert state.get_failed_attempts(card_id) == 2
    assert client.ttls[f"bankflow:test:attempts:{card_id}"] == 60
    state.clear_failed_attempts(card_id)
    assert state.get_failed_attempts(card_id) == 0


def test_session_key_hashes_token_and_round_trips_payload():
    client = FakeRedis()
    state = AuthenticationStateStore(client, prefix="bankflow:test")
    expected = AuthenticationSession(card_id=uuid4(), account_id=uuid4(), customer_id=uuid4())

    token = state.create_session(expected, ttl_seconds=120)

    key = next(iter(client.values))
    assert token not in key
    assert "2468" not in key
    assert state.get_session(token) == expected
    assert state.get_session_ttl(token) == 120
    state.delete_session(token)
    assert state.get_session(token) is None
