"""Read-only access to the Version 1 dbt analytics marts."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Engine, bindparam, text
from sqlalchemy.exc import SQLAlchemyError


class AnalyticsUnavailableError(RuntimeError):
    """The analytics schema is missing, stale, or temporarily unavailable."""


@dataclass(frozen=True)
class AnalyticsOverview:
    total_transactions: int
    successful_transactions: int
    declined_transactions: int
    completed_volume: Decimal
    withdrawal_count: int
    withdrawal_volume: Decimal
    deposit_count: int
    deposit_volume: Decimal
    authentication_failures: int
    locked_cards: int

    @property
    def success_rate(self) -> Decimal:
        if self.total_transactions == 0:
            return Decimal("0.0000")
        return (
            Decimal(self.successful_transactions) / Decimal(self.total_transactions) * 100
        ).quantize(Decimal("0.01"))


@dataclass(frozen=True)
class DailyTransactionMetric:
    transaction_date: date
    transaction_count: int
    successful_count: int
    declined_count: int
    completed_volume: Decimal


@dataclass(frozen=True)
class TransactionTypeMetric:
    transaction_type: str
    transaction_count: int
    completed_volume: Decimal


@dataclass(frozen=True)
class AnalyticsSnapshot:
    overview: AnalyticsOverview
    daily_transactions: tuple[DailyTransactionMetric, ...]
    transaction_types: tuple[TransactionTypeMetric, ...]
    generated_at: datetime

    @property
    def has_activity(self) -> bool:
        return bool(
            self.overview.total_transactions
            or self.overview.authentication_failures
            or self.overview.locked_cards
        )


_OVERVIEW_QUERY = text(
    """
    with transaction_totals as (
        select
            coalesce(sum(transaction_count), 0) as total_transactions,
            coalesce(sum(successful_count), 0) as successful_transactions,
            coalesce(sum(declined_count), 0) as declined_transactions,
            coalesce(sum(completed_amount), 0) as completed_volume,
            coalesce(sum(transaction_count) filter (where transaction_type = 'withdrawal'), 0)
                as withdrawal_count,
            coalesce(sum(completed_amount) filter (where transaction_type = 'withdrawal'), 0)
                as withdrawal_volume,
            coalesce(sum(transaction_count) filter (where transaction_type = 'deposit'), 0)
                as deposit_count,
            coalesce(sum(completed_amount) filter (where transaction_type = 'deposit'), 0)
                as deposit_volume
        from bankflow_analytics.analytics_daily_transactions
        where (:start_date is null or transaction_date >= :start_date)
    ),
    authentication_totals as (
        select
            coalesce(sum(event_count) filter (where event_type = 'authentication.failed'), 0)
                as authentication_failures,
            coalesce(sum(event_count) filter (where event_type = 'card.locked'), 0)
                as locked_cards
        from bankflow_analytics.analytics_authentication_metrics
        where (:start_date is null or authentication_date >= :start_date)
    )
    select * from transaction_totals cross join authentication_totals
    """
).bindparams(bindparam("start_date", type_=Date))

_DAILY_QUERY = text(
    """
    select
        transaction_date,
        sum(transaction_count) as transaction_count,
        sum(successful_count) as successful_count,
        sum(declined_count) as declined_count,
        sum(completed_amount) as completed_volume
    from bankflow_analytics.analytics_daily_transactions
    where (:start_date is null or transaction_date >= :start_date)
    group by transaction_date
    order by transaction_date
    """
).bindparams(bindparam("start_date", type_=Date))

_TYPE_QUERY = text(
    """
    select
        transaction_type,
        sum(transaction_count) as transaction_count,
        sum(completed_amount) as completed_volume
    from bankflow_analytics.analytics_daily_transactions
    where (:start_date is null or transaction_date >= :start_date)
    group by transaction_type
    order by transaction_type
    """
).bindparams(bindparam("start_date", type_=Date))


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def load_analytics_snapshot(
    engine: Engine,
    *,
    start_date: date | None = None,
    now: datetime | None = None,
) -> AnalyticsSnapshot:
    """Load one internally consistent dashboard snapshot from materialized dbt marts."""

    parameters = {"start_date": start_date}
    try:
        with engine.connect() as connection:
            with connection.begin():
                overview_row = connection.execute(_OVERVIEW_QUERY, parameters).mappings().one()
                daily_rows = connection.execute(_DAILY_QUERY, parameters).mappings().all()
                type_rows = connection.execute(_TYPE_QUERY, parameters).mappings().all()
    except SQLAlchemyError as exc:
        raise AnalyticsUnavailableError(
            "BankFlow analytics are unavailable. Run the consumer and rebuild the dbt marts."
        ) from exc

    overview = AnalyticsOverview(
        total_transactions=int(overview_row["total_transactions"]),
        successful_transactions=int(overview_row["successful_transactions"]),
        declined_transactions=int(overview_row["declined_transactions"]),
        completed_volume=_decimal(overview_row["completed_volume"]),
        withdrawal_count=int(overview_row["withdrawal_count"]),
        withdrawal_volume=_decimal(overview_row["withdrawal_volume"]),
        deposit_count=int(overview_row["deposit_count"]),
        deposit_volume=_decimal(overview_row["deposit_volume"]),
        authentication_failures=int(overview_row["authentication_failures"]),
        locked_cards=int(overview_row["locked_cards"]),
    )
    daily = tuple(
        DailyTransactionMetric(
            transaction_date=row["transaction_date"],
            transaction_count=int(row["transaction_count"]),
            successful_count=int(row["successful_count"]),
            declined_count=int(row["declined_count"]),
            completed_volume=_decimal(row["completed_volume"]),
        )
        for row in daily_rows
    )
    transaction_types = tuple(
        TransactionTypeMetric(
            transaction_type=str(row["transaction_type"]),
            transaction_count=int(row["transaction_count"]),
            completed_volume=_decimal(row["completed_volume"]),
        )
        for row in type_rows
    )
    return AnalyticsSnapshot(
        overview=overview,
        daily_transactions=daily,
        transaction_types=transaction_types,
        generated_at=now or datetime.now().astimezone(),
    )
