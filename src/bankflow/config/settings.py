"""Validated environment configuration; importing this module performs no I/O."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr, StringConstraints, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Port = Annotated[int, Field(ge=1, le=65535)]


class ConfigurationError(ValueError):
    """Invalid configuration, with input values omitted from its message."""


class Settings(BaseSettings):
    """Explicit arguments override environment variables, which override dotenv."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
        hide_input_in_errors=True,
        frozen=True,
    )

    app_env: Literal["development", "test", "production"] = "development"
    postgres_host: NonEmpty = "127.0.0.1"
    postgres_port: Port = 5433
    postgres_db: NonEmpty = "bankflow"
    postgres_user: NonEmpty = "bankflow_user"
    postgres_password: SecretStr = Field(repr=False)
    postgres_connect_timeout: int = Field(default=5, ge=1, le=60)
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=5, ge=0, le=20)
    db_pool_timeout: int = Field(default=10, ge=1, le=60)

    redis_host: NonEmpty = "127.0.0.1"
    redis_port: Port = 6380
    redis_username: str = "default"
    redis_password: SecretStr = Field(default=SecretStr(""), repr=False)
    redis_db: int = Field(default=0, ge=0, le=15)
    kafka_bootstrap_servers: NonEmpty = "127.0.0.1:9093"
    kafka_transaction_topic: NonEmpty = "bankflow.transaction.events"
    kafka_consumer_group: NonEmpty = "bankflow-operational-v1"
    max_pin_attempts: int = Field(default=3, ge=1, le=10)
    auto_close_zero_balance: bool = True

    @field_validator("postgres_password")
    @classmethod
    def require_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("must not be blank")
        return value

    @property
    def database_url(self) -> URL:
        """Build a URL without interpolating or manually escaping credentials."""
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


def load_settings(env_file: str | Path | None = ".env") -> Settings:
    """Load explicitly, reporting field names but never submitted values."""
    try:
        return Settings(_env_file=env_file)
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]).upper() for error in exc.errors()})
        raise ConfigurationError(
            "Invalid or missing settings: " + ", ".join(fields) + ". Check your environment file."
        ) from None
