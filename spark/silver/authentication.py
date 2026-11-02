"""Transform BankFlow Bronze authentication events into validated Silver records."""

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

DEFAULT_APP_NAME = "bankflow-silver-authentication"
DEFAULT_AUTH_TABLE = "silver_authentication_events"
DEFAULT_REJECT_TABLE = "silver_authentication_event_rejects"

AUTHENTICATION_EVENT_TYPES = {
    "authentication.succeeded": ("authentication_success", "success"),
    "authentication.failed": ("authentication_failure", "failure"),
    "card.locked": ("card_lockout", "lockout"),
    "session.ended": ("session_end", "session"),
}

AUTHENTICATION_COLUMN_TYPES = {
    "event_id": "string",
    "event_type": "string",
    "source_event_type": "string",
    "event_class": "string",
    "outcome": "string",
    "is_success": "boolean",
    "is_failure": "boolean",
    "is_lockout": "boolean",
    "is_session_end": "boolean",
    "lockout_classification": "string",
    "subject_known": "boolean",
    "customer_id": "string",
    "account_id": "string",
    "card_id": "string",
    "remaining_attempts": "int",
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

AUTH_PAYLOAD_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        field_spec("kind", "string"),
        field_spec("customer_id", "string"),
        field_spec("account_id", "string"),
        field_spec("card_id", "string"),
        field_spec("outcome", "string"),
        field_spec("remaining_attempts", "integer"),
        field_spec("atm_id", "string"),
    ],
}

AUTH_EVENT_SCHEMA_SPEC = {
    "type": "struct",
    "fields": [
        field_spec("event_id", "string"),
        field_spec("event_type", "string"),
        field_spec("schema_version", "integer"),
        field_spec("occurred_at", "string"),
        field_spec("source", "string"),
        field_spec("payload", AUTH_PAYLOAD_SCHEMA_SPEC),
        field_spec("_corrupt_record", "string"),
    ],
}


