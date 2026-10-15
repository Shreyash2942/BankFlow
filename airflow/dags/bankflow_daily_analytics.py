"""Daily orchestration for the BankFlow Version 1 analytics layer."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from textwrap import dedent
from typing import Any

from airflow.operators.bash import BashOperator

from airflow import DAG

DAG_ID = "bankflow_daily_analytics"
PROJECT_DIR = "/home/datalab/bankflow"


class BankFlowBashOperator(BashOperator):
    """Keep inline shell commands from being treated as template filenames."""

    template_ext: tuple[str, ...] = ()


def _script(command: str) -> str:
    return dedent(command).strip()


def _failure_callback(context: dict[str, Any]) -> None:
    """Record useful task identity without logging commands or credentials."""

    task_instance = context["task_instance"]
    exception = context.get("exception")
    task_instance.log.error(
        "BankFlow analytics task failed dag_id=%s task_id=%s run_id=%s "
        "try_number=%s exception_type=%s",
        task_instance.dag_id,
        task_instance.task_id,
        task_instance.run_id,
        task_instance.try_number,
        type(exception).__name__ if exception is not None else "unknown",
    )


DEFAULT_ARGS = {
    "owner": "bankflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10),
    "execution_timeout": timedelta(minutes=20),
    "on_failure_callback": _failure_callback,
}

LOAD_ENV = _script(
    f"""
    PROJECT_DIR="${{BANKFLOW_PROJECT_DIR:-{PROJECT_DIR}}}"
    ENV_FILE="${{BANKFLOW_ENV_FILE:-${{PROJECT_DIR}}/.env}}"
    DBT_PROJECT_DIR="${{BANKFLOW_DBT_PROJECT_DIR:-${{PROJECT_DIR}}/dbt}}"

    if [[ ! -r "${{ENV_FILE}}" ]]; then
      echo "BankFlow environment file is not readable: ${{ENV_FILE}}" >&2
      exit 1
    fi

    set -a
    source "${{ENV_FILE}}"
    set +a

    # The checked-in .env uses host-mapped ports. Airflow executes inside the
    # data-lab container, where PostgreSQL listens on its native port.
    export PGHOST="${{BANKFLOW_AIRFLOW_POSTGRES_HOST:-127.0.0.1}}"
    export PGPORT="${{BANKFLOW_AIRFLOW_POSTGRES_PORT:-5432}}"
    export PGDATABASE="${{POSTGRES_DB}}"
    export PGUSER="${{POSTGRES_USER}}"
    export PGPASSWORD="${{POSTGRES_PASSWORD}}"

    export BANKFLOW_DBT_HOST="${{PGHOST}}"
    export BANKFLOW_DBT_PORT="${{PGPORT}}"
    export BANKFLOW_DBT_DATABASE="${{PGDATABASE}}"
    export BANKFLOW_DBT_USER="${{PGUSER}}"
    export BANKFLOW_DBT_PASSWORD="${{PGPASSWORD}}"
    export BANKFLOW_DBT_SCHEMA="${{BANKFLOW_DBT_SCHEMA:-bankflow_analytics}}"
    export BANKFLOW_DBT_THREADS="${{BANKFLOW_DBT_THREADS:-2}}"
    """
)


def _bash_task(task_id: str, command: str) -> BankFlowBashOperator:
    return BankFlowBashOperator(
        task_id=task_id,
        bash_command=_script(
            f"""
            set -euo pipefail
            {LOAD_ENV}
            {command}
            """
        ),
        do_xcom_push=False,
    )


with DAG(
    dag_id=DAG_ID,
    description="Validate event freshness and rebuild BankFlow V1 dbt analytics.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=45),
    tags=["bankflow", "analytics", "dbt", "v1"],
) as dag:
    postgresql_health = _bash_task(
        "postgresql_health",
        """
        psql --no-psqlrc --set ON_ERROR_STOP=1 --tuples-only --no-align \
          --command "select 1" | grep -qx "1"

        psql --no-psqlrc --set ON_ERROR_STOP=1 --tuples-only --no-align \
          --command "select to_regclass('bankflow.consumed_events') is not null" \
          | grep -qx "t"
        echo "PostgreSQL and bankflow.consumed_events are available."
        """,
    )

    event_freshness = _bash_task(
        "event_freshness",
        """
        FRESHNESS_HOURS="${BANKFLOW_EVENT_FRESHNESS_HOURS:-48}"
        if [[ ! "${FRESHNESS_HOURS}" =~ ^[1-9][0-9]*$ ]]; then
          echo "BANKFLOW_EVENT_FRESHNESS_HOURS must be a positive integer." >&2
          exit 1
        fi

        freshness="$({
          psql --no-psqlrc --set ON_ERROR_STOP=1 --tuples-only --no-align \
            --command "
              select case
                when max(consumed_at) is null then 'empty'
                when max(consumed_at) >= now() - (${FRESHNESS_HOURS} * interval '1 hour')
                  then 'fresh'
                else 'stale'
              end || '|' || coalesce(max(consumed_at)::text, '')
              from bankflow.consumed_events
            "
        } | tr -d '[:space:]')"

        IFS='|' read -r status newest_event <<< "${freshness}"
        case "${status}" in
          fresh)
            echo "Newest consumed event is within ${FRESHNESS_HOURS} hours: ${newest_event}"
            ;;
          empty)
            echo "No consumed events exist yet; freshness is not applicable."
            ;;
          stale)
            echo "Newest consumed event is stale: ${newest_event}" >&2
            exit 1
            ;;
          *)
            echo "Unexpected freshness result." >&2
            exit 1
            ;;
        esac
        """,
    )

    run_dbt_staging = _bash_task(
        "run_dbt_staging",
        """
        dbt run \
          --project-dir "${DBT_PROJECT_DIR}" \
          --profiles-dir "${DBT_PROJECT_DIR}" \
          --select tag:staging
        """,
    )

    run_dbt_marts = _bash_task(
        "run_dbt_marts",
        """
        dbt run \
          --project-dir "${DBT_PROJECT_DIR}" \
          --profiles-dir "${DBT_PROJECT_DIR}" \
          --select tag:intermediate tag:marts
        """,
    )

    run_dbt_tests = _bash_task(
        "run_dbt_tests",
        """
        dbt test \
          --project-dir "${DBT_PROJECT_DIR}" \
          --profiles-dir "${DBT_PROJECT_DIR}"

        dbt docs generate \
          --project-dir "${DBT_PROJECT_DIR}" \
          --profiles-dir "${DBT_PROJECT_DIR}"
        """,
    )

    (postgresql_health >> event_freshness >> run_dbt_staging >> run_dbt_marts >> run_dbt_tests)
