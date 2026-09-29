"""PIN hashing must be salted, verifiable, and safe on malformed input."""

import pytest

from bankflow.utils import InvalidPinError, hash_pin, verify_pin


def test_pin_hash_round_trip_uses_a_fresh_salt():
    first = hash_pin("2468")
    second = hash_pin("2468")

    assert first != second
    assert first.startswith("scrypt$16384$8$1$")
    assert verify_pin("2468", first)
    assert not verify_pin("1357", first)


@pytest.mark.parametrize("candidate", ["", "123", "12345", "12a4", "１２３４"])
def test_pin_hash_rejects_non_four_ascii_digit_values(candidate):
    with pytest.raises(InvalidPinError) as exc_info:
        hash_pin(candidate)
    if candidate:
        assert candidate not in str(exc_info.value)


@pytest.mark.parametrize(
    "encoded_hash",
    ["", "not-a-hash", "argon2$16384$8$1$a$b", "scrypt$2$8$1$a$b"],
)
def test_pin_verification_rejects_malformed_or_unsupported_hashes(encoded_hash):
    assert not verify_pin("2468", encoded_hash)
