"""Build daily account-activity metrics from BankFlow Silver facts."""

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

DEFAULT_APP_NAME = "bankflow-gold-account-metrics"
DEFAULT_TRANSACTION_SOURCE = "silver_transactions"
DEFAULT_ACCOUNT_SOURCE = "silver_account_events"
DEFAULT_ACCOUNT_TABLE = "gold_account_activity"

ACCOUNT_COLUMN_TYPES = {
    "metric_date": "date",
    "account_id": "string",
    "currency": "string",
    "activity_event_count": "bigint",
    "transaction_event_count": "bigint",
    "distinct_transaction_count": "bigint",
    "completed_monetary_transaction_count": "bigint",
    "declined_transaction_count": "bigint",
    "balance_inquiry_count": "bigint",
    "deposit_count": "bigint",
    "successful_withdrawal_count": "bigint",
    "closure_event_count": "bigint",
    "total_deposit_amount": "decimal(38,2)",
    "total_withdrawal_amount": "decimal(38,2)",
    "total_declined_amount": "decimal(38,2)",
    "opening_balance": "decimal(18,2)",
    "closing_balance": "decimal(18,2)",
    "account_status": "string",
    "account_closed": "boolean",
    "first_activity_at": "timestamp",
    "last_activity_at": "timestamp",
    "gold_processed_at": "timestamp",
}

ACCOUNT_QUALITY_RULES = {
    "null_grain": "metric_date IS NULL OR account_id IS NULL OR currency IS NULL",
    "empty_group": "activity_event_count <= 0",
    "activity_reconciliation": (
        "activity_event_count <> transaction_event_count + closure_event_count"
    ),
    "negative_count": (
        "transaction_event_count < 0 OR distinct_transaction_count < 0 OR "
        "completed_monetary_transaction_count < 0 OR declined_transaction_count < 0"
    ),
    "negative_amount": (
        "total_deposit_amount < 0 OR total_withdrawal_amount < 0 "
        "OR total_declined_amount < 0 OR opening_balance < 0 OR closing_balance < 0"
    ),
    "closure_reconciliation": (
        "(account_closed AND closure_event_count = 0) OR "
        "(NOT account_closed AND closure_event_count > 0)"
    ),
    "invalid_time_range": "first_activity_at > last_activity_at",
}


@dataclass(frozen=True)
class AccountMetricsConfig:
    catalog: str = DEFAULT_CATALOG
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    gold_namespace: str = DEFAULT_GOLD_NAMESPACE
    transaction_source: str = DEFAULT_TRANSACTION_SOURCE
    account_source: str = DEFAULT_ACCOUNT_SOURCE
    account_table: str = DEFAULT_ACCOUNT_TABLE
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
            "account_source",
            "account_table",
        )
        validate_runtime_settings(self)
        if self.account_identifier in {
            self.transaction_identifier,
            self.account_source_identifier,
        }:
            raise ValueError("Gold sources and target must differ.")

    @property
    def transaction_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.transaction_source}"

    @property
    def account_source_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.account_source}"

    @property
    def account_identifier(self) -> str:
        return f"{self.catalog}.{self.gold_namespace}.{self.account_table}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=os.getenv("BANKFLOW_ICEBERG_CATALOG", DEFAULT_CATALOG))
    parser.add_argument(
        "--silver-namespace",
        default=os.getenv("BANKFLOW_SILVER_NAMESPACE", DEFAULT_SILVER_NAMESPACE),
    )
    parser.add_argument(
        "--gold-namespace",
        default=os.getenv("BANKFLOW_GOLD_NAMESPACE", DEFAULT_GOLD_NAMESPACE),
    )
    parser.add_argument("--transaction-source", default=DEFAULT_TRANSACTION_SOURCE)
    parser.add_argument("--account-source", default=DEFAULT_ACCOUNT_SOURCE)
    parser.add_argument("--account-table", default=DEFAULT_ACCOUNT_TABLE)
    parser.add_argument(
        "--metastore-uri",
        default=os.getenv("BANKFLOW_HIVE_METASTORE_URI", DEFAULT_METASTORE_URI),
    )
    parser.add_argument(
        "--warehouse", default=os.getenv("BANKFLOW_ICEBERG_WAREHOUSE", DEFAULT_WAREHOUSE)
    )
    parser.add_argument(
        "--namespace-location",
        default=os.getenv("BANKFLOW_GOLD_PATH", DEFAULT_NAMESPACE_LOCATION),
    )
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--app-name", default=DEFAULT_APP_NAME)
    parser.add_argument("--log-level", choices=("ERROR", "WARN", "INFO"), default="WARN")
    return parser


def config_from_args(argv: list[str] | None = None) -> AccountMetricsConfig:
    return AccountMetricsConfig(**vars(build_parser().parse_args(argv)))


