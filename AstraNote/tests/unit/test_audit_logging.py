"""Unit tests for audit logging on note workflows (SRG-05/SRG-07)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.app.repositories.sql_note_repository import SqlNoteRepository
from src.app.security import AuditLogger
from src.app.services.note_service import NoteService


@pytest.mark.unit
def test_audit_log_writes_create_update_delete_restore_entries(tmp_path: Path) -> None:
    db_path = tmp_path / "audit-note-store.db"
    audit_path = tmp_path / "audit-log.jsonl"

    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    logger = AuditLogger(log_path=audit_path)
    service = NoteService(repository, audit_logger=logger)

    created = service.create(title="Audit Note", body="payload", is_private=False)
    service.update(
        created.note_id, title="Audit Note Updated", body="updated payload", is_private=False
    )
    service.delete(created.note_id)
    service.restore(created.note_id)

    lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries = [json.loads(line) for line in lines]

    actions = [entry["action"] for entry in entries]
    outcomes = [entry["outcome"] for entry in entries]

    assert actions == ["create", "update", "delete", "restore"]
    assert outcomes == ["success", "success", "success", "success"]

    for entry in entries:
        assert entry["actor"] == "local-user"
        assert entry["note_id"] == created.note_id
        assert entry["correlation_id"]
        assert entry["timestamp_utc"]


@pytest.mark.unit
def test_audit_log_does_not_store_note_plaintext(tmp_path: Path) -> None:
    db_path = tmp_path / "audit-private-store.db"
    audit_path = tmp_path / "audit-log.jsonl"

    secret_title = "Top Secret Title"
    secret_body = "Top Secret Body 123"

    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    logger = AuditLogger(log_path=audit_path)
    service = NoteService(repository, audit_logger=logger)

    created = service.create(title=secret_title, body=secret_body, is_private=True)
    service.delete(created.note_id)

    content = audit_path.read_text(encoding="utf-8")
    assert secret_title not in content
    assert secret_body not in content

    entries = [json.loads(line) for line in content.splitlines() if line.strip()]
    assert all("title" not in entry for entry in entries)
    assert all("body" not in entry for entry in entries)
