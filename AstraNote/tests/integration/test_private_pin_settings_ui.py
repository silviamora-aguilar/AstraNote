"""Integration tests for app-level private PIN settings UI."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_private_pin_settings_can_change_unlock_pin(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={
            "title": "PIN Change Private Note",
            "body": "super secret",
            "is_private": "true",
        },
    )
    assert create_response.status_code == 201

    marker = 'id="note-'
    start = create_response.text.find(marker)
    assert start != -1
    note_id_start = start + len(marker)
    note_id_end = create_response.text.find('"', note_id_start)
    note_id = create_response.text[note_id_start:note_id_end]

    settings_response = client.post(
        "/ui/security/pin",
        data={"current_pin": "1234", "new_pin": "5678", "confirm_pin": "5678"},
    )
    assert settings_response.status_code == 200
    assert "Change Private Pin updated." in settings_response.text

    old_unlock = client.post(f"/ui/notes/{note_id}/unlock", data={"pin": "1234"})
    assert old_unlock.status_code == 200
    assert "Enter correct pin to unlock private note." in old_unlock.text

    new_unlock = client.post(f"/ui/notes/{note_id}/unlock", data={"pin": "5678"})
    assert new_unlock.status_code == 200
    assert "Edit Note" in new_unlock.text
    assert "super secret" in new_unlock.text
