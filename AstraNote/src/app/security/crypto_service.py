"""Encryption and key-derivation utilities for note protection at rest."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode("ascii"))


@dataclass(slots=True)
class EncryptedValue:
    """Structured encrypted payload used for database persistence."""

    nonce: str
    ciphertext: str

    def encode(self) -> str:
        return f"enc:v1:{self.nonce}:{self.ciphertext}"

    @classmethod
    def decode(cls, raw: str) -> "EncryptedValue | None":
        if not raw or not raw.startswith("enc:v1:"):
            return None
        parts = raw.split(":", 3)
        if len(parts) != 4:
            return None
        return cls(nonce=parts[2], ciphertext=parts[3])


class CryptoService:
    """Performs AES-GCM encryption for note title/body fields."""

    def __init__(self, master_secret: str | None = None, private_pin: str | None = None) -> None:
        self._master_secret = master_secret or os.getenv("ASTRANOTE_MASTER_SECRET", "astranote-dev-master-secret")
        self._private_pin = private_pin or os.getenv("ASTRANOTE_PRIVATE_PIN", "1234")
        self._master_key = self._derive_master_key()
        self._pin_key_cache: dict[tuple[str, str], bytes] = {}

    @property
    def private_pin(self) -> str:
        return self._private_pin

    def validate_pin_format(self, pin: str) -> bool:
        return pin.isdigit() and len(pin) == 4

    def new_pin_salt(self) -> str:
        return _b64e(os.urandom(16))

    def encrypt_public(self, plaintext: str) -> str:
        return self._encrypt(plaintext, self._master_key)

    def decrypt_public(self, raw: str) -> str:
        return self._decrypt(raw, self._master_key)

    def encrypt_private(self, plaintext: str, pin_salt_b64: str) -> str:
        key = self._derive_pin_key(self._private_pin, pin_salt_b64)
        return self._encrypt(plaintext, key)

    def decrypt_private(self, raw: str, pin_salt_b64: str) -> str:
        key = self._derive_pin_key(self._private_pin, pin_salt_b64)
        return self._decrypt(raw, key)

    def verify_pin(self, attempted_pin: str) -> bool:
        if not self.validate_pin_format(attempted_pin):
            return False
        return attempted_pin == self._private_pin

    def set_private_pin(self, pin: str) -> None:
        if not self.validate_pin_format(pin):
            raise ValueError("PIN must be exactly 4 digits.")
        self._private_pin = pin
        self._pin_key_cache.clear()

    def encrypt_private_with_pin(self, plaintext: str, pin_salt_b64: str, pin: str) -> str:
        key = self._derive_pin_key(pin, pin_salt_b64)
        return self._encrypt(plaintext, key)

    def decrypt_private_with_pin(self, raw: str, pin_salt_b64: str, pin: str) -> str:
        key = self._derive_pin_key(pin, pin_salt_b64)
        return self._decrypt(raw, key)

    def _derive_master_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"astranote-master-salt-v1",
            iterations=260_000,
        )
        return kdf.derive(self._master_secret.encode("utf-8"))

    def _derive_pin_key(self, pin: str, pin_salt_b64: str) -> bytes:
        cache_key = (pin, pin_salt_b64)
        if cache_key in self._pin_key_cache:
            return self._pin_key_cache[cache_key]
        salt = _b64d(pin_salt_b64)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=260_000,
        )
        key = kdf.derive(pin.encode("utf-8"))
        self._pin_key_cache[cache_key] = key
        return key

    def _encrypt(self, plaintext: str, key: bytes) -> str:
        nonce = os.urandom(12)
        cipher = AESGCM(key)
        encrypted = cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
        return EncryptedValue(nonce=_b64e(nonce), ciphertext=_b64e(encrypted)).encode()

    def _decrypt(self, raw: str, key: bytes) -> str:
        parsed = EncryptedValue.decode(raw)
        if parsed is None:
            # Legacy plaintext fallback to avoid data loss on existing local stores.
            return raw

        cipher = AESGCM(key)
        decrypted = cipher.decrypt(_b64d(parsed.nonce), _b64d(parsed.ciphertext), None)
        return decrypted.decode("utf-8")
