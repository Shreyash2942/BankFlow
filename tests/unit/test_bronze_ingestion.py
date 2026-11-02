"""Service-free contracts for the Day 17 Iceberg Bronze ingestion job."""

import sys

import pytest

from spark.bronze.ingest_events import (
    BRONZE_COLUMN_TYPES,
    DEFAULT_CATALOG,
    DEFAULT_CHECKPOINT,
    DEFAULT_METASTORE_URI,
    DEFAULT_NAMESPACE,
    DEFAULT_NAMESPACE_LOCATION,
    DEFAULT_TABLE,
    DEFAULT_WAREHOUSE,
    BronzeConfig,
    config_from_args,
    merge_sql,
    namespace_sql,
    table_sql,
)


def test_bronze_module_keeps_pyspark_out_of_service_free_imports():
    assert "pyspark" not in sys.modules


def test_default_catalog_metastore_and_hdfs_contract():
    config = BronzeConfig()

    assert DEFAULT_CATALOG == "bankflow"
    assert DEFAULT_NAMESPACE == "bronze"
    assert DEFAULT_TABLE == "bronze_bankflow_events"
    assert DEFAULT_METASTORE_URI == "thrift://localhost:9083"
    assert DEFAULT_WAREHOUSE == "hdfs://localhost:9000/bankflow/lakehouse"
    assert DEFAULT_NAMESPACE_LOCATION == "hdfs://localhost:9000/bankflow/bronze"
    assert DEFAULT_CHECKPOINT == "hdfs://localhost:9000/bankflow/checkpoints/day17-bronze"
    assert config.table_identifier == "bankflow.bronze.bronze_bankflow_events"


def test_bronze_schema_preserves_raw_payload_transport_and_ingestion_metadata():
    assert BRONZE_COLUMN_TYPES == {
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


def test_namespace_and_table_ddl_use_iceberg_v2_and_ingestion_partition():
    config = BronzeConfig()
    namespace = namespace_sql(config)
    table = table_sql(config)

    assert namespace == (
        "CREATE NAMESPACE IF NOT EXISTS bankflow.bronze "
        "LOCATION 'hdfs://localhost:9000/bankflow/bronze'"
    )
    assert "CREATE TABLE IF NOT EXISTS bankflow.bronze.bronze_bankflow_events" in table
    assert "raw_payload STRING NOT NULL" in table
    assert "ingested_at TIMESTAMP NOT NULL" in table
    assert "USING iceberg" in table
    assert "PARTITIONED BY (days(ingested_at))" in table
    assert "'format-version' = '2'" in table


def test_merge_is_idempotent_by_kafka_position():
    statement = merge_sql(BronzeConfig(), "_batch_7")

    assert "MERGE INTO bankflow.bronze.bronze_bankflow_events" in statement
    assert "target.kafka_topic = source.kafka_topic" in statement
    assert "target.kafka_partition = source.kafka_partition" in statement
    assert "target.kafka_offset = source.kafka_offset" in statement
    assert "WHEN NOT MATCHED THEN INSERT" in statement


def test_cli_builds_create_only_available_now_validation_config():
    config = config_from_args(
        [
            "--topic",
            "bankflow.day17.validation",
            "--checkpoint-location",
            "hdfs://localhost:9000/bankflow/checkpoints/test",
            "--invalid-record-path",
            "hdfs://localhost:9000/bankflow/quarantine/test",
            "--starting-offsets",
            "earliest",
            "--max-offsets-per-trigger",
            "250",
            "--available-now",
            "--create-only",
        ]
    )

    assert config.topic == "bankflow.day17.validation"
    assert config.starting_offsets == "earliest"
    assert config.max_offsets_per_trigger == 250
    assert config.available_now is True
    assert config.create_only is True


@pytest.mark.parametrize("name", ["catalog", "namespace", "table"])
def test_sql_identifiers_reject_unsafe_values(name):
    with pytest.raises(ValueError, match="safe SQL identifier"):
        BronzeConfig(**{name: "unsafe-name; DROP TABLE"})


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"metastore_uri": "http://localhost:9083"}, "thrift"),
        ({"warehouse": "file:///tmp/warehouse"}, "HDFS"),
        ({"namespace_location": "/bankflow/bronze"}, "HDFS"),
        ({"checkpoint_location": "file:///tmp/checkpoint"}, "HDFS"),
        ({"invalid_record_path": "file:///tmp/invalid"}, "HDFS"),
        ({"topic": "two topics"}, "whitespace"),
        ({"starting_offsets": "middle"}, "starting_offsets"),
        ({"max_offsets_per_trigger": 0}, "positive"),
        ({"warehouse": DEFAULT_NAMESPACE_LOCATION}, "must differ"),
    ],
)
def test_bronze_configuration_rejects_unsafe_values(overrides, message):
    with pytest.raises(ValueError, match=message):
        BronzeConfig(**overrides)


def test_merge_view_name_rejects_sql_injection():
    with pytest.raises(ValueError, match="safe SQL identifier"):
        merge_sql(BronzeConfig(), "batch; DROP TABLE bronze")
