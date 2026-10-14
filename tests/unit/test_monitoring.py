import json
from datetime import UTC, datetime
from types import SimpleNamespace

from bankflow.config.settings import Settings
from bankflow.monitoring import (
    DbtBuildHealth,
    HealthState,
    PlatformSnapshot,
    ServiceHealth,
    check_airflow,
    check_kafka,
    read_dbt_build_health,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _settings() -> Settings:
    return Settings(_env_file=None, postgres_password="fixture-secret")


def test_airflow_health_requires_database_and_scheduler_health():
    healthy = check_airflow(
        _settings(),
        opener=lambda *args, **kwargs: FakeResponse(
            {"metadatabase": {"status": "healthy"}, "scheduler": {"status": "healthy"}}
        ),
    )
    degraded = check_airflow(
        _settings(),
        opener=lambda *args, **kwargs: FakeResponse(
            {"metadatabase": {"status": "healthy"}, "scheduler": {"status": "unhealthy"}}
        ),
    )

    assert healthy.state is HealthState.HEALTHY
    assert degraded.state is HealthState.DEGRADED


def test_kafka_health_reports_reachable_broker_count():
    class FakeAdmin:
        def list_topics(self, *, timeout):
            assert timeout == 2
            return SimpleNamespace(brokers={1: object(), 2: object()})

    health = check_kafka(_settings(), admin_factory=lambda config: FakeAdmin())

    assert health.state is HealthState.HEALTHY
    assert health.detail == "2 brokers reachable"


def test_dbt_health_summarizes_successful_artifacts(tmp_path):
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "nodes": {
                    "model.one": {"resource_type": "model"},
                    "model.two": {"resource_type": "model"},
                    "test.one": {"resource_type": "test"},
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "run_results.json").write_text(
        json.dumps(
            {
                "metadata": {"generated_at": "2026-10-14T14:30:00Z"},
                "results": [{"status": "success"}, {"status": "pass"}],
            }
        ),
        encoding="utf-8",
    )

    health = read_dbt_build_health(tmp_path)

    assert health.state is HealthState.HEALTHY
    assert (health.model_count, health.test_count, health.result_count) == (2, 1, 2)
    assert health.generated_at is not None
    assert health.generated_at.tzinfo is UTC


def test_dbt_health_is_pending_before_artifacts_exist(tmp_path):
    health = read_dbt_build_health(tmp_path)
    assert health.state is HealthState.PENDING
    assert "Generate dbt artifacts" in health.detail


def test_missing_analytics_dag_keeps_platform_summary_honestly_degraded():
    snapshot = PlatformSnapshot(
        services=(ServiceHealth("postgresql", "PostgreSQL", HealthState.HEALTHY, "Connected"),),
        dbt=DbtBuildHealth(HealthState.HEALTHY, "73 build results passed"),
        analytics_dag_present=False,
        checked_at=datetime.now(UTC),
    )

    assert snapshot.overall_state is HealthState.DEGRADED
