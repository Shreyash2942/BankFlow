"""Service-free contracts for the Day 20 Gold analytics layer."""

import inspect
import sys

import pytest

from spark.gold.account_metrics import (
    ACCOUNT_COLUMN_TYPES,
    ACCOUNT_QUALITY_RULES,
    DEFAULT_ACCOUNT_TABLE,
    AccountMetricsConfig,
    account_merge_sql,
    account_table_sql,
)
from spark.gold.account_metrics import (
    config_from_args as account_config_from_args,
)
from spark.gold.common import (
    DEFAULT_NAMESPACE_LOCATION,
    merge_upsert_sql,
    namespace_sql,
)
from spark.gold.daily_metrics import (
    AUTH_COLUMN_TYPES,
    AUTH_QUALITY_RULES,
    DAILY_COLUMN_TYPES,
    DAILY_QUALITY_RULES,
    DECLINE_COLUMN_TYPES,
    DECLINE_QUALITY_RULES,
    DEFAULT_AUTH_TABLE,
    DEFAULT_DAILY_TABLE,
    DEFAULT_DECLINE_TABLE,
    DailyMetricsConfig,
    authentication_merge_sql,
    authentication_table_sql,
    build_authentication_metrics,
    build_daily_transaction_metrics,
    build_declined_transaction_metrics,
    daily_merge_sql,
    daily_table_sql,
    decline_merge_sql,
    decline_table_sql,
)
from spark.gold.daily_metrics import (
    config_from_args as daily_config_from_args,
)
from spark.gold.hourly_metrics import (
    DEFAULT_HOURLY_TABLE,
    HOURLY_COLUMN_TYPES,
    HOURLY_QUALITY_RULES,
    HourlyMetricsConfig,
    hourly_merge_sql,
    hourly_table_sql,
)
from spark.gold.hourly_metrics import (
    config_from_args as hourly_config_from_args,
)


def test_day20_modules_keep_pyspark_out_of_service_free_imports():
    assert "pyspark" not in sys.modules


def test_gold_namespace_uses_canonical_hdfs_location():
    config = DailyMetricsConfig()

    assert config.namespace_location == DEFAULT_NAMESPACE_LOCATION
    assert namespace_sql(config) == (
        "CREATE NAMESPACE IF NOT EXISTS bankflow.gold "
        "LOCATION 'hdfs://localhost:9000/bankflow/gold'"
    )


def test_daily_defaults_connect_canonical_silver_sources_to_gold_targets():
    config = DailyMetricsConfig()

    assert DEFAULT_DAILY_TABLE == "gold_daily_transaction_metrics"
    assert DEFAULT_AUTH_TABLE == "gold_authentication_metrics"
    assert DEFAULT_DECLINE_TABLE == "gold_declined_transactions"
    assert config.transaction_identifier == "bankflow.silver.silver_transactions"
    assert config.authentication_identifier == ("bankflow.silver.silver_authentication_events")
    assert config.daily_identifier == "bankflow.gold.gold_daily_transaction_metrics"
    assert config.authentication_metrics_identifier == ("bankflow.gold.gold_authentication_metrics")
    assert config.decline_identifier == "bankflow.gold.gold_declined_transactions"


def test_hourly_and_account_defaults_use_canonical_tables():
    hourly = HourlyMetricsConfig()
    account = AccountMetricsConfig()

    assert DEFAULT_HOURLY_TABLE == "gold_hourly_transaction_volume"
    assert DEFAULT_ACCOUNT_TABLE == "gold_account_activity"
    assert hourly.hourly_identifier == "bankflow.gold.gold_hourly_transaction_volume"
    assert account.account_identifier == "bankflow.gold.gold_account_activity"
    assert account.account_source_identifier == "bankflow.silver.silver_account_events"


def test_daily_table_is_typed_partitioned_iceberg_v2():
    statement = daily_table_sql(DailyMetricsConfig())

    assert "CREATE TABLE IF NOT EXISTS bankflow.gold.gold_daily_transaction_metrics" in statement
    assert "total_deposit_amount DECIMAL(38,2) NOT NULL" in statement
    assert "success_rate DECIMAL(9,6) NOT NULL" in statement
    assert "PARTITIONED BY (metric_date)" in statement
    assert "'format-version' = '2'" in statement


