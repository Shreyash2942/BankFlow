"""Service-free contract tests for the Day 16 Spark streaming entry point."""

import sys

import pytest

from streaming.bankflow_stream import (
    ALL_EVENT_TYPES,
    AUTHENTICATION_EVENT_TYPES,
    DEFAULT_CHECKPOINT,
    DEFAULT_INVALID_PATH,
    DEFAULT_KAFKA_PACKAGE,
    EVENT_SCHEMA_SPEC,
    PAYLOAD_SCHEMA_SPEC,
    TRANSACTION_EVENT_TYPES,
    StreamConfig,
    config_from_args,
    connector_spark_version,
)


def _field_names(schema):
    return {field["name"] for field in schema["fields"]}


def test_stream_module_does_not_require_pyspark_during_service_free_import():
    assert "pyspark" not in sys.modules


def test_event_schema_is_explicit_and_covers_v1_payload_fields():
    assert _field_names(EVENT_SCHEMA_SPEC) == {
        "event_id",
        "event_type",
        "schema_version",
        "occurred_at",
        "source",
        "payload",
        "_corrupt_record",
    }
    assert _field_names(PAYLOAD_SCHEMA_SPEC) == {
        "kind",
        "transaction_id",
        "customer_id",
        "account_id",
        "card_id",
        "transaction_type",
        "status",
        "amount",
        "balance_before",
        "balance_after",
        "currency",
        "account_status",
        "decline_reason",
        "outcome",
        "remaining_attempts",
        "atm_id",
    }
    assert {"pin", "pin_hash", "session_token"}.isdisjoint(_field_names(PAYLOAD_SCHEMA_SPEC))


def test_event_type_sets_cover_the_released_contract_without_overlap():
    assert set(TRANSACTION_EVENT_TYPES).isdisjoint(AUTHENTICATION_EVENT_TYPES)
    assert len(ALL_EVENT_TYPES) == 10
    assert set(ALL_EVENT_TYPES) == {
        "authentication.succeeded",
        "authentication.failed",
        "card.locked",
        "balance.viewed",
        "withdrawal.requested",
        "withdrawal.completed",
        "withdrawal.declined",
        "deposit.completed",
        "account.closed",
        "session.ended",
    }


def test_connector_coordinate_matches_container_spark_runtime():
    assert DEFAULT_KAFKA_PACKAGE == "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
    assert connector_spark_version(DEFAULT_KAFKA_PACKAGE) == "3.5.1"
    assert connector_spark_version("not-a-coordinate") is None


def test_distributed_runtime_paths_use_shared_hdfs_storage():
    assert DEFAULT_CHECKPOINT.startswith("hdfs://localhost:9000/bankflow/checkpoints/")
    assert DEFAULT_INVALID_PATH.startswith("hdfs://localhost:9000/bankflow/quarantine/")


def test_cli_builds_checkpointed_available_now_configuration():
    config = config_from_args(
        [
            "--bootstrap-servers",
            "localhost:9092",
            "--topic",
            "bankflow.day16.test",
            "--checkpoint-location",
            "file:///tmp/checkpoint",
            "--invalid-record-path",
            "file:///tmp/invalid",
            "--starting-offsets",
            "earliest",
            "--max-offsets-per-trigger",
            "250",
            "--available-now",
        ]
    )

    assert config.topic == "bankflow.day16.test"
    assert config.starting_offsets == "earliest"
    assert config.max_offsets_per_trigger == 250
    assert config.available_now is True
    assert config.fail_on_data_loss is True


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"topic": "  "}, "topic"),
        ({"topic": "two topics"}, "whitespace"),
        ({"starting_offsets": "middle"}, "starting_offsets"),
        ({"max_offsets_per_trigger": 0}, "positive"),
        (
            {
                "checkpoint_location": "file:///tmp/same",
                "invalid_record_path": "file:///tmp/same",
            },
            "must differ",
        ),
        ({"kafka_package": "bad"}, "Spark version"),
    ],
)
def test_stream_configuration_rejects_unsafe_values(overrides, message):
    with pytest.raises(ValueError, match=message):
        StreamConfig(**overrides)
