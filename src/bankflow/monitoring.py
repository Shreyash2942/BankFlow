"""Bounded, secret-free service and analytics-build health probes."""

import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from confluent_kafka.admin import AdminClient
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from bankflow.cache import create_redis_client
from bankflow.config.settings import Settings
from bankflow.database.connection import create_database_engine


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"


@dataclass(frozen=True)
class ServiceHealth:
    key: str
    name: str
    state: HealthState
    detail: str
    latency_ms: int | None = None


@dataclass(frozen=True)
class DbtBuildHealth:
    state: HealthState
    detail: str
    model_count: int = 0
    test_count: int = 0
    result_count: int = 0
    generated_at: datetime | None = None


@dataclass(frozen=True)
class PlatformSnapshot:
    services: tuple[ServiceHealth, ...]
    dbt: DbtBuildHealth
    analytics_dag_present: bool
    checked_at: datetime

    @property
    def healthy_count(self) -> int:
        return sum(service.state is HealthState.HEALTHY for service in self.services) + int(
            self.dbt.state is HealthState.HEALTHY
        )

    @property
    def overall_state(self) -> HealthState:
        if not self.analytics_dag_present:
            return HealthState.DEGRADED
        states = {service.state for service in self.services} | {self.dbt.state}
        if HealthState.UNAVAILABLE in states:
            return HealthState.DEGRADED
        if HealthState.DEGRADED in states or HealthState.PENDING in states:
            return HealthState.DEGRADED
        return HealthState.HEALTHY


class _UrlResponse(Protocol):
    def __enter__(self): ...

    def __exit__(self, *args): ...

    def read(self) -> bytes: ...


def _timed(probe: Callable[[], None]) -> int:
    started = perf_counter()
    probe()
    return max(0, round((perf_counter() - started) * 1000))


def check_postgresql(engine: Engine) -> ServiceHealth:
    def probe() -> None:
        with engine.connect() as connection:
            if connection.execute(text("select 1")).scalar_one() != 1:
                raise OSError("PostgreSQL health probe returned an unexpected value.")

    try:
        latency = _timed(probe)
    except SQLAlchemyError, OSError:
        return ServiceHealth(
            "postgresql", "PostgreSQL", HealthState.UNAVAILABLE, "Connection failed"
        )
    finally:
        engine.dispose()
    return ServiceHealth("postgresql", "PostgreSQL", HealthState.HEALTHY, "Connected", latency)


def check_redis(client: Redis) -> ServiceHealth:
    try:
        latency = _timed(lambda: client.ping())
    except RedisError, OSError:
        return ServiceHealth("redis", "Redis", HealthState.UNAVAILABLE, "Connection failed")
    finally:
        client.close()
    return ServiceHealth("redis", "Redis", HealthState.HEALTHY, "Connected", latency)


def check_kafka(
    settings: Settings,
    *,
    admin_factory: Callable[[dict[str, object]], object] = AdminClient,
) -> ServiceHealth:
    try:
        client = admin_factory(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "client.id": f"{settings.kafka_client_id}-health",
                "socket.timeout.ms": settings.platform_health_timeout_seconds * 1000,
            }
        )
        started = perf_counter()
        metadata = client.list_topics(timeout=settings.platform_health_timeout_seconds)
        latency = max(0, round((perf_counter() - started) * 1000))
        broker_count = len(metadata.brokers)
        if broker_count:
            return ServiceHealth(
                "kafka",
                "Kafka",
                HealthState.HEALTHY,
                f"{broker_count} broker{'s' if broker_count != 1 else ''} reachable",
                latency,
            )
    except Exception:
        pass
    return ServiceHealth("kafka", "Kafka", HealthState.UNAVAILABLE, "Broker unavailable")


def check_airflow(
    settings: Settings,
    *,
    opener: Callable[..., _UrlResponse] = urlopen,
) -> ServiceHealth:
    health_url = settings.airflow_base_url.rstrip("/") + "/health"
    try:
        started = perf_counter()
        with opener(health_url, timeout=settings.platform_health_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        latency = max(0, round((perf_counter() - started) * 1000))
        metadata_healthy = payload.get("metadatabase", {}).get("status") == "healthy"
        scheduler_healthy = payload.get("scheduler", {}).get("status") == "healthy"
        if metadata_healthy and scheduler_healthy:
            return ServiceHealth(
                "airflow", "Airflow", HealthState.HEALTHY, "Scheduler healthy", latency
            )
        if metadata_healthy:
            return ServiceHealth(
                "airflow", "Airflow", HealthState.DEGRADED, "Scheduler heartbeat is stale", latency
            )
    except HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError:
        pass
    return ServiceHealth("airflow", "Airflow", HealthState.UNAVAILABLE, "Health API unavailable")


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def read_dbt_build_health(artifact_directory: Path) -> DbtBuildHealth:
    manifest_path = artifact_directory / "manifest.json"
    results_path = artifact_directory / "run_results.json"
    if not manifest_path.is_file() or not results_path.is_file():
        return DbtBuildHealth(
            HealthState.PENDING,
            "Generate dbt artifacts with dbt build and dbt docs generate",
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        run_results = json.loads(results_path.read_text(encoding="utf-8"))
        nodes = tuple(manifest.get("nodes", {}).values())
        model_count = sum(node.get("resource_type") == "model" for node in nodes)
        test_count = sum(node.get("resource_type") == "test" for node in nodes)
        results = tuple(run_results.get("results", ()))
        statuses = tuple(str(result.get("status", "")).casefold() for result in results)
        accepted = {"pass", "success", "skipped", "warn"}
        failed = sum(status not in accepted for status in statuses)
        warned = statuses.count("warn")
    except OSError, ValueError, TypeError, AttributeError:
        return DbtBuildHealth(HealthState.DEGRADED, "dbt artifacts could not be read")
    state = HealthState.HEALTHY if not failed and not warned else HealthState.DEGRADED
    if failed:
        detail = f"{failed} of {len(results)} build results failed"
    elif warned:
        detail = f"{warned} of {len(results)} build results warned"
    else:
        detail = f"{len(results)} build results passed"
    return DbtBuildHealth(
        state,
        detail,
        model_count=model_count,
        test_count=test_count,
        result_count=len(results),
        generated_at=_parse_utc(run_results.get("metadata", {}).get("generated_at")),
    )


def collect_platform_snapshot(
    settings: Settings,
    *,
    project_root: Path,
) -> PlatformSnapshot:
    """Run independent network probes concurrently within one bounded UI refresh."""

    engine = create_database_engine(settings)
    redis_client = create_redis_client(settings)
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="bankflow-health") as executor:
        futures = (
            executor.submit(check_postgresql, engine),
            executor.submit(check_redis, redis_client),
            executor.submit(check_kafka, settings),
            executor.submit(check_airflow, settings),
        )
        services = tuple(future.result() for future in futures)
    return PlatformSnapshot(
        services=services,
        dbt=read_dbt_build_health(project_root / settings.dbt_artifact_directory),
        analytics_dag_present=(
            project_root / "airflow" / "dags" / "bankflow_daily_analytics.py"
        ).is_file(),
        checked_at=datetime.now().astimezone(),
    )
