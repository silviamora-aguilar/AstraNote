"""Concurrency integration tests for API and UI create-note routes."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import httpx
import pytest

from src.app.dependencies import get_note_service
from src.app.repositories import SqlNoteRepository
from src.app.services import NoteService
from src.main import app


def _make_isolated_service(tmp_path: Path, db_name: str) -> NoteService:
    """Create a NoteService backed by a temp SQLite DB for deterministic tests."""
    db_path = tmp_path / db_name
    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    return NoteService(repository)


def _dispose_service_engine(service: NoteService) -> None:
    """Dispose SQLAlchemy engine used by test-scoped service."""
    repository = service.repository
    if hasattr(repository, "engine"):
        repository.engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_route_handles_concurrent_creates_with_unique_titles(tmp_path: Path) -> None:
    """Concurrent API creates should all succeed and allocate non-conflicting titles."""
    service = _make_isolated_service(tmp_path, "api_concurrency.db")
    app.dependency_overrides[get_note_service] = lambda: service

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            base_title = "Concurrent API Note"
            request_count = 8

            async def post_note() -> httpx.Response:
                return await client.post(
                    "/api/notes",
                    json={"title": base_title, "body": "Concurrent body", "is_private": False},
                )

            responses = await asyncio.gather(*[post_note() for _ in range(request_count)])

        assert all(response.status_code == 201 for response in responses)

        titles = [response.json()["title"] for response in responses]
        expected_titles = {base_title} | {
            f"{base_title}{index}" for index in range(1, request_count)
        }
        assert set(titles) == expected_titles
    finally:
        app.dependency_overrides.clear()
        _dispose_service_engine(service)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ui_route_handles_concurrent_creates_with_unique_titles(tmp_path: Path) -> None:
    """Concurrent HTMX creates should all succeed and return distinct title snippets."""
    service = _make_isolated_service(tmp_path, "ui_concurrency.db")
    app.dependency_overrides[get_note_service] = lambda: service

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            base_title = "Concurrent UI Note"
            request_count = 8

            async def post_note() -> httpx.Response:
                return await client.post(
                    "/ui/notes",
                    data={"title": base_title, "body": "Concurrent body", "is_private": "false"},
                )

            responses = await asyncio.gather(*[post_note() for _ in range(request_count)])

        assert all(response.status_code == 201 for response in responses)

        title_pattern = re.compile(
            r'<span class="note-title">\s*(.*?)\s*</span>', re.IGNORECASE | re.DOTALL
        )
        titles: list[str] = []
        for response in responses:
            match = title_pattern.search(response.text)
            assert match is not None
            titles.append(match.group(1))

        expected_titles = {base_title} | {
            f"{base_title}{index}" for index in range(1, request_count)
        }
        assert set(titles) == expected_titles
    finally:
        app.dependency_overrides.clear()
        _dispose_service_engine(service)
