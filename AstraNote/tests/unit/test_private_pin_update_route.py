"""Unit tests for the private PIN update route behavior."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from src.app.api import notes_ui
from src.app.services.private_note_service import PinChangeResult


def _patch_render_pin_panel(monkeypatch: pytest.MonkeyPatch):
    def _fake_render(
        _request,
        error_message=None,
        success_message=None,
        verified_current_pin=None,
        pin_update_completed=False,
    ):
        return {
            "error": error_message,
            "success": success_message,
            "verified_current_pin": verified_current_pin,
            "pin_update_completed": pin_update_completed,
        }

    monkeypatch.setattr(notes_ui, "_render_pin_settings_panel", _fake_render)


def _patch_ui_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        notes_ui,
        "_ui_context",
        lambda _request: {
            "i18n": {
                "current_pin_label": "Current PIN",
                "new_pin_label": "New PIN",
                "change_private_pin": "Private PIN",
            }
        },
    )


@pytest.mark.unit
def test_update_private_pin_rejects_invalid_current_pin_format(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)
    _patch_ui_context(monkeypatch)
    private_note_service = Mock()
    private_note_service.change_pin.return_value = PinChangeResult(code="current_pin_incorrect")

    result = notes_ui.update_private_pin_settings(
        request=object(),
        private_note_service=private_note_service,
        current_pin="12ab",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] == "Current PIN is incorrect."
    assert result["success"] is None
    assert result["verified_current_pin"] is None
    assert result["pin_update_completed"] is False
    private_note_service.change_pin.assert_called_once_with(current_pin="12ab", new_pin="5678", confirm_pin="5678")


@pytest.mark.unit
def test_update_private_pin_successfully_rotates_and_persists_new_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)
    _patch_ui_context(monkeypatch)
    private_note_service = Mock()
    private_note_service.change_pin.return_value = PinChangeResult(
        code="updated",
        verified_current_pin="5678",
        pin_update_completed=True,
    )

    result = notes_ui.update_private_pin_settings(
        request=object(),
        private_note_service=private_note_service,
        current_pin="1234",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] is None
    assert result["success"] == "Private PIN updated."
    assert result["verified_current_pin"] == "5678"
    assert result["pin_update_completed"] is True
    private_note_service.change_pin.assert_called_once_with(current_pin="1234", new_pin="5678", confirm_pin="5678")


@pytest.mark.unit
def test_update_private_pin_rejects_when_current_pin_wrong_and_no_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)
    _patch_ui_context(monkeypatch)
    private_note_service = Mock()
    private_note_service.change_pin.return_value = PinChangeResult(code="current_pin_incorrect")

    result = notes_ui.update_private_pin_settings(
        request=object(),
        private_note_service=private_note_service,
        current_pin="1234",
        new_pin="9999",
        confirm_pin="9999",
    )

    assert result["error"] == "Current PIN is incorrect."
    assert result["success"] is None
    assert result["verified_current_pin"] is None
    assert result["pin_update_completed"] is False
    private_note_service.change_pin.assert_called_once_with(current_pin="1234", new_pin="9999", confirm_pin="9999")


@pytest.mark.unit
def test_update_private_pin_recovery_branch_allows_pin_unchanged_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)
    _patch_ui_context(monkeypatch)
    private_note_service = Mock()
    private_note_service.change_pin.return_value = PinChangeResult(
        code="pin_unchanged_after_recovery",
        verified_current_pin="5678",
        recovered_count=2,
    )

    result = notes_ui.update_private_pin_settings(
        request=object(),
        private_note_service=private_note_service,
        current_pin="1234",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] is None
    assert result["success"] == "Recovered 2 private notes from a previous PIN. PIN unchanged."
    assert result["verified_current_pin"] == "5678"
    assert result["pin_update_completed"] is False
    private_note_service.change_pin.assert_called_once_with(current_pin="1234", new_pin="5678", confirm_pin="5678")


@pytest.mark.unit
def test_update_private_pin_mismatch_preserves_verified_current_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)
    _patch_ui_context(monkeypatch)
    private_note_service = Mock()
    private_note_service.change_pin.return_value = PinChangeResult(
        code="pin_mismatch",
        verified_current_pin="1234",
    )

    result = notes_ui.update_private_pin_settings(
        request=object(),
        private_note_service=private_note_service,
        current_pin="1234",
        new_pin="1111",
        confirm_pin="2222",
    )

    assert result["error"] == "New PIN and confirmation do not match."
    assert result["success"] is None
    assert result["verified_current_pin"] == "1234"
    assert result["pin_update_completed"] is False
    private_note_service.change_pin.assert_called_once_with(current_pin="1234", new_pin="1111", confirm_pin="2222")