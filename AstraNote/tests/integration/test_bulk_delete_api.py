"""Integration tests for BL-03.1 bulk-delete API endpoint."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.integration
def test_bulk_delete_endpoint_deletes_multiple_notes(client) -> None:
    first = client.post(
        "/api/notes",
        json={"title": f"Bulk API A {uuid4()}", "body": "a", "is_private": False},
    )
    second = client.post(
        "/api/notes",
        json={"title": f"Bulk API B {uuid4()}", "body": "b", "is_private": False},
    )
    third = client.post(
        "/api/notes",
        json={"title": f"Bulk API C {uuid4()}", "body": "c", "is_private": False},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201

    first_id = first.json()["note_id"]
    second_id = second.json()["note_id"]
    third_id = third.json()["note_id"]

    response = client.post(
        "/api/notes/bulk-delete",
        json={"note_ids": [first_id, third_id]},
    )

    assert response.status_code == 200
    assert response.json()["deleted_count"] == 2

    # Deleted notes should now return not-found if deleted again.
    assert client.delete(f"/api/notes/{first_id}").status_code == 404
    assert client.delete(f"/api/notes/{third_id}").status_code == 404

    # Non-selected note should still be active and deletable once.
    assert client.delete(f"/api/notes/{second_id}").status_code == 204


@pytest.mark.integration
def test_bulk_delete_endpoint_returns_404_when_none_match(client) -> None:
    response = client.post(
        "/api/notes/bulk-delete",
        json={"note_ids": ["missing-a", "missing-b"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Selected notes were not found"
