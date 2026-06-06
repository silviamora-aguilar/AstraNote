"""Unit tests for deterministic note error codes."""

from __future__ import annotations

import pytest

from src.app.api.error_mapping import map_note_error_code
from src.app.services import (
    NoteCapacityError,
    NoteNotFoundError,
    NotePersistenceError,
    NoteValidationError,
)


@pytest.mark.unit
def test_note_error_codes_are_deterministic() -> None:
    cases = [
        (NoteValidationError("bad input"), "VALIDATION_ERROR"),
        (NoteCapacityError("full"), "CAPACITY_EXCEEDED"),
        (NoteNotFoundError("missing"), "NOT_FOUND"),
        (NotePersistenceError("db unavailable"), "SAVE_ERROR"),
    ]

    for exc, expected_code in cases:
        assert map_note_error_code(exc) == expected_code
        assert map_note_error_code(exc) == expected_code


@pytest.mark.unit
def test_unknown_error_uses_internal_error_code() -> None:
    assert map_note_error_code(RuntimeError("boom")) == "INTERNAL_ERROR"
