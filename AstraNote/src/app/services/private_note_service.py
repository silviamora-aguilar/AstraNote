"""Service abstractions for private-note unlock and PIN management workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class _UnlockGateway(Protocol):
    def is_unlocked(self, note_id: str) -> bool: ...

    def attempt_unlock(self, note_id: str, pin: str) -> tuple[bool, str | None]: ...

    def reset_all(self) -> None: ...


class _PinSettingsGateway(Protocol):
    def get_pin(self) -> str: ...

    def verify_pin(self, pin: str) -> bool: ...

    def set_pin(self, new_pin: str) -> None: ...


class _PinCryptoGateway(Protocol):
    def validate_pin_format(self, pin: str) -> bool: ...

    def set_private_pin(self, pin: str) -> None: ...


class _PrivatePinRotationGateway(Protocol):
    def rotate_private_pin(self, old_pin: str, new_pin: str) -> int: ...


@dataclass(slots=True)
class PinChangeResult:
    """Result metadata for private PIN settings changes."""

    code: str
    verified_current_pin: str | None = None
    recovered_count: int = 0
    pin_update_completed: bool = False


class PrivateNoteService:
    """Encapsulates private-note unlock and app-level PIN workflows."""

    def __init__(
        self,
        *,
        unlock_gateway: _UnlockGateway,
        pin_settings_gateway: _PinSettingsGateway,
        pin_crypto_gateway: _PinCryptoGateway,
        pin_rotation_gateway: _PrivatePinRotationGateway,
    ) -> None:
        self._unlock = unlock_gateway
        self._pin_settings = pin_settings_gateway
        self._pin_crypto = pin_crypto_gateway
        self._pin_rotation = pin_rotation_gateway

    def is_unlocked(self, note_id: str) -> bool:
        return self._unlock.is_unlocked(note_id)

    def attempt_unlock(self, note_id: str, pin: str) -> tuple[bool, str | None]:
        return self._unlock.attempt_unlock(note_id, pin)

    def verify_current_pin(self, current_pin: str) -> PinChangeResult:
        """Validate current PIN before revealing update fields."""
        if not self._pin_crypto.validate_pin_format(current_pin):
            return PinChangeResult(code="current_pin_format")

        if not self._pin_settings.verify_pin(current_pin):
            return PinChangeResult(code="current_pin_incorrect")

        return PinChangeResult(code="verified", verified_current_pin=current_pin)

    def change_pin(self, current_pin: str, new_pin: str, confirm_pin: str) -> PinChangeResult:
        """Rotate private-note encryption PIN while preserving existing UX behavior."""
        if not self._pin_crypto.validate_pin_format(current_pin):
            return PinChangeResult(code="current_pin_incorrect")

        resolution = self._resolve_current_pin(current_pin)
        if resolution is None:
            return PinChangeResult(code="current_pin_incorrect")

        effective_current_pin, recovered_count = resolution

        validation_result = self._validate_new_pin_inputs(
            effective_current_pin, recovered_count, new_pin, confirm_pin
        )
        if validation_result is not None:
            return validation_result

        try:
            self._pin_rotation.rotate_private_pin(old_pin=effective_current_pin, new_pin=new_pin)
            self._pin_settings.set_pin(new_pin)
            self._pin_crypto.set_private_pin(new_pin)
            self._unlock.reset_all()
        except Exception:
            return PinChangeResult(
                code="update_failed",
                verified_current_pin=effective_current_pin,
                recovered_count=recovered_count,
            )

        return PinChangeResult(
            code="updated",
            verified_current_pin=new_pin,
            recovered_count=recovered_count,
            pin_update_completed=True,
        )

    def _resolve_current_pin(self, current_pin: str) -> tuple[str, int] | None:
        active_pin = self._pin_settings.get_pin()
        if self._pin_settings.verify_pin(current_pin):
            return current_pin, 0

        try:
            recovered_count = self._pin_rotation.rotate_private_pin(
                old_pin=current_pin, new_pin=active_pin
            )
        except Exception:
            recovered_count = 0

        if recovered_count <= 0:
            return None

        self._unlock.reset_all()
        return active_pin, recovered_count

    def _validate_new_pin_inputs(
        self,
        effective_current_pin: str,
        recovered_count: int,
        new_pin: str,
        confirm_pin: str,
    ) -> PinChangeResult | None:
        if not self._pin_crypto.validate_pin_format(new_pin):
            return PinChangeResult(
                code="new_pin_format",
                verified_current_pin=effective_current_pin,
                recovered_count=recovered_count,
            )

        if new_pin != confirm_pin:
            return PinChangeResult(
                code="pin_mismatch",
                verified_current_pin=effective_current_pin,
                recovered_count=recovered_count,
            )

        if effective_current_pin != new_pin:
            return None

        unchanged_code = "pin_unchanged_after_recovery" if recovered_count > 0 else "pin_unchanged"
        return PinChangeResult(
            code=unchanged_code,
            verified_current_pin=effective_current_pin,
            recovered_count=recovered_count,
        )
