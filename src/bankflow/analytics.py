"""Read-only access to BankFlow's dbt lakehouse analytics marts."""

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
    transaction_events: int
    successful_transactions: int
    declined_transactions: int
    completed_volume: Decimal
    average_transaction_value: Decimal
    withdrawal_count: int
    withdrawal_volume: Decimal
    deposit_count: int
    deposit_volume: Decimal
    authentication_failures: int
    locked_cards: int
    active_accounts: int
    peak_hourly_events: int

    @property
    def success_rate(self) -> Decimal:
        if self.total_transactions == 0:
            return Decimal("0.00")
        return (
            Decimal(self.successful_transactions) / Decimal(self.total_transactions) * 100
        ).quantize(Decimal("0.01"))

    @property
    def decline_rate(self) -> Decimal:
        if self.total_transactions == 0:
            return Decimal("0.00")
        return (
            Decimal(self.declined_transactions) / Decimal(self.total_transactions) * 100
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
class HourlyVolumeMetric:
    event_hour: datetime
    transaction_events: int


@dataclass(frozen=True)
class AnalyticsSnapshot:
    overview: AnalyticsOverview
    daily_transactions: tuple[DailyTransactionMetric, ...]
    transaction_types: tuple[TransactionTypeMetric, ...]
    hourly_volume: tuple[HourlyVolumeMetric, ...]
    source_gold_processed_at: datetime | None
    serving_loaded_at: datetime | None
    generated_at: datetime

    @property
    def has_activity(self) -> bool:
        return bool(
            self.overview.transaction_events
            or self.overview.authentication_failures
            or self.overview.locked_cards
        )


_OVERVIEW_QUERY = text(
    """
    with transaction_totals as (
        select
            coalesce(sum(transaction_event_count), 0) as transaction_events,
            coalesce(sum(monetary_attempt_count), 0) as total_transactions,
            coalesce(sum(successful_transaction_count), 0) as successful_transactions,
            coalesce(sum(declined_transaction_count), 0) as declined_transactions,
            coalesce(sum(total_deposit_amount + total_withdrawal_amount), 0)
                as completed_volume,
            coalesce(
                sum(total_deposit_amount + total_withdrawal_amount)
                    / nullif(sum(successful_transaction_count), 0),
                0
            ) as average_transaction_value,
            coalesce(sum(successful_withdrawal_count + declined_withdrawal_count), 0)
                as withdrawal_count,
            coalesce(sum(total_withdrawal_amount), 0) as withdrawal_volume,
            coalesce(sum(deposit_count), 0) as deposit_count,
            coalesce(sum(total_deposit_amount), 0) as deposit_volume
        from bankflow_analytics.analytics_lakehouse_daily_transactions
        where (:start_date is null or metric_date >= :start_date)
    ),
    authentication_totals as (
        select
            coalesce(sum(failed_authentication_count), 0) as authentication_failures,
            coalesce(sum(card_lockout_count), 0) as locked_cards
        from bankflow_analytics.analytics_lakehouse_authentication_metrics
        where (:start_date is null or metric_date >= :start_date)
    ),
    account_totals as (
        select count(distinct account_id) as active_accounts
        from bankflow_analytics.analytics_lakehouse_account_activity
        where (:start_date is null or metric_date >= :start_date)
    ),
    hourly_totals as (
        select event_hour, sum(transaction_event_count) as event_count
        from bankflow_analytics.analytics_lakehouse_hourly_volume
        where (:start_date is null or date(event_hour) >= :start_date)
        group by event_hour
    )
    select
        transaction_totals.*,
        authentication_totals.*,
        account_totals.active_accounts,
        coalesce((select max(event_count) from hourly_totals), 0) as peak_hourly_events
    from transaction_totals
    cross join authentication_totals
    cross join account_totals
    """
).bindparams(bindparam("start_date", type_=Date))

_DAILY_QUERY = text(
    """
    select
        metric_date as transaction_date,
        sum(monetary_attempt_count) as transaction_count,
        sum(successful_transaction_count) as successful_count,
        sum(declined_transaction_count) as declined_count,
        sum(total_deposit_amount + total_withdrawal_amount) as completed_volume
    from bankflow_analytics.analytics_lakehouse_daily_transactions
    where (:start_date is null or metric_date >= :start_date)
    group by metric_date
    order by metric_date
    """
).bindparams(bindparam("start_date", type_=Date))

_TYPE_QUERY = text(
    """
    select
        transaction_type,
        sum(transaction_event_count) as transaction_count,
        coalesce(
            sum(total_transaction_amount) filter (where transaction_status = 'completed'),
            0
        ) as completed_volume
    from bankflow_analytics.analytics_lakehouse_hourly_volume
    where (:start_date is null or date(event_hour) >= :start_date)
    group by transaction_type
    order by transaction_type
    """
).bindparams(bindparam("start_date", type_=Date))

_HOURLY_QUERY = text(
    """
    select event_hour, sum(transaction_event_count) as transaction_events
    from bankflow_analytics.analytics_lakehouse_hourly_volume
    where (:start_date is null or date(event_hour) >= :start_date)
    group by event_hour
    order by event_hour
    """
).bindparams(bindparam("start_date", type_=Date))

_FRESHNESS_QUERY = text(
    """
    select
        max(source_gold_processed_at) as source_gold_processed_at,
        max(serving_loaded_at) as serving_loaded_at
    from (
        select source_gold_processed_at, serving_loaded_at
        from bankflow_analytics.analytics_lakehouse_daily_transactions
        union all
        select source_gold_processed_at, serving_loaded_at
        from bankflow_analytics.analytics_lakehouse_authentication_metrics
        union all
        select source_gold_processed_at, serving_loaded_at
        from bankflow_analytics.analytics_lakehouse_account_activity
        union all
        select source_gold_processed_at, serving_loaded_at
        from bankflow_analytics.analytics_lakehouse_hourly_volume
    ) as freshness
    """
)


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _datetime(value: object) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def load_analytics_snapshot(
    engine: Engine,
    *,
    start_date: date | None = None,
    now: datetime | None = None,
) -> AnalyticsSnapshot:
    """Load one consistent snapshot from the dbt lakehouse marts."""

    parameters = {"start_date": start_date}
    try:
        with engine.connect() as connection:
            with connection.begin():
                overview_row = connection.execute(_OVERVIEW_QUERY, parameters).mappings().one()
                daily_rows = connection.execute(_DAILY_QUERY, parameters).mappings().all()
                type_rows = connection.execute(_TYPE_QUERY, parameters).mappings().all()
                hourly_rows = connection.execute(_HOURLY_QUERY, parameters).mappings().all()
                freshness = connection.execute(_FRESHNESS_QUERY).mappings().one()
    except (SQLAlchemyError, ValueError) as exc:
        raise AnalyticsUnavailableError(
            "BankFlow lakehouse analytics are unavailable. Load Gold serving tables and rebuild dbt."
        ) from exc

    overview = AnalyticsOverview(
        total_transactions=int(overview_row["total_transactions"]),
        transaction_events=int(overview_row["transaction_events"]),
        successful_transactions=int(overview_row["successful_transactions"]),
        declined_transactions=int(overview_row["declined_transactions"]),
        completed_volume=_decimal(overview_row["completed_volume"]),
        average_transaction_value=_decimal(overview_row["average_transaction_value"]),
        withdrawal_count=int(overview_row["withdrawal_count"]),
        withdrawal_volume=_decimal(overview_row["withdrawal_volume"]),
        deposit_count=int(overview_row["deposit_count"]),
        deposit_volume=_decimal(overview_row["deposit_volume"]),
        authentication_failures=int(overview_row["authentication_failures"]),
        locked_cards=int(overview_row["locked_cards"]),
        active_accounts=int(overview_row["active_accounts"]),
        peak_hourly_events=int(overview_row["peak_hourly_events"]),
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
    hourly_volume = tuple(
        HourlyVolumeMetric(
            event_hour=_datetime(row["event_hour"]),
            transaction_events=int(row["transaction_events"]),
        )
        for row in hourly_rows
    )
    return AnalyticsSnapshot(
        overview=overview,
        daily_transactions=daily,
        transaction_types=transaction_types,
        hourly_volume=hourly_volume,
        source_gold_processed_at=_datetime(freshness["source_gold_processed_at"]),
        serving_loaded_at=_datetime(freshness["serving_loaded_at"]),
        generated_at=now or datetime.now().astimezone(),
    )
