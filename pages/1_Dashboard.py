"""Authenticated BankFlow account dashboard."""

import streamlit as st

from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    load_runtime_or_stop,
    render_balance_card,
    render_brand_header,
    render_flash_message,
    render_sidebar,
    render_transaction_table,
    require_authentication,
    show_action_error,
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
except Exception:
    show_action_error("Your account could not be loaded. Please try again.")
    st.stop()

render_sidebar(runtime, summary)
render_brand_header()
render_flash_message()
st.title("Account dashboard")
st.write(f"Welcome, {summary.customer_name}. Your current demo account status is shown below.")
render_balance_card(summary)

if st.button("Refresh balance", type="secondary"):
    try:
        runtime.inquire_balance(authentication)
    except Exception:
        show_action_error("The balance inquiry could not be refreshed. Please try again.")
    else:
        st.rerun()

withdraw, deposit, history = st.columns(3, gap="medium")
with withdraw:
    st.page_link("pages/2_Withdraw.py", label="Withdraw funds", icon="💸", width="stretch")
with deposit:
    st.page_link("pages/3_Deposit.py", label="Deposit funds", icon="💰", width="stretch")
with history:
    st.page_link(
        "pages/4_Transaction_History.py",
        label="View history",
        icon="📋",
        width="stretch",
    )

st.subheader("Recent transactions")
try:
    recent = runtime.history(authentication, limit=5)
except Exception:
    show_action_error("Recent transactions could not be loaded. Please try again.")
else:
    render_transaction_table(recent.items)
