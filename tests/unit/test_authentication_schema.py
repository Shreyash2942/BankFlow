"""Authentication contracts mask PINs in object and validation representations."""

import pytest
from pydantic import ValidationError

from bankflow.schemas import AuthenticationRequest


def test_authentication_request_masks_pin_representation():
    request = AuthenticationRequest(card_token="  fictional-card  ", pin="2468")

    assert request.card_token == "fictional-card"
    assert request.pin.get_secret_value() == "2468"
    assert "2468" not in repr(request)
    assert "2468" not in str(request)


def test_authentication_request_validation_error_omits_pin_input():
    with pytest.raises(ValidationError) as exc_info:
        AuthenticationRequest(card_token="fictional-card", pin="pin-value-that-must-stay-secret")

    assert "pin-value-that-must-stay-secret" not in str(exc_info.value)
    assert "four ASCII digits" in str(exc_info.value)