def test_authentication_and_decline_tables_are_business_ready():
    config = DailyMetricsConfig()
    authentication = authentication_table_sql(config)
    declines = decline_table_sql(config)

    assert "card_lockout_count BIGINT NOT NULL" in authentication
    assert "failure_rate DECIMAL(9,6) NOT NULL" in authentication
    assert "decline_reason STRING NOT NULL" in declines
    assert "average_declined_amount DECIMAL(38,2) NOT NULL" in declines


def test_hourly_table_preserves_type_and_status_grain():
    statement = hourly_table_sql(HourlyMetricsConfig())

    assert "event_hour TIMESTAMP NOT NULL" in statement
    assert "transaction_type STRING NOT NULL" in statement
    assert "transaction_status STRING NOT NULL" in statement
    assert "PARTITIONED BY (days(event_hour))" in statement


def test_account_table_captures_activity_balances_and_closure():
    statement = account_table_sql(AccountMetricsConfig())

    assert "distinct_transaction_count BIGINT NOT NULL" in statement
    assert "opening_balance DECIMAL(18,2) NOT NULL" in statement
    assert "closing_balance DECIMAL(18,2) NOT NULL" in statement
    assert "account_closed BOOLEAN NOT NULL" in statement


@pytest.mark.parametrize(
    ("builder", "config", "target", "keys"),
    [
        (
            daily_merge_sql,
            DailyMetricsConfig(),
            "bankflow.gold.gold_daily_transaction_metrics",
            ("metric_date", "currency"),
        ),
        (
            authentication_merge_sql,
            DailyMetricsConfig(),
            "bankflow.gold.gold_authentication_metrics",
            ("metric_date",),
        ),
        (
            decline_merge_sql,
            DailyMetricsConfig(),
            "bankflow.gold.gold_declined_transactions",
            ("metric_date", "currency", "decline_reason"),
        ),
        (
            hourly_merge_sql,
            HourlyMetricsConfig(),
            "bankflow.gold.gold_hourly_transaction_volume",
            ("event_hour", "currency", "transaction_type", "transaction_status"),
        ),
        (
            account_merge_sql,
            AccountMetricsConfig(),
            "bankflow.gold.gold_account_activity",
            ("metric_date", "account_id", "currency"),
        ),
    ],
)
def test_gold_merges_upsert_changed_aggregates(builder, config, target, keys):
    statement = builder(config, "_day20_batch")

    assert f"MERGE INTO {target}" in statement
    assert "WHEN MATCHED THEN UPDATE SET" in statement
    assert "WHEN NOT MATCHED THEN INSERT" in statement
    for key in keys:
        assert f"target.{key} = source.{key}" in statement


def test_shared_merge_rejects_missing_or_unsafe_keys():
    with pytest.raises(ValueError, match="keys"):
        merge_upsert_sql("bankflow.gold.metrics", {"metric_date": "date"}, "batch", ())
    with pytest.raises(ValueError, match="present"):
        merge_upsert_sql(
            "bankflow.gold.metrics",
            {"metric_date": "date"},
            "batch",
            ("currency",),
        )
    with pytest.raises(ValueError, match="safe SQL"):
        merge_upsert_sql(
            "bankflow.gold.metrics",
            {"metric_date": "date"},
            "unsafe-view",
            ("metric_date",),
        )


def test_column_contracts_use_exact_decimal_amounts_and_rates():
    assert DAILY_COLUMN_TYPES["total_deposit_amount"] == "decimal(38,2)"
    assert DAILY_COLUMN_TYPES["average_transaction_value"] == "decimal(38,2)"
    assert DAILY_COLUMN_TYPES["success_rate"] == "decimal(9,6)"
    assert AUTH_COLUMN_TYPES["failure_rate"] == "decimal(9,6)"
    assert DECLINE_COLUMN_TYPES["total_declined_amount"] == "decimal(38,2)"
    assert HOURLY_COLUMN_TYPES["average_transaction_amount"] == "decimal(38,2)"
    assert ACCOUNT_COLUMN_TYPES["opening_balance"] == "decimal(18,2)"


