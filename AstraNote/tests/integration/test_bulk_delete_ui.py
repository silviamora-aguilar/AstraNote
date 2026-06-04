"""Integration tests for BL-03.1 bulk-delete UI endpoint."""

from __future__ import annotations

import re
from uuid import uuid4

import pytest


@pytest.mark.integration
def test_bulk_delete_ui_route_redirects_and_removes_notes(client) -> None:
    title_a = f"Bulk UI A {uuid4()}"
    title_b = f"Bulk UI B {uuid4()}"

    first = client.post(
        "/ui/notes",
        data={"title": title_a, "body": "a", "is_private": "false"},
    )
    second = client.post(
        "/ui/notes",
        data={"title": title_b, "body": "b", "is_private": "false"},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    match_a = re.search(r'id="note-([a-zA-Z0-9-]+)"', first.text)
    match_b = re.search(r'id="note-([a-zA-Z0-9-]+)"', second.text)
    assert match_a is not None
    assert match_b is not None

    note_a = match_a.group(1)
    note_b = match_b.group(1)

    response = client.post(
        "/ui/notes/bulk-delete",
        data={"note_ids": [note_a, note_b]},
    )

    assert response.status_code == 200
    assert response.headers.get("HX-Redirect") in {"/", "/?lang=en"}

    page = client.get("/")
    assert page.status_code == 200
    assert title_a not in page.text
    assert title_b not in page.text


@pytest.mark.integration
def test_bulk_delete_ui_route_returns_404_partial_when_none_match(client) -> None:
    response = client.post(
        "/ui/notes/bulk-delete",
        data={"note_ids": ["missing-a", "missing-b"]},
    )

    assert response.status_code == 404
    assert "Selected notes were not found" in response.text
