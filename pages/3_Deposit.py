"""Authenticated deposit form."""

from decimal import Decimal

import streamlit as st
from pydantic import ValidationError

from bankflow.models import AccountStatus
from bankflow.schemas.transaction import DepositRequest
from bankflow.ui.streamlit_support import (
    apply_design_system,
    configure_page,
    format_money,
    load_runtime_or_stop,
    render_balance_card,
    render_brand_header,
    render_flash_message,
    render_page_heading,
    render_sidebar,
    require_authentication,
    show_action_error,
)


def choose_amount(value: float) -> None:
    st.session_state["bankflow_deposit_amount"] = value


configure_page("Deposit")
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
    "↗",
    "Deposit funds",
    "Add funds to your demo account quickly and securely.",
)

if summary.account_status is not AccountStatus.ACTIVE:
    st.warning(
        f"This account is {summary.account_status.value} and cannot accept a deposit. "
        "Reset the demo to continue."
    )
    st.stop()

main, details = st.columns([1.65, 0.85], gap="large", vertical_alignment="top")
with main:
    st.markdown("**Quick amount options**")
    quick_columns = st.columns(5)
    for column, value in zip(quick_columns, (50.0, 100.0, 200.0, 500.0, 1000.0), strict=True):
        with column:
            st.button(
                f"${value:,.0f}",
                key=f"deposit_quick_{int(value)}",
                on_click=choose_amount,
                args=(value,),
                width="stretch",
            )

    with st.form("deposit_form"):
        amount_value = st.number_input(
            "Deposit amount",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="bankflow_deposit_amount",
            help="Enter an exact amount with no more than two decimal places.",
        )
        submitted = st.form_submit_button("Deposit", type="primary", width="stretch")

    st.markdown(
        """
        <div class="notice-card info">
          <strong>ⓘ No daily demo deposit limit</strong>
          <p>Your deposit is available immediately and reflected in the account balance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with details:
    render_balance_card(summary)
    st.markdown(
        """
        <div class="notice-card success">
          <strong>Deposit information</strong>
          <p>Funds are processed in real time and every completed transaction is recorded.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if submitted:
    try:
        request = DepositRequest(amount=Decimal(str(amount_value)))
        result = runtime.deposit(authentication, request)
    except ValidationError:
        st.warning("Enter a deposit amount greater than $0.00 with no more than two decimals.")
    except Exception:
        show_action_error("The deposit could not be completed. Please try again.")
    else:
        st.session_state["bankflow_balance_inquired"] = False
        st.success(f"Deposit complete. Your new balance is {format_money(result.balance_after)}.")
        receipt, action = st.columns([2, 1])
        with receipt:
            st.caption(f"Digital receipt · Transaction ID: {result.transaction_id}")
        with action:
            st.page_link(
                "pages/4_Transaction_History.py",
                label="View transaction",
                icon="📋",
                width="stretch",
            )

st.page_link("pages/1_Dashboard.py", label="Back to dashboard", icon="↩️")
