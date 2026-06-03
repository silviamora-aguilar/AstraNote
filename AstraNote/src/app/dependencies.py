"""Shared dependency providers for API and UI routes."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from starlette.templating import Jinja2Templates

from src.app.presentation import render_note_body_html, render_note_preview_html
from src.app.repositories import SqlNoteRepository
from src.app.security import CryptoService, PinSettingsManager, UnlockSessionManager
from src.app.services import NoteService


@lru_cache(maxsize=1)
def get_pin_settings_manager() -> PinSettingsManager:
    """Provide persisted app-level private PIN settings."""
    return PinSettingsManager()


@lru_cache(maxsize=1)
def get_crypto_service() -> CryptoService:
    """Provide shared cryptography service."""
    pin_settings = get_pin_settings_manager()
    return CryptoService(private_pin=pin_settings.get_pin())


@lru_cache(maxsize=1)
def get_unlock_session_manager() -> UnlockSessionManager:
    """Provide unlock manager for private-note session gating."""
    return UnlockSessionManager(get_crypto_service())


@lru_cache(maxsize=1)
def get_note_repository() -> SqlNoteRepository:
    """Provide a singleton note repository instance."""
    return SqlNoteRepository(crypto_service=get_crypto_service())


def get_note_service(
    note_repository: Annotated[SqlNoteRepository, Depends(get_note_repository)],
) -> NoteService:
    """Provide the note service using the configured repository."""
    return NoteService(note_repository)


@lru_cache(maxsize=1)
def get_templates() -> Jinja2Templates:
    """Provide Jinja2 template environment for HTML routes."""
    templates_dir = Path(__file__).resolve().parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    templates.env.globals["render_note_preview_html"] = render_note_preview_html
    templates.env.globals["render_note_body_html"] = render_note_body_html
    return templates
