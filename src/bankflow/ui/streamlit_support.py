"""Shared presentation helpers for the BankFlow Streamlit application."""

import logging
import os
from datetime import UTC
from decimal import Decimal

import streamlit as st

from bankflow.schemas.authentication import AuthenticationSession
from bankflow.schemas.transaction import TransactionHistoryItem
from bankflow.ui.runtime import AccountSummary, BankFlowRuntime

LOGGER = logging.getLogger(__name__)
SESSION_TOKEN_KEY = "bankflow_session_token"
FLASH_KEY = "bankflow_flash"


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} | BankFlow",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_design_system() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem;}
        [data-testid="stSidebar"] {border-right: 1px solid #E2E8F0;}
        .bankflow-header {display: flex; align-items: center; justify-content: space-between;
            gap: 1rem; margin-bottom: 2rem;}
        .bankflow-brand {font-size: 1.45rem; font-weight: 750; color: #0F172A;}
        .bankflow-tagline {color: #64748B; font-size: .9rem; margin-top: .1rem;}
        .demo-badge {display: inline-block; padding: .3rem .65rem; border-radius: 999px;
            color: #475569; background: #F1F5F9; border: 1px solid #CBD5E1;
            font-size: .72rem; font-weight: 700; letter-spacing: .06em; white-space: nowrap;}
        .balance-card {background: #FFFFFF; border: 1px solid #E2E8F0;
            border-radius: 14px; padding: 1.5rem 1.75rem; margin: 1rem 0 1.5rem;}
        .balance-label {color: #64748B; font-size: .86rem; font-weight: 650;
            text-transform: uppercase; letter-spacing: .04em;}
        .balance-value {color: #0F172A; font-size: 2.25rem; line-height: 1.25;
            font-weight: 750; margin: .35rem 0;}
        .balance-meta {color: #475569; font-size: .9rem;}
        .notice-card {background: #FFFFFF; border: 1px solid #E2E8F0;
            border-radius: 14px; padding: 1.25rem 1.4rem;}
        div[data-testid="stForm"] {background: #FFFFFF; border: 1px solid #E2E8F0;
            border-radius: 14px; padding: 1.2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def _cached_runtime(env_file: str) -> BankFlowRuntime:
    return BankFlowRuntime.from_env(env_file)


def load_runtime_or_stop() -> BankFlowRuntime:
    env_file = os.environ.get("BANKFLOW_ENV_FILE", ".env")
    try:
        return _cached_runtime(env_file)
    except Exception:
        LOGGER.exception("BankFlow runtime initialization failed")
        st.error(
            "BankFlow could not connect to its demo services. Start PostgreSQL and Redis, "
            "then reload this page."
        )
        st.stop()


def render_brand_header() -> None:
    st.markdown(
        """
        <div class="bankflow-header">
          <div>
            <div class="bankflow-brand">🏦 BankFlow</div>
            <div class="bankflow-tagline">Event-Driven ATM Platform</div>
          </div>
          <span class="demo-badge">DEMO MODE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_money(amount: Decimal, currency: str = "USD") -> str:
    symbol = "$" if currency == "USD" else f"{currency} "
    return f"{symbol}{amount:,.2f}"


def clear_ui_session() -> None:
    for key in list(st.session_state):
        if str(key).startswith("bankflow_"):
            del st.session_state[key]


def active_authentication(runtime: BankFlowRuntime) -> AuthenticationSession | None:
    token = st.session_state.get(SESSION_TOKEN_KEY)
    if not token:
        return None
    try:
        authentication = runtime.resolve_session(token)
    except Exception:
        LOGGER.exception("Authentication-session lookup failed")
        st.error("The session service is temporarily unavailable. Please reload and try again.")
        st.stop()
    if authentication is None:
        clear_ui_session()
    return authentication


def require_authentication(runtime: BankFlowRuntime) -> AuthenticationSession:
    authentication = active_authentication(runtime)
    if authentication is None:
        st.warning("Your demo session is missing or has expired. Authenticate to continue.")
        st.page_link("app.py", label="Return to sign in", icon="🔐")
        st.stop()
    return authentication


def show_action_error(message: str) -> None:
    LOGGER.exception("BankFlow UI action failed")
    st.error(message)


def render_balance_card(summary: AccountSummary) -> None:
    st.markdown(
        f"""
        <div class="balance-card">
          <div class="balance-label">Available balance</div>
          <div class="balance-value">{format_money(summary.balance, summary.currency)}</div>
          <div class="balance-meta">{summary.account_type.value.title()} ••••
            {summary.card_last_four} · {summary.account_status.value.title()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_demo_from_ui(runtime: BankFlowRuntime) -> None:
    token = st.session_state.get(SESSION_TOKEN_KEY)
    try:
        result = runtime.reset_demo(session_token=token)
    except Exception:
        show_action_error("The demo could not be reset. Please try again.")
        return
    clear_ui_session()
    st.session_state[SESSION_TOKEN_KEY] = None
    st.session_state[FLASH_KEY] = (
        f"Demo restored to {format_money(result.balance)} and transaction history cleared."
    )
    st.switch_page("app.py")


def render_sidebar(runtime: BankFlowRuntime, summary: AccountSummary) -> None:
    with st.sidebar:
        st.markdown("### 🏦 BankFlow")
        st.caption("DEMO MODE")
        st.write(f"**{summary.customer_name}**")
        st.caption(f"{summary.account_type.value.title()} •••• {summary.card_last_four}")
        st.divider()
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/2_Withdraw.py", label="Withdraw", icon="💸")
        st.page_link("pages/3_Deposit.py", label="Deposit", icon="💰")
        st.page_link("pages/4_Transaction_History.py", label="Transaction history", icon="📋")
        st.divider()
        if st.button("End session", type="secondary", width="stretch"):
            token = st.session_state.get(SESSION_TOKEN_KEY)
            if token:
                try:
                    runtime.end_session(token)
                except Exception:
                    show_action_error("The session could not be ended. Please try again.")
                    st.stop()
            clear_ui_session()
            st.session_state[SESSION_TOKEN_KEY] = None
            st.session_state[FLASH_KEY] = "Your demo session has ended."
            st.switch_page("app.py")

        with st.expander("Reset demo"):
            st.caption("Restore $500.00, unlock the card, and clear transaction history.")
            confirmed = st.checkbox("I understand this clears the demo history")
            if st.button(
                "Reset demo",
                disabled=not confirmed,
                width="stretch",
                type="secondary",
            ):
                reset_demo_from_ui(runtime)


def render_flash_message() -> None:
    message = st.session_state.pop(FLASH_KEY, None)
    if message:
        st.success(message)


def transaction_rows(items: tuple[TransactionHistoryItem, ...]) -> list[dict[str, str]]:
    return [
        {
            "Date / Time": item.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "Transaction ID": str(item.transaction_id),
            "Type": item.transaction_type.value.replace("_", " ").title(),
            "Amount": format_money(item.amount),
            "Status": item.status.value.title(),
        }
        for item in items
    ]


def render_transaction_table(items: tuple[TransactionHistoryItem, ...]) -> None:
    if not items:
        st.info("No transactions are available for this demo account yet.")
        return
    st.dataframe(
        transaction_rows(items),
        hide_index=True,
        width="stretch",
        column_config={
            "Date / Time": st.column_config.TextColumn(width="medium"),
            "Transaction ID": st.column_config.TextColumn(width="large"),
            "Type": st.column_config.TextColumn(width="medium"),
            "Amount": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
        },
    )
