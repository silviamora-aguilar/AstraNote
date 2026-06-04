"""Unit tests for runtime configuration loading."""

from __future__ import annotations

import json

import pytest

from src.app.runtime.config_service import ConfigService


@pytest.mark.unit
def test_config_service_uses_config_path_parent_as_default_data_dir(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("ASTRANOTE_CONFIG_PATH", str(config_path))

    service = ConfigService()

    assert service.config_path == config_path.resolve()
    assert service.data_dir_path == tmp_path.resolve()


@pytest.mark.unit
def test_config_service_invalid_values_fall_back_to_defaults(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "log_level": "LOUD",
                "inactivity_timeout_minutes": -5,
                "max_notes": 0,
                "unknown_key": "ignored",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ASTRANOTE_CONFIG_PATH", str(config_path))

    service = ConfigService()

    assert service.get("log_level") == "INFO"
    assert service.get("inactivity_timeout_minutes") == 15
    assert service.get("max_notes") == 10_000
    assert len(service.get_warnings()) == 3


@pytest.mark.unit
def test_config_service_accepts_supported_values(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "log_level": "debug",
                "data_dir": str(tmp_path / "data-home"),
                "inactivity_timeout_minutes": 22,
                "max_notes": 250,
                "private_pin_token": "abc",
                "private_pin_version": 2,
            }
        ),
        encoding="utf-8",
    )

    service = ConfigService(config_file=config_path)

    assert service.get("log_level") == "DEBUG"
    assert service.data_dir_path == (tmp_path / "data-home").resolve()
    assert service.get("inactivity_timeout_minutes") == 22
    assert service.get("max_notes") == 250
    assert service.get("private_pin_token") == "abc"