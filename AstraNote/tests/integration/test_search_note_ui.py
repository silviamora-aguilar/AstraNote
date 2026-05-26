"""Integration tests for BL-05 search UI partial endpoint."""

from __future__ import annotations

from uuid import uuid4

import pytest

from src.app.dependencies import get_note_service


class _NoNotesService:
    def list_notes(self):
        return []

    def search(self, query: str):
        return []


@pytest.mark.integration
def test_notes_page_places_search_next_to_create_button(client) -> None:
    response = client.get('/')

    assert response.status_code == 200
    assert 'id="search-form"' in response.text
    assert 'id="note-search"' in response.text

    create_index = response.text.find('Create Note')
    search_index = response.text.find('id="search-form"')
    assert create_index != -1
    assert search_index != -1
    assert search_index > create_index


@pytest.mark.integration
def test_ui_search_filters_notes_and_returns_matching_partial(client) -> None:
    marker = str(uuid4())
    title_hit = f"Hit {marker}"
    title_miss = f"Miss {marker}"

    client.post('/ui/notes', data={'title': title_hit, 'body': 'find-me'})
    client.post('/ui/notes', data={'title': title_miss, 'body': 'ignore-me'})

    response = client.get('/ui/notes/search', params={'query': 'find-me'})

    assert response.status_code == 200
    assert title_hit in response.text
    assert title_miss not in response.text


@pytest.mark.integration
def test_ui_search_no_match_message_when_notes_exist(client) -> None:
    marker = str(uuid4())
    client.post('/ui/notes', data={'title': f'Existing {marker}', 'body': 'content'})

    response = client.get('/ui/notes/search', params={'query': f'no-match-{marker}'})

    assert response.status_code == 200
    assert 'No notes match your search.' in response.text


@pytest.mark.integration
def test_ui_search_no_notes_uses_empty_state_message(client) -> None:
    from src.main import app

    app.dependency_overrides[get_note_service] = lambda: _NoNotesService()
    try:
        response = client.get('/ui/notes/search', params={'query': 'anything'})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert 'No notes yet. Create your first note.' in response.text


@pytest.mark.integration
def test_ui_search_whitespace_query_returns_full_list(client) -> None:
    marker = str(uuid4())
    title_a = f"Whitespace A {marker}"
    title_b = f"Whitespace B {marker}"

    client.post('/ui/notes', data={'title': title_a, 'body': ''})
    client.post('/ui/notes', data={'title': title_b, 'body': ''})

    response = client.get('/ui/notes/search', params={'query': '   '})

    assert response.status_code == 200
    assert title_a in response.text
    assert title_b in response.text
