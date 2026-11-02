"""Transform immutable BankFlow Bronze events into validated Silver transactions."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass

DEFAULT_APP_NAME = "bankflow-silver-transactions"
DEFAULT_CATALOG = "bankflow"
DEFAULT_BRONZE_NAMESPACE = "bronze"
DEFAULT_BRONZE_TABLE = "bronze_bankflow_events"
DEFAULT_SILVER_NAMESPACE = "silver"
DEFAULT_SILVER_TABLE = "silver_transactions"
DEFAULT_REJECT_TABLE = "silver_transaction_rejects"
DEFAULT_METASTORE_URI = "thrift://localhost:9083"
DEFAULT_WAREHOUSE = "hdfs://localhost:9000/bankflow/lakehouse"
DEFAULT_NAMESPACE_LOCATION = "hdfs://localhost:9000/bankflow/silver"
SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

TRANSACTION_EVENT_SHAPES = {
    "balance.viewed": ("balance_inquiry", "completed"),
    "withdrawal.requested": ("withdrawal", "pending"),
    "withdrawal.completed": ("withdrawal", "completed"),
    "withdrawal.declined": ("withdrawal", "declined"),
    "deposit.completed": ("deposit", "completed"),
}

UUID_PATTERN = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ATM_PATTERN = r"^ATM-[A-Z0-9]{4,12}$"
MONEY_PATTERN = r"^(0|[1-9][0-9]{0,15})(\.[0-9]{1,2})?$"

SILVER_COLUMN_TYPES = {
    "event_id": "string",
    "transaction_id": "string",
    "customer_id": "string",
    "account_id": "string",
    "card_id": "string",
    "event_type": "string",
    "transaction_type": "string",
    "transaction_status": "string",
    "amount": "decimal(18,2)",
    "balance_before": "decimal(18,2)",
    "balance_after": "decimal(18,2)",
    "currency": "string",
    "account_status": "string",
    "decline_reason": "string",
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

REJECT_COLUMN_TYPES = {
    "reject_id": "string",
    "event_id": "string",
    "event_type": "string",
    "rejection_reason": "string",
    "kafka_topic": "string",
    "kafka_partition": "int",
    "kafka_offset": "bigint",
    "raw_payload_sha256": "string",
    "bronze_ingested_at": "timestamp",
    "silver_processed_at": "timestamp",
}


def _field(name: str, data_type: str | dict, *, nullable: bool = True) -> dict:
    return {"name": name, "type": data_type, "nullable": nullable, "metadata": {}}


RAW_PAYLOAD_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        _field("kind", "string"),
        _field("transaction_id", "string"),
        _field("customer_id", "string"),
        _field("account_id", "string"),
        _field("card_id", "string"),
        _field("transaction_type", "string"),
        _field("status", "string"),
        _field("amount", "string"),
        _field("balance_before", "string"),
        _field("balance_after", "string"),
        _field("currency", "string"),
        _field("account_status", "string"),
        _field("decline_reason", "string"),
        _field("atm_id", "string"),
    ],
}

RAW_EVENT_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        _field("event_id", "string"),
        _field("event_type", "string"),
        _field("schema_version", "integer"),
        _field("occurred_at", "string"),
        _field("source", "string"),
        _field("payload", RAW_PAYLOAD_SCHEMA_SPEC),
        _field("_corrupt_record", "string"),
    ],
}


@dataclass(frozen=True)
class SilverConfig:
    catalog: str = DEFAULT_CATALOG
    bronze_namespace: str = DEFAULT_BRONZE_NAMESPACE
    bronze_table: str = DEFAULT_BRONZE_TABLE
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    silver_table: str = DEFAULT_SILVER_TABLE
    reject_table: str = DEFAULT_REJECT_TABLE
    metastore_uri: str = DEFAULT_METASTORE_URI
    warehouse: str = DEFAULT_WAREHOUSE
    namespace_location: str = DEFAULT_NAMESPACE_LOCATION
    create_only: bool = False
    app_name: str = DEFAULT_APP_NAME
    log_level: str = "WARN"

    def __post_init__(self) -> None:
        for name in (
            "catalog",
            "bronze_namespace",
            "bronze_table",
            "silver_namespace",
            "silver_table",
            "reject_table",
        ):
            if not SQL_IDENTIFIER.fullmatch(getattr(self, name)):
                raise ValueError(f"{name} must be a safe SQL identifier.")
        for name in ("metastore_uri", "warehouse", "namespace_location", "app_name"):
            value = getattr(self, name)
            if not value.strip() or "'" in value:
                raise ValueError(f"{name} must be non-blank and must not contain a quote.")
        if not self.metastore_uri.startswith("thrift://"):
            raise ValueError("metastore_uri must use thrift://.")
        for name in ("warehouse", "namespace_location"):
            if not getattr(self, name).startswith("hdfs://"):
                raise ValueError(f"{name} must use shared HDFS storage.")
        if self.bronze_identifier in {self.silver_identifier, self.reject_identifier}:
            raise ValueError("Bronze source and Silver targets must differ.")
        if self.silver_identifier == self.reject_identifier:
            raise ValueError("Silver and reject tables must differ.")

    @property
    def bronze_identifier(self) -> str:
        return f"{self.catalog}.{self.bronze_namespace}.{self.bronze_table}"

    @property
    def silver_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.silver_table}"

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
        "--silver-table", default=os.getenv("BANKFLOW_SILVER_TABLE", DEFAULT_SILVER_TABLE)
    )
    parser.add_argument(
        "--reject-table", default=os.getenv("BANKFLOW_SILVER_REJECT_TABLE", DEFAULT_REJECT_TABLE)
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


def config_from_args(argv: list[str] | None = None) -> SilverConfig:
    args = build_parser().parse_args(argv)
    return SilverConfig(
        catalog=args.catalog,
        bronze_namespace=args.bronze_namespace,
        bronze_table=args.bronze_table,
        silver_namespace=args.silver_namespace,
        silver_table=args.silver_table,
        reject_table=args.reject_table,
        metastore_uri=args.metastore_uri,
        warehouse=args.warehouse,
        namespace_location=args.namespace_location,
        create_only=args.create_only,
        app_name=args.app_name,
        log_level=args.log_level,
    )


def namespace_sql(config: SilverConfig) -> str:
    return (
        f"CREATE NAMESPACE IF NOT EXISTS {config.catalog}.{config.silver_namespace} "
        f"LOCATION '{config.namespace_location}'"
    )


def silver_table_sql(config: SilverConfig) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {config.silver_identifier} (
    event_id STRING NOT NULL,
    transaction_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    account_id STRING NOT NULL,
    card_id STRING,
    event_type STRING NOT NULL,
    transaction_type STRING NOT NULL,
    transaction_status STRING NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    balance_before DECIMAL(18,2) NOT NULL,
    balance_after DECIMAL(18,2) NOT NULL,
    currency STRING NOT NULL,
    account_status STRING NOT NULL,
    decline_reason STRING,
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


def reject_table_sql(config: SilverConfig) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {config.reject_identifier} (
    reject_id STRING NOT NULL,
    event_id STRING,
    event_type STRING,
    rejection_reason STRING NOT NULL,
    kafka_topic STRING NOT NULL,
    kafka_partition INT NOT NULL,
    kafka_offset BIGINT NOT NULL,
    raw_payload_sha256 STRING NOT NULL,
    bronze_ingested_at TIMESTAMP NOT NULL,
    silver_processed_at TIMESTAMP NOT NULL
)
USING iceberg
PARTITIONED BY (days(bronze_ingested_at))
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def merge_sql(config: SilverConfig, view_name: str) -> str:
    if not SQL_IDENTIFIER.fullmatch(view_name):
        raise ValueError("view_name must be a safe SQL identifier.")
    columns = ", ".join(SILVER_COLUMN_TYPES)
    values = ", ".join(f"source.{column}" for column in SILVER_COLUMN_TYPES)
    return f"""
