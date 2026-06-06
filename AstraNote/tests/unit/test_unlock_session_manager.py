"""Unit tests for private-note unlock session controls."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.app.security import CryptoService, UnlockSessionManager


@pytest.mark.unit
def test_unlock_requires_valid_pin_and_sets_session_timeout(tmp_path: Path) -> None:
    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(CryptoService(private_pin="1234"), state_file=state_file)

    assert manager.is_unlocked("note-a") is False

    unlocked, error = manager.attempt_unlock("note-a", "1234")
    assert unlocked is True
    assert error is None
    assert manager.is_unlocked("note-a") is True

    other_note_unlocked, other_note_error = manager.attempt_unlock("note-b", "0000")
    assert other_note_unlocked is False
    assert other_note_error == "Enter correct pin to unlock private note."
    assert manager.is_unlocked("note-b") is False


@pytest.mark.unit
def test_unlock_wrong_pin_is_rejected_with_generic_error(tmp_path: Path) -> None:
    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(CryptoService(private_pin="1234"), state_file=state_file)

    unlocked, error = manager.attempt_unlock("note-a", "0000")

    assert unlocked is False
    assert error == "Enter correct pin to unlock private note."
    assert manager.is_unlocked("note-a") is False


@pytest.mark.unit
def test_unlock_internal_pin_error_returns_same_user_message(tmp_path: Path) -> None:
    class _FailingCrypto:
        def verify_pin(self, _pin: str) -> bool:
            raise RuntimeError("crypto backend unavailable")

    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(_FailingCrypto(), state_file=state_file)

    unlocked, error = manager.attempt_unlock("note-a", "1234")

    assert unlocked is False
    assert error == "Enter correct pin to unlock private note."


@pytest.mark.unit
def test_unlock_lockout_triggers_after_five_failures_and_does_not_carry_over(
    tmp_path: Path,
) -> None:
    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(CryptoService(private_pin="1234"), state_file=state_file)

    for _ in range(5):
        unlocked, _ = manager.attempt_unlock("note-a", "0000")
        assert unlocked is False

    locked, lockout_error = manager.attempt_unlock("note-a", "1234")
    assert locked is False
    assert lockout_error is not None
    assert "Try again" in lockout_error

    # Lockout state must not survive manager recreation.
    reloaded = UnlockSessionManager(CryptoService(private_pin="1234"), state_file=state_file)
    unlocked_again, lockout_error_again = reloaded.attempt_unlock("note-a", "1234")
    assert unlocked_again is True
    assert lockout_error_again is None


@pytest.mark.unit
def test_unlock_inactivity_expires_session(tmp_path: Path) -> None:
    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(
        CryptoService(private_pin="1234"), state_file=state_file, unlock_timeout_minutes=15
    )

    unlocked, error = manager.attempt_unlock("note-a", "1234")
    assert unlocked is True
    assert error is None
    assert manager.is_unlocked("note-a") is True

    manager._states["note-a"].unlocked_until = datetime.now(timezone.utc) - timedelta(minutes=16)
    assert manager.is_unlocked("note-a") is False
    assert manager.is_unlocked("note-a") is False