def account_table_sql(config: AccountMetricsConfig) -> str:
    definitions = ",\n    ".join(
        f"{name} {data_type.upper()} NOT NULL" for name, data_type in ACCOUNT_COLUMN_TYPES.items()
    )
    return f"""
CREATE TABLE IF NOT EXISTS {config.account_identifier} (
    {definitions}
)
USING iceberg
PARTITIONED BY (metric_date)
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def account_merge_sql(config: AccountMetricsConfig, view_name: str) -> str:
    return merge_upsert_sql(
        config.account_identifier,
        ACCOUNT_COLUMN_TYPES,
        view_name,
        ("metric_date", "account_id", "currency"),
    )


def _transaction_activity(transactions):
    from pyspark.sql import functions as F

    successful = (F.col("transaction_status") == "completed") & F.col("transaction_type").isin(
        "deposit", "withdrawal"
    )
    declined = F.col("transaction_status") == "declined"
    zero = F.lit(0).cast("decimal(18,2)")
    return transactions.select(
        F.to_date("occurred_at").alias("metric_date"),
        "account_id",
        "currency",
        "event_id",
        "transaction_id",
        F.lit(1).alias("transaction_event"),
        F.lit(0).alias("closure_event"),
        F.when(successful, 1).otherwise(0).alias("completed_monetary"),
        F.when(declined, 1).otherwise(0).alias("declined_transaction"),
        F.when(F.col("transaction_type") == "balance_inquiry", 1)
        .otherwise(0)
        .alias("balance_inquiry"),
        F.when(successful & (F.col("transaction_type") == "deposit"), 1)
        .otherwise(0)
        .alias("deposit"),
        F.when(successful & (F.col("transaction_type") == "withdrawal"), 1)
        .otherwise(0)
        .alias("successful_withdrawal"),
        F.when(successful & (F.col("transaction_type") == "deposit"), F.col("amount"))
        .otherwise(zero)
        .alias("deposit_amount"),
        F.when(successful & (F.col("transaction_type") == "withdrawal"), F.col("amount"))
        .otherwise(zero)
        .alias("withdrawal_amount"),
        F.when(declined, F.col("amount")).otherwise(zero).alias("declined_amount"),
        "balance_before",
        "balance_after",
        "account_status",
        F.lit(False).alias("account_closed"),
        "occurred_at",
    )


def _account_activity(accounts):
    from pyspark.sql import functions as F

    zero = F.lit(0).cast("decimal(18,2)")
    return accounts.select(
        F.to_date("occurred_at").alias("metric_date"),
        "account_id",
        "currency",
        "event_id",
        F.lit(None).cast("string").alias("transaction_id"),
        F.lit(0).alias("transaction_event"),
        F.lit(1).alias("closure_event"),
        F.lit(0).alias("completed_monetary"),
        F.lit(0).alias("declined_transaction"),
        F.lit(0).alias("balance_inquiry"),
        F.lit(0).alias("deposit"),
        F.lit(0).alias("successful_withdrawal"),
        zero.alias("deposit_amount"),
        zero.alias("withdrawal_amount"),
        zero.alias("declined_amount"),
        "balance_before",
        "balance_after",
        "account_status",
        F.lit(True).alias("account_closed"),
        "occurred_at",
    )


def build_account_activity_metrics(transactions, accounts):
    from pyspark.sql import functions as F

    activity = _transaction_activity(transactions).unionByName(_account_activity(accounts))
    order = F.struct("occurred_at", "event_id")
    return (
        activity.groupBy("metric_date", "account_id", "currency")
        .agg(
            F.count("event_id").cast("long").alias("activity_event_count"),
            F.sum("transaction_event").cast("long").alias("transaction_event_count"),
            F.countDistinct("transaction_id").cast("long").alias("distinct_transaction_count"),
            F.sum("completed_monetary").cast("long").alias("completed_monetary_transaction_count"),
            F.sum("declined_transaction").cast("long").alias("declined_transaction_count"),
            F.sum("balance_inquiry").cast("long").alias("balance_inquiry_count"),
            F.sum("deposit").cast("long").alias("deposit_count"),
            F.sum("successful_withdrawal").cast("long").alias("successful_withdrawal_count"),
            F.sum("closure_event").cast("long").alias("closure_event_count"),
            F.sum("deposit_amount").cast("decimal(38,2)").alias("total_deposit_amount"),
            F.sum("withdrawal_amount").cast("decimal(38,2)").alias("total_withdrawal_amount"),
            F.sum("declined_amount").cast("decimal(38,2)").alias("total_declined_amount"),
            F.min_by("balance_before", order).cast("decimal(18,2)").alias("opening_balance"),
            F.max_by("balance_after", order).cast("decimal(18,2)").alias("closing_balance"),
            F.max_by("account_status", order).alias("account_status"),
            (F.max(F.col("account_closed").cast("int")) == 1).alias("account_closed"),
            F.min("occurred_at").alias("first_activity_at"),
            F.max("occurred_at").alias("last_activity_at"),
        )
        .withColumn("gold_processed_at", F.current_timestamp())
        .select(*ACCOUNT_COLUMN_TYPES)
    )


def ensure_table(spark, config: AccountMetricsConfig) -> None:
    spark.sql(namespace_sql(config))
    spark.sql(account_table_sql(config))
    validate_table_schema(spark, config.account_identifier, ACCOUNT_COLUMN_TYPES)


def run_pipeline(config: AccountMetricsConfig) -> int:
    spark = build_spark_session(config)
    frame = None
    view = "_bankflow_gold_accounts"
    try:
        ensure_table(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_gold_account_table_ready",
                        "table": config.account_identifier,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        transactions = spark.table(config.transaction_identifier)
        accounts = spark.table(config.account_source_identifier)
        frame = build_account_activity_metrics(transactions, accounts).cache()
        output_rows = frame.count()
        quality = quality_violation_counts(frame, ACCOUNT_QUALITY_RULES)
        if output_rows:
            frame.createOrReplaceTempView(view)
            spark.sql(account_merge_sql(config, view))
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_account_quality",
                    "source_transaction_rows": transactions.count(),
                    "source_account_rows": accounts.count(),
                    "output_rows": output_rows,
                    "quality_violations": quality,
                    "target_rows": spark.table(config.account_identifier).count(),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 0
    finally:
        if spark.catalog.tableExists(view):
            spark.catalog.dropTempView(view)
        if frame is not None:
            frame.unpersist()
        spark.stop()


def main(argv: list[str] | None = None) -> int:
    try:
        return run_pipeline(config_from_args(argv))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_account_failed",
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
