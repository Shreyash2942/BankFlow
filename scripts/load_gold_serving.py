"""Mirror selected BankFlow Gold tables into PostgreSQL serving tables."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from sqlalchemy import Connection, text
from sqlalchemy.exc import SQLAlchemyError

from bankflow.config.settings import load_settings
from bankflow.database.connection import create_database_engine

SERVING_SCHEMA = "bankflow_serving"
ADVISORY_LOCK_KEY = 2_102_026


@dataclass(frozen=True)
class Dataset:
    name: str
    source_table: str
    target_table: str
    columns: tuple[str, ...]
    keys: tuple[str, ...]
    reconciliation_columns: tuple[str, ...]

    @property
    def target_identifier(self) -> str:
        return f"{SERVING_SCHEMA}.{self.target_table}"

    @property
    def source_query(self) -> str:
        return f"SELECT {', '.join(self.columns)} FROM {self.source_table}"


DAILY = Dataset(
    name="daily_transactions",
    source_table="hive.gold.gold_daily_transaction_metrics",
    target_table="analytics_daily_transactions",
    columns=(
        "metric_date",
        "currency",
        "transaction_event_count",
        "monetary_attempt_count",
        "successful_transaction_count",
        "declined_transaction_count",
        "balance_inquiry_count",
        "deposit_count",
        "successful_withdrawal_count",
        "declined_withdrawal_count",
        "total_deposit_amount",
        "total_withdrawal_amount",
        "total_declined_amount",
        "average_transaction_value",
        "success_rate",
        "decline_rate",
        "unique_account_count",
        "first_event_at",
        "last_event_at",
        "gold_processed_at",
    ),
    keys=("metric_date", "currency"),
    reconciliation_columns=(
        "transaction_event_count",
        "monetary_attempt_count",
        "successful_transaction_count",
        "declined_transaction_count",
        "total_deposit_amount",
        "total_withdrawal_amount",
    ),
)

AUTHENTICATION = Dataset(
    name="authentication_metrics",
    source_table="hive.gold.gold_authentication_metrics",
    target_table="analytics_authentication_metrics",
    columns=(
        "metric_date",
        "authentication_event_count",
        "authentication_attempt_count",
        "successful_authentication_count",
        "failed_authentication_count",
        "card_lockout_count",
        "session_end_count",
        "known_subject_event_count",
        "unknown_subject_event_count",
        "unique_account_count",
        "unique_card_count",
        "success_rate",
        "failure_rate",
        "first_event_at",
        "last_event_at",
        "gold_processed_at",
    ),
    keys=("metric_date",),
    reconciliation_columns=(
        "authentication_event_count",
        "authentication_attempt_count",
        "successful_authentication_count",
        "failed_authentication_count",
        "card_lockout_count",
    ),
)

ACCOUNT = Dataset(
    name="account_activity",
    source_table="hive.gold.gold_account_activity",
    target_table="analytics_account_activity",
    columns=(
        "metric_date",
        "account_id",
        "currency",
        "activity_event_count",
        "transaction_event_count",
        "distinct_transaction_count",
        "completed_monetary_transaction_count",
        "declined_transaction_count",
        "balance_inquiry_count",
        "deposit_count",
        "successful_withdrawal_count",
        "closure_event_count",
        "total_deposit_amount",
        "total_withdrawal_amount",
        "total_declined_amount",
        "opening_balance",
        "closing_balance",
        "account_status",
        "account_closed",
        "first_activity_at",
        "last_activity_at",
        "gold_processed_at",
    ),
    keys=("metric_date", "account_id", "currency"),
    reconciliation_columns=(
        "activity_event_count",
        "transaction_event_count",
        "completed_monetary_transaction_count",
        "declined_transaction_count",
        "total_deposit_amount",
        "total_withdrawal_amount",
    ),
)

HOURLY = Dataset(
    name="hourly_volume",
    source_table="hive.gold.gold_hourly_transaction_volume",
    target_table="analytics_hourly_volume",
    columns=(
        "event_hour",
        "currency",
        "transaction_type",
        "transaction_status",
        "transaction_event_count",
        "total_transaction_amount",
        "average_transaction_amount",
        "unique_account_count",
        "first_event_at",
        "last_event_at",
        "gold_processed_at",
    ),
    keys=("event_hour", "currency", "transaction_type", "transaction_status"),
    reconciliation_columns=("transaction_event_count", "total_transaction_amount"),
)

DATASETS = (DAILY, AUTHENTICATION, ACCOUNT, HOURLY)


class ServingLoadError(RuntimeError):
    """A safe, actionable serving-load failure."""


@dataclass(frozen=True)
class TrinoClient:
    base_url: str
    user: str = "trino"
    timeout_seconds: int = 30

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username:
            raise ValueError("Trino URL must be an HTTP(S) endpoint without embedded credentials.")
        if not self.user.strip() or any(character in self.user for character in "\r\n"):
            raise ValueError("Trino user must be a safe non-blank header value.")
        if not 1 <= self.timeout_seconds <= 300:
            raise ValueError("Trino timeout must be between 1 and 300 seconds.")

    @property
    def statement_url(self) -> str:
        return self.base_url.rstrip("/") + "/v1/statement"

    def _request(self, request: Request) -> dict[str, Any]:
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ServingLoadError("Trino query transport failed.") from exc

    def query(self, sql: str) -> list[dict[str, Any]]:
        headers = {
            "X-Trino-User": self.user,
            "X-Trino-Catalog": "hive",
            "X-Trino-Schema": "gold",
        }
        response = self._request(
            Request(
                self.statement_url,
                data=sql.encode("utf-8"),
                headers=headers,
                method="POST",
            )
        )
        column_names: list[str] | None = None
        rows: list[list[Any]] = []
        while True:
            if response.get("error"):
                error_name = response["error"].get("errorName", "TRINO_QUERY_ERROR")
                raise ServingLoadError(f"Trino rejected a Gold query ({error_name}).")
            if response.get("columns"):
                column_names = [column["name"] for column in response["columns"]]
            rows.extend(response.get("data", []))
            next_uri = response.get("nextUri")
            if not next_uri:
                break
            time.sleep(0.05)
            response = self._request(Request(next_uri, headers=headers, method="GET"))
        if column_names is None:
            raise ServingLoadError("Trino returned no column contract for a Gold query.")
        return [dict(zip(column_names, values, strict=True)) for values in rows]


def _stage_name(dataset: Dataset) -> str:
    return f"stage_{dataset.target_table}"


def _source_signature(dataset: Dataset, rows: list[dict[str, Any]]) -> tuple[Any, ...]:
    values: list[Any] = [len(rows)]
    for column in dataset.reconciliation_columns:
        total = sum((Decimal(str(row[column])) for row in rows), Decimal(0))
        values.append(total)
    return tuple(values)


def _target_signature(connection: Connection, dataset: Dataset) -> tuple[Any, ...]:
    aggregates = ", ".join(
        f"coalesce(sum({column}), 0) AS {column}" for column in dataset.reconciliation_columns
    )
    row = (
        connection.execute(
            text(f"SELECT count(*) AS row_count, {aggregates} FROM {dataset.target_identifier}")
        )
        .mappings()
        .one()
    )
    return (int(row["row_count"]),) + tuple(
        Decimal(str(row[column])) for column in dataset.reconciliation_columns
    )


def mirror_dataset(
    connection: Connection, dataset: Dataset, rows: list[dict[str, Any]]
) -> dict[str, int]:
    for row in rows:
        if tuple(row) != dataset.columns:
            raise ServingLoadError(
                f"{dataset.name} Gold columns do not match the serving contract."
            )
        if any(row[key] is None for key in dataset.keys):
            raise ServingLoadError(f"{dataset.name} contains a null serving key.")
    stage = _stage_name(dataset)
    connection.execute(
        text(
            f"CREATE TEMP TABLE {stage} "
            f"(LIKE {dataset.target_identifier} INCLUDING DEFAULTS) ON COMMIT DROP"
        )
    )
    source_columns = tuple(
        "source_gold_processed_at" if column == "gold_processed_at" else column
        for column in dataset.columns
    )
    parameters = tuple(
        {
            target: row[source]
            for source, target in zip(dataset.columns, source_columns, strict=True)
        }
        for row in rows
    )
    if parameters:
        names = ", ".join(source_columns)
        binds = ", ".join(f":{column}" for column in source_columns)
        connection.execute(text(f"INSERT INTO {stage} ({names}) VALUES ({binds})"), parameters)
    keys = ", ".join(dataset.keys)
    updates = ", ".join(
        f"{column} = EXCLUDED.{column}" for column in source_columns if column not in dataset.keys
    )
    names = ", ".join(source_columns)
    connection.execute(
        text(
            f"INSERT INTO {dataset.target_identifier} ({names}) "
            f"SELECT {names} FROM {stage} "
            f"ON CONFLICT ({keys}) DO UPDATE SET {updates}, loaded_at = now()"
        )
    )
    match = " AND ".join(f"target.{key} = stage.{key}" for key in dataset.keys)
    deleted = connection.execute(
        text(
            f"DELETE FROM {dataset.target_identifier} AS target WHERE NOT EXISTS "
            f"(SELECT 1 FROM {stage} AS stage WHERE {match})"
        )
    ).rowcount
    source_signature = _source_signature(dataset, rows)
    target_signature = _target_signature(connection, dataset)
    if target_signature != source_signature:
        raise ServingLoadError(f"{dataset.name} failed Gold-to-PostgreSQL reconciliation.")
    return {"source_rows": len(rows), "target_rows": target_signature[0], "deleted_rows": deleted}


def run_load(client: TrinoClient, env_file: str) -> dict[str, dict[str, int]]:
    source_rows = {dataset.name: client.query(dataset.source_query) for dataset in DATASETS}
    settings = load_settings(env_file)
    engine = create_database_engine(settings)
    try:
        with engine.begin() as connection:
            connection.execute(
                text("SELECT pg_advisory_xact_lock(:key)"), {"key": ADVISORY_LOCK_KEY}
            )
            results = {
                dataset.name: mirror_dataset(connection, dataset, source_rows[dataset.name])
                for dataset in DATASETS
            }
    except SQLAlchemyError as exc:
        raise ServingLoadError(
            "PostgreSQL serving load failed; verify migration, credentials, and availability."
        ) from exc
    finally:
        engine.dispose()
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=os.getenv("BANKFLOW_ENV_FILE", ".env"))
    parser.add_argument(
        "--trino-url", default=os.getenv("BANKFLOW_TRINO_URL", "http://127.0.0.1:8096")
    )
    parser.add_argument("--trino-user", default=os.getenv("BANKFLOW_TRINO_USER", "trino"))
    parser.add_argument("--trino-timeout", type=int, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results = run_load(
            TrinoClient(args.trino_url, args.trino_user, args.trino_timeout), args.env_file
        )
        print(
            json.dumps(
                {"event": "bankflow_gold_serving_load_complete", "datasets": results},
                sort_keys=True,
            )
        )
        return 0
    except (ServingLoadError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "event": "bankflow_gold_serving_load_failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