@dataclass(frozen=True)
class AuthenticationConfig:
    catalog: str = DEFAULT_CATALOG
    bronze_namespace: str = DEFAULT_BRONZE_NAMESPACE
    bronze_table: str = DEFAULT_BRONZE_TABLE
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE
    auth_table: str = DEFAULT_AUTH_TABLE
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
            "auth_table",
            "reject_table",
        )
        validate_runtime_settings(self)
        if self.bronze_identifier in {self.auth_identifier, self.reject_identifier}:
            raise ValueError("Bronze source and Silver targets must differ.")
        if self.auth_identifier == self.reject_identifier:
            raise ValueError("Authentication and reject tables must differ.")

    @property
    def bronze_identifier(self) -> str:
        return f"{self.catalog}.{self.bronze_namespace}.{self.bronze_table}"

    @property
    def auth_identifier(self) -> str:
        return f"{self.catalog}.{self.silver_namespace}.{self.auth_table}"

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
        "--auth-table", default=os.getenv("BANKFLOW_SILVER_AUTH_TABLE", DEFAULT_AUTH_TABLE)
    )
    parser.add_argument(
        "--reject-table", default=os.getenv("BANKFLOW_SILVER_AUTH_REJECT", DEFAULT_REJECT_TABLE)
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


def config_from_args(argv: list[str] | None = None) -> AuthenticationConfig:
    args = build_parser().parse_args(argv)
    return AuthenticationConfig(
        catalog=args.catalog,
        bronze_namespace=args.bronze_namespace,
        bronze_table=args.bronze_table,
        silver_namespace=args.silver_namespace,
        auth_table=args.auth_table,
        reject_table=args.reject_table,
        metastore_uri=args.metastore_uri,
        warehouse=args.warehouse,
        namespace_location=args.namespace_location,
        create_only=args.create_only,
        app_name=args.app_name,
        log_level=args.log_level,
    )


def authentication_table_sql(config: AuthenticationConfig) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {config.auth_identifier} (
    event_id STRING NOT NULL,
    event_type STRING NOT NULL,
    source_event_type STRING NOT NULL,
    event_class STRING NOT NULL,
    outcome STRING NOT NULL,
    is_success BOOLEAN NOT NULL,
    is_failure BOOLEAN NOT NULL,
    is_lockout BOOLEAN NOT NULL,
    is_session_end BOOLEAN NOT NULL,
    lockout_classification STRING,
    subject_known BOOLEAN NOT NULL,
    customer_id STRING,
    account_id STRING,
    card_id STRING,
    remaining_attempts INT,
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


def merge_sql(config: AuthenticationConfig, view_name: str) -> str:
    return merge_insert_sql(
        config.auth_identifier, AUTHENTICATION_COLUMN_TYPES, view_name, "event_id"
    )


def merge_reject_sql(config: AuthenticationConfig, view_name: str) -> str:
    return merge_insert_sql(config.reject_identifier, REJECT_COLUMN_TYPES, view_name, "reject_id")


def build_auth_event_schema():
    from pyspark.sql.types import StructType

    return StructType.fromJson(AUTH_EVENT_SCHEMA_SPEC)


def transform_bronze_authentication(bronze_df):
    """Normalize authentication events and classify invalid or duplicate rows."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    source = bronze_df.filter(
        (F.col("payload_kind") == "authentication")
        & F.col("event_type").isin(*AUTHENTICATION_EVENT_TYPES)
    )
    parsed = source.withColumn(
        "_raw",
        F.from_json(
            F.col("raw_payload"),
            build_auth_event_schema(),
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    )
    event = F.col("_raw")
    payload = F.col("_raw.payload")
    normalized_type = (
        F.when(event.event_type == "authentication.succeeded", "authentication_success")
        .when(event.event_type == "authentication.failed", "authentication_failure")
        .when(event.event_type == "card.locked", "card_lockout")
        .when(event.event_type == "session.ended", "session_end")
    )
    event_class = (
        F.when(event.event_type == "authentication.succeeded", "success")
        .when(event.event_type == "authentication.failed", "failure")
        .when(event.event_type == "card.locked", "lockout")
        .when(event.event_type == "session.ended", "session")
    )

    normalized = (
        parsed.withColumn("_event_id", F.lower(event.event_id))
        .withColumn("_source_event_type", F.lower(F.trim(event.event_type)))
        .withColumn("_event_type", normalized_type)
        .withColumn("_event_class", event_class)
        .withColumn("_outcome", F.lower(F.trim(payload.outcome)))
        .withColumn("_customer_id", F.lower(payload.customer_id))
        .withColumn("_account_id", F.lower(payload.account_id))
        .withColumn("_card_id", F.lower(payload.card_id))
        .withColumn("_remaining_attempts", payload.remaining_attempts.cast("int"))
        .withColumn("_atm_id", F.upper(F.trim(payload.atm_id)))
        .withColumn("_occurred_at", F.to_utc_timestamp(F.to_timestamp(event.occurred_at), "UTC"))
        .withColumn("_source", F.trim(event.source))
        .withColumn("_schema_version", event.schema_version.cast("int"))
    )
    subject_count = sum(
        F.when(F.col(column).isNotNull(), 1).otherwise(0)
        for column in ("_customer_id", "_account_id", "_card_id")
    )
    all_subjects = subject_count == 3
    no_subjects = subject_count == 0
    identifiers_valid = F.col("_event_id").rlike(UUID_PATTERN) & (
        no_subjects
        | (
            all_subjects
            & F.col("_customer_id").rlike(UUID_PATTERN)
            & F.col("_account_id").rlike(UUID_PATTERN)
            & F.col("_card_id").rlike(UUID_PATTERN)
        )
    )
    shape_valid = (
        F.when(
            F.col("_source_event_type") == "authentication.succeeded",
            (F.col("_outcome") == "authenticated")
            & all_subjects
            & F.col("_remaining_attempts").isNull(),
        )
        .when(
            (F.col("_source_event_type") == "authentication.failed")
            & (F.col("_outcome") == "invalid_credentials"),
            all_subjects & F.col("_remaining_attempts").between(1, 10),
        )
        .when(
            (F.col("_source_event_type") == "authentication.failed")
            & (F.col("_outcome") == "card_unavailable"),
            no_subjects & F.col("_remaining_attempts").isNull(),
        )
        .when(
            F.col("_source_event_type") == "card.locked",
            (F.col("_outcome") == "card_locked")
            & all_subjects
            & (F.col("_remaining_attempts") == 0),
        )
        .when(
            F.col("_source_event_type") == "session.ended",
            (F.col("_outcome") == "session_ended")
            & all_subjects
            & F.col("_remaining_attempts").isNull(),
        )
        .otherwise(F.lit(False))
    )
    required_present = (
        F.col("_event_id").isNotNull()
        & F.col("_source_event_type").isNotNull()
        & F.col("_event_type").isNotNull()
        & F.col("_event_class").isNotNull()
        & F.col("_outcome").isNotNull()
        & F.col("_occurred_at").isNotNull()
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
        & (payload.atm_id.isNull() | payload.atm_id.rlike(ATM_PATTERN))
        & (F.col("_remaining_attempts").isNull() | F.col("_remaining_attempts").between(0, 10))
    )
    base_error = (
        F.when(event.isNull() | event["_corrupt_record"].isNotNull(), "malformed_raw_payload")
        .when(~F.coalesce(required_present, F.lit(False)), "missing_required_field")
        .when(~F.coalesce(metadata_matches, F.lit(False)), "bronze_metadata_mismatch")
        .when(~F.coalesce(identifiers_valid, F.lit(False)), "invalid_subject_identifier")
        .when(~F.coalesce(domain_valid, F.lit(False)), "invalid_domain_value")
        .when(~F.coalesce(shape_valid, F.lit(False)), "invalid_authentication_shape")
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
        F.col("_outcome").alias("outcome"),
        (F.col("_event_class") == "success").alias("is_success"),
        (F.col("_event_class") == "failure").alias("is_failure"),
        (F.col("_event_class") == "lockout").alias("is_lockout"),
        (F.col("_event_class") == "session").alias("is_session_end"),
        F.when(F.col("_event_class") == "lockout", "pin_attempt_limit").alias(
            "lockout_classification"
        ),
        all_subjects.alias("subject_known"),
        F.col("_customer_id").alias("customer_id"),
        F.col("_account_id").alias("account_id"),
        F.col("_card_id").alias("card_id"),
        F.col("_remaining_attempts").alias("remaining_attempts"),
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


def ensure_tables(spark, config: AuthenticationConfig) -> None:
    if not spark.catalog.tableExists(config.bronze_identifier):
        raise RuntimeError(f"Bronze source table does not exist: {config.bronze_identifier}.")
    spark.sql(namespace_sql(config))
    spark.sql(authentication_table_sql(config))
    spark.sql(reject_table_sql(config))
    validate_table_schema(spark, config.auth_identifier, AUTHENTICATION_COLUMN_TYPES, 19)
    validate_table_schema(spark, config.reject_identifier, REJECT_COLUMN_TYPES, 19)


def run_pipeline(config: AuthenticationConfig) -> int:
    from pyspark import StorageLevel
    from pyspark.sql import functions as F

    spark = build_spark_session(config)
    transformed = None
    valid_view = "_bankflow_silver_authentication"
    reject_view = "_bankflow_silver_authentication_rejects"
    try:
        ensure_tables(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_silver_authentication_tables_ready",
                        "source": config.bronze_identifier,
                        "table": config.auth_identifier,
                        "reject_table": config.reject_identifier,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        transformed = transform_bronze_authentication(
            spark.table(config.bronze_identifier)
        ).persist(StorageLevel.MEMORY_AND_DISK)
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
        rows_before = spark.table(config.auth_identifier).count()
        if valid_rows:
            valid = transformed.filter(F.col("validation_error").isNull()).select(
                *AUTHENTICATION_COLUMN_TYPES
            )
            valid.createOrReplaceTempView(valid_view)
            spark.sql(merge_sql(config, valid_view))
        if rejected_rows:
            rejects = select_rejects(transformed, F)
            rejects.createOrReplaceTempView(reject_view)
            spark.sql(merge_reject_sql(config, reject_view))
        rows_after = spark.table(config.auth_identifier).count()
        lockout_rows = transformed.filter(
            F.col("validation_error").isNull() & F.col("is_lockout")
        ).count()
        print(
            json.dumps(
                {
                    "event": "bankflow_silver_authentication_quality",
                    "source_rows": source_rows,
                    "valid_rows": valid_rows,
                    "rejected_rows": rejected_rows,
                    "duplicates_removed": reason_counts.get("duplicate_event_id", 0),
                    "lockout_rows": lockout_rows,
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
                    "event": "bankflow_silver_authentication_failed",
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
