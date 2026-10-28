"""Deterministic, schema-valid synthetic events for streaming demonstrations."""

from __future__ import annotations

import random
import time
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from bankflow.messaging import EventPublisher, deserialize_event, serialize_event
from bankflow.models import AccountStatus, TransactionStatus, TransactionType
from bankflow.schemas.events import (
    AuthenticationEventOutcome,
    AuthenticationEventPayload,
    BankFlowEvent,
    EventType,
    TransactionEventPayload,
)

DEFAULT_SYNTHETIC_START = datetime(2026, 1, 1, tzinfo=UTC)
_SCENARIO_CYCLE = (
    "authentication_succeeded",
    "balance_viewed",
    "deposit_completed",
    "withdrawal_requested",
    "withdrawal_completed",
    "withdrawal_declined",
    "deposit_completed",
    "withdrawal_completed",
    "balance_viewed",
    "authentication_failed_known",
    "withdrawal_completed",
    "deposit_completed",
    "withdrawal_declined",
    "balance_viewed",
    "authentication_failed_unknown",
    "withdrawal_requested",
    "withdrawal_completed",
    "deposit_completed",
    "card_locked",
    "session_ended",
)
_AMOUNTS = tuple(
    Decimal(value) for value in ("10", "20", "25", "40", "50", "75", "100", "150", "200", "250")
)


@dataclass(frozen=True)
class SyntheticGeneratorConfig:
    """Bounded synthetic population and deterministic generation settings."""

    customer_count: int = 100
    atm_count: int = 10
    seed: int | None = None
    start_time: datetime | None = None
    timestamp_step_milliseconds: int = 10

    def __post_init__(self) -> None:
        if self.customer_count < 1:
            raise ValueError("customer_count must be positive.")
        if self.atm_count < 1:
            raise ValueError("atm_count must be positive.")
        if self.timestamp_step_milliseconds < 1:
            raise ValueError("timestamp_step_milliseconds must be positive.")
        if self.start_time is not None and self.start_time.tzinfo is None:
            raise ValueError("start_time must include a timezone.")


@dataclass
class SyntheticAccount:
    """Fictional subject identifiers and an exact evolving balance."""

    customer_id: UUID
    account_id: UUID
    card_id: UUID
    balance: Decimal


@dataclass(frozen=True)
class PendingWithdrawal:
    profile: SyntheticAccount
    transaction_id: UUID
    amount: Decimal
    atm_id: str


