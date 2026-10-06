"""Authenticated transaction-history page."""

import streamlit as st

from bankflow.models import TransactionStatus, TransactionType
from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    format_money,
    load_runtime_or_stop,
    render_brand_header,
    render_flash_message,
    render_metric_card,
    render_page_heading,
    render_sidebar,
    render_transaction_table,
    require_authentication,
    show_action_error,
    transaction_metrics,
)

configure_page("Transaction History")
apply_design_system()
runtime = load_runtime_or_stop()
authentication = require_authentication(runtime)
try:
    summary = runtime.account_summary(authentication)
except Exception:
    show_action_error("Your account could not be loaded. Please try again.")
    st.stop()

render_sidebar(runtime, summary)
render_brand_header()
render_flash_message()
render_page_heading(
    "▤",
    "Transaction history",
    "View, search, and filter your demo transaction records.",
)

limit = st.selectbox("Rows to load", options=(25, 50, 100), index=0)
try:
    history = runtime.history(authentication, limit=limit)
except Exception:
    show_action_error("Transaction history could not be loaded. Please try again.")
    st.stop()

metrics = transaction_metrics(history.items)
total, deposits, withdrawals, success = st.columns(4, gap="medium")
with total:
    render_metric_card("Total transactions", str(metrics.total), "Loaded account activity", "▤")
with deposits:
    render_metric_card(
        "Total deposits", format_money(metrics.deposits), "Completed deposits", "↑", "positive"
    )
with withdrawals:
    render_metric_card(
        "Total withdrawals",
        format_money(metrics.withdrawals),
        "Completed withdrawals",
        "↓",
        "negative",
    )
with success:
    success_rate = 0 if metrics.total == 0 else metrics.completed / metrics.total * 100
    render_metric_card(
        "Success rate",
        f"{success_rate:.1f}%",
        f"{metrics.completed} of {metrics.total} completed",
        "✓",
        "positive",
    )

search, type_filter, status_filter = st.columns([2, 1, 1], gap="medium")
with search:
    query = (
        st.text_input(
            "Search transactions",
            placeholder="Transaction ID or amount",
        )
        .strip()
        .casefold()
    )
with type_filter:
    selected_type = st.selectbox(
        "Transaction type",
        options=("All types", "Balance inquiry", "Withdrawal", "Deposit"),
    )
with status_filter:
    selected_status = st.selectbox(
        "Status",
        options=("All statuses", "Completed", "Declined", "Failed", "Pending"),
    )

filtered = history.items
if selected_type != "All types":
    transaction_type = TransactionType(selected_type.casefold().replace(" ", "_"))
    filtered = tuple(item for item in filtered if item.transaction_type is transaction_type)
if selected_status != "All statuses":
    transaction_status = TransactionStatus(selected_status.casefold())
    filtered = tuple(item for item in filtered if item.status is transaction_status)
if query:
    filtered = tuple(
        item
        for item in filtered
        if query in str(item.transaction_id).casefold()
        or query in str(item.amount).casefold()
        or query in item.transaction_type.value.casefold()
    )

st.caption(f"Showing {len(filtered)} of {metrics.total} loaded transactions")
render_transaction_table(filtered)
st.markdown(
    """
    <div class="notice-card info" style="margin-top: 1rem;">
      <strong>ⓘ Observable by design</strong>
      <p>Every balance inquiry, withdrawal, deposit, and decline is recorded for this
      fictional account and will feed Phase 2 operational analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.page_link("pages/1_Dashboard.py", label="Back to dashboard", icon="↩️")
