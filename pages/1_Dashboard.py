"""Authenticated BankFlow account dashboard."""

import streamlit as st

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

configure_page("Dashboard")
apply_design_system()
runtime = load_runtime_or_stop()
authentication = require_authentication(runtime)

if not st.session_state.get("bankflow_balance_inquired", False):
    try:
        runtime.inquire_balance(authentication)
    except Exception:
        show_action_error("The balance inquiry could not be completed. Please try again.")
        st.stop()
    st.session_state["bankflow_balance_inquired"] = True

try:
    summary = runtime.account_summary(authentication)
    recent = runtime.history(authentication, limit=100)
except Exception:
    show_action_error("Your account dashboard could not be loaded. Please try again.")
    st.stop()

render_sidebar(runtime, summary)
render_brand_header()
render_flash_message()
render_page_heading(
    "☀",
    f"Welcome back, {summary.customer_name}",
    "Manage your account, make transactions, and track your recent activity.",
)

metrics = transaction_metrics(recent.items)
balance, deposits, withdrawals, transactions = st.columns(4, gap="medium")
with balance:
    render_metric_card(
        "Available balance",
        format_money(summary.balance, summary.currency),
        f"{summary.account_type.value.title()} •••• {summary.card_last_four}",
        "▰",
    )
with deposits:
    render_metric_card(
        "Total deposits",
        format_money(metrics.deposits, summary.currency),
        "Completed demo activity",
        "↑",
        "positive",
    )
with withdrawals:
    render_metric_card(
        "Total withdrawals",
        format_money(metrics.withdrawals, summary.currency),
        "Completed demo activity",
        "↓",
        "negative",
    )
with transactions:
    render_metric_card(
        "Transactions",
        str(metrics.total),
        f"{metrics.completed} completed · {metrics.declined} declined",
        "▤",
    )

st.subheader("Quick actions")
withdraw, deposit, history, refresh = st.columns(4, gap="medium")
with withdraw:
    st.page_link("pages/2_Withdraw.py", label="Withdraw funds", icon="↘️", width="stretch")
with deposit:
    st.page_link("pages/3_Deposit.py", label="Deposit funds", icon="↗️", width="stretch")
with history:
    st.page_link(
        "pages/4_Transaction_History.py",
        label="View history",
        icon="📋",
        width="stretch",
    )
with refresh:
    if st.button("Refresh balance", type="secondary", width="stretch"):
        try:
            runtime.inquire_balance(authentication)
        except Exception:
            show_action_error("The balance inquiry could not be refreshed. Please try again.")
        else:
            st.rerun()

st.subheader("Recent transactions")
render_transaction_table(recent.items[:6])
st.markdown(
    """
    <div class="notice-card info" style="margin-top: 1rem;">
      <strong>🛡 Your security matters</strong>
      <p>Keep the demo PIN private during a session. This environment uses fictional data
      for learning and portfolio demonstration.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
