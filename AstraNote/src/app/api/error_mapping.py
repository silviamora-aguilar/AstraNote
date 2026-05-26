"""Error mapping helpers for note route surfaces."""

from __future__ import annotations

from fastapi import status

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
