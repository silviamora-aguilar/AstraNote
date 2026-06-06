"""Integration tests for BL-02 edit-note API endpoint."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.integration
def test_update_note_endpoint_returns_200_and_updated_payload(client) -> None:
    create_title = f"Update API Seed {uuid4()}"
    updated_title = f"Updated Title {uuid4()}"
    create_response = client.post(
        "/api/notes",
        json={"title": create_title, "body": "before", "is_private": False},
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["note_id"]
    created_at = create_response.json()["created_at"]

    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": updated_title, "body": "after"},
    )

    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["note_id"] == note_id
    assert payload["title"] == updated_title
    assert payload["body"] == "after"
    assert payload["created_at"].rstrip("Z") == created_at.rstrip("Z")


@pytest.mark.integration
def test_update_note_endpoint_applies_duplicate_suffix(client) -> None:
    existing_title = f"Duplicate Seed {uuid4()}"
    first = client.post(
        "/api/notes", json={"title": existing_title, "body": "a", "is_private": False}
    )
    assert first.status_code == 201

    second = client.post(
        "/api/notes", json={"title": f"Second {uuid4()}", "body": "b", "is_private": False}
    )
    assert second.status_code == 201
    second_id = second.json()["note_id"]

    update_response = client.put(
        f"/api/notes/{second_id}",
        json={"title": existing_title, "body": "updated"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == f"{existing_title}1"


@pytest.mark.integration
def test_update_note_endpoint_rejects_invalid_title(client) -> None:
    create_response = client.post(
        "/api/notes",
        json={"title": f"Invalid Update Seed {uuid4()}", "body": "before", "is_private": False},
    )
    assert create_response.status_code == 201

    note_id = create_response.json()["note_id"]
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "bad<title", "body": "after"},
    )

    assert update_response.status_code == 400
    assert "unsupported symbols" in update_response.json()["detail"]


@pytest.mark.integration
def test_update_note_endpoint_returns_404_for_missing_note(client) -> None:
    response = client.put(
        "/api/notes/missing-note-id",
        json={"title": "Any Title", "body": "x"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


@pytest.mark.integration
def test_update_note_endpoint_preserves_combined_formatting_markers(client) -> None:
    create_response = client.post(
        "/api/notes",
        json={"title": f"Formatting Seed {uuid4()}", "body": "before", "is_private": False},
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["note_id"]

    formatted_body = "- [ ] **Sprint** item\n- bullet line\n<u>*focus*</u>"
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Formatting Saved", "body": formatted_body, "is_private": False},
    )

    assert update_response.status_code == 200
    assert update_response.json()["body"] == formatted_body
