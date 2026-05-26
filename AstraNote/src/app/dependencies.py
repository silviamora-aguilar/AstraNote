"""Shared dependency providers for API and UI routes."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from starlette.templating import Jinja2Templates

from src.app.repositories import SqlNoteRepository
from src.app.services import NoteService


@lru_cache(maxsize=1)
def get_note_repository() -> SqlNoteRepository:
    """Provide a singleton note repository instance."""
    return SqlNoteRepository()


def get_note_service() -> NoteService:
    """Provide the note service using the configured repository."""
    return NoteService(get_note_repository())


@lru_cache(maxsize=1)
def get_templates() -> Jinja2Templates:
    """Provide Jinja2 template environment for HTML routes."""
    templates_dir = Path(__file__).resolve().parent / "templates"
    return Jinja2Templates(directory=str(templates_dir))
