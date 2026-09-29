"""Transactional card authentication with Redis-backed temporary state."""

from datetime import UTC, datetime
from typing import Any, Callable, TypeVar

from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from bankflow.cache.redis_client import AuthenticationStateStore
from bankflow.config.settings import Settings
from bankflow.models import AuditEvent, Card, CardStatus
from bankflow.repositories import CardRepository
from bankflow.schemas.authentication import (
    AuthenticationOutcome,
    AuthenticationRequest,
    AuthenticationResult,
    AuthenticationSession,
)
from bankflow.utils.pin_hashing import verify_pin

ResultT = TypeVar("ResultT")


class AuthenticationStateUnavailableError(RuntimeError):
    """Redis could not safely maintain authentication state."""


class AuthenticationService:
    """Authenticate one request inside a caller-owned database transaction."""

    def __init__(
        self,
        session: Session,
        state_store: AuthenticationStateStore,
        *,
        max_attempts: int = 3,
        attempt_ttl_seconds: int = 900,
        session_ttl_seconds: int = 900,
    ) -> None:
        if max_attempts < 1 or attempt_ttl_seconds < 1 or session_ttl_seconds < 1:
            raise ValueError("Authentication limits and TTL values must be positive.")
        self._session = session
        self._cards = CardRepository(session)
        self._state = state_store
        self._max_attempts = max_attempts
        self._attempt_ttl_seconds = attempt_ttl_seconds
        self._session_ttl_seconds = session_ttl_seconds

    @classmethod
    def from_settings(
        cls,
        session: Session,
        state_store: AuthenticationStateStore,
        settings: Settings,
    ) -> "AuthenticationService":
        return cls(
            session,
            state_store,
            max_attempts=settings.max_pin_attempts,
            attempt_ttl_seconds=settings.pin_attempt_ttl_seconds,
            session_ttl_seconds=settings.auth_session_ttl_seconds,
        )

    def _redis(self, operation: Callable[..., ResultT], *args: Any, **kwargs: Any) -> ResultT:
        try:
            return operation(*args, **kwargs)
        except RedisError:
            raise AuthenticationStateUnavailableError(
                "Authentication state is temporarily unavailable."
            ) from None

    def _audit(
        self,
        *,
        event_type: str,
        outcome: str,
        card: Card | None,
        details: dict[str, Any],
    ) -> None:
        self._session.add(
            AuditEvent(
                event_type=event_type,
                outcome=outcome,
                customer_id=card.account.customer_id if card is not None else None,
                account_id=card.account_id if card is not None else None,
                card_id=card.id if card is not None else None,
                details=details,
            )
        )

    def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Return a generic denial or an expiring session; never persist input secrets."""
        card = self._cards.get_by_token(request.card_token, for_update=True)
        if card is None:
            self._audit(
                event_type="authentication.denied",
                outcome=AuthenticationOutcome.INVALID_CREDENTIALS,
                card=None,
                details={"reason": AuthenticationOutcome.INVALID_CREDENTIALS},
            )
            self._session.flush()
            return AuthenticationResult(
                authenticated=False,
                outcome=AuthenticationOutcome.INVALID_CREDENTIALS,
                remaining_attempts=None,
            )

        if card.status is not CardStatus.ACTIVE:
            outcome = (
                AuthenticationOutcome.CARD_LOCKED
                if card.status is CardStatus.LOCKED
                else AuthenticationOutcome.CARD_UNAVAILABLE
            )
            self._audit(
                event_type="authentication.denied",
                outcome=outcome,
                card=card,
                details={"reason": outcome},
            )
            self._session.flush()
            return AuthenticationResult(authenticated=False, outcome=outcome)

        if not verify_pin(request.pin.get_secret_value(), card.pin_hash):
            failed_attempts = self._redis(
                self._state.increment_failed_attempts,
                card.id,
                ttl_seconds=self._attempt_ttl_seconds,
            )
            remaining_attempts = max(self._max_attempts - failed_attempts, 0)
            if failed_attempts >= self._max_attempts:
                card.status = CardStatus.LOCKED
                card.locked_at = datetime.now(UTC)
                self._audit(
                    event_type="authentication.card_locked",
                    outcome=AuthenticationOutcome.CARD_LOCKED,
                    card=card,
                    details={"failed_attempts": failed_attempts, "remaining_attempts": 0},
                )
                outcome = AuthenticationOutcome.CARD_LOCKED
            else:
                self._audit(
                    event_type="authentication.denied",
                    outcome=AuthenticationOutcome.INVALID_CREDENTIALS,
                    card=card,
                    details={
                        "reason": AuthenticationOutcome.INVALID_CREDENTIALS,
                        "failed_attempts": failed_attempts,
                        "remaining_attempts": remaining_attempts,
                    },
                )
                outcome = AuthenticationOutcome.INVALID_CREDENTIALS
            self._session.flush()
            return AuthenticationResult(
                authenticated=False,
                outcome=outcome,
                remaining_attempts=remaining_attempts,
            )

        self._redis(self._state.clear_failed_attempts, card.id)
        session_data = AuthenticationSession(
            card_id=card.id,
            account_id=card.account_id,
            customer_id=card.account.customer_id,
        )
        session_token = self._redis(
            self._state.create_session,
            session_data,
            ttl_seconds=self._session_ttl_seconds,
        )
        self._audit(
            event_type="authentication.succeeded",
            outcome=AuthenticationOutcome.AUTHENTICATED,
            card=card,
            details={"session_ttl_seconds": self._session_ttl_seconds},
        )
        try:
            self._session.flush()
        except Exception:
            self._redis(self._state.delete_session, session_token)
            raise
        return AuthenticationResult(
            authenticated=True,
            outcome=AuthenticationOutcome.AUTHENTICATED,
            session_token=session_token,
            expires_in_seconds=self._session_ttl_seconds,
        )
