"""Persistent app-level private PIN settings for single-user mode."""

from __future__ import annotations

import base64
import json
import os
from hashlib import pbkdf2_hmac
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class PinSettingsManager:
    """Stores and verifies a single app-level 4-digit private-note PIN."""

    def __init__(self, config_file: Path | None = None, default_pin: str = "1234") -> None:
        configured_path = os.getenv("ASTRANOTE_CONFIG_PATH")
        if config_file is not None:
            self._config_file = config_file
        elif configured_path:
            self._config_file = Path(configured_path)
        else:
            self._config_file = Path("data/config.json")
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        self._default_pin = default_pin
        self._storage_salt = b"astranote-pin-storage-v1"
        self._migrate_legacy_pin_if_needed()

    @staticmethod
    def validate_pin_format(pin: str) -> bool:
        return pin.isdigit() and len(pin) == 4

    def get_pin(self) -> str:
        """Return active PIN, defaulting to 1234 until changed by user."""
        payload = self._load()
        if payload is None:
            return os.getenv("ASTRANOTE_PRIVATE_PIN", self._default_pin)

        token = payload.get("private_pin_token")
        if isinstance(token, str):
            decrypted = self._decrypt_pin_token(token)
            if decrypted is not None and self.validate_pin_format(decrypted):
                return decrypted

        legacy_pin = payload.get("private_pin")
        if isinstance(legacy_pin, str) and self.validate_pin_format(legacy_pin):
            self._save_pin(legacy_pin)
            return legacy_pin

        return os.getenv("ASTRANOTE_PRIVATE_PIN", self._default_pin)

    def verify_pin(self, pin: str) -> bool:
        if not self.validate_pin_format(pin):
            return False
        return pin == self.get_pin()

    def set_pin(self, new_pin: str) -> None:
        if not self.validate_pin_format(new_pin):
            raise ValueError("PIN must be exactly 4 digits.")

        self._save_pin(new_pin)

    def _load(self) -> dict[str, object] | None:
        if not self._config_file.exists():
            return None
        try:
            payload = json.loads(self._config_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def _derive_key(self) -> bytes:
        master_secret = os.getenv("ASTRANOTE_MASTER_SECRET", "astranote-dev-master-secret")
        return pbkdf2_hmac(
            "sha256",
            master_secret.encode("utf-8"),
            self._storage_salt,
            260_000,
            dklen=32,
        )

    def _encrypt_pin_token(self, pin: str) -> str:
        aesgcm = AESGCM(self._derive_key())
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, pin.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def _decrypt_pin_token(self, token: str) -> str | None:
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii"))
            nonce, ciphertext = raw[:12], raw[12:]
            aesgcm = AESGCM(self._derive_key())
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode("utf-8")
        except Exception:
            return None

    def _save_pin(self, pin: str) -> None:
        payload = {
            "private_pin_version": 2,
            "private_pin_token": self._encrypt_pin_token(pin),
        }
        self._config_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _migrate_legacy_pin_if_needed(self) -> None:
        payload = self._load()
        if payload is None:
            return

        token = payload.get("private_pin_token")
        if isinstance(token, str):
            decrypted = self._decrypt_pin_token(token)
            if decrypted is not None and self.validate_pin_format(decrypted):
                if "private_pin" in payload or payload.get("private_pin_version") != 2:
                    self._save_pin(decrypted)
                return

        legacy_pin = payload.get("private_pin")
        if isinstance(legacy_pin, str) and self.validate_pin_format(legacy_pin):
            self._save_pin(legacy_pin)
