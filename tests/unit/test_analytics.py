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
                create table bankflow_analytics.analytics_lakehouse_daily_transactions (
                    metric_date date not null,
                    currency text not null,
                    transaction_event_count integer not null,
                    monetary_attempt_count integer not null,
                    successful_transaction_count integer not null,
                    declined_transaction_count integer not null,
                    deposit_count integer not null,
                    successful_withdrawal_count integer not null,
                    declined_withdrawal_count integer not null,
                    total_deposit_amount numeric not null,
                    total_withdrawal_amount numeric not null,
                    source_gold_processed_at timestamp not null,
                    serving_loaded_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table bankflow_analytics.analytics_lakehouse_authentication_metrics (
                    metric_date date not null,
                    failed_authentication_count integer not null,
                    card_lockout_count integer not null,
                    source_gold_processed_at timestamp not null,
                    serving_loaded_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table bankflow_analytics.analytics_lakehouse_account_activity (
                    metric_date date not null,
                    account_id text not null,
                    source_gold_processed_at timestamp not null,
                    serving_loaded_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table bankflow_analytics.analytics_lakehouse_hourly_volume (
                    event_hour timestamp not null,
                    transaction_type text not null,
                    transaction_status text not null,
                    transaction_event_count integer not null,
                    total_transaction_amount numeric not null,
                    source_gold_processed_at timestamp not null,
                    serving_loaded_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_lakehouse_daily_transactions values
                    ('2026-10-12', 'USD', 6, 3, 2, 1, 1, 1, 1, 10.25, 25.00,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00'),
                    ('2026-10-13', 'USD', 1, 0, 0, 0, 0, 0, 0, 0.00, 0.00,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00')
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_lakehouse_authentication_metrics values
                    ('2026-10-12', 3, 1, '2026-10-14 10:00:00+00:00',
                     '2026-10-14 10:05:00+00:00'),
                    ('2026-10-13', 0, 0, '2026-10-14 10:00:00+00:00',
                     '2026-10-14 10:05:00+00:00')
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_lakehouse_account_activity values
                    ('2026-10-12', 'account-1', '2026-10-14 10:00:00+00:00',
                     '2026-10-14 10:05:00+00:00'),
                    ('2026-10-12', 'account-2', '2026-10-14 10:00:00+00:00',
                     '2026-10-14 10:05:00+00:00'),
                    ('2026-10-13', 'account-1', '2026-10-14 10:00:00+00:00',
                     '2026-10-14 10:05:00+00:00')
                """
            )
        )
        connection.execute(
            text(
                """
                insert into bankflow_analytics.analytics_lakehouse_hourly_volume values
                    ('2026-10-12 10:00:00+00:00', 'withdrawal', 'completed', 2, 25.00,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00'),
                    ('2026-10-12 10:00:00+00:00', 'deposit', 'completed', 1, 10.25,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00'),
                    ('2026-10-12 11:00:00+00:00', 'balance_inquiry', 'completed', 1, 0.00,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00'),
                    ('2026-10-13 10:00:00+00:00', 'balance_inquiry', 'completed', 1, 0.00,
                     '2026-10-14 10:00:00+00:00', '2026-10-14 10:05:00+00:00')
                """
            )
        )
    yield engine
    engine.dispose()


def test_snapshot_aggregates_exact_lakehouse_metrics(analytics_engine):
    generated_at = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
    snapshot = load_analytics_snapshot(analytics_engine, now=generated_at)

    assert snapshot.overview.total_transactions == 3
    assert snapshot.overview.transaction_events == 7
    assert snapshot.overview.successful_transactions == 2
    assert snapshot.overview.declined_transactions == 1
    assert snapshot.overview.completed_volume == Decimal("35.25")
    assert snapshot.overview.average_transaction_value == Decimal("17.62")
    assert snapshot.overview.withdrawal_count == 2
    assert snapshot.overview.withdrawal_volume == Decimal("25.00")
    assert snapshot.overview.deposit_count == 1
    assert snapshot.overview.deposit_volume == Decimal("10.25")
    assert snapshot.overview.authentication_failures == 3
    assert snapshot.overview.locked_cards == 1
    assert snapshot.overview.active_accounts == 2
    assert snapshot.overview.peak_hourly_events == 3
    assert snapshot.overview.success_rate == Decimal("66.67")
    assert snapshot.overview.decline_rate == Decimal("33.33")
    assert len(snapshot.daily_transactions) == 2
    assert len(snapshot.transaction_types) == 3
    assert len(snapshot.hourly_volume) == 3
    assert snapshot.source_gold_processed_at is not None
    assert snapshot.serving_loaded_at is not None
    assert snapshot.generated_at == generated_at


def test_snapshot_applies_one_date_boundary_to_every_lakehouse_mart(analytics_engine):
    snapshot = load_analytics_snapshot(analytics_engine, start_date=date(2026, 10, 13))

    assert snapshot.overview.total_transactions == 0
    assert snapshot.overview.transaction_events == 1
    assert snapshot.overview.completed_volume == Decimal("0.00")
    assert snapshot.overview.authentication_failures == 0
    assert snapshot.overview.locked_cards == 0
    assert snapshot.overview.active_accounts == 1
    assert snapshot.overview.peak_hourly_events == 1
    assert len(snapshot.daily_transactions) == 1
    assert len(snapshot.hourly_volume) == 1


def test_missing_lakehouse_marts_return_safe_actionable_error():
    engine = create_engine("sqlite://")
    with pytest.raises(AnalyticsUnavailableError) as error:
        load_analytics_snapshot(engine)
    engine.dispose()

    assert "Load Gold serving tables and rebuild dbt" in str(error.value)
    assert "no such table" not in str(error.value)
