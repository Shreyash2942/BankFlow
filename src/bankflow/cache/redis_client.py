"""Redis client construction and expiring authentication state."""

import hashlib
import secrets
from dataclasses import dataclass

from redis import Redis
from redis.exceptions import RedisError

from bankflow.config.settings import Settings
from bankflow.schemas.authentication import AuthenticationSession


@dataclass(frozen=True)
class RedisHealth:
    healthy: bool
    message: str


def create_redis_client(settings: Settings) -> Redis:
    """Build a bounded-time client without performing network I/O."""
    password = settings.redis_password.get_secret_value()
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        username=settings.redis_username or None,
        password=password or None,
        db=settings.redis_db,
        decode_responses=True,
        socket_connect_timeout=settings.redis_socket_timeout,
        socket_timeout=settings.redis_socket_timeout,
        health_check_interval=30,
    )


def check_redis_health(client: Redis) -> RedisHealth:
    try:
        return RedisHealth(bool(client.ping()), "Redis is reachable.")
    except RedisError:
        return RedisHealth(False, "Redis is unavailable; check the service and credentials.")


class AuthenticationStateStore:
    """Store temporary counters and sessions; keys never contain credentials."""

    def __init__(self, client: Redis, *, prefix: str = "bankflow:auth") -> None:
        self._client = client
        self._prefix = prefix.rstrip(":")

    def _attempt_key(self, card_id: object) -> str:
        return f"{self._prefix}:attempts:{card_id}"

    def _session_key(self, token: str) -> str:
        token_digest = hashlib.sha256(token.encode("ascii")).hexdigest()
        return f"{self._prefix}:session:{token_digest}"

    def increment_failed_attempts(self, card_id: object, *, ttl_seconds: int) -> int:
        key = self._attempt_key(card_id)
        with self._client.pipeline(transaction=True) as pipeline:
            pipeline.incr(key)
            pipeline.expire(key, ttl_seconds)
            result = pipeline.execute()
        return int(result[0])

    def get_failed_attempts(self, card_id: object) -> int:
        value = self._client.get(self._attempt_key(card_id))
        return int(value) if value is not None else 0

    def clear_failed_attempts(self, card_id: object) -> None:
        self._client.delete(self._attempt_key(card_id))

    def create_session(self, session: AuthenticationSession, *, ttl_seconds: int) -> str:
        token = secrets.token_urlsafe(32)
        self._client.set(self._session_key(token), session.model_dump_json(), ex=ttl_seconds)
        return token

    def get_session(self, token: str) -> AuthenticationSession | None:
        value = self._client.get(self._session_key(token))
        return AuthenticationSession.model_validate_json(value) if value is not None else None

    def get_session_ttl(self, token: str) -> int:
        return int(self._client.ttl(self._session_key(token)))

    def delete_session(self, token: str) -> None:
        self._client.delete(self._session_key(token))
