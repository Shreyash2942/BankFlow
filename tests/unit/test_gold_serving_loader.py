"""Service-free contracts for the Day 21 Gold serving pipeline."""

import json
from pathlib import Path

import pytest

from scripts import load_gold_serving
from scripts.load_gold_serving import (
    ACCOUNT,
    AUTHENTICATION,
    DAILY,
    DATASETS,
    HOURLY,
    ServingLoadError,
    TrinoClient,
    _source_signature,
)


def test_serving_pipeline_exports_all_planned_gold_datasets():
    assert DATASETS == (DAILY, AUTHENTICATION, ACCOUNT, HOURLY)
    assert {dataset.target_identifier for dataset in DATASETS} == {
        "bankflow_serving.analytics_daily_transactions",
        "bankflow_serving.analytics_authentication_metrics",
        "bankflow_serving.analytics_account_activity",
        "bankflow_serving.analytics_hourly_volume",
    }
    assert {dataset.source_table for dataset in DATASETS} == {
        "hive.gold.gold_daily_transaction_metrics",
        "hive.gold.gold_authentication_metrics",
        "hive.gold.gold_account_activity",
        "hive.gold.gold_hourly_transaction_volume",
    }


def test_serving_datasets_use_complete_deterministic_business_keys():
    assert DAILY.keys == ("metric_date", "currency")
    assert AUTHENTICATION.keys == ("metric_date",)
    assert ACCOUNT.keys == ("metric_date", "account_id", "currency")
    assert HOURLY.keys == (
        "event_hour",
        "currency",
        "transaction_type",
        "transaction_status",
    )
    assert all("gold_processed_at" in dataset.columns for dataset in DATASETS)
    assert all(dataset.reconciliation_columns for dataset in DATASETS)


@pytest.mark.parametrize(
    "url",
    [
        "",
        "localhost:8096",
        "ftp://localhost:8096",
        "http://user:password@localhost:8096",
    ],
)
def test_trino_client_rejects_unsafe_endpoints(url):
    with pytest.raises(ValueError, match="HTTP"):
        TrinoClient(url)


def test_trino_client_polls_pages_and_preserves_column_order(monkeypatch):
    responses = iter(
        [
            {"nextUri": "http://localhost:8096/next/1"},
            {
                "columns": [{"name": "metric_date"}, {"name": "transaction_event_count"}],
                "data": [["2026-01-01", 19]],
                "nextUri": "http://localhost:8096/next/2",
            },
            {"data": [["2026-01-02", 4]]},
        ]
    )
    monkeypatch.setattr(TrinoClient, "_request", lambda self, request: next(responses))

    rows = TrinoClient("http://localhost:8096").query("SELECT metric_date, count FROM gold")

    assert rows == [
        {"metric_date": "2026-01-01", "transaction_event_count": 19},
        {"metric_date": "2026-01-02", "transaction_event_count": 4},
    ]


def test_trino_client_reports_query_errors_without_echoing_sql(monkeypatch):
    monkeypatch.setattr(
        TrinoClient,
        "_request",
        lambda self, request: {"error": {"errorName": "TABLE_NOT_FOUND"}},
    )

    with pytest.raises(ServingLoadError, match="TABLE_NOT_FOUND") as error:
        TrinoClient("http://localhost:8096").query("SELECT secret_value FROM missing")

    assert "secret_value" not in str(error.value)


def test_source_signature_uses_exact_decimal_totals():
    rows = [
        {
            column: (
                "0.10"
                if column == "total_transaction_amount"
                else 1
                if column == "transaction_event_count"
                else "fixture"
            )
            for column in HOURLY.columns
        },
        {
            column: (
                "0.20"
                if column == "total_transaction_amount"
                else 2
                if column == "transaction_event_count"
                else "fixture"
            )
            for column in HOURLY.columns
        },
    ]

    assert tuple(map(str, _source_signature(HOURLY, rows))) == ("2", "3", "0.30")


def test_migration_defines_serving_schema_tables_timestamps_and_constraints():
    source = Path("migrations/versions/0004_create_analytics_serving_schema.py").read_text(
        encoding="utf-8"
    )

    assert 'revision = "0004"' in source
    assert 'down_revision = "0003"' in source
    assert "CreateSchema(SCHEMA)" in source
    for dataset in DATASETS:
        assert f'"{dataset.target_table}"' in source
    assert '"source_gold_processed_at"' in source
    assert '"loaded_at"' in source
    assert 'server_default=sa.text("now()")' in source
    assert "attempt_reconciliation" in source


def test_dbt_and_dashboard_contracts_reference_lakehouse_serving_path():
    sources = Path("dbt/models/staging/_sources.yml").read_text(encoding="utf-8")
    marts = Path("dbt/models/marts/_marts.yml").read_text(encoding="utf-8")
    page = Path("pages/5_Analytics.py").read_text(encoding="utf-8")

    assert "name: bankflow_serving" in sources
    for dataset in DATASETS:
        assert f"name: {dataset.target_table}" in sources
    assert "lakehouse_daily_transactions" in marts
    assert "lakehouse_authentication_metrics" in marts
    assert "lakehouse_account_activity" in marts
    assert "lakehouse_hourly_volume" in marts
    assert "Lakehouse analytics" in page
    assert "Hourly lakehouse volume" in page
    assert "PostgreSQL serving" in page


def test_cli_failure_is_structured_and_secret_free(monkeypatch, capsys):
    monkeypatch.setattr(
        load_gold_serving,
        "run_load",
        lambda client, env_file: (_ for _ in ()).throw(ServingLoadError("safe failure")),
    )

    assert load_gold_serving.main(["--trino-url", "http://localhost:8096"]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output == {
        "event": "bankflow_gold_serving_load_failed",
        "error": "safe failure",
        "error_type": "ServingLoadError",
    }
