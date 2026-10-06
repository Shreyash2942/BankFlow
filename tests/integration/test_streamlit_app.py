"""Live acceptance path for the Day 7 Streamlit application."""

import os
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from streamlit.testing.v1 import AppTest

from bankflow.cache import create_redis_client
from bankflow.database.session import create_session_factory, session_scope
from bankflow.demo import DEMO_ACCOUNT_ID, DEMO_CARD_ID, DEMO_CUSTOMER_ID
from bankflow.models import Account, Transaction
from bankflow.ui.streamlit_support import _cached_runtime
from scripts.seed_database import seed_demo_data

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1",
        reason="Streamlit acceptance test requires PostgreSQL and Redis opt-in",
    ),
]

ROOT = Path(__file__).resolve().parents[2]


def _delete_demo_graph(database_engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM bankflow.audit_events "
                "WHERE customer_id=:customer OR account_id=:account OR card_id=:card"
            ),
            {
                "customer": DEMO_CUSTOMER_ID,
                "account": DEMO_ACCOUNT_ID,
                "card": DEMO_CARD_ID,
            },
        )
        connection.execute(
            text("DELETE FROM bankflow.transactions WHERE account_id=:account"),
            {"account": DEMO_ACCOUNT_ID},
        )
        connection.execute(
            text("DELETE FROM bankflow.cards WHERE id=:card"), {"card": DEMO_CARD_ID}
        )
        connection.execute(
            text("DELETE FROM bankflow.accounts WHERE id=:account"),
            {"account": DEMO_ACCOUNT_ID},
        )
        connection.execute(
            text("DELETE FROM bankflow.customers WHERE id=:customer"),
            {"customer": DEMO_CUSTOMER_ID},
        )


@pytest.fixture
def streamlit_demo(migrated_database, database_engine, database_settings, monkeypatch):
    _delete_demo_graph(database_engine)
    factory = create_session_factory(database_engine)
    with session_scope(factory) as session:
        seed_demo_data(session)

    redis_client = create_redis_client(database_settings)
    auth_keys = list(redis_client.scan_iter(match="bankflow:auth:*"))
    if auth_keys:
        redis_client.delete(*auth_keys)
    monkeypatch.setenv("BANKFLOW_ENV_FILE", str(ROOT / ".env.test"))

    yield database_engine

    _cached_runtime.clear()
    auth_keys = list(redis_client.scan_iter(match="bankflow:auth:*"))
    if auth_keys:
        redis_client.delete(*auth_keys)
    redis_client.close()
    _delete_demo_graph(database_engine)


def _button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def _has_markdown(app: AppTest, text: str) -> bool:
    return any(text in block.value for block in app.markdown)


def test_user_can_authenticate_transact_review_reset_and_end_session(streamlit_demo):
    app = AppTest.from_file(ROOT / "app.py", default_timeout=10).run()
    assert not app.exception
    assert _has_markdown(app, "Welcome to")

    app.text_input[0].input("2468")
    _button(app, "Authenticate").click()
    app.run()
    assert not app.exception
    assert _has_markdown(app, "Welcome back")

    app.switch_page("pages/2_Withdraw.py").run()
    app.number_input[0].set_value(100.0)
    _button(app, "Withdraw").click()
    app.run()
    assert not app.exception
    assert "new balance is $400.00" in app.success[0].value

    app.switch_page("pages/3_Deposit.py").run()
    app.number_input[0].set_value(25.0)
    _button(app, "Deposit").click()
    app.run()
    assert not app.exception
    assert "new balance is $425.00" in app.success[0].value

    app.switch_page("pages/4_Transaction_History.py").run()
    assert not app.exception
    assert _has_markdown(app, "Transaction history")
    history = app.dataframe[0].value
    assert list(history["Type"][:2]) == ["Deposit", "Withdrawal"]

    app.switch_page("pages/1_Dashboard.py").run()
    app.checkbox[0].check()
    app.run()
    _button(app, "Reset demo").click()
    app.run()
    assert not app.exception
    assert _has_markdown(app, "Welcome to")
    assert "Demo restored to $500.00" in app.success[0].value

    with Session(streamlit_demo) as session:
        account = session.get(Account, DEMO_ACCOUNT_ID)
        transaction_types = list(
            session.scalars(
                select(Transaction.transaction_type).where(
                    Transaction.account_id == DEMO_ACCOUNT_ID
                )
            )
        )
    assert account.balance == Decimal("500.00")
    assert transaction_types == []

    assert _has_markdown(app, "Welcome to")


def test_user_can_end_session(streamlit_demo):
    app = AppTest.from_file(ROOT / "app.py", default_timeout=10).run()
    app.text_input[0].input("2468")
    _button(app, "Authenticate").click()
    app.run()
    assert not app.exception
    assert _has_markdown(app, "Welcome back")

    app.switch_page("pages/1_Dashboard.py").run()
    _button(app, "End session").click()
    app.run()
    assert not app.exception
    _button(app, "Confirm end session").click()
    app.run()
    assert not app.exception
    assert app.session_state["bankflow_session_token"] is None
    assert _has_markdown(app, "Welcome to")