@dataclass(frozen=True)
class GenerationReport:
    event_count: int
    event_type_counts: dict[str, int]
    elapsed_seconds: float
    configured_rate: float

    @property
    def achieved_rate(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.event_count / self.elapsed_seconds


class SyntheticEventGenerator:
    """Generate a repeatable mix of transaction and authentication events."""

    def __init__(self, config: SyntheticGeneratorConfig | None = None) -> None:
        self.config = config or SyntheticGeneratorConfig()
        self._random = random.Random(self.config.seed)
        self._start_time = self.config.start_time or (
            DEFAULT_SYNTHETIC_START if self.config.seed is not None else datetime.now(UTC)
        )
        self._profiles = [self._new_profile() for _ in range(self.config.customer_count)]
        self._pending_withdrawal: PendingWithdrawal | None = None

    @property
    def profiles(self) -> tuple[SyntheticAccount, ...]:
        return tuple(self._profiles)

    def iter_events(self, count: int) -> Iterator[BankFlowEvent]:
        """Yield exactly ``count`` canonical events without materializing the batch."""
        if count < 0:
            raise ValueError("count must not be negative.")
        for index in range(count):
            scenario = _SCENARIO_CYCLE[index % len(_SCENARIO_CYCLE)]
            yield self._event_for_scenario(scenario, index)

    def _new_profile(self) -> SyntheticAccount:
        opening_balance = Decimal(self._random.randrange(20, 201) * 25).quantize(Decimal("0.01"))
        return SyntheticAccount(
            customer_id=self._uuid4(),
            account_id=self._uuid4(),
            card_id=self._uuid4(),
            balance=opening_balance,
        )

    def _event_for_scenario(self, scenario: str, index: int) -> BankFlowEvent:
        occurred_at = self._start_time + timedelta(
            milliseconds=index * self.config.timestamp_step_milliseconds
        )
        if scenario.startswith("authentication_") or scenario in {"card_locked", "session_ended"}:
            return self._authentication_event(scenario, index, occurred_at)
        return self._transaction_event(scenario, index, occurred_at)

    def _transaction_event(self, scenario: str, index: int, occurred_at: datetime) -> BankFlowEvent:
        profile = self._random.choice(self._profiles)
        if scenario in {"withdrawal_requested", "withdrawal_completed"}:
            profile = self._funded_profile()
        atm_id = self._atm_id(index)
        transaction_id = self._uuid4()
        before = profile.balance
        amount = Decimal("0.00")
        after = before
        transaction_type = TransactionType.BALANCE_INQUIRY
        status = TransactionStatus.COMPLETED
        decline_reason = None

        if scenario == "deposit_completed":
            transaction_type = TransactionType.DEPOSIT
            amount = self._random.choice(_AMOUNTS)
            after = before + amount
            profile.balance = after
            event_type = EventType.DEPOSIT_COMPLETED
        elif scenario == "withdrawal_requested":
            transaction_type = TransactionType.WITHDRAWAL
            status = TransactionStatus.PENDING
            amount = self._affordable_amount(before)
            event_type = EventType.WITHDRAWAL_REQUESTED
            self._pending_withdrawal = PendingWithdrawal(
                profile=profile,
                transaction_id=transaction_id,
                amount=amount,
                atm_id=atm_id,
            )
        elif scenario == "withdrawal_completed":
            transaction_type = TransactionType.WITHDRAWAL
            event_type = EventType.WITHDRAWAL_COMPLETED
            if self._pending_withdrawal is not None:
                pending = self._pending_withdrawal
                profile = pending.profile
                transaction_id = pending.transaction_id
                amount = pending.amount
                atm_id = pending.atm_id
                before = profile.balance
                self._pending_withdrawal = None
            else:
                amount = self._affordable_amount(before)
            after = before - amount
            profile.balance = after
        elif scenario == "withdrawal_declined":
            transaction_type = TransactionType.WITHDRAWAL
            status = TransactionStatus.DECLINED
            amount = before + self._random.choice(_AMOUNTS)
            decline_reason = "insufficient_funds"
            event_type = EventType.WITHDRAWAL_DECLINED
        else:
            event_type = EventType.BALANCE_VIEWED

        payload = TransactionEventPayload(
            transaction_id=transaction_id,
            customer_id=profile.customer_id,
            account_id=profile.account_id,
            card_id=profile.card_id,
            transaction_type=transaction_type,
            status=status,
            amount=amount,
            balance_before=before,
            balance_after=after,
            currency="USD",
            account_status=AccountStatus.ACTIVE,
            decline_reason=decline_reason,
            atm_id=atm_id,
        )
        return BankFlowEvent(
            event_id=self._uuid4(),
            event_type=event_type,
            occurred_at=occurred_at,
            payload=payload,
        )

    def _authentication_event(
        self, scenario: str, index: int, occurred_at: datetime
    ) -> BankFlowEvent:
        profile = self._random.choice(self._profiles)
        subjects: dict[str, UUID] = {
            "customer_id": profile.customer_id,
            "account_id": profile.account_id,
            "card_id": profile.card_id,
        }
        remaining_attempts = None
        if scenario == "authentication_succeeded":
            event_type = EventType.AUTHENTICATION_SUCCEEDED
            outcome = AuthenticationEventOutcome.AUTHENTICATED
        elif scenario == "authentication_failed_known":
            event_type = EventType.AUTHENTICATION_FAILED
            outcome = AuthenticationEventOutcome.INVALID_CREDENTIALS
            remaining_attempts = self._random.choice((1, 2))
        elif scenario == "authentication_failed_unknown":
            event_type = EventType.AUTHENTICATION_FAILED
            outcome = AuthenticationEventOutcome.CARD_UNAVAILABLE
            subjects = {}
        elif scenario == "card_locked":
            event_type = EventType.CARD_LOCKED
            outcome = AuthenticationEventOutcome.CARD_LOCKED
            remaining_attempts = 0
        else:
            event_type = EventType.SESSION_ENDED
            outcome = AuthenticationEventOutcome.SESSION_ENDED

        payload = AuthenticationEventPayload(
            **subjects,
            outcome=outcome,
            remaining_attempts=remaining_attempts,
            atm_id=self._atm_id(index),
        )
        return BankFlowEvent(
            event_id=self._uuid4(),
            event_type=event_type,
            occurred_at=occurred_at,
            payload=payload,
        )

    def _affordable_amount(self, balance: Decimal) -> Decimal:
        affordable = [amount for amount in _AMOUNTS if amount <= balance]
        if not affordable:
            raise ValueError("No configured withdrawal amount fits the selected account balance.")
        return self._random.choice(affordable)

    def _funded_profile(self) -> SyntheticAccount:
        minimum_withdrawal = min(_AMOUNTS)
        funded = [profile for profile in self._profiles if profile.balance >= minimum_withdrawal]
        if not funded:
            raise ValueError("Synthetic population has no account funded for a withdrawal.")
        return self._random.choice(funded)

    def _atm_id(self, index: int) -> str:
        number = (index % self.config.atm_count) + 1
        return f"ATM-{number:04d}"

    def _uuid4(self) -> UUID:
        return UUID(int=self._random.getrandbits(128), version=4)


def validate_generated_events(events: Iterable[BankFlowEvent]) -> GenerationReport:
    """Round-trip every event through the released JSON contract."""
    counts: Counter[str] = Counter()
    event_count = 0
    for event in events:
        decoded = deserialize_event(serialize_event(event))
        if decoded != event:
            raise ValueError("Synthetic event changed during schema round trip.")
        counts[event.event_type.value] += 1
        event_count += 1
    return GenerationReport(event_count, dict(sorted(counts.items())), 0.0, 0.0)


def publish_generated_events(
    events: Iterable[BankFlowEvent],
    publisher: EventPublisher,
    *,
    rate_per_second: float,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> GenerationReport:
    """Validate and publish events at a configured maximum start rate."""
    if rate_per_second < 0:
        raise ValueError("rate_per_second must not be negative.")
    started_at = clock()
    counts: Counter[str] = Counter()
    event_count = 0
    for index, event in enumerate(events):
        if rate_per_second:
            scheduled_at = started_at + ((index + 1) / rate_per_second)
            remaining = scheduled_at - clock()
            if remaining > 0:
                sleep(remaining)
        decoded = deserialize_event(serialize_event(event))
        if decoded != event:
            raise ValueError("Synthetic event changed during schema round trip.")
        publisher.publish(event)
        counts[event.event_type.value] += 1
        event_count += 1
    elapsed = max(0.0, clock() - started_at)
    return GenerationReport(
        event_count=event_count,
        event_type_counts=dict(sorted(counts.items())),
        elapsed_seconds=elapsed,
        configured_rate=rate_per_second,
    )
