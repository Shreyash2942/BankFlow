"""Build BankFlow Gold daily transaction, authentication, and decline metrics."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from spark.gold.common import (  # noqa: E402
    DEFAULT_CATALOG,
    DEFAULT_GOLD_NAMESPACE,
    DEFAULT_METASTORE_URI,
    DEFAULT_NAMESPACE_LOCATION,
    DEFAULT_SILVER_NAMESPACE,
    DEFAULT_WAREHOUSE,
    build_spark_session,
    merge_upsert_sql,
    namespace_sql,
    quality_violation_counts,
    validate_identifiers,
    validate_runtime_settings,
    validate_table_schema,
)

DEFAULT_APP_NAME = "bankflow-gold-daily-metrics"
DEFAULT_TRANSACTION_SOURCE = "silver_transactions"
DEFAULT_AUTHENTICATION_SOURCE = "silver_authentication_events"
DEFAULT_DAILY_TABLE = "gold_daily_transaction_metrics"
DEFAULT_AUTH_TABLE = "gold_authentication_metrics"
DEFAULT_DECLINE_TABLE = "gold_declined_transactions"

DAILY_COLUMN_TYPES = {
    "metric_date": "date",
    "currency": "string",
    "transaction_event_count": "bigint",
    "monetary_attempt_count": "bigint",
    "successful_transaction_count": "bigint",
    "declined_transaction_count": "bigint",
    "balance_inquiry_count": "bigint",
    "deposit_count": "bigint",
    "successful_withdrawal_count": "bigint",
    "declined_withdrawal_count": "bigint",
    "total_deposit_amount": "decimal(38,2)",
    "total_withdrawal_amount": "decimal(38,2)",
    "total_declined_amount": "decimal(38,2)",
    "average_transaction_value": "decimal(38,2)",
    "success_rate": "decimal(9,6)",
    "decline_rate": "decimal(9,6)",
    "unique_account_count": "bigint",
    "first_event_at": "timestamp",
    "last_event_at": "timestamp",
    "gold_processed_at": "timestamp",
}

AUTH_COLUMN_TYPES = {
    "metric_date": "date",
    "authentication_event_count": "bigint",
    "authentication_attempt_count": "bigint",
    "successful_authentication_count": "bigint",
    "failed_authentication_count": "bigint",
    "card_lockout_count": "bigint",
    "session_end_count": "bigint",
    "known_subject_event_count": "bigint",
    "unknown_subject_event_count": "bigint",
    "unique_account_count": "bigint",
    "unique_card_count": "bigint",
    "success_rate": "decimal(9,6)",
    "failure_rate": "decimal(9,6)",
    "first_event_at": "timestamp",
    "last_event_at": "timestamp",
    "gold_processed_at": "timestamp",
}

DECLINE_COLUMN_TYPES = {
    "metric_date": "date",
    "currency": "string",
    "decline_reason": "string",
    "declined_transaction_count": "bigint",
    "total_declined_amount": "decimal(38,2)",
    "average_declined_amount": "decimal(38,2)",
    "unique_account_count": "bigint",
    "first_declined_at": "timestamp",
    "last_declined_at": "timestamp",
    "gold_processed_at": "timestamp",
}

DAILY_QUALITY_RULES = {
    "null_grain": "metric_date IS NULL OR currency IS NULL",
    "negative_count": (
        "transaction_event_count < 0 OR monetary_attempt_count < 0 OR "
        "successful_transaction_count < 0 OR declined_transaction_count < 0"
    ),
    "attempt_reconciliation": (
        "monetary_attempt_count <> successful_transaction_count + declined_transaction_count"
    ),
    "rate_bounds": ("success_rate < 0 OR success_rate > 1 OR decline_rate < 0 OR decline_rate > 1"),
    "rate_reconciliation": (
        "(monetary_attempt_count > 0 AND ABS(success_rate + decline_rate - 1) > 0.000001) "
        "OR (monetary_attempt_count = 0 AND (success_rate <> 0 OR decline_rate <> 0))"
    ),
    "negative_amount": (
        "total_deposit_amount < 0 OR total_withdrawal_amount < 0 "
        "OR total_declined_amount < 0 OR average_transaction_value < 0"
    ),
}

AUTH_QUALITY_RULES = {
    "null_grain": "metric_date IS NULL",
    "attempt_reconciliation": (
        "authentication_attempt_count <> successful_authentication_count + "
        "failed_authentication_count + card_lockout_count"
    ),
    "event_reconciliation": (
        "authentication_event_count <> authentication_attempt_count + session_end_count"
    ),
    "rate_bounds": ("success_rate < 0 OR success_rate > 1 OR failure_rate < 0 OR failure_rate > 1"),
    "rate_reconciliation": (
        "(authentication_attempt_count > 0 "
        "AND ABS(success_rate + failure_rate - 1) > 0.000001) OR "
        "(authentication_attempt_count = 0 AND (success_rate <> 0 OR failure_rate <> 0))"
    ),
}

DECLINE_QUALITY_RULES = {
    "null_grain": "metric_date IS NULL OR currency IS NULL OR decline_reason IS NULL",
    "empty_group": "declined_transaction_count <= 0",
    "negative_amount": "total_declined_amount < 0 OR average_declined_amount < 0",
}


@dataclass(frozen=True)
class DailyMetricsConfig:
    catalog: str = DEFAULT_CATALOG
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    gold_namespace: str = DEFAULT_GOLD_NAMESPACE
    transaction_source: str = DEFAULT_TRANSACTION_SOURCE
    authentication_source: str = DEFAULT_AUTHENTICATION_SOURCE
    daily_table: str = DEFAULT_DAILY_TABLE
    authentication_table: str = DEFAULT_AUTH_TABLE
    decline_table: str = DEFAULT_DECLINE_TABLE
    metastore_uri: str = DEFAULT_METASTORE_URI
    warehouse: str = DEFAULT_WAREHOUSE
    namespace_location: str = DEFAULT_NAMESPACE_LOCATION
    create_only: bool = False
    app_name: str = DEFAULT_APP_NAME
    log_level: str = "WARN"

    def __post_init__(self) -> None:
        validate_identifiers(
            self,
            "catalog",
            "silver_namespace",
            "gold_namespace",
            "transaction_source",
            "authentication_source",
            "daily_table",
            "authentication_table",
            "decline_table",
        )
        validate_runtime_settings(self)
        sources = {self.transaction_identifier, self.authentication_identifier}
        targets = {
            self.daily_identifier,
            self.authentication_metrics_identifier,
            self.decline_identifier,
        }
        if len(targets) != 3 or sources & targets:
            raise ValueError("Gold sources and targets must all differ.")

    @property
    def transaction_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.transaction_source}"

    @property
    def authentication_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.authentication_source}"

    @property
    def daily_identifier(self) -> str:
        return f"{self.catalog}.{self.gold_namespace}.{self.daily_table}"

    @property
    def authentication_metrics_identifier(self) -> str:
        return f"{self.catalog}.{self.gold_namespace}.{self.authentication_table}"

    @property
    def decline_identifier(self) -> str:
        return f"{self.catalog}.{self.gold_namespace}.{self.decline_table}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=os.getenv("BANKFLOW_ICEBERG_CATALOG", DEFAULT_CATALOG))
    parser.add_argument(
        "--silver-namespace",
        default=os.getenv("BANKFLOW_SILVER_NAMESPACE", DEFAULT_SILVER_NAMESPACE),
    )
    parser.add_argument(
        "--gold-namespace", default=os.getenv("BANKFLOW_GOLD_NAMESPACE", DEFAULT_GOLD_NAMESPACE)
    )
    parser.add_argument("--transaction-source", default=DEFAULT_TRANSACTION_SOURCE)
    parser.add_argument("--authentication-source", default=DEFAULT_AUTHENTICATION_SOURCE)
    parser.add_argument("--daily-table", default=DEFAULT_DAILY_TABLE)
    parser.add_argument("--authentication-table", default=DEFAULT_AUTH_TABLE)
    parser.add_argument("--decline-table", default=DEFAULT_DECLINE_TABLE)
    parser.add_argument(
        "--metastore-uri", default=os.getenv("BANKFLOW_HIVE_METASTORE_URI", DEFAULT_METASTORE_URI)
    )
    parser.add_argument(
        "--warehouse", default=os.getenv("BANKFLOW_ICEBERG_WAREHOUSE", DEFAULT_WAREHOUSE)
    )
    parser.add_argument(
        "--namespace-location", default=os.getenv("BANKFLOW_GOLD_PATH", DEFAULT_NAMESPACE_LOCATION)
    )
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--app-name", default=DEFAULT_APP_NAME)
    parser.add_argument("--log-level", choices=("ERROR", "WARN", "INFO"), default="WARN")
    return parser


def config_from_args(argv: list[str] | None = None) -> DailyMetricsConfig:
    return DailyMetricsConfig(**vars(build_parser().parse_args(argv)))


def _table_sql(identifier: str, columns: dict[str, str], partition: str) -> str:
    definitions = ",\n    ".join(
        f"{name} {data_type.upper()} NOT NULL" for name, data_type in columns.items()
    )
    return f"""
