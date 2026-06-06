"""Additional unit tests for UnlockSessionManager lockout behavior."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.app.security import CryptoService, UnlockSessionManager


@pytest.mark.unit
def test_unlock_lockout_duration_doubles_on_second_lockout(tmp_path: Path) -> None:
    """TP-S11: successive lockouts should double in duration."""
    state_file = tmp_path / "security-state.json"
    manager = UnlockSessionManager(CryptoService(private_pin="1234"), state_file=state_file)

    for _ in range(5):
        unlocked, _ = manager.attempt_unlock("note-a", "0000")
        assert unlocked is False

    first_state = manager._states["note-a"]
    first_duration = int((first_state.lockout_until - datetime.now(timezone.utc)).total_seconds())
    assert 295 <= first_duration <= 300

    first_state.lockout_until = datetime.now(timezone.utc) - timedelta(seconds=1)

    for _ in range(5):
        unlocked, _ = manager.attempt_unlock("note-a", "0000")
        assert unlocked is False

    second_state = manager._states["note-a"]
    second_duration = int((second_state.lockout_until - datetime.now(timezone.utc)).total_seconds())
    assert 595 <= second_duration <= 600
