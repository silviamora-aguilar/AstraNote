"""Security-focused persistence tests for encrypted-at-rest note fields."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from src.app.repositories.sql_note_repository import SqlNoteRepository
from src.app.services.note_service import NoteService


@pytest.mark.unit
def test_repository_persists_title_and_body_encrypted_at_rest(tmp_path: Path) -> None:
    db_path = tmp_path / "encrypted_store.db"
    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    try:
        service = NoteService(repository)

        created = service.create(title="Highly Sensitive", body="top secret payload", is_private=False)

        with repository.engine.connect() as conn:
            row = conn.execute(
                text("SELECT title, body, is_private, pin_salt FROM notes WHERE note_id = :note_id"),
                {"note_id": created.note_id},
            ).mappings().one()

        assert row["title"] != "Highly Sensitive"
        assert row["body"] != "top secret payload"
        assert str(row["title"]).startswith("enc:v1:")
        assert str(row["body"]).startswith("enc:v1:")
        assert row["is_private"] in (False, 0)
        assert row["pin_salt"] is None
    finally:
        repository.engine.dispose()


@pytest.mark.unit
def test_repository_uses_pin_salt_for_private_note_encryption(tmp_path: Path) -> None:
    db_path = tmp_path / "private_encrypted_store.db"
    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    try:
        service = NoteService(repository)

        created = service.create(title="Private Secret", body="classified", is_private=True)

        with repository.engine.connect() as conn:
            row = conn.execute(
                text("SELECT title, body, is_private, pin_salt FROM notes WHERE note_id = :note_id"),
                {"note_id": created.note_id},
            ).mappings().one()

        assert row["title"] != "Private Secret"
        assert row["body"] != "classified"
        assert str(row["title"]).startswith("enc:v1:")
        assert str(row["body"]).startswith("enc:v1:")
        assert row["is_private"] in (True, 1)
        assert row["pin_salt"] is not None
        assert len(str(row["pin_salt"])) > 8
    finally:
        repository.engine.dispose()
