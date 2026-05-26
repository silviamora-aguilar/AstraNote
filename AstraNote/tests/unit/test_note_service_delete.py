"""Unit tests for NoteService.delete — BL-03.

Test plan coverage:
  TP-U11  soft delete sets is_deleted and deleted_at         (REQ-09, REQ-10, SRG-10)
  TP-U12  soft-deleted note excluded from list               (REQ-11, SRG-11)
  TP-U13  soft-deleted note excluded from search             (REQ-11, SRG-11)

Additional edge cases:
  delete unknown note raises NoteNotFoundError
  delete already-deleted note raises NoteNotFoundError
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.app.models.note import Note
from src.app.repositories.note_repository import (
    NoteRepository,
    NoteRepositoryCapacityError,
    NoteRepositoryError,
    NoteRepositoryNotFoundError,
)
from src.app.services.note_service import (
    NoteNotFoundError,
    NotePersistenceError,
    NoteService,
    NoteValidationError,
)


# ---------------------------------------------------------------------------
# Minimal fake repository scoped to delete tests
# ---------------------------------------------------------------------------

class FakeDeleteRepository(NoteRepository):
    """In-memory fake that implements the full repository interface."""

    def __init__(self) -> None:
        self.notes: list[Note] = []

    # --- write operations --------------------------------------------------

    def create_note_atomic(self, title, body, is_private, max_notes):
        if self.count_active_notes() >= max_notes:
            raise NoteRepositoryCapacityError("capacity reached")
        note = Note.new(title=title, body=body, is_private=is_private)
        self.notes.append(note)
        return note

    def save(self, note: Note) -> Note:
        self.notes.append(note)
        return note

    def update_note_atomic(self, note_id, title, body, is_private):
        note = self.get(note_id)
        if note is None or note.is_deleted:
            raise NoteRepositoryNotFoundError("not found")
        note.title = title
        note.body = body
        note.is_private = is_private
        note.updated_at = datetime.now(timezone.utc)
        return note

    def soft_delete(self, note_id: str) -> bool:
        note = self.get(note_id)
        if note is None or note.is_deleted:
            return False
        note.is_deleted = True
        note.deleted_at = datetime.now(timezone.utc)
        return True

    def restore(self, note_id: str) -> bool:
        note = self.get(note_id)
        if note is None or not note.is_deleted:
            return False
        note.is_deleted = False
        note.deleted_at = None
        return True

    # --- read operations ---------------------------------------------------

    def get(self, note_id: str) -> Note | None:
        return next((n for n in self.notes if n.note_id == note_id), None)

    def list(self) -> list[Note]:
        return [n for n in self.notes if not n.is_deleted]

    def search(self, query: str) -> list[Note]:
        q = query.lower()
        return [
            n for n in self.notes
            if not n.is_deleted and (q in n.title.lower() or q in n.body.lower())
        ]

    def count_active_notes(self) -> int:
        return sum(1 for n in self.notes if not n.is_deleted)

    def title_exists(self, title: str) -> bool:
        return any(n.title == title and not n.is_deleted for n in self.notes)

    def title_exists_for_other(self, title: str, note_id: str) -> bool:
        return any(
            n.title == title and n.note_id != note_id and not n.is_deleted
            for n in self.notes
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service() -> tuple[NoteService, FakeDeleteRepository]:
    repo = FakeDeleteRepository()
    service = NoteService(repo)
    return service, repo


# ---------------------------------------------------------------------------
# TP-U11 — soft delete sets is_deleted and deleted_at
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_delete_note_sets_is_deleted_and_deleted_at():
    """TP-U11: deleting a note marks it is_deleted=True and sets deleted_at."""
    service, repo = _make_service()
    note = service.create(title="Temp Note")

    service.delete(note.note_id)

    raw = repo.get(note.note_id)
    assert raw is not None
    assert raw.is_deleted is True
    assert raw.deleted_at is not None


# ---------------------------------------------------------------------------
# TP-U12 — soft-deleted note excluded from list
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_delete_note_excluded_from_list():
    """TP-U12: after delete, note no longer appears in list()."""
    service, repo = _make_service()
    note = service.create(title="Listed Note")
    assert any(n.note_id == note.note_id for n in service.list_notes())

    service.delete(note.note_id)

    assert not any(n.note_id == note.note_id for n in service.list_notes())


@pytest.mark.unit
def test_delete_note_keeps_other_notes_in_list():
    """TP-U12 variant: deleting one note does not remove other notes from list."""
    service, _ = _make_service()
    note_a = service.create(title="Keep Me")
    note_b = service.create(title="Delete Me")

    service.delete(note_b.note_id)

    ids = [n.note_id for n in service.list_notes()]
    assert note_a.note_id in ids
    assert note_b.note_id not in ids


# ---------------------------------------------------------------------------
# TP-U13 — soft-deleted note excluded from search
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_delete_note_excluded_from_search():
    """TP-U13: after delete, note does not appear in search results."""
    service, _ = _make_service()
    note = service.create(title="Searchable Note", body="unique content xyz")

    service.delete(note.note_id)

    results = service.search("unique content xyz")
    assert not any(n.note_id == note.note_id for n in results)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_delete_unknown_note_raises_not_found():
    """Deleting a note that does not exist raises NoteNotFoundError."""
    service, _ = _make_service()
    with pytest.raises(NoteNotFoundError):
        service.delete("nonexistent-id")


@pytest.mark.unit
def test_delete_already_deleted_note_raises_not_found():
    """Deleting an already-deleted note raises NoteNotFoundError."""
    service, _ = _make_service()
    note = service.create(title="Gone Note")
    service.delete(note.note_id)

    with pytest.raises(NoteNotFoundError):
        service.delete(note.note_id)


@pytest.mark.unit
def test_get_note_returns_none_after_delete():
    """get_note() returns None for a soft-deleted note."""
    service, _ = _make_service()
    note = service.create(title="Hidden Note")

    service.delete(note.note_id)

    assert service.get_note(note.note_id) is None


@pytest.mark.unit
def test_bulk_delete_selected_notes_marks_all_deleted():
    """BL-03.1: bulk delete marks selected notes as deleted."""
    service, repo = _make_service()
    note_a = service.create(title="Bulk A")
    note_b = service.create(title="Bulk B")
    note_c = service.create(title="Bulk C")

    deleted_count = service.bulk_delete([note_a.note_id, note_c.note_id])

    assert deleted_count == 2
    assert repo.get(note_a.note_id).is_deleted is True
    assert repo.get(note_b.note_id).is_deleted is False
    assert repo.get(note_c.note_id).is_deleted is True


@pytest.mark.unit
def test_bulk_delete_rejects_empty_selection():
    """BL-03.1: empty selection is a validation error."""
    service, _ = _make_service()
    with pytest.raises(NoteValidationError):
        service.bulk_delete([])


@pytest.mark.unit
def test_bulk_delete_raises_not_found_when_no_ids_match():
    """BL-03.1: no matches in selection raises NoteNotFoundError."""
    service, _ = _make_service()
    with pytest.raises(NoteNotFoundError):
        service.bulk_delete(["missing-1", "missing-2"])


@pytest.mark.unit
def test_search_whitespace_query_returns_full_active_list():
    """BL-05: whitespace-only query should return full list."""
    service, _ = _make_service()
    note_a = service.create(title="Alpha", body="first")
    note_b = service.create(title="Bravo", body="second")
    service.delete(note_b.note_id)

    results = service.search("   ")

    assert [note.note_id for note in results] == [note_a.note_id]


@pytest.mark.unit
def test_search_trims_query_before_repository_match():
    """BL-05: query trimming should still return the expected match."""
    service, _ = _make_service()
    target = service.create(title="Project Plan", body="Milestone notes")
    service.create(title="Unrelated", body="Something else")

    results = service.search("   project   ")

    assert [note.note_id for note in results] == [target.note_id]
