"""Persist validated BankFlow Kafka events into the Iceberg Bronze layer."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from streaming.bankflow_stream import (  # noqa: E402
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_KAFKA_PACKAGE,
    DEFAULT_TOPIC,
    StreamConfig,
    connector_spark_version,
    parse_kafka_events,
    read_kafka_stream,
)

DEFAULT_APP_NAME = "bankflow-iceberg-bronze"
DEFAULT_CATALOG = "bankflow"
DEFAULT_NAMESPACE = "bronze"
DEFAULT_TABLE = "bronze_bankflow_events"
DEFAULT_METASTORE_URI = "thrift://localhost:9083"
DEFAULT_WAREHOUSE = "hdfs://localhost:9000/bankflow/lakehouse"
DEFAULT_NAMESPACE_LOCATION = "hdfs://localhost:9000/bankflow/bronze"
DEFAULT_CHECKPOINT = "hdfs://localhost:9000/bankflow/checkpoints/day17-bronze"
DEFAULT_INVALID_PATH = "hdfs://localhost:9000/bankflow/quarantine/day17-bronze"
SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

BRONZE_COLUMN_TYPES = {
    "event_id": "string",
    "event_type": "string",
    "schema_version": "int",
    "occurred_at": "timestamp",
    "source": "string",
    "payload_kind": "string",
    "raw_payload": "string",
    "raw_payload_sha256": "string",
    "kafka_topic": "string",
    "kafka_partition": "int",
    "kafka_offset": "bigint",
    "kafka_key": "string",
    "kafka_timestamp": "timestamp",
    "ingested_at": "timestamp",
}


@dataclass(frozen=True)
class BronzeConfig:
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS
    topic: str = DEFAULT_TOPIC
    catalog: str = DEFAULT_CATALOG
    namespace: str = DEFAULT_NAMESPACE
    table: str = DEFAULT_TABLE
    metastore_uri: str = DEFAULT_METASTORE_URI
    warehouse: str = DEFAULT_WAREHOUSE
    namespace_location: str = DEFAULT_NAMESPACE_LOCATION
    checkpoint_location: str = DEFAULT_CHECKPOINT
    invalid_record_path: str = DEFAULT_INVALID_PATH
    starting_offsets: str = "latest"
    max_offsets_per_trigger: int = 10_000
    processing_time: str = "10 seconds"
    available_now: bool = False
    create_only: bool = False
    fail_on_data_loss: bool = True
    app_name: str = DEFAULT_APP_NAME
    query_name: str = "bankflow-bronze-v1"
    kafka_package: str = DEFAULT_KAFKA_PACKAGE
    log_level: str = "WARN"

    def __post_init__(self) -> None:
        for name in ("catalog", "namespace", "table"):
            value = getattr(self, name)
            if not SQL_IDENTIFIER.fullmatch(value):
                raise ValueError(f"{name} must be a safe SQL identifier.")
        text_fields = {
            "bootstrap_servers": self.bootstrap_servers,
            "topic": self.topic,
            "metastore_uri": self.metastore_uri,
            "warehouse": self.warehouse,
            "namespace_location": self.namespace_location,
            "checkpoint_location": self.checkpoint_location,
            "invalid_record_path": self.invalid_record_path,
            "processing_time": self.processing_time,
            "app_name": self.app_name,
            "query_name": self.query_name,
            "kafka_package": self.kafka_package,
        }
        for name, value in text_fields.items():
            if not value.strip():
                raise ValueError(f"{name} must not be blank.")
            if "'" in value:
                raise ValueError(f"{name} must not contain a single quote.")
        for name in (
            "warehouse",
            "namespace_location",
            "checkpoint_location",
            "invalid_record_path",
        ):
            if not getattr(self, name).startswith("hdfs://"):
                raise ValueError(f"{name} must use shared HDFS storage.")
        if not self.metastore_uri.startswith("thrift://"):
            raise ValueError("metastore_uri must use thrift://.")
        if any(character.isspace() for character in self.topic):
            raise ValueError("topic must not contain whitespace.")
        if self.starting_offsets not in {"earliest", "latest"}:
            raise ValueError("starting_offsets must be earliest or latest.")
        if self.max_offsets_per_trigger < 1:
            raise ValueError("max_offsets_per_trigger must be positive.")
        runtime_paths = {
            self.warehouse,
            self.namespace_location,
            self.checkpoint_location,
            self.invalid_record_path,
        }
        if len(runtime_paths) != 4:
            raise ValueError("warehouse, namespace, checkpoint, and quarantine paths must differ.")
        if connector_spark_version(self.kafka_package) is None:
            raise ValueError("kafka_package must end with a Spark version coordinate.")

    @property
    def table_identifier(self) -> str:
        return f"{self.catalog}.{self.namespace}.{self.table}"

    def stream_config(self) -> StreamConfig:
        return StreamConfig(
            bootstrap_servers=self.bootstrap_servers,
            topic=self.topic,
            checkpoint_location=self.checkpoint_location,
            invalid_record_path=self.invalid_record_path,
            starting_offsets=self.starting_offsets,
            max_offsets_per_trigger=self.max_offsets_per_trigger,
            processing_time=self.processing_time,
            available_now=self.available_now,
            fail_on_data_loss=self.fail_on_data_loss,
            app_name=self.app_name,
            query_name=self.query_name,
            kafka_package=self.kafka_package,
            log_level=self.log_level,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bootstrap-servers",
        default=os.getenv("BANKFLOW_SPARK_KAFKA_BOOTSTRAP_SERVERS", DEFAULT_BOOTSTRAP_SERVERS),
    )
    parser.add_argument("--topic", default=os.getenv("KAFKA_TRANSACTION_TOPIC", DEFAULT_TOPIC))
    parser.add_argument("--catalog", default=os.getenv("BANKFLOW_ICEBERG_CATALOG", DEFAULT_CATALOG))
    parser.add_argument(
        "--namespace", default=os.getenv("BANKFLOW_BRONZE_NAMESPACE", DEFAULT_NAMESPACE)
    )
    parser.add_argument("--table", default=os.getenv("BANKFLOW_BRONZE_TABLE", DEFAULT_TABLE))
    parser.add_argument(
        "--metastore-uri",
        default=os.getenv("BANKFLOW_HIVE_METASTORE_URI", DEFAULT_METASTORE_URI),
    )
    parser.add_argument(
        "--warehouse", default=os.getenv("BANKFLOW_ICEBERG_WAREHOUSE", DEFAULT_WAREHOUSE)
    )
    parser.add_argument(
        "--namespace-location",
        default=os.getenv("BANKFLOW_BRONZE_PATH", DEFAULT_NAMESPACE_LOCATION),
    )
    parser.add_argument(
        "--checkpoint-location",
        default=os.getenv("BANKFLOW_BRONZE_CHECKPOINT", DEFAULT_CHECKPOINT),
    )
    parser.add_argument(
        "--invalid-record-path",
        default=os.getenv("BANKFLOW_BRONZE_INVALID_PATH", DEFAULT_INVALID_PATH),
    )
    parser.add_argument("--starting-offsets", choices=("earliest", "latest"), default="latest")
    parser.add_argument("--max-offsets-per-trigger", type=int, default=10_000)
    parser.add_argument("--processing-time", default="10 seconds")
    parser.add_argument("--available-now", action="store_true")
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--allow-data-loss", action="store_true")
    parser.add_argument("--app-name", default=DEFAULT_APP_NAME)
    parser.add_argument("--query-name", default="bankflow-bronze-v1")
    parser.add_argument("--kafka-package", default=DEFAULT_KAFKA_PACKAGE)
    parser.add_argument("--log-level", choices=("ERROR", "WARN", "INFO"), default="WARN")
    return parser


def config_from_args(argv: list[str] | None = None) -> BronzeConfig:
    args = build_parser().parse_args(argv)
    return BronzeConfig(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        catalog=args.catalog,
        namespace=args.namespace,
        table=args.table,
        metastore_uri=args.metastore_uri,
        warehouse=args.warehouse,
        namespace_location=args.namespace_location,
        checkpoint_location=args.checkpoint_location,
        invalid_record_path=args.invalid_record_path,
        starting_offsets=args.starting_offsets,
        max_offsets_per_trigger=args.max_offsets_per_trigger,
        processing_time=args.processing_time,
        available_now=args.available_now,
        create_only=args.create_only,
        fail_on_data_loss=not args.allow_data_loss,
        app_name=args.app_name,
        query_name=args.query_name,
        kafka_package=args.kafka_package,
        log_level=args.log_level,
    )


def namespace_sql(config: BronzeConfig) -> str:
    return (
        f"CREATE NAMESPACE IF NOT EXISTS {config.catalog}.{config.namespace} "
        f"LOCATION '{config.namespace_location}'"
    )


def table_sql(config: BronzeConfig) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {config.table_identifier} (
    event_id STRING NOT NULL,
    event_type STRING NOT NULL,
    schema_version INT NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    source STRING NOT NULL,
    payload_kind STRING NOT NULL,
    raw_payload STRING NOT NULL,
    raw_payload_sha256 STRING NOT NULL,
    kafka_topic STRING NOT NULL,
    kafka_partition INT NOT NULL,
    kafka_offset BIGINT NOT NULL,
    kafka_key STRING,
    kafka_timestamp TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP NOT NULL
)
USING iceberg
PARTITIONED BY (days(ingested_at))
TBLPROPERTIES (
    'format-version' = '2',
    'write.parquet.compression-codec' = 'zstd'
)
""".strip()


