"""Unit tests for app-level private PIN settings."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.app.security import PinSettingsManager


@pytest.mark.unit
def test_pin_defaults_to_1234_when_config_missing(tmp_path: Path) -> None:
    manager = PinSettingsManager(config_file=tmp_path / "config.json")

    assert manager.get_pin() == "1234"
    assert manager.verify_pin("1234") is True
    assert manager.verify_pin("0000") is False


@pytest.mark.unit
def test_pin_set_persists_and_verifies(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    manager = PinSettingsManager(config_file=config_path)

    manager.set_pin("5678")

    raw_config = config_path.read_text(encoding="utf-8")
    assert '"private_pin":' not in raw_config
    assert '"private_pin_token":' in raw_config

    reloaded = PinSettingsManager(config_file=config_path)
    assert reloaded.get_pin() == "5678"
    assert reloaded.verify_pin("5678") is True
    assert reloaded.verify_pin("1234") is False


@pytest.mark.unit
def test_legacy_plaintext_pin_migrates_to_encrypted_token(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"private_pin": "2468"}', encoding="utf-8")

    manager = PinSettingsManager(config_file=config_path)

    migrated = config_path.read_text(encoding="utf-8")
    assert '"private_pin":' not in migrated
    assert '"private_pin_token":' in migrated

    assert manager.get_pin() == "2468"
