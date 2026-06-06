"""Integration tests for initial Jinja2 + HTMX UI wiring."""

from __future__ import annotations

import pytest
from uuid import uuid4

from src.app.dependencies import get_note_service
from src.app.services import NoteCapacityError, NotePersistenceError


class _CapacityService:
    def create(self, title: str, body: str = "", is_private: bool = False):
        raise NoteCapacityError("Note limit reached (10,000). Delete notes to create a new one.")

    def list_notes(self):
        return []


class _PersistenceFailureService:
    def create(self, title: str, body: str = "", is_private: bool = False):
        raise NotePersistenceError("Could not persist note")

    def list_notes(self):
        return []


@pytest.mark.integration
def test_notes_page_renders_jinja_template(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "AstraNote" in response.text
    assert 'hx-post="/ui/notes?lang=' in response.text
    assert 'id="editor-slot"' in response.text
    assert 'id="create-panel-template"' in response.text
    assert 'id="editor-panel"' not in response.text
    assert "notes-panel-body" in response.text
    assert "syncWorkbenchHeight" in response.text


@pytest.mark.integration
def test_htmx_create_note_returns_html_snippet(client) -> None:
    title = f"UI Note {uuid4()}"
    response = client.post(
        "/ui/notes",
        data={
            "title": title,
            "body": "Created via HTMX",
            "is_private": "true",
        },
    )

    assert response.status_code == 201
    assert title in response.text
    assert "note-item" in response.text
    assert 'hx-get="/ui/notes/' in response.text
    assert "/editor?lang=" in response.text


@pytest.mark.integration
def test_htmx_create_note_returns_error_snippet_on_invalid_title(client) -> None:
    response = client.post("/ui/notes", data={"title": "bad<title", "body": ""})

    assert response.status_code == 400
    assert "unsupported symbols" in response.text


@pytest.mark.integration
def test_htmx_create_note_returns_409_for_capacity_error(client) -> None:
    from src.main import app

    app.dependency_overrides[get_note_service] = lambda: _CapacityService()
    try:
        response = client.post("/ui/notes", data={"title": "Capacity Test", "body": ""})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "Note limit reached" in response.text


@pytest.mark.integration
def test_htmx_create_note_returns_503_for_persistence_failure(client) -> None:
    from src.main import app

    app.dependency_overrides[get_note_service] = lambda: _PersistenceFailureService()
    try:
        response = client.post("/ui/notes", data={"title": "Store Failure Test", "body": ""})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "Storage temporarily unavailable" in response.text


@pytest.mark.integration
def test_notes_page_includes_wysiwyg_enter_key_handler(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "function handleWysiwygEnterKey(event)" in response.text
    assert "if (event.key !== 'Enter') return;" in response.text
    assert (
        "const checklistLi = node.closest && node.closest('.editor-checklist > li');"
        in response.text
    )


@pytest.mark.integration
def test_notes_page_includes_wysiwyg_enter_key_exit_behavior(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "if (!content)" in response.text
    assert "function handleWysiwygEnterKey" in response.text