def merge_sql(config: BronzeConfig, view_name: str) -> str:
    if not SQL_IDENTIFIER.fullmatch(view_name):
        raise ValueError("view_name must be a safe SQL identifier.")
    columns = ", ".join(BRONZE_COLUMN_TYPES)
    values = ", ".join(f"source.{column}" for column in BRONZE_COLUMN_TYPES)
    return f"""
MERGE INTO {config.table_identifier} AS target
USING {view_name} AS source
ON target.kafka_topic = source.kafka_topic
AND target.kafka_partition = source.kafka_partition
AND target.kafka_offset = source.kafka_offset
WHEN NOT MATCHED THEN INSERT ({columns}) VALUES ({values})
""".strip()


def build_spark_session(config: BronzeConfig):
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(config.app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.streaming.metricsEnabled", "true")
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
    expected_version = connector_spark_version(config.kafka_package)
    if spark.version != expected_version:
        spark.stop()
        raise RuntimeError(
            f"Kafka connector targets Spark {expected_version}, but runtime is {spark.version}."
        )
    loader = spark._jvm.Thread.currentThread().getContextClassLoader()  # noqa: SLF001
    required_classes = (
        "org.apache.spark.sql.kafka010.KafkaSourceProvider",
        "org.apache.iceberg.spark.SparkCatalog",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    try:
        for class_name in required_classes:
            loader.loadClass(class_name)
    except Exception as exc:
        spark.stop()
        raise RuntimeError(
            "Spark requires its Kafka connector and the installed Iceberg runtime. Start with "
            f"--packages {config.kafka_package} inside the bankflow container."
        ) from exc
    spark.sparkContext.setLogLevel(config.log_level)
    return spark


def ensure_bronze_table(spark, config: BronzeConfig) -> None:
    spark.sql(namespace_sql(config))
    spark.sql(table_sql(config))
    actual = {
        field.name: field.dataType.simpleString()
        for field in spark.table(config.table_identifier).schema.fields
    }
    if actual != BRONZE_COLUMN_TYPES:
        raise RuntimeError(
            f"Existing Bronze table schema does not match Day 17 contract: {actual!r}."
        )


@dataclass(frozen=True)
class BronzeBatchWriter:
    config: BronzeConfig

    def __call__(self, batch_df, batch_id: int) -> None:
        from pyspark import StorageLevel
        from pyspark.sql import functions as F

        cached = batch_df.persist(StorageLevel.MEMORY_AND_DISK)
        view_name = f"_bankflow_bronze_batch_{batch_id}"
        try:
            status_counts = {
                row["record_status"]: row["count"]
                for row in cached.groupBy("record_status").count().collect()
            }
            valid_count = status_counts.get("valid", 0)
            invalid_count = status_counts.get("invalid", 0)
            invalid_reason_counts = {
                row["validation_error"]: row["count"]
                for row in cached.filter(F.col("record_status") == "invalid")
                .groupBy("validation_error")
                .count()
                .collect()
            }
            if invalid_count:
                (
                    cached.filter(F.col("record_status") == "invalid")
                    .select(
                        "kafka_topic",
                        "kafka_partition",
                        "kafka_offset",
                        "kafka_timestamp",
                        "validation_error",
                        F.sha2("raw_value", 256).alias("value_sha256"),
                    )
                    .write.mode("append")
                    .json(self.config.invalid_record_path)
                )
            if valid_count:
                bronze_rows = cached.filter(F.col("record_status") == "valid").select(
                    "event_id",
                    "event_type",
                    "schema_version",
                    "occurred_at",
                    "source",
                    F.col("payload.kind").alias("payload_kind"),
                    F.col("raw_value").alias("raw_payload"),
                    F.sha2("raw_value", 256).alias("raw_payload_sha256"),
                    "kafka_topic",
                    "kafka_partition",
                    "kafka_offset",
                    "kafka_key",
                    "kafka_timestamp",
                    F.current_timestamp().alias("ingested_at"),
                )
                bronze_rows.createOrReplaceTempView(view_name)
                batch_df.sparkSession.sql(merge_sql(self.config, view_name))
            print(
                json.dumps(
                    {
                        "event": "bankflow_bronze_batch",
                        "batch_id": batch_id,
                        "input_rows": valid_count + invalid_count,
                        "valid_rows_merged": valid_count,
                        "invalid_rows": invalid_count,
                        "invalid_reasons": dict(sorted(invalid_reason_counts.items())),
                        "table": self.config.table_identifier,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        finally:
            if batch_df.sparkSession.catalog.tableExists(view_name):
                batch_df.sparkSession.catalog.dropTempView(view_name)
            cached.unpersist()


def run_ingestion(config: BronzeConfig) -> int:
    spark = build_spark_session(config)
    query = None
    try:
        ensure_bronze_table(spark, config)
        if config.create_only:
            print(
                json.dumps(
                    {
                        "event": "bankflow_bronze_table_ready",
                        "table": config.table_identifier,
                        "location": config.namespace_location,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        parsed = parse_kafka_events(read_kafka_stream(spark, config.stream_config()))
        writer = (
            parsed.writeStream.queryName(config.query_name)
            .outputMode("append")
            .option("checkpointLocation", config.checkpoint_location)
            .foreachBatch(BronzeBatchWriter(config))
        )
        if config.available_now:
            writer = writer.trigger(availableNow=True)
        else:
            writer = writer.trigger(processingTime=config.processing_time)
        query = writer.start()
        print(
            json.dumps(
                {
                    "event": "bankflow_bronze_started",
                    "query_id": str(query.id),
                    "query_name": config.query_name,
                    "topic": config.topic,
                    "table": config.table_identifier,
                    "checkpoint_location": config.checkpoint_location,
                    "available_now": config.available_now,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        query.awaitTermination()
        return 0
    except KeyboardInterrupt:
        if query is not None and query.isActive:
            query.stop()
        return 130
    finally:
        spark.stop()


def main(argv: list[str] | None = None) -> int:
    try:
        return run_ingestion(config_from_args(argv))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_bronze_failed",
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
