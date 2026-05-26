"""Main entry point for the AstraNotes FastAPI backend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app.api.notes_api import router as notes_api_router
from src.app.api.notes_ui import router as notes_ui_router


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    application = FastAPI(title="AstraNotes API", version="0.1.0")
    application.mount("/static", StaticFiles(directory=Path(__file__).parent / "app" / "static"), name="static")
    application.mount("/docs", StaticFiles(directory=Path(__file__).parent.parent / "docs"), name="docs")
    application.mount("/planning", StaticFiles(directory=Path(__file__).parent.parent / "planning"), name="planning")
    application.include_router(notes_api_router)
    application.include_router(notes_ui_router)

    @application.get("/health")
    def health_check() -> dict[str, str]:
        """Simple health endpoint used during early scaffolding."""
        return {"status": "ok"}

    return application


app = create_app()
