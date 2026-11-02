"""Shared Iceberg catalog and quality helpers for BankFlow Silver jobs."""

from __future__ import annotations

import re

DEFAULT_CATALOG = "bankflow"
DEFAULT_BRONZE_NAMESPACE = "bronze"
DEFAULT_BRONZE_TABLE = "bronze_bankflow_events"
DEFAULT_SILVER_NAMESPACE = "silver"
DEFAULT_METASTORE_URI = "thrift://localhost:9083"
DEFAULT_WAREHOUSE = "hdfs://localhost:9000/bankflow/lakehouse"
DEFAULT_NAMESPACE_LOCATION = "hdfs://localhost:9000/bankflow/silver"
SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
UUID_PATTERN = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ATM_PATTERN = r"^ATM-[A-Z0-9]{4,12}$"
MONEY_PATTERN = r"^(0|[1-9][0-9]{0,15})(\.[0-9]{1,2})?$"

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


def field_spec(name: str, data_type: str | dict, *, nullable: bool = True) -> dict:
    return {"name": name, "type": data_type, "nullable": nullable, "metadata": {}}


def validate_identifiers(config, *names: str) -> None:
    for name in names:
        if not SQL_IDENTIFIER.fullmatch(getattr(config, name)):
            raise ValueError(f"{name} must be a safe SQL identifier.")


def validate_runtime_settings(config) -> None:
    for name in ("metastore_uri", "warehouse", "namespace_location", "app_name"):
        value = getattr(config, name)
        if not value.strip() or "'" in value:
            raise ValueError(f"{name} must be non-blank and must not contain a quote.")
    if not config.metastore_uri.startswith("thrift://"):
        raise ValueError("metastore_uri must use thrift://.")
    for name in ("warehouse", "namespace_location"):
        if not getattr(config, name).startswith("hdfs://"):
            raise ValueError(f"{name} must use shared HDFS storage.")


def namespace_sql(config) -> str:
    return (
        f"CREATE NAMESPACE IF NOT EXISTS {config.catalog}.{config.silver_namespace} "
        f"LOCATION '{config.namespace_location}'"
    )


def reject_table_sql(config) -> str:
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


def merge_insert_sql(identifier: str, columns: dict[str, str], view_name: str, key: str) -> str:
    for value, label in ((view_name, "view_name"), (key, "key")):
        if not SQL_IDENTIFIER.fullmatch(value):
            raise ValueError(f"{label} must be a safe SQL identifier.")
    column_names = ", ".join(columns)
    values = ", ".join(f"source.{column}" for column in columns)
    return f"""
MERGE INTO {identifier} AS target
USING {view_name} AS source
ON target.{key} = source.{key}
WHEN NOT MATCHED THEN INSERT ({column_names}) VALUES ({values})
""".strip()


def build_spark_session(config):
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


def validate_table_schema(spark, identifier: str, expected: dict[str, str], day: int) -> None:
    actual = {field.name: field.dataType.simpleString() for field in spark.table(identifier).schema}
    if actual != expected:
        raise RuntimeError(
            f"Existing table {identifier} does not match Day {day} schema: {actual!r}."
        )


def select_rejects(transformed, functions):
    return (
        transformed.filter(functions.col("validation_error").isNotNull())
        .select(
            functions.sha2(
                functions.concat_ws(
                    ":",
                    "kafka_topic",
                    functions.col("kafka_partition").cast("string"),
                    functions.col("kafka_offset").cast("string"),
                ),
                256,
            ).alias("reject_id"),
            "event_id",
            "source_event_type",
            functions.col("validation_error").alias("rejection_reason"),
            "kafka_topic",
            "kafka_partition",
            "kafka_offset",
            "raw_payload_sha256",
            "bronze_ingested_at",
            "silver_processed_at",
        )
        .withColumnRenamed("source_event_type", "event_type")
    )
