"""Transform BankFlow Bronze account lifecycle events into validated Silver records."""

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

from spark.silver.common import (  # noqa: E402
    ATM_PATTERN,
    DEFAULT_BRONZE_NAMESPACE,
    DEFAULT_BRONZE_TABLE,
    DEFAULT_CATALOG,
    DEFAULT_METASTORE_URI,
    DEFAULT_NAMESPACE_LOCATION,
    DEFAULT_SILVER_NAMESPACE,
    DEFAULT_WAREHOUSE,
    MONEY_PATTERN,
    REJECT_COLUMN_TYPES,
    UUID_PATTERN,
    build_spark_session,
    field_spec,
    merge_insert_sql,
    namespace_sql,
    reject_table_sql,
    select_rejects,
    validate_identifiers,
    validate_runtime_settings,
    validate_table_schema,
)

DEFAULT_APP_NAME = "bankflow-silver-accounts"
DEFAULT_ACCOUNT_TABLE = "silver_account_events"
DEFAULT_REJECT_TABLE = "silver_account_event_rejects"
ACCOUNT_EVENT_TYPES = {"account.closed": ("account_closed", "closure")}

ACCOUNT_COLUMN_TYPES = {
    "event_id": "string",
    "event_type": "string",
    "source_event_type": "string",
    "event_class": "string",
    "closure_classification": "string",
    "transaction_id": "string",
    "customer_id": "string",
    "account_id": "string",
    "card_id": "string",
    "account_status": "string",
    "amount": "decimal(18,2)",
    "balance_before": "decimal(18,2)",
    "balance_after": "decimal(18,2)",
    "currency": "string",
    "atm_id": "string",
    "occurred_at": "timestamp",
    "source": "string",
    "schema_version": "int",
    "bronze_ingested_at": "timestamp",
    "silver_processed_at": "timestamp",
    "kafka_topic": "string",
    "kafka_partition": "int",
    "kafka_offset": "bigint",
    "raw_payload_sha256": "string",
}

ACCOUNT_PAYLOAD_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        field_spec("kind", "string"),
        field_spec("transaction_id", "string"),
        field_spec("customer_id", "string"),
        field_spec("account_id", "string"),
        field_spec("card_id", "string"),
        field_spec("transaction_type", "string"),
        field_spec("status", "string"),
        field_spec("amount", "string"),
        field_spec("balance_before", "string"),
        field_spec("balance_after", "string"),
        field_spec("currency", "string"),
        field_spec("account_status", "string"),
        field_spec("decline_reason", "string"),
        field_spec("atm_id", "string"),
    ],
}

ACCOUNT_EVENT_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        field_spec("event_id", "string"),
        field_spec("event_type", "string"),
        field_spec("schema_version", "integer"),
        field_spec("occurred_at", "string"),
        field_spec("source", "string"),
        field_spec("payload", ACCOUNT_PAYLOAD_SCHEMA_SPEC),
        field_spec("_corrupt_record", "string"),
    ],
}


@dataclass(frozen=True)
class AccountConfig:
    catalog: str = DEFAULT_CATALOG
    bronze_namespace: str = DEFAULT_BRONZE_NAMESPACE
    bronze_table: str = DEFAULT_BRONZE_TABLE
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    account_table: str = DEFAULT_ACCOUNT_TABLE
    reject_table: str = DEFAULT_REJECT_TABLE
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
            "bronze_namespace",
            "bronze_table",
            "silver_namespace",
            "account_table",
            "reject_table",
        )
        validate_runtime_settings(self)
        if self.bronze_identifier in {self.account_identifier, self.reject_identifier}:
            raise ValueError("Bronze source and Silver targets must differ.")
        if self.account_identifier == self.reject_identifier:
            raise ValueError("Account and reject tables must differ.")

    @property
    def bronze_identifier(self) -> str:
        return f"{self.catalog}.{self.bronze_namespace}.{self.bronze_table}"

    @property
    def account_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.account_table}"

    @property
    def reject_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.reject_table}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=os.getenv("BANKFLOW_ICEBERG_CATALOG", DEFAULT_CATALOG))
    parser.add_argument(
        "--bronze-namespace",
        default=os.getenv("BANKFLOW_BRONZE_NAMESPACE", DEFAULT_BRONZE_NAMESPACE),
    )
    parser.add_argument(
        "--bronze-table", default=os.getenv("BANKFLOW_BRONZE_TABLE", DEFAULT_BRONZE_TABLE)
    )
    parser.add_argument(
        "--silver-namespace",
        default=os.getenv("BANKFLOW_SILVER_NAMESPACE", DEFAULT_SILVER_NAMESPACE),
    )
    parser.add_argument(
        "--account-table",
        default=os.getenv("BANKFLOW_SILVER_ACCOUNT_TABLE", DEFAULT_ACCOUNT_TABLE),
    )
    parser.add_argument(
        "--reject-table",
        default=os.getenv("BANKFLOW_SILVER_ACCOUNT_REJECT", DEFAULT_REJECT_TABLE),
    )
    parser.add_argument(
        "--metastore-uri",
        default=os.getenv("BANKFLOW_HIVE_METASTORE_URI", DEFAULT_METASTORE_URI),
    )
    parser.add_argument(
        "--warehouse", default=os.getenv("BANKFLOW_ICEBERG_WAREHOUSE", DEFAULT_WAREHOUSE)
    )
    parser.add_argument(
        "--namespace-location",
        default=os.getenv("BANKFLOW_SILVER_PATH", DEFAULT_NAMESPACE_LOCATION),
    )
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--app-name", default=DEFAULT_APP_NAME)
    parser.add_argument("--log-level", choices=("ERROR", "WARN", "INFO"), default="WARN")
    return parser


