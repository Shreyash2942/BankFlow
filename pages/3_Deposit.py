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
st.title("Deposit funds")
st.write("Choose a preset or enter an exact amount for the fictional demo account.")
render_balance_card(summary)

if summary.account_status is not AccountStatus.ACTIVE:
    st.warning(
        f"This account is {summary.account_status.value} and cannot accept a deposit. "
        "Reset the demo to continue."
    )
    st.stop()

st.markdown("**Quick amounts**")
quick_columns = st.columns(4)
for column, value in zip(quick_columns, (25.0, 50.0, 100.0, 250.0), strict=True):
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
    )
    submitted = st.form_submit_button("Deposit", type="primary", width="stretch")

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
        st.caption(f"Transaction ID: {result.transaction_id}")

st.page_link("pages/1_Dashboard.py", label="Back to dashboard", icon="↩️")
