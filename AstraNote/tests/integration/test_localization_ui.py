"""Integration tests for BL-23 UI localization toggle (English/Spanish)."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_notes_page_defaults_to_english_labels(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Create Note" in response.text
    assert "View Trash" in response.text


@pytest.mark.integration
def test_notes_page_renders_spanish_labels_when_lang_query_is_es(client) -> None:
    response = client.get("/", params={"lang": "es"})

    assert response.status_code == 200
    assert "Crear nota" in response.text
    assert "Ver papelera" in response.text
    assert "Mas recientes primero" in response.text
    assert ">Notas</h2>" in response.text
    assert "Ultimos 7 dias" in response.text


@pytest.mark.integration
def test_notes_page_persists_language_via_cookie(client) -> None:
    first = client.get("/", params={"lang": "es"})
    assert first.status_code == 200

    second = client.get("/")
    assert second.status_code == 200
    assert "Crear nota" in second.text


@pytest.mark.integration
def test_ui_search_uses_spanish_empty_state_message_when_lang_query_is_es(client) -> None:
    response = client.get("/ui/notes/search", params={"query": "anything", "lang": "es"})

    assert response.status_code == 200
    assert "Aun no hay notas. Crea tu primera nota." in response.text
    assert "Ultimos 7 dias" in response.text
