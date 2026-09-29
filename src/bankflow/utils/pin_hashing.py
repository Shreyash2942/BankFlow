"""Scrypt PIN hashing with a versioned, self-describing storage format."""

import base64
import hashlib
import hmac
import secrets

_ALGORITHM = "scrypt"
_N = 2**14
_R = 8
_P = 1
_SALT_BYTES = 16
_KEY_BYTES = 32


class InvalidPinError(ValueError):
    """A PIN failed the public four-digit input contract."""


def _validate_pin(pin: str) -> None:
    if len(pin) != 4 or not pin.isascii() or not pin.isdecimal():
        raise InvalidPinError("PIN must contain exactly four ASCII digits.")


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)


def hash_pin(pin: str) -> str:
    """Return a salted scrypt hash; the plaintext PIN is never retained."""
    _validate_pin(pin)
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.scrypt(pin.encode("ascii"), salt=salt, n=_N, r=_R, p=_P, dklen=_KEY_BYTES)
    return f"{_ALGORITHM}${_N}${_R}${_P}${_encode(salt)}${_encode(digest)}"


def verify_pin(pin: str, encoded_hash: str) -> bool:
    """Verify a PIN in constant time and reject malformed hashes safely."""
    try:
        _validate_pin(pin)
        algorithm, n, r, p, salt_value, digest_value = encoded_hash.split("$")
        if algorithm != _ALGORITHM:
            return False
        parameters = (int(n), int(r), int(p))
        if parameters != (_N, _R, _P):
            return False
        salt = _decode(salt_value)
        expected = _decode(digest_value)
        if len(salt) != _SALT_BYTES or len(expected) != _KEY_BYTES:
            return False
        actual = hashlib.scrypt(
            pin.encode("ascii"),
            salt=salt,
            n=parameters[0],
            r=parameters[1],
            p=parameters[2],
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except InvalidPinError, UnicodeError, ValueError:
        return False
