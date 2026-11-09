"""Authenticated analytics backed by Iceberg Gold, PostgreSQL serving, and dbt."""

from datetime import date, timedelta

import streamlit as st

from bankflow.analytics import AnalyticsUnavailableError
from bankflow.quality import QualityUnavailableError
from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    format_money,
    load_runtime_or_stop,
    render_brand_header,
    render_metric_card,
    render_page_heading,
    render_sidebar,
    require_authentication,
    show_action_error,
)

configure_page("Analytics")
apply_design_system()
runtime = load_runtime_or_stop()
authentication = require_authentication(runtime)

try:
    account = runtime.account_summary(authentication)
except Exception:
    show_action_error("Your account could not be loaded. Please try again.")
    st.stop()

render_sidebar(runtime, account)
render_brand_header()
render_page_heading(
    "📊",
    "Lakehouse analytics",
    "Explore Gold transaction, account, hourly, and authentication metrics served through dbt.",
)

try:
    quality_run = runtime.latest_quality_run()
except QualityUnavailableError:
    quality_run = None

st.subheader("Data quality")
if quality_run is None:
    st.info(
        "No data-quality run is available yet. Run the Day 23 quality framework to publish indicators."
    )
else:
    quality_status, quality_checks, quality_violations, quality_time = st.columns(4, gap="medium")
    with quality_status:
        render_metric_card(
            "Latest status",
            quality_run.status.upper(),
            "Cross-layer validation",
            "Q",
            "positive" if quality_run.status == "passed" else "negative",
        )
    with quality_checks:
        render_metric_card(
            "Checks passed",
            f"{quality_run.passed_rules}/{len(quality_run.results)}",
            f"{quality_run.error_rules} query errors",
            "✓",
            "positive" if quality_run.status == "passed" else "",
        )
    with quality_violations:
        render_metric_card(
            "Violations",
            f"{quality_run.total_violations:,}",
            f"{quality_run.failed_rules} failed rules",
            "!",
            "negative" if quality_run.total_violations else "positive",
        )
    with quality_time:
        render_metric_card(
            "Last checked",
            quality_run.completed_at.strftime("%b %d"),
            quality_run.completed_at.strftime("%I:%M %p %Z"),
            "T",
        )

st.write("")

range_label = st.selectbox(
    "Date range",
    options=("Last 7 days", "Last 30 days", "Last 90 days", "All available data"),
    index=1,
)
days = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All available data": None,
}[range_label]
start_date = date.today() - timedelta(days=days - 1) if days is not None else None

try:
    snapshot = runtime.analytics_snapshot(start_date=start_date)
except AnalyticsUnavailableError as exc:
    st.warning(str(exc))
    st.info(
        "The ATM remains available. Load the Gold serving tables and rebuild dbt to restore analytics."
    )
    st.stop()

overview = snapshot.overview
total, volume, success, declined = st.columns(4, gap="medium")
with total:
    render_metric_card(
        "Monetary attempts",
        f"{overview.total_transactions:,}",
        f"{overview.transaction_events:,} lifecycle events",
        "▤",
    )
with volume:
    render_metric_card(
        "Completed volume",
        format_money(overview.completed_volume),
        "Successful withdrawals and deposits",
        "$",
        "positive",
    )
with success:
    render_metric_card(
        "Success rate",
        f"{overview.success_rate:.2f}%",
        f"{overview.successful_transactions:,} successful",
        "✓",
        "positive",
    )
with declined:
    render_metric_card(
        "Declined",
        f"{overview.declined_transactions:,}",
        f"{overview.decline_rate:.2f}% decline rate",
        "!",
        "negative",
    )

st.write("")
withdrawals, deposits, auth_failures, locked = st.columns(4, gap="medium")
with withdrawals:
    render_metric_card(
        "Withdrawals",
        format_money(overview.withdrawal_volume),
        f"{overview.withdrawal_count:,} requests",
        "↓",
        "negative",
    )
with deposits:
    render_metric_card(
        "Deposits",
        format_money(overview.deposit_volume),
        f"{overview.deposit_count:,} completed",
        "↑",
        "positive",
    )
with auth_failures:
    render_metric_card(
        "Authentication failures",
        f"{overview.authentication_failures:,}",
        "Known and unknown cards",
        "🔐",
        "negative",
    )
with locked:
    render_metric_card(
        "Locked cards",
        f"{overview.locked_cards:,}",
        "Card-lock events",
        "🔒",
        "negative" if overview.locked_cards else "",
    )

st.write("")
events, average, accounts, peak = st.columns(4, gap="medium")
with events:
    render_metric_card(
        "Lakehouse events",
        f"{overview.transaction_events:,}",
        "Validated transaction lifecycle events",
        "E",
    )
with average:
    render_metric_card(
        "Average transaction",
        format_money(overview.average_transaction_value),
        "Successful monetary outcomes",
        "A",
    )
with accounts:
    render_metric_card(
        "Active accounts",
        f"{overview.active_accounts:,}",
        "Distinct accounts in range",
        "#",
    )
with peak:
    render_metric_card(
        "Peak hourly events",
        f"{overview.peak_hourly_events:,}",
        "Highest Gold hourly volume",
        "H",
    )

st.write("")
if not snapshot.has_activity:
    st.info(
        "No Gold events are represented in this date range yet. Run the lakehouse pipeline, "
        "load PostgreSQL serving tables, and rebuild dbt to populate these charts."
    )
else:
    volume_chart, type_chart = st.columns([1.7, 1], gap="medium")
    with volume_chart:
        st.subheader("Transaction volume over time")
        st.caption("How transaction activity and outcomes change by day")
        daily_rows = [
            {
                "Date": metric.transaction_date,
                "Transactions": metric.transaction_count,
                "Successful": metric.successful_count,
                "Declined": metric.declined_count,
            }
            for metric in snapshot.daily_transactions
        ]
        st.line_chart(
            daily_rows,
            x="Date",
            y=("Transactions", "Successful", "Declined"),
            color=("#0B6CF2", "#059669", "#DC2626"),
            height=340,
        )
    with type_chart:
        st.subheader("Transactions by type")
        st.caption("Which operations occur most often")
        type_rows = [
            {
                "Type": metric.transaction_type.replace("_", " ").title(),
                "Transactions": metric.transaction_count,
            }
            for metric in snapshot.transaction_types
        ]
        st.bar_chart(
            type_rows,
            x="Type",
            y="Transactions",
            color="#0B6CF2",
            height=340,
        )

    if snapshot.hourly_volume:
        st.subheader("Hourly lakehouse volume")
        st.caption("Validated transaction lifecycle events by UTC hour")
        hourly_rows = [
            {
                "Hour": metric.event_hour,
                "Events": metric.transaction_events,
            }
            for metric in snapshot.hourly_volume
        ]
        st.line_chart(
            hourly_rows,
            x="Hour",
            y="Events",
            color="#7C3AED",
            height=280,
        )

freshness = (
    snapshot.serving_loaded_at.strftime("%b %d, %Y %I:%M:%S %p %Z")
    if snapshot.serving_loaded_at
    else "not available"
)
st.caption(
    "Dashboard snapshot "
    + snapshot.generated_at.strftime("%b %d, %Y %I:%M:%S %p %Z")
    + " · Serving load "
    + freshness
    + " · Source: Iceberg Gold → PostgreSQL serving → dbt"
)
st.markdown(
    """
    <div class="notice-card info" style="margin-top: 1rem;">
      <strong>Data-driven banking</strong>
      <p>Metrics flow from validated Kafka events through Iceberg Bronze, Silver, and Gold,
      then through an idempotent PostgreSQL serving load and tested dbt marts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
