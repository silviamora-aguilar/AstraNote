"""Unit tests for PrivateNoteService abstraction and PIN workflow behavior."""

from __future__ import annotations

import pytest

from src.app.services.private_note_service import PrivateNoteService


class _FakeUnlockGateway:
    def __init__(self) -> None:
        self.unlocked: set[str] = set()
        self.reset_calls = 0

    def is_unlocked(self, note_id: str) -> bool:
        return note_id in self.unlocked

    def attempt_unlock(self, note_id: str, pin: str) -> tuple[bool, str | None]:
        if pin == "1234":
            self.unlocked.add(note_id)
            return True, None
        return False, "wrong pin"

    def reset_all(self) -> None:
        self.unlocked.clear()
        self.reset_calls += 1


class _FakePinSettingsGateway:
    def __init__(self, active_pin: str = "1234") -> None:
        self.active_pin = active_pin

    def get_pin(self) -> str:
        return self.active_pin

    def verify_pin(self, pin: str) -> bool:
        return pin == self.active_pin

    def set_pin(self, new_pin: str) -> None:
        self.active_pin = new_pin


class _FakePinCryptoGateway:
    @staticmethod
    def validate_pin_format(pin: str) -> bool:
        return pin.isdigit() and len(pin) == 4

    def __init__(self) -> None:
        self.private_pin = "1234"

    def set_private_pin(self, pin: str) -> None:
        self.private_pin = pin


class _FakeRotationGateway:
    def __init__(self, recover_count: int = 0) -> None:
        self.recover_count = recover_count
        self.calls: list[tuple[str, str]] = []

    def rotate_private_pin(self, old_pin: str, new_pin: str) -> int:
        self.calls.append((old_pin, new_pin))
        if old_pin != "1234" and new_pin == "1234":
            return self.recover_count
        return self.recover_count if (old_pin, new_pin) != ("1234", "5678") else 2


@pytest.mark.unit
def test_verify_current_pin_rejects_invalid_format() -> None:
    service = PrivateNoteService(
        unlock_gateway=_FakeUnlockGateway(),
        pin_settings_gateway=_FakePinSettingsGateway(),
        pin_crypto_gateway=_FakePinCryptoGateway(),
        pin_rotation_gateway=_FakeRotationGateway(),
    )

    result = service.verify_current_pin("12")

    assert result.code == "current_pin_format"


@pytest.mark.unit
def test_verify_current_pin_accepts_valid_active_pin() -> None:
    service = PrivateNoteService(
        unlock_gateway=_FakeUnlockGateway(),
        pin_settings_gateway=_FakePinSettingsGateway(active_pin="2468"),
        pin_crypto_gateway=_FakePinCryptoGateway(),
        pin_rotation_gateway=_FakeRotationGateway(),
    )

    result = service.verify_current_pin("2468")

    assert result.code == "verified"
    assert result.verified_current_pin == "2468"


@pytest.mark.unit
def test_change_pin_updates_pin_and_marks_completed() -> None:
    unlock = _FakeUnlockGateway()
    settings = _FakePinSettingsGateway(active_pin="1234")
    crypto = _FakePinCryptoGateway()
    rotation = _FakeRotationGateway()
    service = PrivateNoteService(
        unlock_gateway=unlock,
        pin_settings_gateway=settings,
        pin_crypto_gateway=crypto,
        pin_rotation_gateway=rotation,
    )

    result = service.change_pin(current_pin="1234", new_pin="5678", confirm_pin="5678")

    assert result.code == "updated"
    assert result.pin_update_completed is True
    assert result.verified_current_pin == "5678"
    assert settings.active_pin == "5678"
    assert crypto.private_pin == "5678"
    assert unlock.reset_calls == 1


@pytest.mark.unit
def test_change_pin_rejects_mismatch() -> None:
    service = PrivateNoteService(
        unlock_gateway=_FakeUnlockGateway(),
        pin_settings_gateway=_FakePinSettingsGateway(active_pin="1234"),
        pin_crypto_gateway=_FakePinCryptoGateway(),
        pin_rotation_gateway=_FakeRotationGateway(),
    )

    result = service.change_pin(current_pin="1234", new_pin="5678", confirm_pin="0000")

    assert result.code == "pin_mismatch"
    assert result.pin_update_completed is False


@pytest.mark.unit
def test_change_pin_allows_recovery_then_unchanged_success() -> None:
    unlock = _FakeUnlockGateway()
    settings = _FakePinSettingsGateway(active_pin="1234")
    rotation = _FakeRotationGateway(recover_count=3)
    service = PrivateNoteService(
        unlock_gateway=unlock,
        pin_settings_gateway=settings,
        pin_crypto_gateway=_FakePinCryptoGateway(),
        pin_rotation_gateway=rotation,
    )

    result = service.change_pin(current_pin="9999", new_pin="1234", confirm_pin="1234")

    assert result.code == "pin_unchanged_after_recovery"
    assert result.recovered_count == 3
    assert result.verified_current_pin == "1234"
    assert unlock.reset_calls == 1
