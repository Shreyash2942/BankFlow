"""Day 23 cross-layer data-quality framework coverage."""

from datetime import UTC, datetime

from bankflow.quality import (
    QUALITY_RULES,
    QualityResult,
    build_quality_run,
    execute_quality_rules,
    persist_quality_run,
)


class StubClient:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response
        return [{"violation_count": 0}]


class RecordingConnection:
    def __init__(self):
        self.calls = []

    def execute(self, statement, parameters=None):
        self.calls.append((str(statement), parameters))


def test_rule_registry_covers_day_23_layers_and_rule_categories():
    ids = [rule.rule_id for rule in QUALITY_RULES]

    assert len(ids) == len(set(ids))
    assert {rule.layer for rule in QUALITY_RULES} >= {
        "bronze",
        "silver",
        "gold",
        "cross_layer",
    }
    assert {rule.category for rule in QUALITY_RULES} >= {
        "null",
        "duplicate",
        "domain",
        "range",
        "consistency",
        "reconciliation",
    }
    assert any("bronze_to_silver" in rule_id for rule_id in ids)
    assert sum("silver_to_gold" in rule_id for rule_id in ids) >= 4


def test_all_rules_pass_when_queries_report_no_violations():
    checked_at = datetime(2026, 11, 9, 12, tzinfo=UTC)
    client = StubClient()

    results = execute_quality_rules(client, now=checked_at)
    run = build_quality_run(
        results,
        triggered_by="pytest",
        started_at=checked_at,
        completed_at=checked_at,
    )

    assert len(client.queries) == len(QUALITY_RULES)
    assert run.status == "passed"
    assert run.passed_rules == len(QUALITY_RULES)
    assert run.failed_rules == 0
    assert run.error_rules == 0
    assert run.total_violations == 0


def test_rule_failures_and_query_errors_are_isolated_and_safely_reported():
    responses = [
        [{"violation_count": 3}],
        RuntimeError("sensitive backend detail"),
        *([[{"violation_count": 0}]] * (len(QUALITY_RULES) - 2)),
    ]

    results = execute_quality_rules(StubClient(responses))
    run = build_quality_run(results)

    assert results[0].status == "failed"
    assert results[0].violation_count == 3
    assert results[1].status == "error"
    assert results[1].message == "Quality query could not be evaluated."
    assert "sensitive" not in results[1].message
    assert run.status == "error"
    assert run.failed_rules == 1
    assert run.error_rules == 1
    assert run.total_violations == 3


def test_quality_run_persistence_writes_summary_and_each_rule_result():
    checked_at = datetime(2026, 11, 9, 12, tzinfo=UTC)
    rule = QUALITY_RULES[0]
    run = build_quality_run(
        (QualityResult(rule, "failed", 2, checked_at),),
        triggered_by="airflow",
        started_at=checked_at,
        completed_at=checked_at,
    )
    connection = RecordingConnection()

    persist_quality_run(connection, run)

    assert len(connection.calls) == 2
    summary_sql, summary = connection.calls[0]
    results_sql, results = connection.calls[1]
    assert "bankflow_quality.quality_runs" in summary_sql
    assert summary["status"] == "failed"
    assert summary["total_violations"] == 2
    assert "bankflow_quality.quality_results" in results_sql
    assert results[0]["rule_id"] == rule.rule_id
    assert results[0]["violation_count"] == 2
