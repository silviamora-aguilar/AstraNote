"""Unit tests for the private PIN update route behavior."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from src.app.api import notes_ui


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


@pytest.mark.unit
def test_update_private_pin_rejects_invalid_current_pin_format(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)

    note_repository = Mock()
    crypto_service = Mock()
    pin_settings = Mock()
    unlock_manager = Mock()
    crypto_service.validate_pin_format.return_value = False

    result = notes_ui.update_private_pin_settings(
        request=object(),
        note_repository=note_repository,
        crypto_service=crypto_service,
        pin_settings=pin_settings,
        unlock_manager=unlock_manager,
        current_pin="12ab",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] == "Current PIN is incorrect."
    assert result["success"] is None
    assert result["verified_current_pin"] is None
    assert result["pin_update_completed"] is False
    note_repository.rotate_private_pin.assert_not_called()


@pytest.mark.unit
def test_update_private_pin_successfully_rotates_and_persists_new_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)

    note_repository = Mock()
    crypto_service = Mock()
    pin_settings = Mock()
    unlock_manager = Mock()
    crypto_service.validate_pin_format.return_value = True
    pin_settings.get_pin.return_value = "1234"
    pin_settings.verify_pin.return_value = True

    result = notes_ui.update_private_pin_settings(
        request=object(),
        note_repository=note_repository,
        crypto_service=crypto_service,
        pin_settings=pin_settings,
        unlock_manager=unlock_manager,
        current_pin="1234",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] is None
    assert result["success"] == "Private PIN updated."
    assert result["verified_current_pin"] == "5678"
    assert result["pin_update_completed"] is True
    note_repository.rotate_private_pin.assert_called_once_with(old_pin="1234", new_pin="5678")
    pin_settings.set_pin.assert_called_once_with("5678")
    crypto_service.set_private_pin.assert_called_once_with("5678")
    unlock_manager.reset_all.assert_called_once()


@pytest.mark.unit
def test_update_private_pin_rejects_when_current_pin_wrong_and_no_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)

    note_repository = Mock()
    crypto_service = Mock()
    pin_settings = Mock()
    unlock_manager = Mock()
    crypto_service.validate_pin_format.return_value = True
    pin_settings.get_pin.return_value = "5678"
    pin_settings.verify_pin.return_value = False
    note_repository.rotate_private_pin.return_value = 0

    result = notes_ui.update_private_pin_settings(
        request=object(),
        note_repository=note_repository,
        crypto_service=crypto_service,
        pin_settings=pin_settings,
        unlock_manager=unlock_manager,
        current_pin="1234",
        new_pin="9999",
        confirm_pin="9999",
    )

    assert result["error"] == "Current PIN is incorrect."
    assert result["success"] is None
    assert result["verified_current_pin"] is None
    assert result["pin_update_completed"] is False
    note_repository.rotate_private_pin.assert_called_once_with(old_pin="1234", new_pin="5678")
    pin_settings.set_pin.assert_not_called()
    crypto_service.set_private_pin.assert_not_called()
    unlock_manager.reset_all.assert_not_called()


@pytest.mark.unit
def test_update_private_pin_recovery_branch_allows_pin_unchanged_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)

    note_repository = Mock()
    crypto_service = Mock()
    pin_settings = Mock()
    unlock_manager = Mock()
    crypto_service.validate_pin_format.return_value = True
    pin_settings.get_pin.return_value = "5678"
    pin_settings.verify_pin.return_value = False
    note_repository.rotate_private_pin.return_value = 2

    result = notes_ui.update_private_pin_settings(
        request=object(),
        note_repository=note_repository,
        crypto_service=crypto_service,
        pin_settings=pin_settings,
        unlock_manager=unlock_manager,
        current_pin="1234",
        new_pin="5678",
        confirm_pin="5678",
    )

    assert result["error"] is None
    assert result["success"] == "Recovered 2 private notes from a previous PIN. PIN unchanged."
    assert result["verified_current_pin"] == "5678"
    assert result["pin_update_completed"] is False
    note_repository.rotate_private_pin.assert_called_once_with(old_pin="1234", new_pin="5678")
    pin_settings.set_pin.assert_not_called()
    crypto_service.set_private_pin.assert_not_called()
    unlock_manager.reset_all.assert_called_once()


@pytest.mark.unit
def test_update_private_pin_mismatch_preserves_verified_current_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_render_pin_panel(monkeypatch)

    note_repository = Mock()
    crypto_service = Mock()
    pin_settings = Mock()
    unlock_manager = Mock()
    crypto_service.validate_pin_format.return_value = True
    pin_settings.get_pin.return_value = "1234"
    pin_settings.verify_pin.return_value = True

    result = notes_ui.update_private_pin_settings(
        request=object(),
        note_repository=note_repository,
        crypto_service=crypto_service,
        pin_settings=pin_settings,
        unlock_manager=unlock_manager,
        current_pin="1234",
        new_pin="1111",
        confirm_pin="2222",
    )

    assert result["error"] == "New PIN and confirmation do not match."
    assert result["success"] is None
    assert result["verified_current_pin"] == "1234"
    assert result["pin_update_completed"] is False
    note_repository.rotate_private_pin.assert_not_called()