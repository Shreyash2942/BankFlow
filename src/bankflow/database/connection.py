"""Lazy SQLAlchemy engine construction; the caller owns engine disposal."""

from sqlalchemy import Engine, create_engine

from bankflow.config.settings import Settings


def create_database_engine(settings: Settings) -> Engine:
    """Create a pool without opening a connection until first use."""
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        hide_parameters=True,
        echo=False,
        connect_args={
            "connect_timeout": settings.postgres_connect_timeout,
            "application_name": "bankflow",
        },
    )
