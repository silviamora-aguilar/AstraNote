"""API routes and endpoints."""

from .notes_api import router as notes_api_router
from .notes_ui import router as notes_ui_router

__all__ = ["notes_api_router", "notes_ui_router"]