def config_from_args(argv: list[str] | None = None) -> AccountConfig:
    args = build_parser().parse_args(argv)
    return AccountConfig(
        catalog=args.catalog,
        bronze_namespace=args.bronze_namespace,
        bronze_table=args.bronze_table,
        silver_namespace=args.silver_namespace,
        account_table=args.account_table,
        reject_table=args.reject_table,
        metastore_uri=args.metastore_uri,
        warehouse=args.warehouse,
        namespace_location=args.namespace_location,
        create_only=args.create_only,
        app_name=args.app_name,
        log_level=args.log_level,
    )


def account_table_sql(config: AccountConfig) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {config.account_identifier} (
    event_id STRING NOT NULL,
    event_type STRING NOT NULL,
    source_event_type STRING NOT NULL,
    event_class STRING NOT NULL,
    closure_classification STRING NOT NULL,
    transaction_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    account_id STRING NOT NULL,
    card_id STRING,
    account_status STRING NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    balance_before DECIMAL(18,2) NOT NULL,
    balance_after DECIMAL(18,2) NOT NULL,
    currency STRING NOT NULL,
    atm_id STRING,
    occurred_at TIMESTAMP NOT NULL,
    source STRING NOT NULL,
    schema_version INT NOT NULL,
    bronze_ingested_at TIMESTAMP NOT NULL,
    silver_processed_at TIMESTAMP NOT NULL,
    kafka_topic STRING NOT NULL,
    kafka_partition INT NOT NULL,
    kafka_offset BIGINT NOT NULL,
    raw_payload_sha256 STRING NOT NULL
)
USING iceberg
PARTITIONED BY (days(occurred_at))
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def merge_sql(config: AccountConfig, view_name: str) -> str:
    return merge_insert_sql(config.account_identifier, ACCOUNT_COLUMN_TYPES, view_name, "event_id")


def merge_reject_sql(config: AccountConfig, view_name: str) -> str:
    return merge_insert_sql(config.reject_identifier, REJECT_COLUMN_TYPES, view_name, "reject_id")


def build_account_event_schema():
    from pyspark.sql.types import StructType

    return StructType.fromJson(ACCOUNT_EVENT_SCHEMA_SPEC)


