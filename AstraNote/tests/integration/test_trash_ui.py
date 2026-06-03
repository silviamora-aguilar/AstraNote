"""Integration tests for trash can workflows and retention purge."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.app.dependencies import get_note_repository
from src.main import app


@pytest.mark.integration
def test_deleted_note_appears_in_trash_and_can_be_restored(client) -> None:
    title = f"Trash Restore {uuid4()}"
    created = client.post("/ui/notes", data={"title": title, "body": "restore me", "is_private": "false"})
    assert created.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
    assert match is not None
    note_id = match.group(1)

    deleted = client.delete(f"/ui/notes/{note_id}")
    assert deleted.status_code == 200

    trash = client.get("/ui/notes/search", params={"view": "trash", "query": ""})
    assert trash.status_code == 200
    assert title in trash.text

    restored = client.post(f"/ui/notes/{note_id}/restore")
    assert restored.status_code == 200
    assert restored.headers.get("HX-Redirect") == "/?view=trash"

    page = client.get("/")
    assert page.status_code == 200
    assert title in page.text


@pytest.mark.integration
def test_notes_older_than_15_days_in_trash_are_auto_purged(client) -> None:
    title = f"Trash Purge {uuid4()}"
    created = client.post("/ui/notes", data={"title": title, "body": "purge me", "is_private": "false"})
    assert created.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
    assert match is not None
    note_id = match.group(1)

    deleted = client.delete(f"/ui/notes/{note_id}")
    assert deleted.status_code == 200

    repository = app.dependency_overrides[get_note_repository]()
    old_deleted_at = datetime.now(timezone.utc) - timedelta(days=16)
    now_iso = datetime.now(timezone.utc).isoformat()
    with repository.engine.begin() as conn:
        conn.exec_driver_sql(
            "UPDATE notes SET deleted_at = ?, updated_at = ? WHERE note_id = ?",
            (old_deleted_at.isoformat(), now_iso, note_id),
        )

    _ = client.get("/ui/notes/search", params={"view": "active", "query": ""})

    assert repository.get(note_id) is None


@pytest.mark.integration
def test_bulk_delete_forever_removes_selected_trashed_notes(client) -> None:
    titles = [f"Trash Bulk Purge A {uuid4()}", f"Trash Bulk Purge B {uuid4()}"]
    note_ids: list[str] = []

    for title in titles:
        created = client.post("/ui/notes", data={"title": title, "body": "bulk purge", "is_private": "false"})
        assert created.status_code == 201
        match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
        assert match is not None
        note_id = match.group(1)
        note_ids.append(note_id)
        deleted = client.delete(f"/ui/notes/{note_id}")
        assert deleted.status_code == 200

    response = client.post("/ui/notes/trash/bulk-purge", data={"note_ids": note_ids})
    assert response.status_code == 200
    assert response.headers.get("HX-Redirect") == "/?view=trash"

    trash = client.get("/ui/notes/search", params={"view": "trash", "query": ""})
    assert trash.status_code == 200
    for title in titles:
        assert title not in trash.text


@pytest.mark.integration
def test_trash_viewer_shows_body_for_non_private_note(client) -> None:
    title = f"Trash Viewer Public {uuid4()}"
    body = "This body should be visible in trash viewer."
    created = client.post("/ui/notes", data={"title": title, "body": body, "is_private": "false"})
    assert created.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
    assert match is not None
    note_id = match.group(1)

    deleted = client.delete(f"/ui/notes/{note_id}")
    assert deleted.status_code == 200

    viewer = client.get(f"/ui/notes/{note_id}/trash-viewer")
    assert viewer.status_code == 200
    assert "Trash Note" in viewer.text
    assert body in viewer.text


@pytest.mark.integration
def test_trash_viewer_prompts_unlock_for_private_note_and_reveals_body_after_pin(client) -> None:
    title = f"Trash Viewer Private {uuid4()}"
    body = "Private body shown after unlock in trash."
    created = client.post("/ui/notes", data={"title": title, "body": body, "is_private": "true"})
    assert created.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
    assert match is not None
    note_id = match.group(1)

    deleted = client.delete(f"/ui/notes/{note_id}")
    assert deleted.status_code == 200

    viewer_locked = client.get(f"/ui/notes/{note_id}/trash-viewer")
    assert viewer_locked.status_code == 200
    assert "Enter your 4-digit PIN to continue." in viewer_locked.text

    unlocked = client.post(f"/ui/notes/{note_id}/unlock?view=trash", data={"pin": "1234"})
    assert unlocked.status_code == 200
    assert "Trash Note" in unlocked.text
    assert body in unlocked.text


@pytest.mark.integration
def test_trash_viewer_renders_checklist_and_inline_formatting_as_html(client) -> None:
    title = f"Trash Viewer Format {uuid4()}"
    body = "- [x] **done** task\n- [ ] *next* task"
    created = client.post("/ui/notes", data={"title": title, "body": body, "is_private": "false"})
    assert created.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', created.text)
    assert match is not None
    note_id = match.group(1)

    deleted = client.delete(f"/ui/notes/{note_id}")
    assert deleted.status_code == 200

    viewer = client.get(f"/ui/notes/{note_id}/trash-viewer")
    assert viewer.status_code == 200
    assert 'class="editor-checklist"' in viewer.text
    assert 'type="checkbox"' in viewer.text
    assert "checked" in viewer.text
    assert "<strong>done</strong>" in viewer.text
    assert "<em>next</em>" in viewer.text
    assert "[x]" not in viewer.text


@pytest.mark.integration
def test_create_note_from_trash_context_is_visible_in_active_view(client) -> None:
    existing_title = f"Trash Seed {uuid4()}"
    seed_created = client.post("/ui/notes", data={"title": existing_title, "body": "seed", "is_private": "false"})
    assert seed_created.status_code == 201

    seed_match = re.search(r'id="note-([a-zA-Z0-9-]+)"', seed_created.text)
    assert seed_match is not None
    seed_note_id = seed_match.group(1)
    seed_deleted = client.delete(f"/ui/notes/{seed_note_id}")
    assert seed_deleted.status_code == 200

    trash_page = client.get("/", params={"view": "trash"})
    assert trash_page.status_code == 200
    assert "Notes in Trash" in trash_page.text

    title = f"Create From Trash Context {uuid4()}"
    created = client.post(
        "/ui/notes",
        data={"title": title, "body": "created while user is in trash view", "is_private": "false"},
        headers={"HX-Request": "true", "Referer": "http://testserver/?view=trash"},
    )
    assert created.status_code == 201
    assert title in created.text

    trash_results = client.get("/ui/notes/search", params={"view": "trash", "query": ""})
    assert trash_results.status_code == 200
    assert title not in trash_results.text

    active_results = client.get("/ui/notes/search", params={"view": "active", "query": ""})
    assert active_results.status_code == 200
    assert title in active_results.text
