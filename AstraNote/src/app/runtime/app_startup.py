"""Startup validation for local runtime prerequisites."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from src.app.repositories.sql_note_repository import SqlNoteRepository
from src.app.runtime.config_service import ConfigService
from src.app.runtime.app_logger import AppLogger


class AppStartup:
    """Verifies startup prerequisites for the local single-user runtime."""

    def __init__(self, config_service: ConfigService, logger: AppLogger) -> None:
        self._config = config_service
        self._logger = logger

    @property
    def database_path(self) -> Path:
        return self._config.data_dir_path / "astranote.db"

    def initialize(self) -> None:
        self._ensure_data_dir()
        for warning in self._config.get_warnings():
            self._logger.warning(warning, tier="runtime")
        self._verify_persistence_store()

    def _ensure_data_dir(self) -> None:
        data_dir = self._config.data_dir_path
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            probe = data_dir / ".astranote-write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except Exception as exc:
            raise RuntimeError(f"AstraNote data directory is not writable: {data_dir}") from exc

    def _verify_persistence_store(self) -> None:
        database_url = f"sqlite:///{self.database_path}"
        try:
            repository = SqlNoteRepository(database_url=database_url)
            repository.engine.dispose()
        except (SQLAlchemyError, RuntimeError, OSError, ValueError) as exc:
            self._logger.error(
                "Primary persistence store failed startup verification.",
                tier="storage",
                operation="startup_verify_store",
                database_path=str(self.database_path),
            )
            raise RuntimeError(
                f"AstraNote could not open the local note store at {self.database_path}. "
                "Please repair or replace the store before launching."
            ) from exc