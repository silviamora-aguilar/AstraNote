"""Main entry point for the AstraNotes FastAPI backend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src import __version__
from src.app.api.notes_api import router as notes_api_router
from src.app.api.notes_ui import router as notes_ui_router
from src.app.dependencies import get_app_logger, get_app_startup, get_config_service


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    startup = get_app_startup()
    startup.initialize()
    application = FastAPI(title="AstraNotes API", version=__version__)
    application.state.config = get_config_service()
    application.state.app_logger = get_app_logger()
    application.state.app_version = __version__
    application.state.app_logger.info(
        "AstraNote startup completed.",
        tier="runtime",
        version=__version__,
        data_dir=str(application.state.config.data_dir_path),
    )
    application.mount("/static", StaticFiles(directory=Path(__file__).parent / "app" / "static"), name="static")
    application.mount("/docs", StaticFiles(directory=Path(__file__).parent.parent / "docs"), name="docs")
    application.mount("/planning", StaticFiles(directory=Path(__file__).parent.parent / "planning"), name="planning")
    application.include_router(notes_api_router)
    application.include_router(notes_ui_router)

    @application.get("/health")
    def health_check() -> dict[str, str]:
        """Simple health endpoint used during early scaffolding."""
        return {"status": "ok", "version": __version__}

    return application


app = create_app()
