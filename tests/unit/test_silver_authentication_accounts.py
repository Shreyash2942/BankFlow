"""Service-free contracts for Day 19 Silver authentication and account pipelines."""

import sys

import pytest

from spark.silver.accounts import (
    ACCOUNT_COLUMN_TYPES,
    ACCOUNT_EVENT_SCHEMA_SPEC,
    ACCOUNT_EVENT_TYPES,
    DEFAULT_ACCOUNT_TABLE,
    AccountConfig,
    account_table_sql,
)
from spark.silver.accounts import (
    DEFAULT_REJECT_TABLE as DEFAULT_ACCOUNT_REJECT_TABLE,
)
from spark.silver.accounts import (
    config_from_args as account_config_from_args,
)
from spark.silver.accounts import (
    merge_reject_sql as account_merge_reject_sql,
)
from spark.silver.accounts import (
    merge_sql as account_merge_sql,
)
from spark.silver.authentication import (
    AUTH_EVENT_SCHEMA_SPEC,
    AUTHENTICATION_COLUMN_TYPES,
    AUTHENTICATION_EVENT_TYPES,
    DEFAULT_AUTH_TABLE,
    AuthenticationConfig,
    authentication_table_sql,
)
from spark.silver.authentication import (
    DEFAULT_REJECT_TABLE as DEFAULT_AUTH_REJECT_TABLE,
)
from spark.silver.authentication import (
    config_from_args as auth_config_from_args,
)
from spark.silver.authentication import (
    merge_reject_sql as auth_merge_reject_sql,
)
from spark.silver.authentication import (
    merge_sql as auth_merge_sql,
)
from spark.silver.common import (
    DEFAULT_NAMESPACE_LOCATION,
    REJECT_COLUMN_TYPES,
    merge_insert_sql,
    namespace_sql,
    reject_table_sql,
)


def test_day19_modules_keep_pyspark_out_of_service_free_imports():
    assert "pyspark" not in sys.modules


def test_authentication_defaults_target_canonical_silver_tables():
    config = AuthenticationConfig()

    assert DEFAULT_AUTH_TABLE == "silver_authentication_events"
    assert DEFAULT_AUTH_REJECT_TABLE == "silver_authentication_event_rejects"
    assert config.bronze_identifier == "bankflow.bronze.bronze_bankflow_events"
    assert config.auth_identifier == "bankflow.silver.silver_authentication_events"
    assert config.reject_identifier == "bankflow.silver.silver_authentication_event_rejects"
    assert config.namespace_location == DEFAULT_NAMESPACE_LOCATION


def test_account_defaults_target_canonical_silver_tables():
    config = AccountConfig()

    assert DEFAULT_ACCOUNT_TABLE == "silver_account_events"
    assert DEFAULT_ACCOUNT_REJECT_TABLE == "silver_account_event_rejects"
    assert config.bronze_identifier == "bankflow.bronze.bronze_bankflow_events"
    assert config.account_identifier == "bankflow.silver.silver_account_events"
    assert config.reject_identifier == "bankflow.silver.silver_account_event_rejects"


def test_authentication_event_normalization_and_lockout_classification_contract():
    assert AUTHENTICATION_EVENT_TYPES == {
        "authentication.succeeded": ("authentication_success", "success"),
        "authentication.failed": ("authentication_failure", "failure"),
        "card.locked": ("card_lockout", "lockout"),
        "session.ended": ("session_end", "session"),
    }
    assert AUTHENTICATION_COLUMN_TYPES["is_lockout"] == "boolean"
    assert AUTHENTICATION_COLUMN_TYPES["lockout_classification"] == "string"
    assert AUTHENTICATION_COLUMN_TYPES["subject_known"] == "boolean"


def test_account_event_normalization_is_reserved_for_account_closed():
    assert ACCOUNT_EVENT_TYPES == {"account.closed": ("account_closed", "closure")}
    assert ACCOUNT_COLUMN_TYPES["closure_classification"] == "string"
    assert ACCOUNT_COLUMN_TYPES["amount"] == "decimal(18,2)"
    assert ACCOUNT_COLUMN_TYPES["balance_after"] == "decimal(18,2)"


def test_authentication_raw_schema_contains_subject_and_lockout_fields():
    fields = {field["name"]: field["type"] for field in AUTH_EVENT_SCHEMA_SPEC["fields"]}
    payload = {field["name"]: field["type"] for field in fields["payload"]["fields"]}

    assert payload["customer_id"] == "string"
    assert payload["account_id"] == "string"
    assert payload["card_id"] == "string"
    assert payload["outcome"] == "string"
    assert payload["remaining_attempts"] == "integer"


def test_account_raw_schema_reads_financial_values_as_strings_before_casting():
    fields = {field["name"]: field["type"] for field in ACCOUNT_EVENT_SCHEMA_SPEC["fields"]}
    payload = {field["name"]: field["type"] for field in fields["payload"]["fields"]}

    assert payload["amount"] == "string"
    assert payload["balance_before"] == "string"
    assert payload["balance_after"] == "string"
    assert payload["account_status"] == "string"