MERGE INTO {config.silver_identifier} AS target
USING {view_name} AS source
ON target.event_id = source.event_id
WHEN NOT MATCHED THEN INSERT ({columns}) VALUES ({values})
""".strip()


def merge_reject_sql(config: SilverConfig, view_name: str) -> str:
    if not SQL_IDENTIFIER.fullmatch(view_name):
        raise ValueError("view_name must be a safe SQL identifier.")
    columns = ", ".join(REJECT_COLUMN_TYPES)
    values = ", ".join(f"source.{column}" for column in REJECT_COLUMN_TYPES)
    return f"""
MERGE INTO {config.reject_identifier} AS target
USING {view_name} AS source
ON target.reject_id = source.reject_id
WHEN NOT MATCHED THEN INSERT ({columns}) VALUES ({values})
""".strip()


def build_spark_session(config: SilverConfig):
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(config.app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            f"spark.sql.catalog.{config.catalog}",
            "org.apache.iceberg.spark.SparkCatalog",
        )
        .config(f"spark.sql.catalog.{config.catalog}.type", "hive")
        .config(f"spark.sql.catalog.{config.catalog}.uri", config.metastore_uri)
        .config(f"spark.sql.catalog.{config.catalog}.warehouse", config.warehouse)
        .config(
            f"spark.sql.catalog.{config.catalog}.io-impl",
            "org.apache.iceberg.hadoop.HadoopFileIO",
        )
        .getOrCreate()
    )
    try:
        (
            spark._jvm.Thread.currentThread()  # noqa: SLF001
            .getContextClassLoader()
            .loadClass("org.apache.iceberg.spark.SparkCatalog")
        )
    except Exception as exc:
        spark.stop()
        raise RuntimeError("The installed Iceberg Spark runtime is required.") from exc
    spark.sparkContext.setLogLevel(config.log_level)
    return spark


def build_raw_event_schema():
    from pyspark.sql.types import StructType

    return StructType.fromJson(RAW_EVENT_SCHEMA_SPEC)


def transform_bronze_transactions(bronze_df):
    """Return normalized transaction candidates with one deterministic rejection reason."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    event_types = tuple(TRANSACTION_EVENT_SHAPES)
    source = bronze_df.filter(
        (F.col("payload_kind") == "transaction") & F.col("event_type").isin(*event_types)
    )
    parsed = source.withColumn(
        "_raw",
        F.from_json(
            F.col("raw_payload"),
            build_raw_event_schema(),
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    )
    event = F.col("_raw")
    payload = F.col("_raw.payload")

    normalized = (
        parsed.withColumn("_event_id", F.lower(event.event_id))
        .withColumn("_transaction_id", F.lower(payload.transaction_id))
        .withColumn("_customer_id", F.lower(payload.customer_id))
        .withColumn("_account_id", F.lower(payload.account_id))
        .withColumn("_card_id", F.lower(payload.card_id))
        .withColumn("_event_type", F.lower(F.trim(event.event_type)))
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
        .withColumn("_account_status", F.lower(F.trim(payload.account_status)))
        .withColumn("_decline_reason", F.trim(payload.decline_reason))
        .withColumn("_atm_id", F.upper(F.trim(payload.atm_id)))
        .withColumn("_occurred_at", F.to_utc_timestamp(F.to_timestamp(event.occurred_at), "UTC"))
        .withColumn("_source", F.trim(event.source))
        .withColumn("_schema_version", event.schema_version.cast("int"))
    )

    required_present = (
        F.col("_event_id").isNotNull()
        & F.col("_transaction_id").isNotNull()
        & F.col("_customer_id").isNotNull()
        & F.col("_account_id").isNotNull()
        & F.col("_event_type").isNotNull()
        & F.col("_transaction_type").isNotNull()
        & F.col("_transaction_status").isNotNull()
        & F.col("_amount_text").isNotNull()
        & F.col("_balance_before_text").isNotNull()
        & F.col("_balance_after_text").isNotNull()
        & F.col("_currency").isNotNull()
        & F.col("_account_status").isNotNull()
        & F.col("_occurred_at").isNotNull()
    )
    identifiers_valid = (
        F.col("_event_id").rlike(UUID_PATTERN)
        & F.col("_transaction_id").rlike(UUID_PATTERN)
        & F.col("_customer_id").rlike(UUID_PATTERN)
        & F.col("_account_id").rlike(UUID_PATTERN)
        & (F.col("_card_id").isNull() | F.col("_card_id").rlike(UUID_PATTERN))
    )
    money_text_valid = (
        F.col("_amount_text").rlike(MONEY_PATTERN)
        & F.col("_balance_before_text").rlike(MONEY_PATTERN)
        & F.col("_balance_after_text").rlike(MONEY_PATTERN)
        & F.col("_amount").isNotNull()
        & F.col("_balance_before").isNotNull()
        & F.col("_balance_after").isNotNull()
    )
    event_shape_valid = (
        F.when(
            F.col("_event_type") == "balance.viewed",
            (F.col("_transaction_type") == "balance_inquiry")
            & (F.col("_transaction_status") == "completed"),
        )
        .when(
            F.col("_event_type") == "withdrawal.requested",
            (F.col("_transaction_type") == "withdrawal")
            & (F.col("_transaction_status") == "pending"),
        )
        .when(
            F.col("_event_type") == "withdrawal.completed",
            (F.col("_transaction_type") == "withdrawal")
            & (F.col("_transaction_status") == "completed"),
        )
        .when(
            F.col("_event_type") == "withdrawal.declined",
            (F.col("_transaction_type") == "withdrawal")
            & (F.col("_transaction_status") == "declined"),
        )
        .when(
            F.col("_event_type") == "deposit.completed",
            (F.col("_transaction_type") == "deposit")
            & (F.col("_transaction_status") == "completed"),
        )
        .otherwise(F.lit(False))
    )
    financial_shape_valid = (
        F.when(
            F.col("_event_type") == "balance.viewed",
            (F.col("_amount") == 0)
            & (F.col("_balance_before") == F.col("_balance_after"))
            & F.col("_decline_reason").isNull(),
        )
        .when(
            F.col("_event_type") == "withdrawal.requested",
            (F.col("_amount") > 0)
            & (F.col("_balance_before") == F.col("_balance_after"))
            & F.col("_decline_reason").isNull(),
        )
        .when(
            F.col("_event_type") == "withdrawal.completed",
            (F.col("_amount") > 0)
            & ((F.col("_balance_before") - F.col("_balance_after")) == F.col("_amount"))
            & F.col("_decline_reason").isNull(),
        )
        .when(
            F.col("_event_type") == "withdrawal.declined",
            (F.col("_amount") > 0)
            & (F.col("_balance_before") == F.col("_balance_after"))
            & F.col("_decline_reason").isNotNull()
            & F.length(F.col("_decline_reason")).between(1, 64),
        )
        .when(
            F.col("_event_type") == "deposit.completed",
            (F.col("_amount") > 0)
            & ((F.col("_balance_after") - F.col("_balance_before")) == F.col("_amount"))
            & F.col("_decline_reason").isNull(),
        )
        .otherwise(F.lit(False))
    )
    metadata_matches = (
        (F.col("_event_id") == F.lower(F.col("event_id")))
        & (F.col("_event_type") == F.col("event_type"))
        & (F.col("_schema_version") == F.col("schema_version"))
        & (F.col("_source") == F.col("source"))
        & (payload.kind == F.col("payload_kind"))
        & (F.col("_occurred_at") == F.col("occurred_at"))
    )
    domain_values_valid = (
        F.col("_currency").rlike(r"^[A-Z]{3}$")
        & F.col("_account_status").isin("active", "closed", "frozen")
        & (payload.atm_id.isNull() | payload.atm_id.rlike(ATM_PATTERN))
        & (F.col("_schema_version") == 1)
        & (F.col("_source") == "bankflow.application")
    )

    base_error = (
        F.when(event.isNull() | event["_corrupt_record"].isNotNull(), "malformed_raw_payload")
        .when(~F.coalesce(required_present, F.lit(False)), "missing_required_field")
        .when(~F.coalesce(metadata_matches, F.lit(False)), "bronze_metadata_mismatch")
        .when(~F.coalesce(identifiers_valid, F.lit(False)), "invalid_identifier")
        .when(~F.coalesce(event_shape_valid, F.lit(False)), "invalid_event_shape")
        .when(~F.coalesce(money_text_valid, F.lit(False)), "invalid_numeric_value")
        .when(~F.coalesce(domain_values_valid, F.lit(False)), "invalid_domain_value")
        .when(~F.coalesce(financial_shape_valid, F.lit(False)), "invalid_financial_balance")
    )
    ranked = normalized.withColumn("_base_validation_error", base_error).withColumn(
        "_event_rank",
        F.row_number().over(
            Window.partitionBy("_event_id").orderBy(
                F.when(F.col("_base_validation_error").isNull(), 0).otherwise(1),
                F.col("kafka_timestamp"),
                F.col("kafka_topic"),
                F.col("kafka_partition"),
                F.col("kafka_offset"),
            )
        ),
    )
    validation_error = F.coalesce(
        F.col("_base_validation_error"),
        F.when(F.col("_event_rank") > 1, "duplicate_event_id"),
    )

    return ranked.select(
        F.col("_event_id").alias("event_id"),
        F.col("_transaction_id").alias("transaction_id"),
        F.col("_customer_id").alias("customer_id"),
        F.col("_account_id").alias("account_id"),
        F.col("_card_id").alias("card_id"),
        F.col("_event_type").alias("event_type"),
        F.col("_transaction_type").alias("transaction_type"),
        F.col("_transaction_status").alias("transaction_status"),
        F.col("_amount").alias("amount"),
        F.col("_balance_before").alias("balance_before"),
        F.col("_balance_after").alias("balance_after"),
        F.col("_currency").alias("currency"),
        F.col("_account_status").alias("account_status"),
        F.col("_decline_reason").alias("decline_reason"),
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


def _validate_table_schema(spark, identifier: str, expected: dict[str, str]) -> None:
    actual = {field.name: field.dataType.simpleString() for field in spark.table(identifier).schema}
    if actual != expected:
        raise RuntimeError(f"Existing table {identifier} does not match Day 18 schema: {actual!r}.")


def ensure_silver_tables(spark, config: SilverConfig) -> None:
    if not spark.catalog.tableExists(config.bronze_identifier):
        raise RuntimeError(f"Bronze source table does not exist: {config.bronze_identifier}.")
    spark.sql(namespace_sql(config))
    spark.sql(silver_table_sql(config))
    spark.sql(reject_table_sql(config))
    _validate_table_schema(spark, config.silver_identifier, SILVER_COLUMN_TYPES)
    _validate_table_schema(spark, config.reject_identifier, REJECT_COLUMN_TYPES)


def run_pipeline(config: SilverConfig) -> int:
    from pyspark import StorageLevel
    from pyspark.sql import functions as F

    spark = build_spark_session(config)
    transformed = None
    valid_view = "_bankflow_silver_transactions"
    reject_view = "_bankflow_silver_transaction_rejects"
    try:
        ensure_silver_tables(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_silver_tables_ready",
                        "source": config.bronze_identifier,
                        "table": config.silver_identifier,
                        "reject_table": config.reject_identifier,
                        "location": config.namespace_location,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0

        transformed = transform_bronze_transactions(spark.table(config.bronze_identifier)).persist(
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
        rows_before = spark.table(config.silver_identifier).count()

        if valid_rows:
            valid = transformed.filter(F.col("validation_error").isNull()).select(
                *SILVER_COLUMN_TYPES
            )
            valid.createOrReplaceTempView(valid_view)
            spark.sql(merge_sql(config, valid_view))
        if rejected_rows:
            rejects = transformed.filter(F.col("validation_error").isNotNull()).select(
                F.sha2(
                    F.concat_ws(
                        ":",
                        "kafka_topic",
                        F.col("kafka_partition").cast("string"),
                        F.col("kafka_offset").cast("string"),
                    ),
                    256,
                ).alias("reject_id"),
                "event_id",
                "event_type",
                F.col("validation_error").alias("rejection_reason"),
                "kafka_topic",
                "kafka_partition",
                "kafka_offset",
                "raw_payload_sha256",
                "bronze_ingested_at",
                "silver_processed_at",
            )
            rejects.createOrReplaceTempView(reject_view)
            spark.sql(merge_reject_sql(config, reject_view))

        rows_after = spark.table(config.silver_identifier).count()
        print(
            json.dumps(
                {
                    "event": "bankflow_silver_transaction_quality",
                    "source": config.bronze_identifier,
                    "table": config.silver_identifier,
                    "source_transaction_rows": source_rows,
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
                    "event": "bankflow_silver_transactions_failed",
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
