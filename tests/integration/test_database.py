"""Opt in with BANKFLOW_RUN_DB_TESTS=1; never run migrations against the app database."""

import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy import text

from bankflow.database.connection import create_database_engine
from bankflow.database.health import check_database_health
from bankflow.database.session import create_session_factory, session_scope

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("BANKFLOW_RUN_DB_TESTS") != "1", reason="database tests require opt-in"
    ),
]


def test_real_postgres_health_and_role_privileges(database_engine):
    assert check_database_health(database_engine).healthy
    with database_engine.connect() as connection:
        assert connection.execute(text("SELECT current_database()")).scalar_one() == "bankflow_test"
        assert not connection.execute(
            text(
                "SELECT rolsuper OR rolcreatedb OR rolcreaterole FROM pg_roles WHERE rolname=current_user"
            )
        ).scalar_one()


def test_bad_credentials_are_reported_without_driver_details(database_settings):
    broken = database_settings.model_copy(
        update={"postgres_password": SecretStr("definitely-wrong")}
    )
    engine = create_database_engine(broken)
    try:
        result = check_database_health(engine)
        assert not result.healthy
        assert "credentials" in result.message
        assert "definitely-wrong" not in result.message
    finally:
        engine.dispose()


def test_session_commits_success_and_rolls_back_failed_work(database_engine):
    name = "day2_probe_" + uuid4().hex
    with database_engine.begin() as connection:
        connection.execute(text(f"CREATE TABLE public.{name} (value integer NOT NULL)"))
    factory = create_session_factory(database_engine)
    try:
        with session_scope(factory) as session:
            session.execute(text(f"INSERT INTO public.{name} VALUES (10)"))
        with pytest.raises(RuntimeError, match="abort"):
            with session_scope(factory) as session:
                session.execute(text(f"INSERT INTO public.{name} VALUES (20)"))
                raise RuntimeError("abort")
        with database_engine.connect() as connection:
            assert connection.execute(text(f"SELECT value FROM public.{name}")).scalars().all() == [
                10
            ]
    finally:
        with database_engine.begin() as connection:
            connection.execute(text(f"DROP TABLE public.{name}"))


def test_migration_upgrade_downgrade_and_reupgrade(database_settings, database_engine):
    config = Config("alembic.ini")
    config.attributes["settings"] = database_settings
    command.upgrade(config, "head")
    command.upgrade(config, "head")  # Already at head must be a no-op.
    with database_engine.connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == "0002"
        )
        assert (
            connection.execute(text("SELECT to_regnamespace('bankflow')")).scalar_one()
            == "bankflow"
        )
    command.downgrade(config, "base")
    with database_engine.connect() as connection:
        assert connection.execute(text("SELECT to_regnamespace('bankflow')")).scalar_one() is None
    command.upgrade(config, "head")


def test_test_role_cannot_connect_to_application_database(database_settings):
    wrong_db = database_settings.model_copy(update={"postgres_db": "bankflow"})
    engine = create_database_engine(wrong_db)
    try:
        assert not check_database_health(engine).healthy
    finally:
        engine.dispose()
