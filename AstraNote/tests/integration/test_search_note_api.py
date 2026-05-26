"""Integration tests for BL-05 search API endpoint."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.integration
def test_search_api_filters_by_title_or_body_case_insensitive(client) -> None:
    marker = str(uuid4())
    hit_title = f"Roadmap {marker}"
    hit_body = f"Body marker {marker}"
    miss_title = f"Other {marker}"

    client.post('/api/notes', json={'title': hit_title, 'body': 'alpha', 'is_private': False})
    client.post('/api/notes', json={'title': miss_title, 'body': hit_body, 'is_private': False})
    client.post('/api/notes', json={'title': f'No hit {marker}', 'body': 'zzz', 'is_private': False})

    by_title = client.get('/api/notes/search', params={'q': marker.lower()})

    assert by_title.status_code == 200
    payload = by_title.json()
    assert len(payload) >= 2
    returned_titles = {item['title'] for item in payload}
    assert hit_title in returned_titles
    assert miss_title in returned_titles


@pytest.mark.integration
def test_search_api_whitespace_query_returns_full_list(client) -> None:
    marker = str(uuid4())
    title_a = f"Search Full A {marker}"
    title_b = f"Search Full B {marker}"

    client.post('/api/notes', json={'title': title_a, 'body': '', 'is_private': False})
    client.post('/api/notes', json={'title': title_b, 'body': '', 'is_private': False})

    response = client.get('/api/notes/search', params={'q': '   '})

    assert response.status_code == 200
    titles = {item['title'] for item in response.json()}
    assert title_a in titles
    assert title_b in titles


@pytest.mark.integration
def test_search_api_treats_percent_and_underscore_as_literal_text(client) -> None:
    marker = str(uuid4())
    literal_body = f"100%_literal {marker}"
    response_create = client.post(
        '/api/notes',
        json={'title': f'Literal Marker {marker}', 'body': literal_body, 'is_private': False},
    )
    assert response_create.status_code == 201

    response = client.get('/api/notes/search', params={'q': '%_'})

    assert response.status_code == 200
    bodies = {item['body'] for item in response.json()}
    assert literal_body in bodies