def test_daily_transformation_counts_only_terminal_monetary_events_as_attempts():
    source = inspect.getsource(build_daily_transaction_metrics)

    assert 'transaction_status") == "completed"' in source
    assert ".isin(" in source
    assert '"deposit", "withdrawal"' in source
    assert 'transaction_status") == "declined"' in source
    assert "successful | declined" in source


def test_authentication_rates_include_lockout_as_an_unsuccessful_attempt():
    source = inspect.getsource(build_authentication_metrics)

    assert 'F.col("is_success") | F.col("is_failure") | F.col("is_lockout")' in source
    assert 'F.col("failed_authentication_count") + F.col("card_lockout_count")' in source


def test_decline_metrics_filter_to_declined_transactions():
    source = inspect.getsource(build_declined_transaction_metrics)

    assert 'transaction_status") == "declined"' in source
    assert 'groupBy(F.to_date("occurred_at").alias("metric_date")' in source


def test_gold_quality_rules_cover_rates_reconciliation_and_nonnegative_values():
    assert "attempt_reconciliation" in DAILY_QUALITY_RULES
    assert "rate_bounds" in DAILY_QUALITY_RULES
    assert "rate_reconciliation" in DAILY_QUALITY_RULES
    assert "negative_amount" in DAILY_QUALITY_RULES
    assert "attempt_reconciliation" in AUTH_QUALITY_RULES
    assert "event_reconciliation" in AUTH_QUALITY_RULES
    assert "empty_group" in DECLINE_QUALITY_RULES
    assert "empty_group" in HOURLY_QUALITY_RULES
    assert "activity_reconciliation" in ACCOUNT_QUALITY_RULES
    assert "closure_reconciliation" in ACCOUNT_QUALITY_RULES


def test_daily_cli_supports_isolated_validation_tables():
    config = daily_config_from_args(
        [
            "--silver-namespace",
            "day20_silver",
            "--gold-namespace",
            "day20_gold",
            "--daily-table",
            "daily",
            "--authentication-table",
            "authentication",
            "--decline-table",
            "declines",
            "--namespace-location",
            "hdfs://localhost:9000/bankflow/day20-gold",
            "--create-only",
        ]
    )

    assert config.daily_identifier == "bankflow.day20_gold.daily"
    assert config.authentication_metrics_identifier == "bankflow.day20_gold.authentication"
    assert config.decline_identifier == "bankflow.day20_gold.declines"
    assert config.create_only is True


def test_hourly_and_account_clis_support_isolated_tables():
    hourly = hourly_config_from_args(
        ["--gold-namespace", "day20_gold", "--hourly-table", "hourly", "--create-only"]
    )
    account = account_config_from_args(
        ["--gold-namespace", "day20_gold", "--account-table", "accounts", "--create-only"]
    )

    assert hourly.hourly_identifier == "bankflow.day20_gold.hourly"
    assert hourly.create_only is True
    assert account.account_identifier == "bankflow.day20_gold.accounts"
    assert account.create_only is True


@pytest.mark.parametrize(
    "config_type", [DailyMetricsConfig, HourlyMetricsConfig, AccountMetricsConfig]
)
@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"catalog": "unsafe-name"}, "safe SQL identifier"),
        ({"metastore_uri": "http://localhost:9083"}, "thrift"),
        ({"warehouse": "file:///tmp/warehouse"}, "HDFS"),
        ({"namespace_location": "/bankflow/gold"}, "HDFS"),
        ({"app_name": ""}, "non-blank"),
    ],
)
def test_gold_configs_reject_unsafe_runtime_boundaries(config_type, overrides, message):
    with pytest.raises(ValueError, match=message):
        config_type(**overrides)


def test_gold_configs_reject_source_target_collisions():
    with pytest.raises(ValueError, match="must all differ"):
        DailyMetricsConfig(silver_namespace="gold", transaction_source=DEFAULT_DAILY_TABLE)
    with pytest.raises(ValueError, match="must differ"):
        HourlyMetricsConfig(silver_namespace="gold", transaction_source=DEFAULT_HOURLY_TABLE)
    with pytest.raises(ValueError, match="must differ"):
        AccountMetricsConfig(silver_namespace="gold", transaction_source=DEFAULT_ACCOUNT_TABLE)
