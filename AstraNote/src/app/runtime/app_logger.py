"""Diagnostic logger for AstraNote runtime events."""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AppLogger:
    """Writes structured diagnostic log entries to a rotating log file."""

    def __init__(
        self,
        log_path: Path | str,
        *,
        level: str = "INFO",
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 2,
    ) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger(f"astranote.app.{self._path}")
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.propagate = False
        self._logger.handlers.clear()

        handler = RotatingFileHandler(
            self._path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

    @property
    def log_path(self) -> Path:
        return self._path

    def debug(self, message: str, **context: object) -> None:
        self._emit(logging.DEBUG, message, context)

    def info(self, message: str, **context: object) -> None:
        self._emit(logging.INFO, message, context)

    def warning(self, message: str, **context: object) -> None:
        self._emit(logging.WARNING, message, context)

    def error(self, message: str, **context: object) -> None:
        self._emit(logging.ERROR, message, context)

    def _emit(self, level: int, message: str, context: dict[str, object]) -> None:
        disallowed_keys = {"title", "body", "version_content", "private_note"}
        leaked_keys = sorted(disallowed_keys.intersection(context.keys()))
        if leaked_keys:
            leaked_fields = ", ".join(leaked_keys)
            raise ValueError(
                "Diagnostic log context may not include note plaintext fields: " f"{leaked_fields}"
            )

        payload = {
            "timestamp_utc": __import__("datetime")
            .datetime.now(__import__("datetime").timezone.utc)
            .isoformat(),
            "severity": logging.getLevelName(level),
            "message": message,
        }
        if context:
            payload.update({key: value for key, value in context.items() if value is not None})

        self._logger.log(level, json.dumps(payload, ensure_ascii=True))
