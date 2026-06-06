"""Unit tests for diagnostic application logging."""

from __future__ import annotations

import json

import pytest

from src.app.runtime.app_logger import AppLogger


@pytest.mark.unit
def test_app_logger_writes_structured_entry(tmp_path) -> None:
    log_path = tmp_path / "astranote.log"
    logger = AppLogger(log_path, level="INFO")

    logger.warning(
        "Route failure.", tier="ui", operation="create", note_id="n-1", error_code="SAVE_ERROR"
    )

    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["severity"] == "WARNING"
    assert entry["message"] == "Route failure."
    assert entry["tier"] == "ui"
    assert entry["operation"] == "create"
    assert entry["note_id"] == "n-1"


@pytest.mark.unit
def test_app_logger_rotates_files(tmp_path) -> None:
    log_path = tmp_path / "astranote.log"
    logger = AppLogger(log_path, level="INFO", max_bytes=120, backup_count=2)

    for index in range(12):
        logger.info(f"entry-{index}", tier="runtime")

    rotated = sorted(path.name for path in tmp_path.glob("astranote.log*"))
    assert "astranote.log" in rotated
    assert any(name.endswith(".1") for name in rotated)


@pytest.mark.unit
def test_app_logger_rejects_note_plaintext_fields(tmp_path) -> None:
    logger = AppLogger(tmp_path / "astranote.log")

    with pytest.raises(ValueError, match="plaintext fields"):
        logger.error("bad", title="Secret Note")
