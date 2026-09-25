"""Alembic environment using the same validated settings as the application."""

from logging.config import fileConfig

from alembic import context
from alembic.util import CommandError
from sqlalchemy.exc import SQLAlchemyError

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.database.base import Base
from bankflow.database.connection import create_database_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def include_name(name, type_, parent_names):
    """Autogeneration must not propose changes to unrelated schemas."""
    return name == "bankflow" if type_ == "schema" else True


def run_migrations_offline():
    context.configure(
        dialect_name="postgresql",
        target_metadata=Base.metadata,
        literal_binds=True,
        include_schemas=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    try:
        settings = config.attributes.get("settings") or load_settings()
    except ConfigurationError as exc:
        raise CommandError(str(exc)) from None
    engine = create_database_engine(settings)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=Base.metadata,
                include_schemas=True,
                include_name=include_name,
            )
            with context.begin_transaction():
                context.run_migrations()
    except SQLAlchemyError:
        raise CommandError(
            "PostgreSQL migration failed. Check credentials, availability, permissions, "
            "and the current schema revision."
        ) from None
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
