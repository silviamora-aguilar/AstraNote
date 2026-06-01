"""Service layer for note workflows."""

from __future__ import annotations

import re

from src.app.models.note import Note
from src.app.repositories.note_repository import (
    NoteRepository,
    NoteRepositoryCapacityError,
    NoteRepositoryError,
    NoteRepositoryNotFoundError,
)

MAX_NOTES = 10_000
MAX_TITLE_LENGTH = 255
MAX_BODY_LENGTH = 10_000
CAPACITY_ERROR_MESSAGE = "Note limit reached (10,000). Delete notes to create a new one."
ALLOWED_TITLE_PUNCTUATION = {" ", ".", ",", "-", "'", '"', "@", "#", "&", ":", ";", "!", "?", "(", ")", "[", "]", "/", "+", "_", "¿", "¡"}
CHECKLIST_LINE_RE = re.compile(r"^(\s*[-*+]\s+\[)( |x|X)(\]\s.*)$")
UNICODE_CHECKLIST_LINE_RE = re.compile(r"^(\s*)(☐|☑)\s+(.*)$")


class NoteValidationError(ValueError):
    """Raised when input fails note validation rules."""


class NoteCapacityError(ValueError):
    """Raised when the repository is at capacity."""


class NotePersistenceError(RuntimeError):
    """Raised when persistent storage cannot complete an operation."""


class NoteNotFoundError(ValueError):
    """Raised when a requested note does not exist."""


class NoteService:
    """Business rules for note operations."""

    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def create(self, title: str, body: str = "", is_private: bool = False) -> Note:
        """Create and persist a new note using BL-01 rules."""
        cleaned_title = self._validate_title(title)
        cleaned_body = self._validate_body(body)
        try:
            return self.repository.create_note_atomic(
                title=cleaned_title,
                body=cleaned_body,
                is_private=is_private,
                max_notes=MAX_NOTES,
            )
        except NoteRepositoryCapacityError as exc:
            raise NoteCapacityError(CAPACITY_ERROR_MESSAGE) from exc
        except NoteRepositoryError as exc:
            raise NotePersistenceError("Could not persist note") from exc

    def list_notes(self) -> list[Note]:
        """Return active notes newest-first from the repository."""
        return self.repository.list()

    def get_note(self, note_id: str) -> Note | None:
        """Get an active note by id."""
        note = self.repository.get(note_id)
        if note is None or note.is_deleted:
            return None
        return note

    def delete(self, note_id: str) -> None:
        """Soft-delete a note by id (BL-03)."""
        note = self.repository.get(note_id)
        if note is None or note.is_deleted:
            raise NoteNotFoundError("Note not found")
        try:
            self.repository.soft_delete(note_id)
        except NoteRepositoryError as exc:
            raise NotePersistenceError("Could not delete note") from exc

    def bulk_delete(self, note_ids: list[str]) -> int:
        """Soft-delete multiple notes for BL-03.1 bulk-delete workflow."""
        unique_note_ids = list(dict.fromkeys(note_ids))
        if not unique_note_ids:
            raise NoteValidationError("Select at least one note to delete")

        deleted_count = 0
        for note_id in unique_note_ids:
            note = self.repository.get(note_id)
            if note is None or note.is_deleted:
                continue
            try:
                if self.repository.soft_delete(note_id):
                    deleted_count += 1
            except NoteRepositoryError as exc:
                raise NotePersistenceError("Could not delete selected notes") from exc

        if deleted_count == 0:
            raise NoteNotFoundError("Selected notes were not found")
        return deleted_count

    def search(self, query: str) -> list[Note]:
        """Return active notes matching query in title or body."""
        normalized_query = (query or "").strip()
        if not normalized_query:
            return self.repository.list()
        return self.repository.search(normalized_query)

    def update(self, note_id: str, title: str, body: str = "", is_private: bool = False) -> Note:
        """Update title/body using BL-02 rules."""
        cleaned_title = self._validate_title(title)
        cleaned_body = self._validate_body(body)
        try:
            return self.repository.update_note_atomic(
                note_id=note_id,
                title=cleaned_title,
                body=cleaned_body,
                is_private=is_private,
            )
        except NoteRepositoryNotFoundError as exc:
            raise NoteNotFoundError("Note not found") from exc
        except NoteRepositoryError as exc:
            raise NotePersistenceError("Could not persist note") from exc

    def toggle_checklist_item(self, note_id: str, line_index: int, checked: bool) -> Note:
        """Toggle a checklist item (`- [ ]`/`- [x]`) and persist immediately."""
        note = self.get_note(note_id)
        if note is None:
            raise NoteNotFoundError("Note not found")
        if line_index < 0:
            raise NoteValidationError("Checklist item index must be non-negative")

        lines = note.body.split("\n")
        checklist_line_positions: list[int] = []
        for idx, line in enumerate(lines):
            if CHECKLIST_LINE_RE.match(line) or UNICODE_CHECKLIST_LINE_RE.match(line):
                checklist_line_positions.append(idx)

        if line_index >= len(checklist_line_positions):
            raise NoteValidationError("Checklist item index is out of range")

        target_line_idx = checklist_line_positions[line_index]
        line = lines[target_line_idx]
        line_match = CHECKLIST_LINE_RE.match(line)
        unicode_match = UNICODE_CHECKLIST_LINE_RE.match(line)
        if line_match is not None:
            replacement_mark = "x" if checked else " "
            lines[target_line_idx] = f"{line_match.group(1)}{replacement_mark}{line_match.group(3)}"
        elif unicode_match is not None:
            replacement_mark = "☑" if checked else "☐"
            lines[target_line_idx] = f"{unicode_match.group(1)}{replacement_mark} {unicode_match.group(3)}"
        else:
            raise NoteValidationError("Checklist item format is invalid")
        updated_body = "\n".join(lines)
        return self.update(
            note_id=note.note_id,
            title=note.title,
            body=updated_body,
            is_private=note.is_private,
        )

    def _validate_title(self, title: str) -> str:
        if title is None:
            raise NoteValidationError("Title is required")

        trimmed_title = title.strip()
        if not trimmed_title:
            raise NoteValidationError("Title is required")
        if len(trimmed_title) > MAX_TITLE_LENGTH:
            raise NoteValidationError("Title must be 1-255 characters")

        for char in trimmed_title:
            if char in {"\n", "\r"}:
                raise NoteValidationError("Title cannot contain newlines")
            if char.isalnum() or char in ALLOWED_TITLE_PUNCTUATION:
                continue
            raise NoteValidationError(
                "Title contains unsupported symbols. Allowed punctuation: . , - ' \" @ # & : ; ! ? ( ) [ ] / + _ ¿ ¡"
            )

        return trimmed_title

    def _validate_body(self, body: str) -> str:
        safe_body = body or ""
        if len(safe_body) > MAX_BODY_LENGTH:
            raise NoteValidationError("Body must be 0-10000 characters")
        return safe_body

