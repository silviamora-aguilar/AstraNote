"""Configuration loading and validation for AstraNote runtime services."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_INACTIVITY_TIMEOUT_MINUTES = 15
DEFAULT_MAX_NOTES = 10_000
SUPPORTED_CONFIG_KEYS = {
    "log_level",
    "data_dir",
    "inactivity_timeout_minutes",
    "max_notes",
    "private_pin_token",
    "private_pin_version",
}


def get_default_data_dir() -> Path:
    """Return the default app data directory for the current platform."""
    configured = os.getenv("ASTRANOTE_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()

    if sys.platform == "darwin":
        return (Path.home() / "Library" / "Application Support" / "AstraNote").resolve()
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        base = Path(appdata) if appdata else (Path.home() / "AppData" / "Roaming")
        return (base / "AstraNote").resolve()
    return (Path.home() / ".local" / "share" / "astranote").resolve()


class ConfigService:
    """Loads supported runtime configuration keys with safe defaults."""

    def __init__(self, config_file: Path | None = None) -> None:
        self._config_path = self._resolve_config_path(config_file)
        self._warnings: list[str] = []
        self._config = self._load_validated_config()

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def data_dir_path(self) -> Path:
        return Path(self._config["data_dir"])

    def get(self, key: str):
        return self._config.get(key)

    def get_warnings(self) -> list[str]:
        return list(self._warnings)

    def _resolve_config_path(self, config_file: Path | None) -> Path:
        configured_path = os.getenv("ASTRANOTE_CONFIG_PATH")
        if config_file is not None:
            return config_file.expanduser().resolve()
        if configured_path:
            return Path(configured_path).expanduser().resolve()
        return get_default_data_dir() / "config.json"

    def _load_validated_config(self) -> dict[str, object]:
        raw = self._load_raw()
        default_data_dir = self._config_path.parent if os.getenv("ASTRANOTE_CONFIG_PATH") else get_default_data_dir()
        validated: dict[str, object] = {
            "log_level": DEFAULT_LOG_LEVEL,
            "data_dir": str(default_data_dir),
            "inactivity_timeout_minutes": DEFAULT_INACTIVITY_TIMEOUT_MINUTES,
            "max_notes": DEFAULT_MAX_NOTES,
        }

        if not raw:
            return validated

        data_dir = raw.get("data_dir")
        if isinstance(data_dir, str) and data_dir.strip():
            validated["data_dir"] = str(Path(data_dir).expanduser().resolve())
        elif data_dir is not None:
            self._warnings.append("Invalid config value for data_dir; using default.")

        log_level = raw.get("log_level")
        if isinstance(log_level, str) and log_level.upper() in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            validated["log_level"] = log_level.upper()
        elif log_level is not None:
            self._warnings.append("Invalid config value for log_level; using INFO.")

        inactivity_timeout = raw.get("inactivity_timeout_minutes")
        if isinstance(inactivity_timeout, int) and inactivity_timeout > 0:
            validated["inactivity_timeout_minutes"] = inactivity_timeout
        elif inactivity_timeout is not None:
            self._warnings.append("Invalid config value for inactivity_timeout_minutes; using default.")

        max_notes = raw.get("max_notes")
        if isinstance(max_notes, int) and max_notes > 0:
            validated["max_notes"] = max_notes
        elif max_notes is not None:
            self._warnings.append("Invalid config value for max_notes; using default.")

        if isinstance(raw.get("private_pin_token"), str):
            validated["private_pin_token"] = raw["private_pin_token"]
        if isinstance(raw.get("private_pin_version"), int):
            validated["private_pin_version"] = raw["private_pin_version"]

        return validated

    def _load_raw(self) -> dict[str, object] | None:
        if not self._config_path.exists():
            return None
        try:
            payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        except Exception:
            self._warnings.append("Invalid config.json; using defaults.")
            return None
        if not isinstance(payload, dict):
            self._warnings.append("Config root must be an object; using defaults.")
            return None
        return dict(payload)