def transform_bronze_accounts(bronze_df):
    """Normalize account-closure facts and classify invalid or duplicate rows."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    source = bronze_df.filter(
        (F.col("payload_kind") == "transaction") & F.col("event_type").isin(*ACCOUNT_EVENT_TYPES)
    )
    parsed = source.withColumn(
        "_raw",
        F.from_json(
            F.col("raw_payload"),
            build_account_event_schema(),
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    )
    event = F.col("_raw")
    payload = F.col("_raw.payload")
    normalized = (
        parsed.withColumn("_event_id", F.lower(event.event_id))
        .withColumn("_source_event_type", F.lower(F.trim(event.event_type)))
        .withColumn("_event_type", F.lit("account_closed"))
        .withColumn("_event_class", F.lit("closure"))
        .withColumn("_closure_classification", F.lit("zero_balance_withdrawal"))
        .withColumn("_transaction_id", F.lower(payload.transaction_id))
        .withColumn("_customer_id", F.lower(payload.customer_id))
        .withColumn("_account_id", F.lower(payload.account_id))
        .withColumn("_card_id", F.lower(payload.card_id))
        .withColumn("_account_status", F.lower(F.trim(payload.account_status)))
        .withColumn("_transaction_type", F.lower(F.trim(payload.transaction_type)))
        .withColumn("_transaction_status", F.lower(F.trim(payload.status)))
        .withColumn("_amount_text", F.trim(payload.amount))
        .withColumn("_balance_before_text", F.trim(payload.balance_before))
        .withColumn("_balance_after_text", F.trim(payload.balance_after))
        .withColumn("_amount", F.expr("try_cast(_raw.payload.amount AS DECIMAL(18,2))"))
        .withColumn(
            "_balance_before",
            F.expr("try_cast(_raw.payload.balance_before AS DECIMAL(18,2))"),
        )
        .withColumn(
            "_balance_after",
            F.expr("try_cast(_raw.payload.balance_after AS DECIMAL(18,2))"),
        )
        .withColumn("_currency", F.upper(F.trim(payload.currency)))
        .withColumn("_atm_id", F.upper(F.trim(payload.atm_id)))
        .withColumn("_occurred_at", F.to_utc_timestamp(F.to_timestamp(event.occurred_at), "UTC"))
        .withColumn("_source", F.trim(event.source))
        .withColumn("_schema_version", event.schema_version.cast("int"))
    )
    required_present = (
        F.col("_event_id").isNotNull()
        & F.col("_source_event_type").isNotNull()
        & F.col("_transaction_id").isNotNull()
        & F.col("_customer_id").isNotNull()
        & F.col("_account_id").isNotNull()
        & F.col("_account_status").isNotNull()
        & F.col("_amount_text").isNotNull()
        & F.col("_balance_before_text").isNotNull()
        & F.col("_balance_after_text").isNotNull()
        & F.col("_currency").isNotNull()
        & F.col("_occurred_at").isNotNull()
    )
    identifiers_valid = (
        F.col("_event_id").rlike(UUID_PATTERN)
        & F.col("_transaction_id").rlike(UUID_PATTERN)
        & F.col("_customer_id").rlike(UUID_PATTERN)
        & F.col("_account_id").rlike(UUID_PATTERN)
        & (F.col("_card_id").isNull() | F.col("_card_id").rlike(UUID_PATTERN))
    )
    money_valid = (
        F.col("_amount_text").rlike(MONEY_PATTERN)
        & F.col("_balance_before_text").rlike(MONEY_PATTERN)
        & F.col("_balance_after_text").rlike(MONEY_PATTERN)
        & F.col("_amount").isNotNull()
        & F.col("_balance_before").isNotNull()
        & F.col("_balance_after").isNotNull()
    )
    closure_valid = (
        (F.col("_source_event_type") == "account.closed")
        & (F.col("_transaction_type") == "withdrawal")
        & (F.col("_transaction_status") == "completed")
        & (F.col("_account_status") == "closed")
        & (F.col("_amount") > 0)
        & (F.col("_balance_after") == 0)
        & ((F.col("_balance_before") - F.col("_balance_after")) == F.col("_amount"))
        & payload.decline_reason.isNull()
    )
    metadata_matches = (
        (F.col("_event_id") == F.lower(F.col("event_id")))
        & (F.col("_source_event_type") == F.col("event_type"))
        & (F.col("_schema_version") == F.col("schema_version"))
        & (F.col("_source") == F.col("source"))
        & (payload.kind == F.col("payload_kind"))
        & (F.col("_occurred_at") == F.col("occurred_at"))
    )
    domain_valid = (
        (F.col("_schema_version") == 1)
        & (F.col("_source") == "bankflow.application")
        & F.col("_currency").rlike(r"^[A-Z]{3}$")
        & (payload.atm_id.isNull() | payload.atm_id.rlike(ATM_PATTERN))
    )
    base_error = (
        F.when(event.isNull() | event["_corrupt_record"].isNotNull(), "malformed_raw_payload")
        .when(~F.coalesce(required_present, F.lit(False)), "missing_required_field")
        .when(~F.coalesce(metadata_matches, F.lit(False)), "bronze_metadata_mismatch")
        .when(~F.coalesce(identifiers_valid, F.lit(False)), "invalid_account_identifier")
        .when(~F.coalesce(money_valid, F.lit(False)), "invalid_numeric_value")
        .when(~F.coalesce(domain_valid, F.lit(False)), "invalid_domain_value")
        .when(~F.coalesce(closure_valid, F.lit(False)), "invalid_account_closure")
    )
    ranked = normalized.withColumn("_base_validation_error", base_error).withColumn(
        "_event_rank",
        F.row_number().over(
            Window.partitionBy("_event_id").orderBy(
                F.when(F.col("_base_validation_error").isNull(), 0).otherwise(1),
                "kafka_timestamp",
                "kafka_topic",
                "kafka_partition",
                "kafka_offset",
            )
        ),
    )
    validation_error = F.coalesce(
        F.col("_base_validation_error"),
        F.when(F.col("_event_rank") > 1, "duplicate_event_id"),
    )
    return ranked.select(
        F.col("_event_id").alias("event_id"),
        F.col("_event_type").alias("event_type"),
        F.col("_source_event_type").alias("source_event_type"),
        F.col("_event_class").alias("event_class"),
        F.col("_closure_classification").alias("closure_classification"),
        F.col("_transaction_id").alias("transaction_id"),
        F.col("_customer_id").alias("customer_id"),
        F.col("_account_id").alias("account_id"),
        F.col("_card_id").alias("card_id"),
        F.col("_account_status").alias("account_status"),
        F.col("_amount").alias("amount"),
        F.col("_balance_before").alias("balance_before"),
        F.col("_balance_after").alias("balance_after"),
        F.col("_currency").alias("currency"),
        F.col("_atm_id").alias("atm_id"),
        F.col("_occurred_at").alias("occurred_at"),
        F.col("_source").alias("source"),
        F.col("_schema_version").alias("schema_version"),
        F.col("ingested_at").alias("bronze_ingested_at"),
        F.current_timestamp().alias("silver_processed_at"),
        "kafka_topic",
        "kafka_partition",
        "kafka_offset",
        "raw_payload_sha256",
        validation_error.alias("validation_error"),
    )


def ensure_tables(spark, config: AccountConfig) -> None:
    if not spark.catalog.tableExists(config.bronze_identifier):
        raise RuntimeError(f"Bronze source table does not exist: {config.bronze_identifier}.")
    spark.sql(namespace_sql(config))
    spark.sql(account_table_sql(config))
    spark.sql(reject_table_sql(config))
    validate_table_schema(spark, config.account_identifier, ACCOUNT_COLUMN_TYPES, 19)
    validate_table_schema(spark, config.reject_identifier, REJECT_COLUMN_TYPES, 19)


def run_pipeline(config: AccountConfig) -> int:
    from pyspark import StorageLevel
    from pyspark.sql import functions as F

    spark = build_spark_session(config)
    transformed = None
    valid_view = "_bankflow_silver_accounts"
    reject_view = "_bankflow_silver_account_rejects"
    try:
        ensure_tables(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_silver_account_tables_ready",
                        "source": config.bronze_identifier,
                        "table": config.account_identifier,
                        "reject_table": config.reject_identifier,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        transformed = transform_bronze_accounts(spark.table(config.bronze_identifier)).persist(
            StorageLevel.MEMORY_AND_DISK
        )
        source_rows = transformed.count()
        reason_counts = {
            row["validation_error"]: row["count"]
            for row in transformed.filter(F.col("validation_error").isNotNull())
            .groupBy("validation_error")
            .count()
            .collect()
        }
        rejected_rows = sum(reason_counts.values())
        valid_rows = source_rows - rejected_rows
        rows_before = spark.table(config.account_identifier).count()
        if valid_rows:
            valid = transformed.filter(F.col("validation_error").isNull()).select(
                *ACCOUNT_COLUMN_TYPES
            )
            valid.createOrReplaceTempView(valid_view)
            spark.sql(merge_sql(config, valid_view))
        if rejected_rows:
            rejects = select_rejects(transformed, F)
            rejects.createOrReplaceTempView(reject_view)
            spark.sql(merge_reject_sql(config, reject_view))
        rows_after = spark.table(config.account_identifier).count()
        print(
            json.dumps(
                {
                    "event": "bankflow_silver_account_quality",
                    "source_rows": source_rows,
                    "valid_rows": valid_rows,
                    "rejected_rows": rejected_rows,
                    "duplicates_removed": reason_counts.get("duplicate_event_id", 0),
                    "rejection_reasons": dict(sorted(reason_counts.items())),
                    "rows_inserted": rows_after - rows_before,
                    "target_rows": rows_after,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 0
    finally:
        for view_name in (valid_view, reject_view):
            if spark.catalog.tableExists(view_name):
                spark.catalog.dropTempView(view_name)
        if transformed is not None:
            transformed.unpersist()
        spark.stop()


def main(argv: list[str] | None = None) -> int:
    try:
        return run_pipeline(config_from_args(argv))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_silver_accounts_failed",
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
