"""Public, failure-tolerant health view for the BankFlow Version 1 platform."""

import os
from pathlib import Path

import streamlit as st

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.monitoring import HealthState, PlatformSnapshot, collect_platform_snapshot
from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    render_brand_header,
    render_metric_card,
    render_page_heading,
    render_platform_sidebar,
    render_status_card,
)

ROOT = Path(__file__).resolve().parents[1]


@st.cache_data(ttl=15, show_spinner=False)
def _platform_snapshot(env_file: str) -> PlatformSnapshot:
    settings = load_settings(env_file)
    return collect_platform_snapshot(settings, project_root=ROOT)


configure_page("Platform Status")
apply_design_system()
render_platform_sidebar()
render_brand_header()
render_page_heading(
    "⚙",
    "Platform status",
    "Live, bounded health checks for BankFlow services and analytics build artifacts.",
)

refresh, timestamp = st.columns([1, 5], vertical_alignment="center")
with refresh:
    if st.button("Refresh status", type="primary", width="stretch"):
        _platform_snapshot.clear()
        st.rerun()

env_file = os.environ.get("BANKFLOW_ENV_FILE", ".env")
try:
    with st.spinner("Checking platform services..."):
        snapshot = _platform_snapshot(env_file)
except ConfigurationError as exc:
    st.error(str(exc))
    st.stop()
except Exception:
    st.error("Platform status could not be collected. Check the local configuration and retry.")
    st.stop()

with timestamp:
    st.caption("Last checked " + snapshot.checked_at.strftime("%b %d, %Y %I:%M:%S %p %Z"))

overall_label = (
    "All monitored systems healthy"
    if snapshot.overall_state is HealthState.HEALTHY
    else "Some monitored systems need attention"
)
if snapshot.overall_state is HealthState.HEALTHY:
    st.success(overall_label)
else:
    st.warning(overall_label)

service_columns = st.columns(5, gap="medium")
for column, service in zip(service_columns[:4], snapshot.services, strict=True):
    with column:
        render_status_card(
            service.name,
            service.state.value,
            service.detail,
            latency_ms=service.latency_ms,
        )
with service_columns[4]:
    render_status_card("dbt", snapshot.dbt.state.value, snapshot.dbt.detail)

st.write("")
healthy, models, tests, results = st.columns(4, gap="medium")
with healthy:
    render_metric_card(
        "Healthy checks",
        f"{snapshot.healthy_count}/5",
        "PostgreSQL · Redis · Kafka · Airflow · dbt",
        "✓",
        "positive" if snapshot.healthy_count == 5 else "",
    )
with models:
    render_metric_card(
        "Analytics models",
        str(snapshot.dbt.model_count),
        "Staging, intermediate, and marts",
        "▤",
    )
with tests:
    render_metric_card(
        "dbt tests",
        str(snapshot.dbt.test_count),
        "Source, schema, and reconciliation checks",
        "✓",
        "positive" if snapshot.dbt.test_count else "",
    )
with results:
    render_metric_card(
        "Last build results",
        str(snapshot.dbt.result_count),
        snapshot.dbt.state.value.title(),
        "↻",
        "positive" if snapshot.dbt.state is HealthState.HEALTHY else "",
    )

st.write("")
airflow_column, dbt_column = st.columns(2, gap="medium")
airflow_health = next(service for service in snapshot.services if service.key == "airflow")
with airflow_column:
    st.subheader("Airflow orchestration")
    render_status_card(
        "bankflow_daily_analytics",
        airflow_health.state.value if snapshot.analytics_dag_present else HealthState.PENDING.value,
        (
            "DAG file installed; " + airflow_health.detail.casefold()
            if snapshot.analytics_dag_present
            else "Day 12 analytics DAG has not been implemented yet"
        ),
        latency_ms=airflow_health.latency_ms,
    )
with dbt_column:
    st.subheader("dbt analytics build")
    generated = (
        snapshot.dbt.generated_at.strftime("%b %d, %Y %I:%M:%S %p UTC")
        if snapshot.dbt.generated_at
        else "No completed build timestamp"
    )
    render_status_card(
        "BankFlow dbt",
        snapshot.dbt.state.value,
        f"{snapshot.dbt.detail} · {generated}",
    )

st.markdown(
    """
    <div class="notice-card info" style="margin-top: 1rem;">
      <strong>Operational boundary</strong>
      <p>Health checks are read-only and time-bounded. This page remains reachable without an
      ATM session so service failures can still be diagnosed. It never displays credentials or
      raw driver errors.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
