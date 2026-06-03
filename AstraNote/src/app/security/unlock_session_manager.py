"""Private-note unlock session state and lockout controls."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.app.security.crypto_service import CryptoService


@dataclass(slots=True)
class _UnlockState:
    failed_attempts: int
    lockout_level: int
    lockout_until: datetime | None
    unlocked_until: datetime | None


class UnlockSessionManager:
    """Tracks unlock state for private notes in single-user local mode."""

    def __init__(
        self,
        crypto_service: CryptoService,
        state_file=None,
        unlock_timeout_minutes: int = 15,
    ) -> None:
        self._crypto_service = crypto_service
        self._unlock_timeout_minutes = unlock_timeout_minutes
        self._state_file = state_file
        self._states: dict[str, _UnlockState] = {}

    def is_unlocked(self, note_id: str) -> bool:
        state = self._states.get(note_id)
        if state is None or state.unlocked_until is None:
            return False
        now = datetime.now(timezone.utc)
        if state.unlocked_until <= now:
            state.unlocked_until = None
            return False
        return True

    def attempt_unlock(self, note_id: str, pin: str) -> tuple[bool, str | None]:
        now = datetime.now(timezone.utc)
        state = self._states.setdefault(
            note_id,
            _UnlockState(failed_attempts=0, lockout_level=0, lockout_until=None, unlocked_until=None),
        )

        if state.lockout_until is not None and state.lockout_until > now:
            remaining = int((state.lockout_until - now).total_seconds())
            return False, f"Enter correct pin to unlock private note. Try again in {max(1, remaining)}s."

        try:
            is_valid_pin = self._crypto_service.verify_pin(pin)
        except Exception:
            is_valid_pin = False

        if not is_valid_pin:
            state.failed_attempts += 1
            if state.failed_attempts >= 5:
                state.lockout_level += 1
                duration_seconds = 300 * (2 ** (state.lockout_level - 1))
                state.lockout_until = now + timedelta(seconds=duration_seconds)
                state.failed_attempts = 0
            return False, "Enter correct pin to unlock private note."

        state.failed_attempts = 0
        state.lockout_until = None
        state.unlocked_until = now + timedelta(minutes=self._unlock_timeout_minutes)
        return True, None

    def lock(self, note_id: str) -> None:
        state = self._states.setdefault(
            note_id,
            _UnlockState(failed_attempts=0, lockout_level=0, lockout_until=None, unlocked_until=None),
        )
        state.unlocked_until = None

    def reset_all(self) -> None:
        """Clear all per-note unlock and lockout state."""
        self._states.clear()
