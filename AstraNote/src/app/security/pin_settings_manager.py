"""Persistent app-level private PIN settings for single-user mode."""

from __future__ import annotations

import json
import os
from pathlib import Path


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

    @staticmethod
    def validate_pin_format(pin: str) -> bool:
        return pin.isdigit() and len(pin) == 4

    def get_pin(self) -> str:
        """Return active PIN, defaulting to 1234 until changed by user."""
        payload = self._load()
        if payload is None:
            return os.getenv("ASTRANOTE_PRIVATE_PIN", self._default_pin)
        pin = payload.get("private_pin")
        if isinstance(pin, str) and self.validate_pin_format(pin):
            return pin
        return os.getenv("ASTRANOTE_PRIVATE_PIN", self._default_pin)

    def verify_pin(self, pin: str) -> bool:
        if not self.validate_pin_format(pin):
            return False
        return pin == self.get_pin()

    def set_pin(self, new_pin: str) -> None:
        if not self.validate_pin_format(new_pin):
            raise ValueError("PIN must be exactly 4 digits.")

        payload = {"private_pin": new_pin, "private_pin_version": 1}
        self._config_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

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
