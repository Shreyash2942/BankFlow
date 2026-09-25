"""Run with python -m bankflow.database.health from the repository root."""

import argparse
from dataclasses import dataclass

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.database.connection import create_database_engine


@dataclass(frozen=True)
class DatabaseHealth:
    healthy: bool
    message: str


def check_database_health(engine: Engine) -> DatabaseHealth:
    """Probe a real connection without returning raw driver errors or credentials."""
    try:
        with engine.connect() as connection:
            if connection.execute(text("SELECT 1")).scalar_one() == 1:
                return DatabaseHealth(True, "PostgreSQL connection is healthy.")
    except SQLAlchemyError, OSError:
        pass
    return DatabaseHealth(
        False,
        "PostgreSQL connection failed. Check service availability and POSTGRES_* credentials.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BankFlow PostgreSQL connectivity.")
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()
    try:
        settings = load_settings(args.env_file)
    except ConfigurationError as exc:
        print(str(exc))
        return 2
    engine = create_database_engine(settings)
    try:
        result = check_database_health(engine)
        print(result.message)
        return 0 if result.healthy else 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
