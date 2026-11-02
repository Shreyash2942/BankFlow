"""Service-free contracts for the Day 18 Bronze-to-Silver transaction pipeline."""

import sys

import pytest

from spark.silver.transactions import (
    DEFAULT_BRONZE_NAMESPACE,
    DEFAULT_BRONZE_TABLE,
    DEFAULT_CATALOG,
    DEFAULT_METASTORE_URI,
    DEFAULT_NAMESPACE_LOCATION,
    DEFAULT_REJECT_TABLE,
    DEFAULT_SILVER_NAMESPACE,
    DEFAULT_SILVER_TABLE,
    DEFAULT_WAREHOUSE,
    RAW_EVENT_SCHEMA_SPEC,
    REJECT_COLUMN_TYPES,
    SILVER_COLUMN_TYPES,
    TRANSACTION_EVENT_SHAPES,
    SilverConfig,
    config_from_args,
    merge_reject_sql,
    merge_sql,
    namespace_sql,
    reject_table_sql,
    silver_table_sql,
)


def test_silver_module_keeps_pyspark_out_of_service_free_imports():
    assert "pyspark" not in sys.modules


def test_default_catalog_source_and_targets_are_explicit():
    config = SilverConfig()

    assert DEFAULT_CATALOG == "bankflow"
    assert DEFAULT_BRONZE_NAMESPACE == "bronze"
    assert DEFAULT_BRONZE_TABLE == "bronze_bankflow_events"
    assert DEFAULT_SILVER_NAMESPACE == "silver"
    assert DEFAULT_SILVER_TABLE == "silver_transactions"
    assert DEFAULT_REJECT_TABLE == "silver_transaction_rejects"
    assert DEFAULT_METASTORE_URI == "thrift://localhost:9083"
    assert DEFAULT_WAREHOUSE == "hdfs://localhost:9000/bankflow/lakehouse"
    assert DEFAULT_NAMESPACE_LOCATION == "hdfs://localhost:9000/bankflow/silver"
    assert config.bronze_identifier == "bankflow.bronze.bronze_bankflow_events"
    assert config.silver_identifier == "bankflow.silver.silver_transactions"
    assert config.reject_identifier == "bankflow.silver.silver_transaction_rejects"


def test_day18_event_shapes_exclude_authentication_and_account_events():
    assert TRANSACTION_EVENT_SHAPES == {
        "balance.viewed": ("balance_inquiry", "completed"),
        "withdrawal.requested": ("withdrawal", "pending"),
        "withdrawal.completed": ("withdrawal", "completed"),
        "withdrawal.declined": ("withdrawal", "declined"),
        "deposit.completed": ("deposit", "completed"),
    }
    assert "account.closed" not in TRANSACTION_EVENT_SHAPES
    assert all(not event.startswith("authentication.") for event in TRANSACTION_EVENT_SHAPES)


def test_raw_schema_reads_financial_values_as_strings_before_exact_casting():
    event_fields = {field["name"]: field["type"] for field in RAW_EVENT_SCHEMA_SPEC["fields"]}
    payload_fields = {field["name"]: field["type"] for field in event_fields["payload"]["fields"]}

    assert payload_fields["amount"] == "string"
    assert payload_fields["balance_before"] == "string"
    assert payload_fields["balance_after"] == "string"
    assert event_fields["occurred_at"] == "string"


def test_silver_schema_contains_normalized_business_and_lineage_fields():
    assert SILVER_COLUMN_TYPES["amount"] == "decimal(18,2)"
    assert SILVER_COLUMN_TYPES["balance_before"] == "decimal(18,2)"
    assert SILVER_COLUMN_TYPES["balance_after"] == "decimal(18,2)"
    assert SILVER_COLUMN_TYPES["occurred_at"] == "timestamp"
    assert SILVER_COLUMN_TYPES["bronze_ingested_at"] == "timestamp"
    assert SILVER_COLUMN_TYPES["silver_processed_at"] == "timestamp"
    assert SILVER_COLUMN_TYPES["kafka_offset"] == "bigint"
    assert "raw_payload" not in SILVER_COLUMN_TYPES


