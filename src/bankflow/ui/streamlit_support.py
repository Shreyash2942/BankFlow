"""Shared presentation helpers for the BankFlow Streamlit application."""

import html
import logging
import os
from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal

import streamlit as st

from bankflow.models import TransactionStatus, TransactionType
from bankflow.schemas.authentication import AuthenticationSession
from bankflow.schemas.transaction import TransactionHistoryItem
from bankflow.ui.runtime import AccountSummary, BankFlowRuntime

LOGGER = logging.getLogger(__name__)
SESSION_TOKEN_KEY = "bankflow_session_token"
FLASH_KEY = "bankflow_flash"


@dataclass(frozen=True)
class TransactionMetrics:
    """Small presentation summary derived from an account's loaded history."""

    deposits: Decimal
    withdrawals: Decimal
    completed: int
    declined: int
    total: int


def configure_page(title: str, *, sidebar: str = "expanded") -> None:
    st.set_page_config(
        page_title=f"{title} | BankFlow",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state=sidebar,
    )


def apply_design_system() -> None:
    """Apply the restrained visual system defined by the supplied UI references."""

    st.markdown(
        """
        <style>
        :root {
          --bf-navy: #071b35;
          --bf-navy-soft: #0b3159;
          --bf-blue: #0b6cf2;
          --bf-blue-dark: #0758ca;
          --bf-emerald: #059669;
          --bf-red: #dc2626;
          --bf-ink: #0f2344;
          --bf-muted: #5d7192;
          --bf-line: #dce7f5;
          --bf-surface: #ffffff;
          --bf-canvas: #f4f8fe;
        }
        .stApp {
          background:
            radial-gradient(circle at 86% 0%, rgba(37, 99, 235, .08), transparent 28rem),
            var(--bf-canvas);
        }
        .block-container {max-width: 1280px; padding-top: 1.4rem; padding-bottom: 3rem;}
        h1, h2, h3 {color: var(--bf-ink); letter-spacing: -.025em;}
        h1 {font-size: clamp(2rem, 3vw, 3rem) !important; line-height: 1.08 !important;}
        p, label, [data-testid="stCaptionContainer"] {color: var(--bf-muted);}
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #061a33 0%, #082747 100%);
          border-right: 0; box-shadow: 8px 0 30px rgba(7, 27, 53, .12);
        }
        [data-testid="stSidebar"] * {color: #dceaff;}
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] hr {border-color: rgba(174, 205, 244, .2);}
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
          border-radius: 10px; margin: .18rem 0; padding: .68rem .8rem;
        }
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
          background: rgba(20, 111, 239, .28);
        }
        [data-testid="stSidebar"] button[kind="secondary"] {
          border-color: rgba(248, 113, 113, .8); color: #fecaca;
          background: rgba(127, 29, 29, .12);
        }
        .bankflow-header {
          display: flex; align-items: center; justify-content: space-between;
          gap: 1rem; margin-bottom: 1.35rem; padding: .25rem 0 .9rem;
          border-bottom: 1px solid var(--bf-line);
        }
        .bankflow-brand {font-size: 1.5rem; font-weight: 800; color: var(--bf-ink);}
        .bankflow-tagline {color: var(--bf-muted); font-size: .86rem; margin-top: .08rem;}
        .demo-badge, .status-pill {
          display: inline-flex; align-items: center; gap: .4rem; padding: .38rem .72rem;
          border-radius: 999px; font-size: .72rem; font-weight: 750;
          letter-spacing: .035em; white-space: nowrap;
        }
        .demo-badge {color: #047857; background: #d9f8eb; border: 1px solid #b8ecd8;}
        .status-pill {color: #047857; background: #dcfce7;}
        .sidebar-brand {padding: .5rem .15rem 1.2rem;}
        .sidebar-brand-name {font-size: 1.55rem; font-weight: 800; color: #fff;}
        .sidebar-brand-mark {color: #47a3ff; margin-right: .35rem;}
        .sidebar-tagline {font-size: .78rem; line-height: 1.4; color: #b8cbe3; margin-top: .2rem;}
        .sidebar-profile {
          padding: .85rem; border-radius: 12px; margin: .6rem 0 1rem;
          background: rgba(255,255,255,.07); border: 1px solid rgba(174,205,244,.15);
        }
        .sidebar-profile strong {color: #fff;}
        .sidebar-demo {
          padding: .8rem; border-radius: 12px; margin-top: 1rem; color: #a7f3d0;
          background: rgba(5,150,105,.22); border: 1px solid rgba(52,211,153,.28);
          font-size: .82rem;
        }
        .page-heading {
          display: flex; align-items: center; gap: 1rem; margin: .3rem 0 1.35rem;
          padding: 1.05rem 1.2rem; border: 1px solid var(--bf-line); border-radius: 16px;
          background: linear-gradient(105deg, #fff 0%, #edf5ff 72%, #d9eaff 100%);
        }
        .page-heading-icon {
          display: grid; place-items: center; width: 3.3rem; height: 3.3rem; flex: 0 0 3.3rem;
          border-radius: 14px; color: var(--bf-blue); background: #e4efff; font-size: 1.55rem;
        }
        .page-heading h1 {font-size: 2rem !important; margin: 0 0 .2rem !important;}
        .page-heading p {margin: 0;}
        .eyebrow {
          color: var(--bf-blue); font-size: .76rem; font-weight: 800;
          letter-spacing: .08em; text-transform: uppercase; margin-bottom: .35rem;
        }
        .hero-panel {
          min-height: 30rem; border-radius: 22px; padding: clamp(1.8rem, 4vw, 3.4rem);
          color: #fff; overflow: hidden; position: relative;
          background:
            radial-gradient(circle at 82% 30%, rgba(30, 136, 255, .48), transparent 11rem),
            linear-gradient(145deg, #071a32 0%, #0a315c 60%, #0d4f8d 100%);
          box-shadow: 0 18px 50px rgba(7, 27, 53, .16);
        }
        .hero-panel:after {
          content: ""; position: absolute; inset: auto -6rem -7rem auto;
          width: 20rem; height: 20rem; border: 1px solid rgba(120, 190, 255, .25);
          border-radius: 42%; transform: rotate(25deg);
        }
        .hero-panel h1 {
          color: #fff; font-size: clamp(2.5rem, 5vw, 4.25rem) !important;
          margin: .5rem 0 1rem;
        }
        .hero-panel h1 span {color: #2f8cff;}
        .hero-panel p {color: #c6d6e9; max-width: 34rem; font-size: 1.03rem; line-height: 1.65;}
        .hero-kicker {color: #55a7ff; font-weight: 800; letter-spacing: .08em; font-size: .78rem;}
        .hero-feature {display: flex; gap: .8rem; margin-top: 1.25rem; align-items: flex-start;}
        .hero-feature-icon {
          display: grid; place-items: center; flex: 0 0 2.6rem; height: 2.6rem;
          border-radius: 10px; background: rgba(47, 140, 255, .2); color: #7abbff;
        }
        .hero-feature strong {display: block; color: #fff; font-size: .94rem; margin-bottom: .15rem;}
        .hero-feature small {color: #b8cbe3; line-height: 1.45;}
        .auth-heading {margin-bottom: .7rem;}
        .auth-heading h2 {font-size: 1.8rem; margin: .2rem 0;}
        .auth-heading p {margin: 0;}
        .secure-strip {
          display: flex; justify-content: space-between; gap: .8rem; margin-top: 1.15rem;
          padding: .85rem; border-radius: 12px; background: #eff6ff;
          border: 1px solid #d7e8ff; color: #36557f; font-size: .78rem;
        }
        .metric-card, .balance-card, .notice-card, .content-card {
          background: rgba(255,255,255,.94); border: 1px solid var(--bf-line);
          box-shadow: 0 5px 18px rgba(15, 35, 68, .045);
        }
        .metric-card {border-radius: 14px; padding: 1.05rem 1.1rem; min-height: 7.5rem;}
        .metric-icon {
          float: left; display: grid; place-items: center; width: 2.65rem; height: 2.65rem;
          border-radius: 11px; margin-right: .8rem; background: #e5efff;
          color: var(--bf-blue); font-size: 1.2rem;
        }
        .metric-label {color: var(--bf-muted); font-size: .78rem; font-weight: 650;}
        .metric-value {color: var(--bf-ink); font-size: 1.65rem; line-height: 1.2; font-weight: 800; margin-top: .25rem;}
        .metric-meta {clear: both; padding-top: .65rem; color: var(--bf-muted); font-size: .76rem;}
        .metric-meta.positive {color: var(--bf-emerald);}
        .metric-meta.negative {color: var(--bf-red);}
        .balance-card {border-radius: 16px; padding: 1.3rem 1.45rem; margin: .15rem 0 1rem;}
        .balance-label {
          color: var(--bf-muted); font-size: .82rem; font-weight: 700;
          text-transform: uppercase; letter-spacing: .05em;
        }
        .balance-value {color: var(--bf-ink); font-size: 2.25rem; line-height: 1.2; font-weight: 800; margin: .4rem 0;}
        .balance-meta {color: var(--bf-muted); font-size: .88rem;}
        .notice-card, .content-card {border-radius: 14px; padding: 1.15rem 1.3rem;}
        .notice-card.info {background: #edf5ff; border-color: #cfe2ff;}
        .notice-card.success {background: #ecfdf5; border-color: #b7efd5;}
        .notice-card.warning {background: #fff8e8; border-color: #f9df9a;}
        .notice-card strong, .content-card strong {color: var(--bf-ink);}
        .notice-card p:last-child {margin-bottom: 0;}
        .service-card {
          min-height: 9rem; padding: 1.05rem; border-radius: 14px;
          background: rgba(255,255,255,.96); border: 1px solid var(--bf-line);
          box-shadow: 0 5px 18px rgba(15,35,68,.04);
        }
        .service-name {color: var(--bf-ink); font-weight: 800; font-size: .98rem;}
        .service-state {font-weight: 750; margin: .65rem 0 .35rem; text-transform: capitalize;}
        .service-state:before {
          content: ""; display: inline-block; width: .6rem; height: .6rem;
          margin-right: .45rem; border-radius: 50%; background: #94a3b8;
        }
        .service-state.healthy {color: #047857;}
        .service-state.healthy:before {background: var(--bf-emerald);}
        .service-state.degraded, .service-state.pending {color: #b45309;}
        .service-state.degraded:before, .service-state.pending:before {background: #f59e0b;}
        .service-state.unavailable {color: #b91c1c;}
        .service-state.unavailable:before {background: var(--bf-red);}
        .service-detail {color: var(--bf-muted); font-size: .78rem; line-height: 1.4;}
        div[data-testid="stForm"] {
          background: rgba(255,255,255,.96); border: 1px solid var(--bf-line);
          border-radius: 16px; padding: 1.25rem; box-shadow: 0 5px 18px rgba(15,35,68,.04);
        }
        div[data-testid="stButton"] button, a[data-testid="stPageLink-NavLink"] {border-radius: 9px;}
        button[kind="primary"], div[data-testid="stFormSubmitButton"] button[kind="primary"] {
          background: linear-gradient(135deg, var(--bf-blue), #136fec);
          border-color: var(--bf-blue); font-weight: 750;
        }
        button[kind="primary"]:hover {background: var(--bf-blue-dark); border-color: var(--bf-blue-dark);}
        [data-testid="stMetric"] {
          background: #fff; border: 1px solid var(--bf-line); border-radius: 14px; padding: 1rem;
        }
        [data-testid="stDataFrame"] {border: 1px solid var(--bf-line); border-radius: 14px; overflow: hidden;}
        [data-testid="stAlert"] {border-radius: 12px;}
        [data-testid="stDialog"] > div {border-radius: 18px;}
        @media (max-width: 760px) {
          .block-container {padding-top: .8rem;}
          .bankflow-header {align-items: flex-start;}
          .hero-panel {min-height: auto; padding: 1.5rem;}
          .page-heading {align-items: flex-start;}
          .secure-strip {flex-direction: column;}
        }
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
            <div class="bankflow-tagline">Transactions Today. Insights Tomorrow.</div>
          </div>
          <span class="demo-badge">⚗ DEMO ENVIRONMENT</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_heading(icon: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="page-heading">
          <div class="page-heading-icon">{html.escape(icon)}</div>
          <div><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, meta: str, icon: str, tone: str = "") -> None:
    tone_class = tone if tone in {"positive", "negative"} else ""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-icon">{html.escape(icon)}</div>
          <div class="metric-label">{html.escape(label)}</div>
          <div class="metric-value">{html.escape(value)}</div>
          <div class="metric-meta {tone_class}">{html.escape(meta)}</div>
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
            {html.escape(summary.card_last_four)} · {summary.account_status.value.title()}</div>
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


def _end_session(runtime: BankFlowRuntime) -> None:
    token = st.session_state.get(SESSION_TOKEN_KEY)
    if token:
        try:
            runtime.end_session(token)
        except Exception:
            show_action_error("The session could not be ended. Please try again.")
            return
    clear_ui_session()
    st.session_state[SESSION_TOKEN_KEY] = None
    st.session_state[FLASH_KEY] = "Your demo session has ended securely."
    st.switch_page("app.py")


@st.dialog("End ATM session?")
def confirm_end_session(runtime: BankFlowRuntime) -> None:
    st.write("You will be signed out and returned to the BankFlow welcome screen.")
    st.info("Make sure you have completed all demo transactions before ending the session.")
    cancel, confirm = st.columns(2)
    with cancel:
        if st.button("Cancel", width="stretch"):
            st.session_state.pop("bankflow_show_end_session", None)
            st.rerun()
    with confirm:
        if st.button("Confirm end session", type="primary", width="stretch"):
            _end_session(runtime)


def render_sidebar(runtime: BankFlowRuntime, summary: AccountSummary) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="sidebar-brand-name"><span class="sidebar-brand-mark">▰</span>BankFlow</div>
              <div class="sidebar-tagline">Transactions Today.<br>Insights Tomorrow.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="sidebar-profile">
              <strong>{html.escape(summary.customer_name)}</strong><br>
              <span>{summary.account_type.value.title()} •••• {html.escape(summary.card_last_four)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/2_Withdraw.py", label="Withdraw", icon="↘️")
        st.page_link("pages/3_Deposit.py", label="Deposit", icon="↗️")
        st.page_link("pages/4_Transaction_History.py", label="Transaction history", icon="📋")
        st.page_link("pages/5_Analytics.py", label="Analytics", icon="📊")
        st.page_link("pages/6_Platform_Status.py", label="Platform status", icon="⚙️")
        st.divider()
        st.markdown(
            """
            <div class="sidebar-demo"><strong>⚗ Demo Environment</strong><br>
            Learning · Testing · Exploring</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("End session", type="secondary", width="stretch"):
            st.session_state["bankflow_show_end_session"] = True
        if st.session_state.get("bankflow_show_end_session", False):
            confirm_end_session(runtime)

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
        st.caption("BankFlow v0.1.0 · Phase 2 in progress")


def render_platform_sidebar() -> None:
    """Render navigation that remains available while application services are down."""

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="sidebar-brand-name"><span class="sidebar-brand-mark">▰</span>BankFlow</div>
              <div class="sidebar-tagline">Transactions Today.<br>Insights Tomorrow.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="Welcome", icon="🏦")
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/5_Analytics.py", label="Analytics", icon="📊")
        st.page_link("pages/6_Platform_Status.py", label="Platform status", icon="⚙️")
        st.divider()
        st.markdown(
            """
            <div class="sidebar-demo"><strong>⚗ Demo Environment</strong><br>
            Live, bounded service probes</div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("BankFlow v0.1.0 · Phase 2 in progress")


def render_status_card(
    name: str,
    state: str,
    detail: str,
    *,
    latency_ms: int | None = None,
) -> None:
    safe_state = state if state in {"healthy", "degraded", "unavailable", "pending"} else "pending"
    latency = f" · {latency_ms} ms" if latency_ms is not None else ""
    st.markdown(
        f"""
        <div class="service-card">
          <div class="service-name">{html.escape(name)}</div>
          <div class="service-state {safe_state}">{html.escape(safe_state)}</div>
          <div class="service-detail">{html.escape(detail)}{html.escape(latency)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_flash_message() -> None:
    message = st.session_state.pop(FLASH_KEY, None)
    if message:
        st.success(message)


def transaction_metrics(items: tuple[TransactionHistoryItem, ...]) -> TransactionMetrics:
    completed = tuple(item for item in items if item.status is TransactionStatus.COMPLETED)
    return TransactionMetrics(
        deposits=sum(
            (item.amount for item in completed if item.transaction_type is TransactionType.DEPOSIT),
            start=Decimal("0.00"),
        ),
        withdrawals=sum(
            (
                item.amount
                for item in completed
                if item.transaction_type is TransactionType.WITHDRAWAL
            ),
            start=Decimal("0.00"),
        ),
        completed=len(completed),
        declined=sum(item.status is TransactionStatus.DECLINED for item in items),
        total=len(items),
    )


def transaction_rows(items: tuple[TransactionHistoryItem, ...]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in items:
        amount = format_money(item.amount)
        if item.transaction_type is TransactionType.WITHDRAWAL:
            amount = f"−{amount}"
        elif item.transaction_type is TransactionType.DEPOSIT:
            amount = f"+{amount}"
        rows.append(
            {
                "Date / Time": item.created_at.astimezone(UTC).strftime("%b %d, %Y %I:%M %p UTC"),
                "Transaction ID": str(item.transaction_id),
                "Type": item.transaction_type.value.replace("_", " ").title(),
                "Amount": amount,
                "Balance": format_money(item.balance_after),
                "Status": item.status.value.title(),
            }
        )
    return rows


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
            "Balance": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
        },
    )
