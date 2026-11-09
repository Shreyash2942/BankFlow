"""Cross-layer data-quality rules, execution, persistence, and dashboard reads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import SQLAlchemyError


class QueryClient(Protocol):
    def query(self, sql: str) -> list[dict[str, object]]: ...


@dataclass(frozen=True)
class QualityRule:
    rule_id: str
    layer: str
    category: str
    description: str
    sql: str


@dataclass(frozen=True)
class QualityResult:
    rule: QualityRule
    status: str
    violation_count: int
    checked_at: datetime
    message: str | None = None


@dataclass(frozen=True)
class QualityRun:
    run_id: UUID
    started_at: datetime
    completed_at: datetime
    triggered_by: str
    results: tuple[QualityResult, ...]

    @property
    def passed_rules(self) -> int:
        return sum(result.status == "passed" for result in self.results)

    @property
    def failed_rules(self) -> int:
        return sum(result.status == "failed" for result in self.results)

    @property
    def error_rules(self) -> int:
        return sum(result.status == "error" for result in self.results)

    @property
    def total_violations(self) -> int:
        return sum(result.violation_count for result in self.results)

    @property
    def status(self) -> str:
        if self.error_rules:
            return "error"
        return "failed" if self.failed_rules else "passed"


def _count_rule(rule_id: str, layer: str, category: str, description: str, query: str):
    return QualityRule(rule_id, layer, category, description, query.strip())


QUALITY_RULES = (
    _count_rule(
        "bronze.required_fields",
        "bronze",
        "null",
        "Bronze required metadata is populated.",
        """SELECT count(*) violation_count FROM hive.bronze.bronze_bankflow_events
        WHERE event_id IS NULL OR event_type IS NULL OR schema_version IS NULL
           OR occurred_at IS NULL OR source IS NULL OR payload_kind IS NULL
           OR raw_payload IS NULL OR raw_payload_sha256 IS NULL OR ingested_at IS NULL""",
    ),
    _count_rule(
        "bronze.duplicate_event_id",
        "bronze",
        "duplicate",
        "Bronze event IDs are unique.",
        """SELECT count(*) violation_count FROM (
        SELECT event_id FROM hive.bronze.bronze_bankflow_events
        GROUP BY event_id HAVING count(*) > 1) duplicates""",
    ),
    _count_rule(
        "bronze.duplicate_kafka_position",
        "bronze",
        "duplicate",
        "A Kafka position is ingested at most once.",
        """SELECT count(*) violation_count FROM (
        SELECT kafka_topic, kafka_partition, kafka_offset
        FROM hive.bronze.bronze_bankflow_events
        GROUP BY kafka_topic, kafka_partition, kafka_offset HAVING count(*) > 1) duplicates""",
    ),
    _count_rule(
        "silver.transaction_required_fields",
        "silver",
        "null",
        "Silver transaction business keys and values are populated.",
        """SELECT count(*) violation_count FROM hive.silver.silver_transactions
        WHERE event_id IS NULL OR transaction_id IS NULL OR customer_id IS NULL
           OR account_id IS NULL OR transaction_type IS NULL OR transaction_status IS NULL
           OR amount IS NULL OR balance_before IS NULL OR balance_after IS NULL
           OR currency IS NULL OR occurred_at IS NULL""",
    ),
    _count_rule(
        "silver.duplicate_transaction_event",
        "silver",
        "duplicate",
        "Silver transaction event IDs are unique.",
        """SELECT count(*) violation_count FROM (
        SELECT event_id FROM hive.silver.silver_transactions
        GROUP BY event_id HAVING count(*) > 1) duplicates""",
    ),
    _count_rule(
        "silver.transaction_status",
        "silver",
        "domain",
        "Transaction statuses use the supported lifecycle values.",
        """SELECT count(*) violation_count FROM hive.silver.silver_transactions
        WHERE transaction_status NOT IN ('pending', 'completed', 'declined')""",
    ),
    _count_rule(
        "silver.transaction_amount_range",
        "silver",
        "range",
        "Transaction amounts are between zero and one million currency units.",
        """SELECT count(*) violation_count FROM hive.silver.silver_transactions
        WHERE amount < 0 OR amount > DECIMAL '1000000.00'""",
    ),
    _count_rule(
        "silver.transaction_balance_consistency",
        "silver",
        "consistency",
        "Transaction balances agree with type and status semantics.",
        """SELECT count(*) violation_count FROM hive.silver.silver_transactions WHERE
        (transaction_status <> 'completed' AND balance_before <> balance_after)
        OR (transaction_type = 'balance_inquiry' AND (amount <> 0 OR balance_before <> balance_after))
        OR (transaction_status = 'completed' AND transaction_type = 'withdrawal'
            AND balance_before - amount <> balance_after)
        OR (transaction_status = 'completed' AND transaction_type = 'deposit'
            AND balance_before + amount <> balance_after)""",
    ),
    _count_rule(
        "silver.duplicate_authentication_event",
        "silver",
        "duplicate",
        "Silver authentication event IDs are unique.",
        """SELECT count(*) violation_count FROM (
        SELECT event_id FROM hive.silver.silver_authentication_events
        GROUP BY event_id HAVING count(*) > 1) duplicates""",
    ),
    _count_rule(
        "silver.duplicate_account_event",
        "silver",
        "duplicate",
        "Silver account event IDs are unique.",
        """SELECT count(*) violation_count FROM (
        SELECT event_id FROM hive.silver.silver_account_events
        GROUP BY event_id HAVING count(*) > 1) duplicates""",
    ),
    _count_rule(
        "reconciliation.bronze_to_silver",
        "cross_layer",
        "reconciliation",
        "Every Bronze event is represented by a valid or rejected Silver record.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.bronze.bronze_bankflow_events) bronze_count,
          (SELECT count(*) FROM hive.silver.silver_transactions) +
          (SELECT count(*) FROM hive.silver.silver_authentication_events) +
          (SELECT count(*) FROM hive.silver.silver_account_events) +
          (SELECT count(*) FROM hive.silver.silver_transaction_rejects) +
          (SELECT count(*) FROM hive.silver.silver_authentication_event_rejects) +
          (SELECT count(*) FROM hive.silver.silver_account_event_rejects) silver_count)
        SELECT CASE WHEN bronze_count = silver_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "reconciliation.silver_to_gold_daily",
        "cross_layer",
        "reconciliation",
        "Silver transaction events reconcile to Gold daily metrics.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.silver.silver_transactions) silver_count,
          (SELECT coalesce(sum(transaction_event_count), 0)
           FROM hive.gold.gold_daily_transaction_metrics) gold_count)
        SELECT CASE WHEN silver_count = gold_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "reconciliation.silver_to_gold_hourly",
        "cross_layer",
        "reconciliation",
        "Silver transaction events reconcile to Gold hourly metrics.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.silver.silver_transactions) silver_count,
          (SELECT coalesce(sum(transaction_event_count), 0)
           FROM hive.gold.gold_hourly_transaction_volume) gold_count)
        SELECT CASE WHEN silver_count = gold_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "reconciliation.silver_to_gold_authentication",
        "cross_layer",
        "reconciliation",
        "Silver authentication events reconcile to Gold authentication metrics.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.silver.silver_authentication_events) silver_count,
          (SELECT coalesce(sum(authentication_event_count), 0)
           FROM hive.gold.gold_authentication_metrics) gold_count)
        SELECT CASE WHEN silver_count = gold_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "reconciliation.silver_to_gold_account",
        "cross_layer",
        "reconciliation",
        "Silver transaction and account events reconcile to Gold account activity.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.silver.silver_transactions) +
          (SELECT count(*) FROM hive.silver.silver_account_events) silver_count,
          (SELECT coalesce(sum(activity_event_count), 0)
           FROM hive.gold.gold_account_activity) gold_count)
        SELECT CASE WHEN silver_count = gold_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "reconciliation.silver_to_gold_declines",
        "cross_layer",
        "reconciliation",
        "Silver declined transactions reconcile to Gold decline metrics.",
        """WITH counts AS (
        SELECT (SELECT count(*) FROM hive.silver.silver_transactions
                WHERE transaction_status = 'declined') silver_count,
          (SELECT coalesce(sum(declined_transaction_count), 0)
           FROM hive.gold.gold_declined_transactions) gold_count)
        SELECT CASE WHEN silver_count = gold_count THEN 0 ELSE 1 END violation_count FROM counts""",
    ),
    _count_rule(
        "gold.daily_metric_consistency",
        "gold",
        "consistency",
        "Gold daily attempts, rates, and nonnegative values are internally consistent.",
        """SELECT count(*) violation_count FROM hive.gold.gold_daily_transaction_metrics
        WHERE monetary_attempt_count <> successful_transaction_count + declined_transaction_count
           OR success_rate < 0 OR success_rate > 1 OR decline_rate < 0 OR decline_rate > 1
           OR total_deposit_amount < 0 OR total_withdrawal_amount < 0
           OR total_declined_amount < 0 OR average_transaction_value < 0""",
    ),
)


def execute_quality_rules(
    client: QueryClient, *, now: datetime | None = None
) -> tuple[QualityResult, ...]:
    checked_at = now or datetime.now().astimezone()
    results = []
    for rule in QUALITY_RULES:
        try:
            rows = client.query(rule.sql)
            if len(rows) != 1 or "violation_count" not in rows[0]:
                raise ValueError("query did not return one violation_count")
            violations = int(rows[0]["violation_count"])
            if violations < 0:
                raise ValueError("negative violation count")
            results.append(
                QualityResult(
                    rule, "passed" if violations == 0 else "failed", violations, checked_at
                )
            )
        except Exception:
            results.append(
                QualityResult(rule, "error", 0, checked_at, "Quality query could not be evaluated.")
            )
    return tuple(results)


def build_quality_run(
    results: tuple[QualityResult, ...],
    *,
    triggered_by: str = "manual",
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> QualityRun:
    start = started_at or datetime.now().astimezone()
    return QualityRun(
        uuid4(), start, completed_at or datetime.now().astimezone(), triggered_by, results
    )


def persist_quality_run(connection: Connection, run: QualityRun) -> None:
    connection.execute(
        text("""INSERT INTO bankflow_quality.quality_runs
        (run_id, started_at, completed_at, status, triggered_by, total_rules, passed_rules,
         failed_rules, error_rules, total_violations)
        VALUES (:run_id, :started_at, :completed_at, :status, :triggered_by, :total_rules,
                :passed_rules, :failed_rules, :error_rules, :total_violations)"""),
        {
            "run_id": run.run_id,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "status": run.status,
            "triggered_by": run.triggered_by,
            "total_rules": len(run.results),
            "passed_rules": run.passed_rules,
            "failed_rules": run.failed_rules,
            "error_rules": run.error_rules,
            "total_violations": run.total_violations,
        },
    )
    connection.execute(
        text("""INSERT INTO bankflow_quality.quality_results
        (run_id, rule_id, layer, category, description, status, violation_count, message, checked_at)
        VALUES (:run_id, :rule_id, :layer, :category, :description, :status,
                :violation_count, :message, :checked_at)"""),
        [
            {
                "run_id": run.run_id,
                "rule_id": result.rule.rule_id,
                "layer": result.rule.layer,
                "category": result.rule.category,
                "description": result.rule.description,
                "status": result.status,
                "violation_count": result.violation_count,
                "message": result.message,
                "checked_at": result.checked_at,
            }
            for result in run.results
        ],
    )


class QualityUnavailableError(RuntimeError):
    """The quality result store has not been initialized or cannot be read."""


def load_latest_quality_run(engine: Engine) -> QualityRun | None:
    try:
        with engine.connect() as connection:
            run_row = (
                connection.execute(
                    text("""SELECT * FROM bankflow_quality.quality_runs
                ORDER BY completed_at DESC, run_id DESC LIMIT 1""")
                )
                .mappings()
                .one_or_none()
            )
            if run_row is None:
                return None
            result_rows = (
                connection.execute(
                    text("""SELECT * FROM bankflow_quality.quality_results
                WHERE run_id = :run_id ORDER BY rule_id"""),
                    {"run_id": run_row["run_id"]},
                )
                .mappings()
                .all()
            )
    except (SQLAlchemyError, ValueError) as exc:
        raise QualityUnavailableError("BankFlow data-quality results are unavailable.") from exc
    results = tuple(
        QualityResult(
            QualityRule(row["rule_id"], row["layer"], row["category"], row["description"], ""),
            row["status"],
            int(row["violation_count"]),
            row["checked_at"],
            row["message"],
        )
        for row in result_rows
    )
    return QualityRun(
        UUID(str(run_row["run_id"])),
        run_row["started_at"],
        run_row["completed_at"],
        run_row["triggered_by"],
        results,
    )