CREATE TABLE IF NOT EXISTS {identifier} (
    {definitions}
)
USING iceberg
PARTITIONED BY ({partition})
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def daily_table_sql(config: DailyMetricsConfig) -> str:
    return _table_sql(config.daily_identifier, DAILY_COLUMN_TYPES, "metric_date")


def authentication_table_sql(config: DailyMetricsConfig) -> str:
    return _table_sql(config.authentication_metrics_identifier, AUTH_COLUMN_TYPES, "metric_date")


def decline_table_sql(config: DailyMetricsConfig) -> str:
    return _table_sql(config.decline_identifier, DECLINE_COLUMN_TYPES, "metric_date")


def daily_merge_sql(config: DailyMetricsConfig, view_name: str) -> str:
    return merge_upsert_sql(
        config.daily_identifier, DAILY_COLUMN_TYPES, view_name, ("metric_date", "currency")
    )


def authentication_merge_sql(config: DailyMetricsConfig, view_name: str) -> str:
    return merge_upsert_sql(
        config.authentication_metrics_identifier,
        AUTH_COLUMN_TYPES,
        view_name,
        ("metric_date",),
    )


def decline_merge_sql(config: DailyMetricsConfig, view_name: str) -> str:
    return merge_upsert_sql(
        config.decline_identifier,
        DECLINE_COLUMN_TYPES,
        view_name,
        ("metric_date", "currency", "decline_reason"),
    )


