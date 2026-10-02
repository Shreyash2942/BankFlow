"""Authenticated transaction-history page."""

import streamlit as st

from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    load_runtime_or_stop,
    render_brand_header,
    render_flash_message,
    render_sidebar,
    render_transaction_table,
    require_authentication,
    show_action_error,
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
st.title("Transaction history")
st.write("Review the most recent balance inquiries, withdrawals, deposits, and declines.")

limit = st.selectbox("Rows to display", options=(25, 50, 100), index=0)
try:
    history = runtime.history(authentication, limit=limit)
except Exception:
    show_action_error("Transaction history could not be loaded. Please try again.")
else:
    render_transaction_table(history.items)

st.page_link("pages/1_Dashboard.py", label="Back to dashboard", icon="↩️")
