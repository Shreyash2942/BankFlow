"""Live PostgreSQL validation for the Day 21 Gold serving mirror."""

import os
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text

from scripts.load_gold_serving import ACCOUNT, AUTHENTICATION, DAILY, HOURLY, mirror_dataset

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1",
        reason="Gold serving tests require PostgreSQL opt-in",
    ),
]


def _rows():
    processed_at = datetime(2026, 11, 8, 12, 0, tzinfo=UTC)
    account_id = uuid4()
    daily = {
        "metric_date": date(2026, 1, 1),
        "currency": "USD",
        "transaction_event_count": 19,
        "monetary_attempt_count": 12,
        "successful_transaction_count": 10,
        "declined_transaction_count": 2,
        "balance_inquiry_count": 4,
        "deposit_count": 5,
        "successful_withdrawal_count": 5,
        "declined_withdrawal_count": 2,
        "total_deposit_amount": Decimal("445.00"),
        "total_withdrawal_amount": Decimal("660.00"),
        "total_declined_amount": Decimal("125.00"),
        "average_transaction_value": Decimal("110.50"),
        "success_rate": Decimal("0.833333"),
        "decline_rate": Decimal("0.166667"),
        "unique_account_count": 7,
        "first_event_at": processed_at,
        "last_event_at": processed_at,
        "gold_processed_at": processed_at,
    }
    authentication = {
        "metric_date": date(2026, 1, 1),
        "authentication_event_count": 6,
        "authentication_attempt_count": 5,
        "successful_authentication_count": 2,
        "failed_authentication_count": 2,
        "card_lockout_count": 1,
        "session_end_count": 1,
        "known_subject_event_count": 5,
        "unknown_subject_event_count": 1,
        "unique_account_count": 2,
        "unique_card_count": 2,
        "success_rate": Decimal("0.400000"),
        "failure_rate": Decimal("0.600000"),
        "first_event_at": processed_at,
        "last_event_at": processed_at,
        "gold_processed_at": processed_at,
    }
    account = {
        "metric_date": date(2026, 1, 1),
        "account_id": account_id,
        "currency": "USD",
        "activity_event_count": 3,
        "transaction_event_count": 3,
        "distinct_transaction_count": 2,
        "completed_monetary_transaction_count": 1,
        "declined_transaction_count": 1,
        "balance_inquiry_count": 1,
        "deposit_count": 0,
        "successful_withdrawal_count": 1,
        "closure_event_count": 0,
        "total_deposit_amount": Decimal("0.00"),
        "total_withdrawal_amount": Decimal("25.00"),
        "total_declined_amount": Decimal("100.00"),
        "opening_balance": Decimal("200.00"),
        "closing_balance": Decimal("175.00"),
        "account_status": "active",
        "account_closed": False,
        "first_activity_at": processed_at,
        "last_activity_at": processed_at,
        "gold_processed_at": processed_at,
    }
    hourly = {
        "event_hour": processed_at,
        "currency": "USD",
        "transaction_type": "withdrawal",
        "transaction_status": "completed",
        "transaction_event_count": 3,
        "total_transaction_amount": Decimal("75.00"),
        "average_transaction_amount": Decimal("25.00"),
        "unique_account_count": 2,
        "first_event_at": processed_at,
        "last_event_at": processed_at,
        "gold_processed_at": processed_at,
    }
    return daily, authentication, account, hourly


def _clear(connection):
    connection.execute(
        text(
            "TRUNCATE bankflow_serving.analytics_daily_transactions, "
            "bankflow_serving.analytics_authentication_metrics, "
            "bankflow_serving.analytics_account_activity, "
            "bankflow_serving.analytics_hourly_volume"
        )
    )


def test_gold_serving_mirror_is_idempotent_timestamped_and_exact(
    migrated_database, database_engine
):
    daily, authentication, account, hourly = _rows()
    extra_daily = {**daily, "metric_date": date(2026, 1, 2)}
    try:
        with database_engine.begin() as connection:
            _clear(connection)
            first = {
                "daily": mirror_dataset(connection, DAILY, [daily, extra_daily]),
                "authentication": mirror_dataset(connection, AUTHENTICATION, [authentication]),
                "account": mirror_dataset(connection, ACCOUNT, [account]),
                "hourly": mirror_dataset(connection, HOURLY, [hourly]),
            }
        assert first["daily"]["target_rows"] == 2
        assert all(result["target_rows"] >= 1 for result in first.values())

        with database_engine.begin() as connection:
            second = {
                "daily": mirror_dataset(connection, DAILY, [daily, extra_daily]),
                "authentication": mirror_dataset(connection, AUTHENTICATION, [authentication]),
                "account": mirror_dataset(connection, ACCOUNT, [account]),
                "hourly": mirror_dataset(connection, HOURLY, [hourly]),
            }
        assert second == first

        with database_engine.begin() as connection:
            pruned = mirror_dataset(connection, DAILY, [daily])
            stored = connection.execute(
                text(
                    "SELECT count(*), sum(transaction_event_count), "
                    "min(loaded_at), min(source_gold_processed_at) "
                    "FROM bankflow_serving.analytics_daily_transactions"
                )
            ).one()
        assert pruned == {"source_rows": 1, "target_rows": 1, "deleted_rows": 1}
        assert stored[0:2] == (1, 19)
        assert stored[2] is not None
        assert stored[3] == daily["gold_processed_at"]
    finally:
        with database_engine.begin() as connection:
            _clear(connection)
