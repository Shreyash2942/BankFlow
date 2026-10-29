"""Consume BankFlow Kafka events with a checkpointed Spark Structured Streaming query."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any

DEFAULT_APP_NAME = "bankflow-streaming-foundation"
DEFAULT_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_TOPIC = "bankflow.transaction.events"
DEFAULT_CHECKPOINT = "hdfs://localhost:9000/bankflow/checkpoints/day16"
DEFAULT_INVALID_PATH = "hdfs://localhost:9000/bankflow/quarantine/day16"
DEFAULT_KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
UUID4_PATTERN = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
ATM_PATTERN = r"^ATM-[A-Z0-9]{4,12}$"

TRANSACTION_EVENT_TYPES = (
    "account.closed",
    "balance.viewed",
    "deposit.completed",
    "withdrawal.completed",
    "withdrawal.declined",
    "withdrawal.requested",
)
AUTHENTICATION_EVENT_TYPES = (
    "authentication.failed",
    "authentication.succeeded",
    "card.locked",
    "session.ended",
)
ALL_EVENT_TYPES = TRANSACTION_EVENT_TYPES + AUTHENTICATION_EVENT_TYPES


def _field(name: str, data_type: str | dict[str, Any], nullable: bool = True) -> dict[str, Any]:
    return {"name": name, "type": data_type, "nullable": nullable, "metadata": {}}


PAYLOAD_SCHEMA_SPEC: dict[str, Any] = {
    "type": "struct",
    "fields": [
        _field("kind", "string"),
        _field("transaction_id", "string"),
        _field("customer_id", "string"),
        _field("account_id", "string"),
        _field("card_id", "string"),
        _field("transaction_type", "string"),
        _field("status", "string"),
        _field("amount", "decimal(18,2)"),
        _field("balance_before", "decimal(18,2)"),
        _field("balance_after", "decimal(18,2)"),
        _field("currency", "string"),
        _field("account_status", "string"),
        _field("decline_reason", "string"),
        _field("outcome", "string"),
        _field("remaining_attempts", "integer"),
        _field("atm_id", "string"),
    ],
}

EVENT_SCHEMA_SPEC: dict[str, Any] = {
    "type": "struct",
    "fields": [
        _field("event_id", "string"),
        _field("event_type", "string"),
        _field("schema_version", "integer"),
        _field("occurred_at", "timestamp"),
        _field("source", "string"),
        _field("payload", PAYLOAD_SCHEMA_SPEC),
        _field("_corrupt_record", "string"),
    ],
}


@dataclass(frozen=True)
class StreamConfig:
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS
    topic: str = DEFAULT_TOPIC
    checkpoint_location: str = DEFAULT_CHECKPOINT
    invalid_record_path: str = DEFAULT_INVALID_PATH
    starting_offsets: str = "latest"
    max_offsets_per_trigger: int = 10_000
    processing_time: str = "10 seconds"
    available_now: bool = False
    fail_on_data_loss: bool = True
    app_name: str = DEFAULT_APP_NAME
    query_name: str = "bankflow-events-v1"
    kafka_package: str = DEFAULT_KAFKA_PACKAGE
    log_level: str = "WARN"

    def __post_init__(self) -> None:
        text_fields = {
            "bootstrap_servers": self.bootstrap_servers,
            "topic": self.topic,
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
        if any(character.isspace() for character in self.topic):
            raise ValueError("topic must not contain whitespace.")
        if self.starting_offsets not in {"earliest", "latest"}:
            raise ValueError("starting_offsets must be earliest or latest.")
        if self.max_offsets_per_trigger < 1:
            raise ValueError("max_offsets_per_trigger must be positive.")
        if self.checkpoint_location == self.invalid_record_path:
            raise ValueError("checkpoint_location and invalid_record_path must differ.")
        if connector_spark_version(self.kafka_package) is None:
            raise ValueError("kafka_package must end with a Spark version coordinate.")


def connector_spark_version(coordinate: str) -> str | None:
    """Return the Spark artifact version from a Maven coordinate."""
    parts = coordinate.rsplit(":", maxsplit=2)
    if len(parts) != 3 or not all(parts):
        return None
    return parts[-1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bootstrap-servers",
        default=os.getenv("BANKFLOW_SPARK_KAFKA_BOOTSTRAP_SERVERS", DEFAULT_BOOTSTRAP_SERVERS),
    )
    parser.add_argument("--topic", default=os.getenv("KAFKA_TRANSACTION_TOPIC", DEFAULT_TOPIC))
    parser.add_argument(
        "--checkpoint-location",
        default=os.getenv("BANKFLOW_SPARK_CHECKPOINT", DEFAULT_CHECKPOINT),
    )
    parser.add_argument(
        "--invalid-record-path",
        default=os.getenv("BANKFLOW_SPARK_INVALID_PATH", DEFAULT_INVALID_PATH),
    )
    parser.add_argument("--starting-offsets", choices=("earliest", "latest"), default="latest")
    parser.add_argument("--max-offsets-per-trigger", type=int, default=10_000)
    parser.add_argument("--processing-time", default="10 seconds")
    parser.add_argument(
        "--available-now",
        action="store_true",
        help="Process all currently available records and stop; useful for validation.",
    )
    parser.add_argument(
        "--allow-data-loss",
        action="store_true",
        help="Continue if Kafka offsets disappeared; disabled by default.",
    )
    parser.add_argument("--app-name", default=DEFAULT_APP_NAME)
    parser.add_argument("--query-name", default="bankflow-events-v1")
    parser.add_argument("--kafka-package", default=DEFAULT_KAFKA_PACKAGE)
    parser.add_argument("--log-level", choices=("ERROR", "WARN", "INFO"), default="WARN")
    return parser


def config_from_args(argv: list[str] | None = None) -> StreamConfig:
    args = build_parser().parse_args(argv)
    return StreamConfig(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        checkpoint_location=args.checkpoint_location,
        invalid_record_path=args.invalid_record_path,
        starting_offsets=args.starting_offsets,
        max_offsets_per_trigger=args.max_offsets_per_trigger,
        processing_time=args.processing_time,
        available_now=args.available_now,
        fail_on_data_loss=not args.allow_data_loss,
        app_name=args.app_name,
        query_name=args.query_name,
        kafka_package=args.kafka_package,
        log_level=args.log_level,
    )


def build_spark_session(config: StreamConfig):
    """Create a UTC Spark session for the connector supplied through spark-submit."""
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(config.app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.streaming.metricsEnabled", "true")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    expected_version = connector_spark_version(config.kafka_package)
    if spark.version != expected_version:
        spark.stop()
        raise RuntimeError(
            f"Kafka connector targets Spark {expected_version}, but runtime is {spark.version}."
        )
    try:
        (
            spark._jvm.Thread.currentThread()  # noqa: SLF001
            .getContextClassLoader()
            .loadClass("org.apache.spark.sql.kafka010.KafkaSourceProvider")
        )
    except Exception as exc:
        spark.stop()
        raise RuntimeError(
            "Spark Kafka connector is unavailable. Start spark-submit with "
            f"--packages {config.kafka_package}."
        ) from exc
    spark.sparkContext.setLogLevel(config.log_level)
    return spark


def read_kafka_stream(spark, config: StreamConfig):
    """Subscribe to one BankFlow topic with bounded batches and explicit loss behavior."""
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", config.bootstrap_servers)
        .option("subscribe", config.topic)
        .option("startingOffsets", config.starting_offsets)
        .option("maxOffsetsPerTrigger", config.max_offsets_per_trigger)
        .option("failOnDataLoss", str(config.fail_on_data_loss).lower())
        .load()
    )


def build_event_schema():
    """Build the explicit Spark schema without inferring from live financial events."""
    from pyspark.sql.types import StructType

    return StructType.fromJson(EVENT_SCHEMA_SPEC)


def parse_kafka_events(kafka_df):
    """Parse and classify Kafka values while retaining transport metadata for replay."""
    from pyspark.sql import functions as F

    decoded = kafka_df.select(
        F.col("topic").alias("kafka_topic"),
        F.col("partition").alias("kafka_partition"),
        F.col("offset").alias("kafka_offset"),
        F.col("timestamp").alias("kafka_timestamp"),
        F.col("key").cast("string").alias("kafka_key"),
        F.col("value").cast("string").alias("raw_value"),
    )
    parsed = decoded.withColumn(
        "_event",
        F.from_json(
            F.col("raw_value"),
            build_event_schema(),
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    )

    event = F.col("_event")
    payload = F.col("_event.payload")
    subject_count = sum(
        F.when(payload[field].isNotNull(), F.lit(1)).otherwise(F.lit(0))
        for field in ("customer_id", "account_id", "card_id")
    )
    subject_ids_valid = (subject_count == 0) | (
        (subject_count == 3)
        & payload.customer_id.rlike(UUID_PATTERN)
        & payload.account_id.rlike(UUID_PATTERN)
        & payload.card_id.rlike(UUID_PATTERN)
    )
    transaction_shape_valid = (
        F.when(
            event.event_type == "balance.viewed",
            (payload.transaction_type == "balance_inquiry")
            & (payload.status == "completed")
            & (payload.amount == F.lit(0))
            & payload.decline_reason.isNull(),
        )
        .when(
            event.event_type == "withdrawal.requested",
            (payload.transaction_type == "withdrawal")
            & (payload.status == "pending")
            & (payload.amount > 0)
            & payload.decline_reason.isNull(),
        )
        .when(
            event.event_type == "withdrawal.completed",
            (payload.transaction_type == "withdrawal")
            & (payload.status == "completed")
            & (payload.amount > 0)
            & payload.decline_reason.isNull(),
        )
        .when(
            event.event_type == "withdrawal.declined",
            (payload.transaction_type == "withdrawal")
            & (payload.status == "declined")
            & (payload.amount > 0)
            & payload.decline_reason.isNotNull(),
        )
        .when(
            event.event_type == "deposit.completed",
            (payload.transaction_type == "deposit")
            & (payload.status == "completed")
            & (payload.amount > 0)
            & payload.decline_reason.isNull(),
        )
        .when(
            event.event_type == "account.closed",
            (payload.transaction_type == "withdrawal")
            & (payload.status == "completed")
            & (payload.amount > 0)
            & (payload.account_status == "closed"),
        )
        .otherwise(F.lit(False))
    )
    authentication_shape_valid = (
        F.when(
            event.event_type == "authentication.succeeded",
            (payload.outcome == "authenticated") & (subject_count == 3),
        )
        .when(
            event.event_type == "authentication.failed",
            payload.outcome.isin("invalid_credentials", "card_unavailable")
            & subject_count.isin(0, 3),
        )
        .when(
            event.event_type == "card.locked",
            (payload.outcome == "card_locked") & (subject_count == 3),
        )
        .when(
            event.event_type == "session.ended",
            (payload.outcome == "session_ended") & (subject_count == 3),
        )
        .otherwise(F.lit(False))
    )
    transaction_required = (
        payload.transaction_id.rlike(UUID_PATTERN)
        & payload.customer_id.rlike(UUID_PATTERN)
        & payload.account_id.rlike(UUID_PATTERN)
        & (payload.card_id.isNull() | payload.card_id.rlike(UUID_PATTERN))
        & payload.amount.isNotNull()
        & payload.balance_before.isNotNull()
        & payload.balance_after.isNotNull()
        & (payload.amount >= 0)
        & (payload.balance_before >= 0)
        & (payload.balance_after >= 0)
        & payload.currency.rlike(r"^[A-Z]{3}$")
        & payload.account_status.isin("active", "closed", "frozen")
    )
    authentication_required = (
        payload.outcome.isNotNull()
        & subject_ids_valid
        & (payload.remaining_attempts.isNull() | payload.remaining_attempts.between(0, 10))
    )
    transaction_payload_valid = F.coalesce(
        transaction_required & transaction_shape_valid, F.lit(False)
    )
    authentication_payload_valid = F.coalesce(
        authentication_required & authentication_shape_valid, F.lit(False)
    )

    validation_error = (
        F.when(event["_corrupt_record"].isNotNull() | event.isNull(), "malformed_json")
        .when(
            event.event_id.isNull()
            | event.event_type.isNull()
            | event.schema_version.isNull()
            | event.occurred_at.isNull()
            | event.source.isNull()
            | event.payload.isNull()
            | payload.kind.isNull(),
            "missing_envelope_field",
        )
        .when(~event.event_id.rlike(UUID4_PATTERN), "invalid_event_id")
        .when(event.schema_version != 1, "unsupported_schema_version")
        .when(event.source != "bankflow.application", "invalid_source")
        .when(~event.event_type.isin(*ALL_EVENT_TYPES), "unknown_event_type")
        .when(payload.atm_id.isNotNull() & ~payload.atm_id.rlike(ATM_PATTERN), "invalid_atm_id")
        .when(
            (payload.kind == "transaction") & ~transaction_payload_valid,
            "invalid_transaction_payload",
        )
        .when(
            (payload.kind == "authentication") & ~authentication_payload_valid,
            "invalid_authentication_payload",
        )
        .when(
            payload.kind.isNull() | ~payload.kind.isin("transaction", "authentication"),
            "invalid_payload_kind",
        )
    )

    return parsed.select(
        "kafka_topic",
        "kafka_partition",
        "kafka_offset",
        "kafka_timestamp",
        "kafka_key",
        "raw_value",
        event.event_id.alias("event_id"),
        event.event_type.alias("event_type"),
        event.schema_version.alias("schema_version"),
        event.occurred_at.alias("occurred_at"),
        event.source.alias("source"),
        event.payload.alias("payload"),
        validation_error.alias("validation_error"),
        F.when(validation_error.isNull(), F.lit("valid"))
        .otherwise(F.lit("invalid"))
        .alias("record_status"),
    )


@dataclass(frozen=True)
class BatchMetricsReporter:
    """Emit bounded batch metrics and quarantine only safe invalid-record metadata."""

    invalid_record_path: str

    def __call__(self, batch_df, batch_id: int) -> None:
        from pyspark import StorageLevel
        from pyspark.sql import functions as F

        cached = batch_df.persist(StorageLevel.MEMORY_AND_DISK)
        try:
            status_counts = {
                row["record_status"]: row["count"]
                for row in cached.groupBy("record_status").count().collect()
            }
            valid_count = status_counts.get("valid", 0)
            invalid_count = status_counts.get("invalid", 0)
            event_type_counts = {
                row["event_type"]: row["count"]
                for row in cached.filter(F.col("record_status") == "valid")
                .groupBy("event_type")
                .count()
                .collect()
            }
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
                    .json(self.invalid_record_path)
                )
            print(
                json.dumps(
                    {
                        "event": "bankflow_stream_batch",
                        "batch_id": batch_id,
                        "input_rows": valid_count + invalid_count,
                        "valid_rows": valid_count,
                        "invalid_rows": invalid_count,
                        "event_types": dict(sorted(event_type_counts.items())),
                        "invalid_reasons": dict(sorted(invalid_reason_counts.items())),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        finally:
            cached.unpersist()


def run_stream(config: StreamConfig) -> int:
    spark = build_spark_session(config)
    query = None
    try:
        parsed = parse_kafka_events(read_kafka_stream(spark, config))
        writer = (
            parsed.writeStream.queryName(config.query_name)
            .outputMode("append")
            .option("checkpointLocation", config.checkpoint_location)
            .foreachBatch(BatchMetricsReporter(config.invalid_record_path))
        )
        if config.available_now:
            writer = writer.trigger(availableNow=True)
        else:
            writer = writer.trigger(processingTime=config.processing_time)
        query = writer.start()
        print(
            json.dumps(
                {
                    "event": "bankflow_stream_started",
                    "query_id": str(query.id),
                    "query_name": config.query_name,
                    "topic": config.topic,
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
        return run_stream(config_from_args(argv))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_stream_failed",
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
