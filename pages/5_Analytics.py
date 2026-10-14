"""Authenticated operational analytics backed by the Version 1 dbt marts."""

from datetime import date, timedelta

import streamlit as st

from bankflow.analytics import AnalyticsUnavailableError
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
    "Analytics dashboard",
    "Explore transaction volume, outcomes, and authentication activity from the dbt marts.",
)

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
        "The ATM remains available. Start the Kafka consumer and rebuild dbt to restore analytics."
    )
    st.stop()

overview = snapshot.overview
total, volume, success, declined = st.columns(4, gap="medium")
with total:
    render_metric_card(
        "Total transactions",
        f"{overview.total_transactions:,}",
        range_label,
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
        "Terminal declined transactions",
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
if not snapshot.has_activity:
    st.info(
        "No consumed events are represented in this date range yet. Complete a demo operation, "
        "run the consumer, and rebuild dbt to populate these charts."
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

st.caption(
    "Snapshot loaded "
    + snapshot.generated_at.strftime("%b %d, %Y %I:%M:%S %p %Z")
    + " · Source: bankflow_analytics dbt marts"
)
st.markdown(
    """
    <div class="notice-card info" style="margin-top: 1rem;">
      <strong>Data-driven banking</strong>
      <p>Metrics are generated from validated, deduplicated Kafka events persisted by the
      operational consumer. Dashboard freshness follows the latest successful dbt build.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
