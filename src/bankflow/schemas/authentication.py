"""Secret-safe request and response contracts for card authentication."""

from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints, field_validator

CardToken = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class AuthenticationOutcome(StrEnum):
    AUTHENTICATED = "authenticated"
    INVALID_CREDENTIALS = "invalid_credentials"
    CARD_LOCKED = "card_locked"
    CARD_UNAVAILABLE = "card_unavailable"


class AuthenticationRequest(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True, extra="forbid")

    card_token: CardToken
    pin: SecretStr = Field(repr=False)

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: SecretStr) -> SecretStr:
        pin = value.get_secret_value()
        if len(pin) != 4 or not pin.isascii() or not pin.isdecimal():
            raise ValueError("PIN must contain exactly four ASCII digits.")
        return value


class AuthenticationResult(BaseModel):
    authenticated: bool
    outcome: AuthenticationOutcome
    remaining_attempts: int | None = Field(default=None, ge=0)
    session_token: SecretStr | None = Field(default=None, repr=False)
    expires_in_seconds: int | None = Field(default=None, ge=1)


class AuthenticationSession(BaseModel):
    card_id: UUID
    account_id: UUID
    customer_id: UUID
