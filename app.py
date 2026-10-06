"""BankFlow welcome and authentication screen."""

import streamlit as st
from pydantic import ValidationError

from bankflow.demo import DEMO_PIN
from bankflow.models import CardStatus
from bankflow.schemas.authentication import AuthenticationOutcome
from bankflow.ui.streamlit_support import (
    FLASH_KEY,
    SESSION_TOKEN_KEY,
    active_authentication,
    apply_design_system,
    configure_page,
    load_runtime_or_stop,
    render_brand_header,
    render_flash_message,
    render_page_heading,
    render_sidebar,
    reset_demo_from_ui,
    show_action_error,
)

configure_page("Welcome", sidebar="collapsed")
apply_design_system()
runtime = load_runtime_or_stop()
render_brand_header()
render_flash_message()

authentication = active_authentication(runtime)
if authentication is not None:
    try:
        summary = runtime.account_summary(authentication)
    except Exception:
        show_action_error("Your account could not be loaded. Please try again.")
        st.stop()
    render_sidebar(runtime, summary)
    render_page_heading(
        "✓",
        f"Welcome back, {summary.customer_name}",
        "Your secure demo session is active and ready to continue.",
    )
    st.page_link(
        "pages/1_Dashboard.py",
        label="Continue to dashboard",
        icon="🏠",
        width="stretch",
    )
    st.stop()

left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="top")
with left:
    st.markdown(
        """
        <div class="hero-panel">
          <div class="hero-kicker">MODERN BANKING · REAL DATA · BIGGER POSSIBILITIES</div>
          <h1>Welcome to<br>Bank<span>Flow</span></h1>
          <p>An event-driven ATM transaction and analytics platform built for the modern
          data world. Explore secure demo banking operations and see how everyday
          transactions become useful data.</p>
          <div class="hero-feature">
            <div class="hero-feature-icon">▣</div>
            <div><strong>Realistic ATM experience</strong>
            <small>Authenticate, withdraw, deposit, and review account activity.</small></div>
          </div>
          <div class="hero-feature">
            <div class="hero-feature-icon">▥</div>
            <div><strong>Data-driven foundation</strong>
            <small>Built on PostgreSQL, Redis, and a versioned event contract.</small></div>
          </div>
          <div class="hero-feature">
            <div class="hero-feature-icon">◇</div>
            <div><strong>Safe to explore</strong>
            <small>Fictional accounts only. No real money or customer data.</small></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="auth-heading">
          <div class="eyebrow">🔒 ATM ACCESS</div>
          <h2>Select a demo card</h2>
          <p>Choose a fictional card and enter its PIN to access the demo account.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        cards = runtime.list_demo_cards()
    except Exception:
        show_action_error("The demo card could not be loaded. Please try again.")
        st.stop()

    if not cards:
        st.error("The fictional demo card is missing. Run `python scripts/seed_database.py`.")
        st.stop()

    selected_card = st.selectbox(
        "Demo card",
        options=cards,
        format_func=lambda card: card.label,
    )
    if selected_card.card_status is CardStatus.LOCKED:
        st.error("This demo card is locked after repeated invalid PIN attempts.")
    elif selected_card.card_status is not CardStatus.ACTIVE:
        st.warning(f"This demo card is {selected_card.card_status.value}.")

    with st.form("authentication_form"):
        pin = st.text_input(
            "Enter four-digit PIN",
            type="password",
            max_chars=4,
            help="The PIN is masked and is never stored by the interface.",
        )
        st.caption(f"Demo credentials · PIN: {DEMO_PIN}")
        submitted = st.form_submit_button("Authenticate", type="primary", width="stretch")

    if submitted:
        try:
            result = runtime.authenticate(selected_card.card_token, pin)
        except ValidationError:
            st.warning("Enter exactly four digits for the demo PIN.")
        except Exception:
            show_action_error("Authentication is temporarily unavailable. Please try again.")
        else:
            if result.authenticated and result.session_token is not None:
                st.session_state[SESSION_TOKEN_KEY] = result.session_token.get_secret_value()
                st.session_state[FLASH_KEY] = "Authentication successful. Welcome to BankFlow."
                st.switch_page("pages/1_Dashboard.py")
            elif result.outcome is AuthenticationOutcome.INVALID_CREDENTIALS:
                attempts = result.remaining_attempts
                suffix = "" if attempts is None else f" {attempts} attempt(s) remaining."
                st.warning("The card or PIN was not recognized." + suffix)
            elif result.outcome is AuthenticationOutcome.CARD_LOCKED:
                st.error("The demo card is locked. Use Reset demo below to restore it.")
            else:
                st.error("This demo card is currently unavailable.")

    st.markdown(
        """
        <div class="secure-strip">
          <span>🛡 Secure demo</span><span>▰ Real data model</span><span>▥ Event ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Reset demo environment"):
        st.caption("Restore $500.00, unlock the card, and clear transaction history.")
        confirmed = st.checkbox("I understand this clears the demo history")
        if st.button("Reset demo", disabled=not confirmed, width="stretch"):
            reset_demo_from_ui(runtime)
