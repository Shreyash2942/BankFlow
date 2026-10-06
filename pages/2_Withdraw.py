"""Authenticated withdrawal form."""

from decimal import Decimal

import streamlit as st
from pydantic import ValidationError

from bankflow.models import AccountStatus, TransactionStatus
from bankflow.schemas.transaction import WithdrawalRequest
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
    st.session_state["bankflow_withdraw_amount"] = value


configure_page("Withdraw")
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
    "↘",
    "Withdraw funds",
    "Enter the amount you want to withdraw from your demo account.",
)

if summary.account_status is not AccountStatus.ACTIVE:
    st.warning(
        f"This account is {summary.account_status.value} and cannot accept a withdrawal. "
        "Reset the demo to continue."
    )
    st.stop()

main, details = st.columns([1.65, 0.85], gap="large", vertical_alignment="top")
with main:
    st.markdown("**Quick amount options**")
    quick_columns = st.columns(5)
    for column, value in zip(quick_columns, (20.0, 50.0, 100.0, 200.0, 500.0), strict=True):
        with column:
            st.button(
                f"${value:,.0f}",
                key=f"withdraw_quick_{int(value)}",
                on_click=choose_amount,
                args=(value,),
                width="stretch",
            )

    with st.form("withdrawal_form"):
        amount_value = st.number_input(
            "Withdrawal amount",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="bankflow_withdraw_amount",
            help="Enter an exact amount with no more than two decimal places.",
        )
        submitted = st.form_submit_button("Withdraw", type="primary", width="stretch")

    st.markdown(
        """
        <div class="notice-card info">
          <strong>ⓘ Transaction information</strong>
          <p>Withdrawals are processed immediately. Requests over the available balance
          are recorded as declined transactions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with details:
    render_balance_card(summary)
    st.markdown(
        """
        <div class="notice-card success">
          <strong>Secure demo withdrawal</strong>
          <p>Values are validated to the cent. Every request is recorded in transaction history.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if submitted:
    try:
        request = WithdrawalRequest(amount=Decimal(str(amount_value)))
        result = runtime.withdraw(authentication, request)
    except ValidationError:
        st.warning("Enter a withdrawal amount greater than $0.00 with no more than two decimals.")
    except Exception:
        show_action_error("The withdrawal could not be completed. Please try again.")
    else:
        st.session_state["bankflow_balance_inquired"] = False
        if result.status is TransactionStatus.COMPLETED:
            st.success(
                f"Withdrawal complete. Your new balance is {format_money(result.balance_after)}."
            )
            receipt, action = st.columns([2, 1])
            with receipt:
                st.caption(f"Digital receipt · Transaction ID: {result.transaction_id}")
            with action:
                st.page_link(
                    "pages/1_Dashboard.py",
                    label="Return to dashboard",
                    icon="🏠",
                    width="stretch",
                )
            if result.account_status is AccountStatus.CLOSED:
                st.warning("The demo account closed after reaching a zero balance.")
        else:
            st.warning(
                "Withdrawal declined because the amount exceeds the available balance. "
                f"Your balance remains {format_money(result.balance_after)}."
            )
            st.caption(f"Transaction ID: {result.transaction_id}")

st.page_link("pages/1_Dashboard.py", label="Back to dashboard", icon="↩️")
