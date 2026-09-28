from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from bankflow.config.settings import load_settings
from bankflow.database.connection import create_database_engine

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def database_settings():
    result = load_settings(ROOT / ".env.test")
    if (result.app_env, result.postgres_db, result.postgres_user) != (
        "test",
        "bankflow_test",
        "bankflow_test_user",
    ):
        pytest.fail("Integration tests require dedicated bankflow_test credentials.")
    return result


@pytest.fixture
def database_engine(database_settings):
    engine = create_database_engine(database_settings)
    yield engine
    engine.dispose()


@pytest.fixture
def migrated_database(database_settings):
    config = Config(str(ROOT / "alembic.ini"))
    config.attributes["settings"] = database_settings
    command.upgrade(config, "head")
