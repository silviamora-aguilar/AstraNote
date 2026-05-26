"""Integration tests for BL-01 create-note endpoint."""

from __future__ import annotations

import pytest
from uuid import uuid4

from src.app.dependencies import get_note_service
from src.app.services import NoteCapacityError, NotePersistenceError


class _CapacityService:
    def create(self, title: str, body: str = "", is_private: bool = False):
        raise NoteCapacityError("Note limit reached (10,000). Delete notes to create a new one.")


class _PersistenceFailureService:
    def create(self, title: str, body: str = "", is_private: bool = False):
        raise NotePersistenceError("Could not persist note")


@pytest.mark.integration
def test_create_note_endpoint_returns_201_and_note_payload(client) -> None:
    title = f'Integration Title {uuid4()}'
    response = client.post(
        '/api/notes',
        json={'title': title, 'body': 'Integration body', 'is_private': False},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload['note_id']
    assert payload['title'] == title
    assert payload['body'] == 'Integration body'
    assert payload['is_private'] is False
    assert payload['is_deleted'] is False


@pytest.mark.integration
def test_create_note_endpoint_rejects_invalid_title(client) -> None:
    response = client.post('/api/notes', json={'title': 'bad@title', 'body': ''})

    assert response.status_code == 400
    assert 'unsupported symbols' in response.json()['detail']


@pytest.mark.integration
def test_create_note_endpoint_returns_409_for_capacity_error(client) -> None:
    from src.main import app

    app.dependency_overrides[get_note_service] = lambda: _CapacityService()
    try:
        response = client.post('/api/notes', json={'title': 'Capacity Test', 'body': ''})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert 'Note limit reached' in response.json()['detail']


@pytest.mark.integration
def test_create_note_endpoint_returns_503_for_persistence_failure(client) -> None:
    from src.main import app

    app.dependency_overrides[get_note_service] = lambda: _PersistenceFailureService()
    try:
        response = client.post('/api/notes', json={'title': 'Store Failure Test', 'body': ''})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()['detail'] == 'Storage temporarily unavailable. Please try again.'
