"""Integration tests for private-note unlock UX flow."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.integration
def test_private_note_editor_requires_unlock(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={
            "title": f"Private Unlock Seed {uuid4()}",
            "body": "very secret content",
            "is_private": "true",
        },
    )
    assert create_response.status_code == 201

    page_response = client.get("/")
    assert page_response.status_code == 200

    # Grab note id from newly created item and request editor panel.
    marker = "id=\"note-"
    start = create_response.text.find(marker)
    assert start != -1
    note_id_start = start + len(marker)
    note_id_end = create_response.text.find("\"", note_id_start)
    note_id = create_response.text[note_id_start:note_id_end]

    editor_response = client.get(f"/ui/notes/{note_id}/editor")
    assert editor_response.status_code == 200
    assert "Unlock:" in editor_response.text
    assert "Enter your 4-digit PIN to continue." in editor_response.text
    assert "very secret content" not in editor_response.text


@pytest.mark.integration
def test_private_note_unlock_with_wrong_then_correct_pin(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={
            "title": f"Private Unlock Retry Seed {uuid4()}",
            "body": "unlock me",
            "is_private": "true",
        },
    )
    assert create_response.status_code == 201

    marker = "id=\"note-"
    start = create_response.text.find(marker)
    assert start != -1
    note_id_start = start + len(marker)
    note_id_end = create_response.text.find("\"", note_id_start)
    note_id = create_response.text[note_id_start:note_id_end]

    wrong_response = client.post(f"/ui/notes/{note_id}/unlock", data={"pin": "0000"})
    assert wrong_response.status_code == 200
    assert "Enter correct pin to unlock private note." in wrong_response.text
    assert "Unlock:" in wrong_response.text

    # Default development pin for local single-user mode.
    success_response = client.post(f"/ui/notes/{note_id}/unlock", data={"pin": "1234"})
    assert success_response.status_code == 200
    assert "Edit Note" in success_response.text
    assert "unlock me" in success_response.text