def build_daily_transaction_metrics(transactions):
    from pyspark.sql import functions as F

    successful = (F.col("transaction_status") == "completed") & F.col("transaction_type").isin(
        "deposit", "withdrawal"
    )
    declined = F.col("transaction_status") == "declined"
    aggregated = transactions.groupBy(
        F.to_date("occurred_at").alias("metric_date"), "currency"
    ).agg(
        F.count("event_id").cast("long").alias("transaction_event_count"),
        F.sum(F.when(successful | declined, 1).otherwise(0))
        .cast("long")
        .alias("monetary_attempt_count"),
        F.sum(F.when(successful, 1).otherwise(0))
        .cast("long")
        .alias("successful_transaction_count"),
        F.sum(F.when(declined, 1).otherwise(0)).cast("long").alias("declined_transaction_count"),
        F.sum(F.when(F.col("transaction_type") == "balance_inquiry", 1).otherwise(0))
        .cast("long")
        .alias("balance_inquiry_count"),
        F.sum(F.when(successful & (F.col("transaction_type") == "deposit"), 1).otherwise(0))
        .cast("long")
        .alias("deposit_count"),
        F.sum(F.when(successful & (F.col("transaction_type") == "withdrawal"), 1).otherwise(0))
        .cast("long")
        .alias("successful_withdrawal_count"),
        F.sum(F.when(declined & (F.col("transaction_type") == "withdrawal"), 1).otherwise(0))
        .cast("long")
        .alias("declined_withdrawal_count"),
        F.sum(
            F.when(
                successful & (F.col("transaction_type") == "deposit"), F.col("amount")
            ).otherwise(F.lit(0))
        )
        .cast("decimal(38,2)")
        .alias("total_deposit_amount"),
        F.sum(
            F.when(
                successful & (F.col("transaction_type") == "withdrawal"), F.col("amount")
            ).otherwise(F.lit(0))
        )
        .cast("decimal(38,2)")
        .alias("total_withdrawal_amount"),
        F.sum(F.when(declined, F.col("amount")).otherwise(F.lit(0)))
        .cast("decimal(38,2)")
        .alias("total_declined_amount"),
        F.coalesce(F.avg(F.when(successful, F.col("amount"))), F.lit(0))
        .cast("decimal(38,2)")
        .alias("average_transaction_value"),
        F.countDistinct("account_id").cast("long").alias("unique_account_count"),
        F.min("occurred_at").alias("first_event_at"),
        F.max("occurred_at").alias("last_event_at"),
    )
    return (
        aggregated.withColumn(
            "success_rate",
            F.when(
                F.col("monetary_attempt_count") > 0,
                F.col("successful_transaction_count") / F.col("monetary_attempt_count"),
            )
            .otherwise(F.lit(0))
            .cast("decimal(9,6)"),
        )
        .withColumn(
            "decline_rate",
            F.when(
                F.col("monetary_attempt_count") > 0,
                F.col("declined_transaction_count") / F.col("monetary_attempt_count"),
            )
            .otherwise(F.lit(0))
            .cast("decimal(9,6)"),
        )
        .withColumn("gold_processed_at", F.current_timestamp())
        .select(*DAILY_COLUMN_TYPES)
    )


