"""Service-free contract checks for the checked-in Airflow analytics DAG."""

import ast
from pathlib import Path

DAG_PATH = Path("airflow/dags/bankflow_daily_analytics.py")


def test_airflow_dag_is_valid_python_with_expected_release_contract():
    source = DAG_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(DAG_PATH))

    assert compile(tree, str(DAG_PATH), "exec")
    assert 'DAG_ID = "bankflow_daily_analytics"' in source
    assert 'schedule="0 2 * * *"' in source
    assert "catchup=False" in source
    assert "max_active_runs=1" in source

    for task_id in (
        "postgresql_health",
        "event_freshness",
        "run_dbt_staging",
        "run_dbt_marts",
        "run_dbt_tests",
    ):
        assert f'"{task_id}"' in source

    assert (
        "postgresql_health >> event_freshness >> run_dbt_staging >> run_dbt_marts >> run_dbt_tests"
    ) in source
    assert "dbt test" in source
    assert "dbt docs generate" in source
