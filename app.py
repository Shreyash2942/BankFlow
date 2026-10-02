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
    render_sidebar,
    reset_demo_from_ui,
    show_action_error,
)

configure_page("Welcome")
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
    st.title(f"Welcome back, {summary.customer_name}")
    st.write("Your fictional demo session is active.")
    st.page_link(
        "pages/1_Dashboard.py",
        label="Continue to dashboard",
        icon="🏠",
        width="stretch",
    )
    st.stop()

left, right = st.columns([1.15, 0.85], gap="large")
with left:
    st.title("Welcome to BankFlow")
    st.write(
        "Explore an event-driven ATM platform with an isolated fictional account. "
        "Select the demo card and authenticate to begin."
    )
    st.info("Demo environment · No real financial data")
    st.markdown(
        """
        <div class="notice-card">
          <strong>What you can try</strong><br><br>
          View an exact account balance, make withdrawals and deposits, and inspect the
          resulting transaction history.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Start a demo session")
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
            "Four-digit PIN",
            type="password",
            max_chars=4,
            help="This field is masked and the PIN is never stored by the interface.",
        )
        st.caption(f"Fictional demo PIN: {DEMO_PIN}")
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
                st.session_state[FLASH_KEY] = "Authentication successful."
                st.switch_page("pages/1_Dashboard.py")
            elif result.outcome is AuthenticationOutcome.INVALID_CREDENTIALS:
                attempts = result.remaining_attempts
                suffix = "" if attempts is None else f" {attempts} attempt(s) remaining."
                st.warning("The card or PIN was not recognized." + suffix)
            elif result.outcome is AuthenticationOutcome.CARD_LOCKED:
                st.error("The demo card is locked. Use Reset demo below to restore it.")
            else:
                st.error("This demo card is currently unavailable.")

    with st.expander("Reset demo"):
        st.caption("Restore $500.00, unlock the card, and clear transaction history.")
        confirmed = st.checkbox("I understand this clears the demo history")
        if st.button("Reset demo", disabled=not confirmed, width="stretch"):
            reset_demo_from_ui(runtime)