def build_authentication_metrics(authentication):
    from pyspark.sql import functions as F

    attempt = F.col("is_success") | F.col("is_failure") | F.col("is_lockout")
    aggregated = authentication.groupBy(F.to_date("occurred_at").alias("metric_date")).agg(
        F.count("event_id").cast("long").alias("authentication_event_count"),
        F.sum(F.when(attempt, 1).otherwise(0)).cast("long").alias("authentication_attempt_count"),
        F.sum(F.when(F.col("is_success"), 1).otherwise(0))
        .cast("long")
        .alias("successful_authentication_count"),
        F.sum(F.when(F.col("is_failure"), 1).otherwise(0))
        .cast("long")
        .alias("failed_authentication_count"),
        F.sum(F.when(F.col("is_lockout"), 1).otherwise(0)).cast("long").alias("card_lockout_count"),
        F.sum(F.when(F.col("is_session_end"), 1).otherwise(0))
        .cast("long")
        .alias("session_end_count"),
        F.sum(F.when(F.col("subject_known"), 1).otherwise(0))
        .cast("long")
        .alias("known_subject_event_count"),
        F.sum(F.when(~F.col("subject_known"), 1).otherwise(0))
        .cast("long")
        .alias("unknown_subject_event_count"),
        F.countDistinct("account_id").cast("long").alias("unique_account_count"),
        F.countDistinct("card_id").cast("long").alias("unique_card_count"),
        F.min("occurred_at").alias("first_event_at"),
        F.max("occurred_at").alias("last_event_at"),
    )
    failures = F.col("failed_authentication_count") + F.col("card_lockout_count")
    return (
        aggregated.withColumn(
            "success_rate",
            F.when(
                F.col("authentication_attempt_count") > 0,
                F.col("successful_authentication_count") / F.col("authentication_attempt_count"),
            )
            .otherwise(F.lit(0))
            .cast("decimal(9,6)"),
        )
        .withColumn(
            "failure_rate",
            F.when(
                F.col("authentication_attempt_count") > 0,
                failures / F.col("authentication_attempt_count"),
            )
            .otherwise(F.lit(0))
            .cast("decimal(9,6)"),
        )
        .withColumn("gold_processed_at", F.current_timestamp())
        .select(*AUTH_COLUMN_TYPES)
    )


