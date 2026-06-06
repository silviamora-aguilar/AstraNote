"""Unit tests for CryptoService security behavior (TP-S01..TP-S05)."""

from __future__ import annotations

import pytest

from src.app.security import CryptoService


@pytest.mark.unit
def test_pin_key_derivation_is_deterministic_for_same_pin_and_salt() -> None:
    """TP-S01: same PIN and salt must produce the same derived key."""
    crypto = CryptoService(private_pin="1234")
    salt = crypto.new_pin_salt()

    first = crypto._derive_pin_key("1234", salt)
    second = crypto._derive_pin_key("1234", salt)

    assert first == second
    assert len(first) == 32


@pytest.mark.unit
def test_pin_key_derivation_changes_when_salt_changes() -> None:
    """TP-S02: changing the salt must produce a different derived key."""
    crypto = CryptoService(private_pin="1234")
    first = crypto._derive_pin_key("1234", crypto.new_pin_salt())
    second = crypto._derive_pin_key("1234", crypto.new_pin_salt())

    assert first != second


@pytest.mark.unit
def test_pin_key_derivation_output_does_not_expose_raw_pin() -> None:
    """TP-S03: derived-key output should not expose the raw PIN value."""
    crypto = CryptoService(private_pin="1234")
    salt = crypto.new_pin_salt()

    derived = crypto._derive_pin_key("1234", salt)

    assert b"1234" not in derived
    assert not hasattr(derived, "pin")


@pytest.mark.unit
def test_private_encrypt_then_decrypt_returns_original_plaintext() -> None:
    """TP-S04: private note encryption round-trip restores original plaintext."""
    crypto = CryptoService(private_pin="1234")
    salt = crypto.new_pin_salt()
    plaintext = "Highly sensitive note body"

    encrypted = crypto.encrypt_private(plaintext, salt)
    restored = crypto.decrypt_private(encrypted, salt)

    assert restored == plaintext


@pytest.mark.unit
def test_private_ciphertext_does_not_contain_plaintext() -> None:
    """TP-S05: ciphertext should not contain the original plaintext."""
    crypto = CryptoService(private_pin="1234")
    salt = crypto.new_pin_salt()
    plaintext = "Do not leak this string"

    encrypted = crypto.encrypt_private(plaintext, salt)

    assert plaintext not in encrypted
    assert encrypted.startswith("enc:v1:")
