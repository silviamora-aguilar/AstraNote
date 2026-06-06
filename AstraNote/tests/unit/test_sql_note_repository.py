"""Unit tests for SqlNoteRepository persistence semantics (TP-R01..TP-R06)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.app.models.note import Note
from src.app.repositories.note_repository import NoteRepositoryError
from src.app.repositories.sql_note_repository import SqlNoteRepository


@pytest.mark.unit
def test_save_and_get_round_trip(tmp_path: Path) -> None:
    """TP-R01: saved note is recoverable with all key fields intact."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r01.db'}")
    try:
        note = Note.new(title="Repository Round Trip", body="Body payload", is_private=False)
        repository.save(note)

        restored = repository.get(note.note_id)

        assert restored is not None
        assert restored.note_id == note.note_id
        assert restored.title == "Repository Round Trip"
        assert restored.body == "Body payload"
        assert restored.created_at.replace(tzinfo=None) == note.created_at.replace(tzinfo=None)
        assert restored.updated_at.replace(tzinfo=None) == note.updated_at.replace(tzinfo=None)
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_save_duplicate_primary_key_is_atomic(tmp_path: Path) -> None:
    """TP-R02: failed insert does not partially commit additional rows."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r02.db'}")
    try:
        original = Note.new(title="Original", body="v1", is_private=False)
        repository.save(original)

        duplicate_id = Note(
            note_id=original.note_id,
            title="Conflicting",
            body="v2",
            is_private=False,
            is_deleted=False,
            created_at=original.created_at,
            updated_at=original.updated_at,
            deleted_at=None,
        )

        with pytest.raises(NoteRepositoryError, match="Failed to persist note"):
            repository.save(duplicate_id)

        fetched = repository.get(original.note_id)
        assert fetched is not None
        assert fetched.title == "Original"
        assert fetched.body == "v1"
        assert repository.count_active_notes() == 1
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_storage_plaintext_allowlist_blocks_title_and_body(tmp_path: Path) -> None:
    """TP-R03: persisted row must not expose plaintext title/body."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r03.db'}")
    try:
        note = Note.new(title="Top Secret Title", body="Highly classified body", is_private=True)
        repository.save(note)

        with repository.engine.connect() as conn:
            row = (
                conn.execute(
                    text("SELECT title, body, pin_salt FROM notes WHERE note_id = :note_id"),
                    {"note_id": note.note_id},
                )
                .mappings()
                .one()
            )

        assert "Top Secret Title" not in str(row["title"])
        assert "Highly classified body" not in str(row["body"])
        assert str(row["title"]).startswith("enc:v1:")
        assert str(row["body"]).startswith("enc:v1:")
        assert row["pin_salt"] is not None
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_list_excludes_soft_deleted_notes(tmp_path: Path) -> None:
    """TP-R04: list() returns only active notes."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r04.db'}")
    try:
        active = Note.new(title="Keep", body="active", is_private=False)
        deleted = Note.new(title="Delete", body="trash", is_private=False)
        repository.save(active)
        repository.save(deleted)

        assert repository.soft_delete(deleted.note_id) is True

        listed_ids = {note.note_id for note in repository.list()}
        assert active.note_id in listed_ids
        assert deleted.note_id not in listed_ids
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_restore_reactivates_soft_deleted_note_within_window(tmp_path: Path) -> None:
    """TP-R05: restore() returns note to active state."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r05.db'}")
    try:
        note = Note.new(title="Restore Me", body="recover", is_private=False)
        repository.save(note)
        assert repository.soft_delete(note.note_id) is True

        assert repository.restore(note.note_id) is True

        restored = repository.get(note.note_id)
        assert restored is not None
        assert restored.is_deleted is False
        assert restored.deleted_at is None
        assert any(item.note_id == note.note_id for item in repository.list())
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_failed_write_does_not_mutate_existing_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TP-R06: write failure leaves previously committed rows unchanged."""
    repository = SqlNoteRepository(database_url=f"sqlite:///{tmp_path / 'r06.db'}")
    try:
        baseline = Note.new(title="Baseline", body="stable", is_private=False)
        repository.save(baseline)

        class _FailingSession:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def add(self, _record):
                raise SQLAlchemyError("forced failure")

            def commit(self):
                return None

            def rollback(self):
                return None

        original_factory = repository._session_factory
        monkeypatch.setattr(repository, "_session_factory", lambda: _FailingSession())

        with pytest.raises(NoteRepositoryError, match="Failed to persist note"):
            repository.save(Note.new(title="Should Fail", body="new", is_private=False))

        monkeypatch.setattr(repository, "_session_factory", original_factory)
        fetched = repository.get(baseline.note_id)
        assert fetched is not None
        assert fetched.title == "Baseline"
        assert fetched.body == "stable"
        assert repository.count_active_notes() == 1
    finally:
        repository.engine.dispose()