def build_declined_transaction_metrics(transactions):
    from pyspark.sql import functions as F

    return (
        transactions.filter(F.col("transaction_status") == "declined")
        .groupBy(F.to_date("occurred_at").alias("metric_date"), "currency", "decline_reason")
        .agg(
            F.count("event_id").cast("long").alias("declined_transaction_count"),
            F.sum("amount").cast("decimal(38,2)").alias("total_declined_amount"),
            F.avg("amount").cast("decimal(38,2)").alias("average_declined_amount"),
            F.countDistinct("account_id").cast("long").alias("unique_account_count"),
            F.min("occurred_at").alias("first_declined_at"),
            F.max("occurred_at").alias("last_declined_at"),
        )
        .withColumn("gold_processed_at", F.current_timestamp())
        .select(*DECLINE_COLUMN_TYPES)
    )


def ensure_tables(spark, config: DailyMetricsConfig) -> None:
    spark.sql(namespace_sql(config))
    for statement in (
        daily_table_sql(config),
        authentication_table_sql(config),
        decline_table_sql(config),
    ):
        spark.sql(statement)
    validate_table_schema(spark, config.daily_identifier, DAILY_COLUMN_TYPES)
    validate_table_schema(spark, config.authentication_metrics_identifier, AUTH_COLUMN_TYPES)
    validate_table_schema(spark, config.decline_identifier, DECLINE_COLUMN_TYPES)


def run_pipeline(config: DailyMetricsConfig) -> int:
    spark = build_spark_session(config)
    frames = []
    views = ("_bankflow_gold_daily", "_bankflow_gold_auth", "_bankflow_gold_declines")
    try:
        ensure_tables(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_gold_daily_tables_ready",
                        "tables": [
                            config.daily_identifier,
                            config.authentication_metrics_identifier,
                            config.decline_identifier,
                        ],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        transactions = spark.table(config.transaction_identifier)
        authentication = spark.table(config.authentication_identifier)
        frames = [
            build_daily_transaction_metrics(transactions).cache(),
            build_authentication_metrics(authentication).cache(),
            build_declined_transaction_metrics(transactions).cache(),
        ]
        rules = (DAILY_QUALITY_RULES, AUTH_QUALITY_RULES, DECLINE_QUALITY_RULES)
        merges = (daily_merge_sql, authentication_merge_sql, decline_merge_sql)
        quality = {}
        rows = {}
        for frame, view, checks, merge_builder in zip(frames, views, rules, merges, strict=True):
            rows[view] = frame.count()
            quality[view] = quality_violation_counts(frame, checks)
            if rows[view]:
                frame.createOrReplaceTempView(view)
                spark.sql(merge_builder(config, view))
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_daily_quality",
                    "source_transaction_rows": transactions.count(),
                    "source_authentication_rows": authentication.count(),
                    "output_rows": rows,
                    "quality_violations": quality,
                    "target_rows": {
                        "daily": spark.table(config.daily_identifier).count(),
                        "authentication": spark.table(
                            config.authentication_metrics_identifier
                        ).count(),
                        "declines": spark.table(config.decline_identifier).count(),
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 0
    finally:
        for view in views:
            if spark.catalog.tableExists(view):
                spark.catalog.dropTempView(view)
        for frame in frames:
            frame.unpersist()
        spark.stop()


def main(argv: list[str] | None = None) -> int:
    try:
        return run_pipeline(config_from_args(argv))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_daily_failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
