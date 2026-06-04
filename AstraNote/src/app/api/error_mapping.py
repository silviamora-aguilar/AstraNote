"""Error mapping helpers for note route surfaces."""

from __future__ import annotations

from fastapi import status

from src.app.dependencies import get_app_logger
from src.app.services import NoteCapacityError, NoteNotFoundError, NotePersistenceError, NoteValidationError


def map_note_error_status(exc: Exception) -> int:
    """Map domain errors to consistent HTTP status codes."""
    if isinstance(exc, NoteValidationError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, NoteCapacityError):
        return status.HTTP_409_CONFLICT
    if isinstance(exc, NoteNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, NotePersistenceError):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def map_note_error_message(exc: Exception) -> str:
    """Return user-safe error messages for route responses."""
    if isinstance(exc, (NoteValidationError, NoteCapacityError, NoteNotFoundError)):
        return str(exc)
    if isinstance(exc, NotePersistenceError):
        return "Storage temporarily unavailable. Please try again."
    return "Unexpected error while processing note request."


def map_note_error_code(exc: Exception) -> str:
    """Return a deterministic machine-readable error code."""
    if isinstance(exc, NoteValidationError):
        return "VALIDATION_ERROR"
    if isinstance(exc, NoteCapacityError):
        return "CAPACITY_EXCEEDED"
    if isinstance(exc, NoteNotFoundError):
        return "NOT_FOUND"
    if isinstance(exc, NotePersistenceError):
        return "SAVE_ERROR"
    return "INTERNAL_ERROR"


def log_note_exception(exc: Exception, *, surface: str, operation: str, note_id: str | None = None) -> None:
    """Write a user-safe diagnostic entry for note route failures."""
    logger = get_app_logger()
    level = "warning" if isinstance(exc, (NoteValidationError, NoteCapacityError, NoteNotFoundError, NotePersistenceError)) else "error"
    getattr(logger, level)(
        f"{surface} note operation failed.",
        tier=surface,
        operation=operation,
        note_id=note_id,
        error_code=map_note_error_code(exc),
        exception_type=type(exc).__name__,
    )
