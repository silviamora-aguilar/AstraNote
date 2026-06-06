"""Unit tests for local runtime startup checks."""

from __future__ import annotations

import json

import pytest

from src.app.runtime import AppLogger, AppStartup, ConfigService


@pytest.mark.unit
def test_app_startup_creates_missing_data_dir(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    data_dir = tmp_path / "app-data"
    config_path.write_text(json.dumps({"data_dir": str(data_dir)}), encoding="utf-8")
    config = ConfigService(config_file=config_path)
    logger = AppLogger(tmp_path / "startup.log")

    startup = AppStartup(config, logger)
    startup.initialize()

    assert data_dir.exists()
    assert (data_dir / "astranote.db").exists()


@pytest.mark.unit
def test_app_startup_fails_fast_for_corrupt_store(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    data_dir = tmp_path / "app-data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "astranote.db").write_text("not a sqlite database", encoding="utf-8")
    config_path.write_text(json.dumps({"data_dir": str(data_dir)}), encoding="utf-8")
    config = ConfigService(config_file=config_path)
    logger = AppLogger(tmp_path / "startup.log")

    startup = AppStartup(config, logger)

    with pytest.raises(RuntimeError, match="could not open the local note store"):
        startup.initialize()


@pytest.mark.unit
def test_create_app_health_exposes_version(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("ASTRANOTE_CONFIG_PATH", str(config_path))

    from src.app.dependencies import (
        get_app_logger,
        get_app_startup,
        get_config_service,
        get_crypto_service,
        get_note_repository,
        get_pin_settings_manager,
        get_unlock_session_manager,
    )

    get_config_service.cache_clear()
    get_app_logger.cache_clear()
    get_app_startup.cache_clear()
    get_crypto_service.cache_clear()
    get_note_repository.cache_clear()
    get_pin_settings_manager.cache_clear()
    get_unlock_session_manager.cache_clear()

    from src.main import create_app

    app = create_app()
    health = next(
        route.endpoint for route in app.routes if getattr(route, "path", None) == "/health"
    )()

    assert health["status"] == "ok"
    assert health["version"] == "0.1.0"