def test_reject_schema_is_pointer_only_and_does_not_copy_raw_payload():
    assert REJECT_COLUMN_TYPES["rejection_reason"] == "string"
    assert REJECT_COLUMN_TYPES["raw_payload_sha256"] == "string"
    assert "raw_payload" not in REJECT_COLUMN_TYPES
    assert {"kafka_topic", "kafka_partition", "kafka_offset"}.issubset(REJECT_COLUMN_TYPES)


def test_namespace_and_tables_use_hdfs_iceberg_v2():
    config = SilverConfig()
    namespace = namespace_sql(config)
    silver = silver_table_sql(config)
    rejects = reject_table_sql(config)

    assert namespace == (
        "CREATE NAMESPACE IF NOT EXISTS bankflow.silver "
        "LOCATION 'hdfs://localhost:9000/bankflow/silver'"
    )
    assert "CREATE TABLE IF NOT EXISTS bankflow.silver.silver_transactions" in silver
    assert "amount DECIMAL(18,2) NOT NULL" in silver
    assert "PARTITIONED BY (days(occurred_at))" in silver
    assert "'format-version' = '2'" in silver
    assert "CREATE TABLE IF NOT EXISTS bankflow.silver.silver_transaction_rejects" in rejects
    assert "PARTITIONED BY (days(bronze_ingested_at))" in rejects


def test_merges_make_valid_and_reject_outputs_idempotent():
    config = SilverConfig()
    valid_merge = merge_sql(config, "_valid_day18")
    reject_merge = merge_reject_sql(config, "_reject_day18")

    assert "MERGE INTO bankflow.silver.silver_transactions" in valid_merge
    assert "target.event_id = source.event_id" in valid_merge
    assert "WHEN NOT MATCHED THEN INSERT" in valid_merge
    assert "MERGE INTO bankflow.silver.silver_transaction_rejects" in reject_merge
    assert "target.reject_id = source.reject_id" in reject_merge


def test_cli_supports_isolated_source_and_target_namespaces():
    config = config_from_args(
        [
            "--bronze-namespace",
            "day18_bronze",
            "--bronze-table",
            "events",
            "--silver-namespace",
            "day18_silver",
            "--silver-table",
            "transactions",
            "--reject-table",
            "rejects",
            "--namespace-location",
            "hdfs://localhost:9000/bankflow/day18-silver",
            "--create-only",
        ]
    )

    assert config.bronze_identifier == "bankflow.day18_bronze.events"
    assert config.silver_identifier == "bankflow.day18_silver.transactions"
    assert config.reject_identifier == "bankflow.day18_silver.rejects"
    assert config.create_only is True


@pytest.mark.parametrize(
    "name",
    [
        "catalog",
        "bronze_namespace",
        "bronze_table",
        "silver_namespace",
        "silver_table",
        "reject_table",
    ],
)
def test_sql_identifiers_reject_unsafe_values(name):
    with pytest.raises(ValueError, match="safe SQL identifier"):
        SilverConfig(**{name: "unsafe-name; DROP TABLE"})


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"metastore_uri": "http://localhost:9083"}, "thrift"),
        ({"warehouse": "file:///tmp/warehouse"}, "HDFS"),
        ({"namespace_location": "/bankflow/silver"}, "HDFS"),
        ({"app_name": ""}, "non-blank"),
        (
            {
                "bronze_namespace": "silver",
                "bronze_table": "silver_transactions",
            },
            "must differ",
        ),
        ({"reject_table": "silver_transactions"}, "must differ"),
    ],
)
def test_configuration_rejects_unsafe_boundaries(overrides, message):
    with pytest.raises(ValueError, match=message):
        SilverConfig(**overrides)


@pytest.mark.parametrize("builder", [merge_sql, merge_reject_sql])
def test_merge_view_name_rejects_sql_injection(builder):
    with pytest.raises(ValueError, match="safe SQL identifier"):
        builder(SilverConfig(), "batch; DROP TABLE silver")
