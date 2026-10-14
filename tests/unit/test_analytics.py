from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from bankflow.analytics import AnalyticsUnavailableError, load_analytics_snapshot


@pytest.fixture
def analytics_engine():
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    with engine.begin() as connection:
        connection.execute(text("attach database ':memory:' as bankflow_analytics"))
        connection.execute(
            text(
                """
                create table bankflow_analytics.analytics_daily_transactions (
                    transaction_date date not null,
                    transaction_type text not null,
                    transaction_count integer not null,
                    successful_count integer not null,
                    declined_count integer not null,
                    completed_amount numeric not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table bankflow_analytics.analytics_authentication_metrics (
                    authentication_date date not null,
                    event_type text not null,
                    event_count integer not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_daily_transactions values
                    ('2026-10-12', 'withdrawal', 2, 1, 1, 25.00),
                    ('2026-10-12', 'deposit', 1, 1, 0, 10.25),
                    ('2026-10-13', 'balance_inquiry', 1, 1, 0, 0.00)
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_authentication_metrics values
                    ('2026-10-12', 'authentication.failed', 3),
                    ('2026-10-12', 'card.locked', 1),
                    ('2026-10-13', 'authentication.succeeded', 2)
                """
            )
        )
    yield engine
    engine.dispose()


def test_snapshot_aggregates_exact_mart_metrics(analytics_engine):
    generated_at = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
    snapshot = load_analytics_snapshot(analytics_engine, now=generated_at)

    assert snapshot.overview.total_transactions == 4
    assert snapshot.overview.successful_transactions == 3
    assert snapshot.overview.declined_transactions == 1
    assert snapshot.overview.completed_volume == Decimal("35.25")
    assert snapshot.overview.withdrawal_count == 2
    assert snapshot.overview.withdrawal_volume == Decimal("25.00")
    assert snapshot.overview.deposit_count == 1
    assert snapshot.overview.deposit_volume == Decimal("10.25")
    assert snapshot.overview.authentication_failures == 3
    assert snapshot.overview.locked_cards == 1
    assert snapshot.overview.success_rate == Decimal("75.00")
    assert len(snapshot.daily_transactions) == 2
    assert len(snapshot.transaction_types) == 3
    assert snapshot.generated_at == generated_at


def test_snapshot_applies_one_date_boundary_to_transaction_and_authentication_marts(
    analytics_engine,
):
    snapshot = load_analytics_snapshot(analytics_engine, start_date=date(2026, 10, 13))

    assert snapshot.overview.total_transactions == 1
    assert snapshot.overview.completed_volume == Decimal("0.00")
    assert snapshot.overview.authentication_failures == 0
    assert snapshot.overview.locked_cards == 0
    assert len(snapshot.daily_transactions) == 1


def test_missing_analytics_schema_returns_safe_actionable_error():
    engine = create_engine("sqlite://")
    with pytest.raises(AnalyticsUnavailableError) as error:
        load_analytics_snapshot(engine)
    engine.dispose()

    assert "rebuild the dbt marts" in str(error.value)
    assert "no such table" not in str(error.value)
