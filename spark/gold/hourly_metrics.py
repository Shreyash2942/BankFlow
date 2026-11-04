"""Build hourly BankFlow transaction-volume metrics from validated Silver events."""

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

DEFAULT_APP_NAME = "bankflow-gold-hourly-metrics"
DEFAULT_TRANSACTION_SOURCE = "silver_transactions"
DEFAULT_HOURLY_TABLE = "gold_hourly_transaction_volume"

HOURLY_COLUMN_TYPES = {
    "event_hour": "timestamp",
    "currency": "string",
    "transaction_type": "string",
    "transaction_status": "string",
    "transaction_event_count": "bigint",
    "total_transaction_amount": "decimal(38,2)",
    "average_transaction_amount": "decimal(38,2)",
    "unique_account_count": "bigint",
    "first_event_at": "timestamp",
    "last_event_at": "timestamp",
    "gold_processed_at": "timestamp",
}

HOURLY_QUALITY_RULES = {
    "null_grain": (
        "event_hour IS NULL OR currency IS NULL OR transaction_type IS NULL "
        "OR transaction_status IS NULL"
    ),
    "empty_group": "transaction_event_count <= 0",
    "negative_amount": ("total_transaction_amount < 0 OR average_transaction_amount < 0"),
    "invalid_time_range": "first_event_at > last_event_at",
}


@dataclass(frozen=True)
class HourlyMetricsConfig:
    catalog: str = DEFAULT_CATALOG
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    gold_namespace: str = DEFAULT_GOLD_NAMESPACE
    transaction_source: str = DEFAULT_TRANSACTION_SOURCE
    hourly_table: str = DEFAULT_HOURLY_TABLE
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
            "hourly_table",
        )
        validate_runtime_settings(self)
        if self.transaction_identifier == self.hourly_identifier:
            raise ValueError("Gold source and target must differ.")

    @property
    def transaction_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.transaction_source}"

    @property
    def hourly_identifier(self) -> str:
        return f"{self.catalog}.{self.gold_namespace}.{self.hourly_table}"


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
    parser.add_argument("--hourly-table", default=DEFAULT_HOURLY_TABLE)
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


def config_from_args(argv: list[str] | None = None) -> HourlyMetricsConfig:
    return HourlyMetricsConfig(**vars(build_parser().parse_args(argv)))


def hourly_table_sql(config: HourlyMetricsConfig) -> str:
    definitions = ",\n    ".join(
        f"{name} {data_type.upper()} NOT NULL" for name, data_type in HOURLY_COLUMN_TYPES.items()
    )
    return f"""
CREATE TABLE IF NOT EXISTS {config.hourly_identifier} (
    {definitions}
)
USING iceberg
PARTITIONED BY (days(event_hour))
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def hourly_merge_sql(config: HourlyMetricsConfig, view_name: str) -> str:
    return merge_upsert_sql(
        config.hourly_identifier,
        HOURLY_COLUMN_TYPES,
        view_name,
        ("event_hour", "currency", "transaction_type", "transaction_status"),
    )


def build_hourly_transaction_metrics(transactions):
    from pyspark.sql import functions as F

    return (
        transactions.groupBy(
            F.date_trunc("hour", "occurred_at").alias("event_hour"),
            "currency",
            "transaction_type",
            "transaction_status",
        )
        .agg(
            F.count("event_id").cast("long").alias("transaction_event_count"),
            F.sum("amount").cast("decimal(38,2)").alias("total_transaction_amount"),
            F.avg("amount").cast("decimal(38,2)").alias("average_transaction_amount"),
            F.countDistinct("account_id").cast("long").alias("unique_account_count"),
            F.min("occurred_at").alias("first_event_at"),
            F.max("occurred_at").alias("last_event_at"),
        )
        .withColumn("gold_processed_at", F.current_timestamp())
        .select(*HOURLY_COLUMN_TYPES)
    )


def ensure_table(spark, config: HourlyMetricsConfig) -> None:
    spark.sql(namespace_sql(config))
    spark.sql(hourly_table_sql(config))
    validate_table_schema(spark, config.hourly_identifier, HOURLY_COLUMN_TYPES)


def run_pipeline(config: HourlyMetricsConfig) -> int:
    spark = build_spark_session(config)
    frame = None
    view = "_bankflow_gold_hourly"
    try:
        ensure_table(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_gold_hourly_table_ready",
                        "table": config.hourly_identifier,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        source = spark.table(config.transaction_identifier)
        frame = build_hourly_transaction_metrics(source).cache()
        output_rows = frame.count()
        quality = quality_violation_counts(frame, HOURLY_QUALITY_RULES)
        if output_rows:
            frame.createOrReplaceTempView(view)
            spark.sql(hourly_merge_sql(config, view))
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_hourly_quality",
                    "source_rows": source.count(),
                    "output_rows": output_rows,
                    "quality_violations": quality,
                    "target_rows": spark.table(config.hourly_identifier).count(),
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
                    "event": "bankflow_gold_hourly_failed",
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