def test_authentication_table_is_typed_partitioned_iceberg_v2():
    statement = authentication_table_sql(AuthenticationConfig())

    assert "CREATE TABLE IF NOT EXISTS bankflow.silver.silver_authentication_events" in statement
    assert "is_lockout BOOLEAN NOT NULL" in statement
    assert "remaining_attempts INT" in statement
    assert "PARTITIONED BY (days(occurred_at))" in statement
    assert "'format-version' = '2'" in statement


def test_account_table_is_typed_partitioned_iceberg_v2():
    statement = account_table_sql(AccountConfig())

    assert "CREATE TABLE IF NOT EXISTS bankflow.silver.silver_account_events" in statement
    assert "closure_classification STRING NOT NULL" in statement
    assert "amount DECIMAL(18,2) NOT NULL" in statement
    assert "PARTITIONED BY (days(occurred_at))" in statement
    assert "'format-version' = '2'" in statement


def test_shared_namespace_and_reject_contract_is_pointer_only():
    config = AuthenticationConfig()
    namespace = namespace_sql(config)
    rejects = reject_table_sql(config)

    assert namespace == (
        "CREATE NAMESPACE IF NOT EXISTS bankflow.silver "
        "LOCATION 'hdfs://localhost:9000/bankflow/silver'"
    )
    assert "raw_payload_sha256 STRING NOT NULL" in rejects
    assert "raw_payload STRING" not in rejects
    assert "PARTITIONED BY (days(bronze_ingested_at))" in rejects
    assert "raw_payload" not in REJECT_COLUMN_TYPES


@pytest.mark.parametrize(
    ("builder", "config", "target", "key"),
    [
        (
            auth_merge_sql,
            AuthenticationConfig(),
            "bankflow.silver.silver_authentication_events",
            "event_id",
        ),
        (
            auth_merge_reject_sql,
            AuthenticationConfig(),
            "bankflow.silver.silver_authentication_event_rejects",
            "reject_id",
        ),
        (
            account_merge_sql,
            AccountConfig(),
            "bankflow.silver.silver_account_events",
            "event_id",
        ),
        (
            account_merge_reject_sql,
            AccountConfig(),
            "bankflow.silver.silver_account_event_rejects",
            "reject_id",
        ),
    ],
)
def test_day19_merges_are_idempotent(builder, config, target, key):
    statement = builder(config, "_day19_batch")

    assert f"MERGE INTO {target}" in statement
    assert f"target.{key} = source.{key}" in statement
    assert "WHEN NOT MATCHED THEN INSERT" in statement


def test_authentication_cli_supports_isolated_validation_tables():
    config = auth_config_from_args(
        [
            "--bronze-namespace",
            "day19_bronze",
            "--bronze-table",
            "events",
            "--silver-namespace",
            "day19_auth",
            "--auth-table",
            "authentication",
            "--reject-table",
            "rejects",
            "--namespace-location",
            "hdfs://localhost:9000/bankflow/day19-auth",
            "--create-only",
        ]
    )

    assert config.auth_identifier == "bankflow.day19_auth.authentication"
    assert config.reject_identifier == "bankflow.day19_auth.rejects"
    assert config.create_only is True


def test_account_cli_supports_isolated_validation_tables():
    config = account_config_from_args(
        [
            "--bronze-namespace",
            "day19_bronze",
            "--bronze-table",
            "events",
            "--silver-namespace",
            "day19_accounts",
            "--account-table",
            "accounts",
            "--reject-table",
            "rejects",
            "--namespace-location",
            "hdfs://localhost:9000/bankflow/day19-accounts",
            "--create-only",
        ]
    )

    assert config.account_identifier == "bankflow.day19_accounts.accounts"
    assert config.reject_identifier == "bankflow.day19_accounts.rejects"
    assert config.create_only is True


@pytest.mark.parametrize("config_type", [AuthenticationConfig, AccountConfig])
@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"catalog": "unsafe-name"}, "safe SQL identifier"),
        ({"metastore_uri": "http://localhost:9083"}, "thrift"),
        ({"warehouse": "file:///tmp/warehouse"}, "HDFS"),
        ({"namespace_location": "/bankflow/silver"}, "HDFS"),
        ({"app_name": ""}, "non-blank"),
    ],
)
def test_day19_configs_reject_unsafe_runtime_boundaries(config_type, overrides, message):
    with pytest.raises(ValueError, match=message):
        config_type(**overrides)


def test_authentication_config_rejects_target_collision():
    with pytest.raises(ValueError, match="must differ"):
        AuthenticationConfig(reject_table=DEFAULT_AUTH_TABLE)


def test_account_config_rejects_target_collision():
    with pytest.raises(ValueError, match="must differ"):
        AccountConfig(reject_table=DEFAULT_ACCOUNT_TABLE)


@pytest.mark.parametrize(
    ("view_name", "key", "message"),
    [
        ("bad; DROP TABLE silver", "event_id", "view_name"),
        ("safe_view", "bad-key", "key"),
    ],
)
def test_shared_merge_rejects_unsafe_identifiers(view_name, key, message):
    with pytest.raises(ValueError, match=message):
        merge_insert_sql("bankflow.silver.target", {"event_id": "string"}, view_name, key)
