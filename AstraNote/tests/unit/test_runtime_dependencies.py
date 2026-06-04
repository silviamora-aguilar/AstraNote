"""Unit tests for BL-21 runtime dependency wiring."""

from __future__ import annotations

import json

import pytest

from src.app.dependencies import (
    get_audit_logger,
    get_app_logger,
    get_app_startup,
    get_config_service,
    get_crypto_service,
    get_note_repository,
    get_note_service,
    get_pin_settings_manager,
    get_unlock_session_manager,
)
from src.app.services import NoteCapacityError


def _clear_runtime_caches() -> None:
    get_config_service.cache_clear()
    get_app_logger.cache_clear()
    get_app_startup.cache_clear()
    get_crypto_service.cache_clear()
    get_note_repository.cache_clear()
    get_audit_logger.cache_clear()
    get_pin_settings_manager.cache_clear()
    get_unlock_session_manager.cache_clear()


@pytest.mark.unit
def test_note_service_uses_configured_max_notes(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"max_notes": 1}), encoding="utf-8")
    monkeypatch.setenv("ASTRANOTE_CONFIG_PATH", str(config_path))
    _clear_runtime_caches()

    repository = get_note_repository()
    audit_logger = get_audit_logger()
    service = get_note_service(note_repository=repository, audit_logger=audit_logger)

    service.create("First")

    with pytest.raises(NoteCapacityError):
        service.create("Second")

    repository.engine.dispose()


@pytest.mark.unit
def test_unlock_session_manager_uses_configured_timeout(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"inactivity_timeout_minutes": 3}), encoding="utf-8")
    monkeypatch.setenv("ASTRANOTE_CONFIG_PATH", str(config_path))
    _clear_runtime_caches()

    manager = get_unlock_session_manager()

    assert manager._unlock_timeout_minutes == 3