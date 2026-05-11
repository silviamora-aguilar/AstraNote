"""Main entry point for the AstraNotes FastAPI backend."""

from fastapi import FastAPI


app = FastAPI(title="AstraNotes API", version="0.1.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint used during early scaffolding."""
    return {"status": "ok"}
