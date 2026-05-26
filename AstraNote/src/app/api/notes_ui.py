"""Server-rendered UI routes for notes pages and HTMX partial updates."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, Response

from src.app.api.error_mapping import map_note_error_message, map_note_error_status
from src.app.dependencies import get_note_service, get_templates
from src.app.services import NoteService


router = APIRouter(tags=["notes-ui"])


PACIFIC_TZ = ZoneInfo("America/Los_Angeles")


def _format_created_pacific(created_at: datetime) -> str:
    """Format UTC-ish timestamps as Month Day, Year HH:MM XM Pacific time."""
    if created_at.tzinfo is None:
        created_at_utc = created_at.replace(tzinfo=timezone.utc)
    else:
        created_at_utc = created_at.astimezone(timezone.utc)
    created_at_pacific = created_at_utc.astimezone(PACIFIC_TZ)
    return created_at_pacific.strftime("%B %d, %Y %I:%M %p %Z")


def _format_modified_pacific(updated_at: datetime) -> str:
    """Format UTC-ish updated timestamps as Month Day, Year HH:MM Pacific time."""
    if updated_at.tzinfo is None:
        updated_at_utc = updated_at.replace(tzinfo=timezone.utc)
    else:
        updated_at_utc = updated_at.astimezone(timezone.utc)
    updated_at_pacific = updated_at_utc.astimezone(PACIFIC_TZ)
    return updated_at_pacific.strftime("%B %d, %Y %H:%M %Z")


def _build_note_groups(notes):
    """Group notes for panel-2 rendering buckets."""
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    start_of_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    if now.month == 1:
        last_month_year = now.year - 1
        last_month = 12
    else:
        last_month_year = now.year
        last_month = now.month - 1

    today_notes = []
    recent_notes = []
    last_month_notes = []
    this_year_notes = []

    for note in notes:
        created_at = note.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at.astimezone(timezone.utc)
        if created_at >= start_of_today:
            today_notes.append(note)
            continue

        if created_at >= seven_days_ago:
            recent_notes.append(note)
            continue

        if created_at.year == last_month_year and created_at.month == last_month:
            last_month_notes.append(note)
            continue

        if created_at.year == now.year:
            this_year_notes.append(note)

    return {
        "today_notes": today_notes,
        "recent_notes": recent_notes,
        "last_month_notes": last_month_notes,
        "last_month_label": datetime(last_month_year, last_month, 1, tzinfo=timezone.utc).strftime("%B %Y"),
        "this_year_label": str(now.year),
        "this_year_notes": this_year_notes,
    }


def _build_search_context(note_service: NoteService, query: str) -> dict:
    """Prepare list-group and empty-state context for BL-05 search rendering."""
    all_notes = note_service.list_notes()
    normalized_query = (query or "").strip()
    notes = note_service.search(normalized_query)

    empty_state_message = None
    if not notes:
        if not all_notes:
            empty_state_message = "No notes yet. Create your first note."
        elif normalized_query:
            empty_state_message = "No notes match your search."

    return {
        "notes": notes,
        "note_count": len(notes),
        "search_query": normalized_query,
        "empty_state_message": empty_state_message,
        **_build_note_groups(notes),
    }


@router.get("/", response_class=HTMLResponse)
def notes_page(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> HTMLResponse:
    """Render initial notes page with create form and notes list."""
    templates = get_templates()
    search_context = _build_search_context(note_service, "")
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "error_message": None,
            **search_context,
        },
    )


@router.get("/ui/notes/search", response_class=HTMLResponse)
def search_notes_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    query: str = Query(default=""),
) -> HTMLResponse:
    """Return filtered note-list markup for BL-05 live search."""
    templates = get_templates()
    search_context = _build_search_context(note_service, query)
    return templates.TemplateResponse(
        request,
        "partials/note_list_results.html",
        search_context,
        status_code=200,
    )


@router.post("/ui/notes", response_class=HTMLResponse)
def create_note_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    title: str = Form(...),
    body: str = Form(""),
    is_private: bool = Form(False),
) -> HTMLResponse:
    """Create note and return either note-item or error partial for HTMX."""
    templates = get_templates()
    try:
        note = note_service.create(title=title, body=body, is_private=is_private)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )

    return templates.TemplateResponse(
        request,
        "partials/note_list_item.html",
        {"note": note, "selected_note_id": None, "oob_swap": False},
        status_code=201,
    )


@router.get("/ui/notes/{note_id}/editor", response_class=HTMLResponse)
def get_note_editor_panel(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> HTMLResponse:
    """Load a selected note into the dedicated editor panel."""
    templates = get_templates()
    note = note_service.get_note(note_id)
    if note is None:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": "Note not found"},
            status_code=404,
        )

    return templates.TemplateResponse(
        request,
        "partials/editor_panel.html",
        {
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "edit_error_message": None,
            "oob_note": note,
            "selected_note_id": note.note_id,
        },
        status_code=200,
    )


@router.post("/ui/notes/{note_id}/editor", response_class=HTMLResponse)
def update_note_editor_panel(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    title: str = Form(...),
    body: str | None = Form(None),
    is_private: bool = Form(False),
) -> HTMLResponse:
    """Edit selected note and refresh editor panel plus selected list item."""
    templates = get_templates()
    existing_note = note_service.get_note(note_id)
    if existing_note is None:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": "Note not found"},
            status_code=404,
        )

    resolved_body = "" if body is None else body
    try:
        note = note_service.update(note_id=note_id, title=title, body=resolved_body, is_private=is_private)
    except Exception as exc:
        current_note = note_service.get_note(note_id)
        if current_note is None:
            return templates.TemplateResponse(
                request,
                "partials/error_message.html",
                {"error_message": map_note_error_message(exc)},
                status_code=map_note_error_status(exc),
            )
        return templates.TemplateResponse(
            request,
            "partials/editor_panel.html",
            {
                "note": current_note,
                "created_display": _format_created_pacific(current_note.created_at),
                "modified_display": _format_modified_pacific(current_note.updated_at),
                "edit_error_message": map_note_error_message(exc),
                "oob_note": current_note,
                "selected_note_id": current_note.note_id,
            },
            status_code=map_note_error_status(exc),
        )

    return templates.TemplateResponse(
        request,
        "partials/editor_panel.html",
        {
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "edit_error_message": None,
            "oob_note": note,
            "selected_note_id": note.note_id,
        },
        status_code=200,
    )


@router.delete("/ui/notes/{note_id}", response_class=HTMLResponse)
def delete_note_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> Response:
    """Soft-delete a note and redirect the page to reflect the updated list."""
    templates = get_templates()
    try:
        note_service.delete(note_id)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    return Response(status_code=200, headers={"HX-Redirect": "/"})


@router.post("/ui/notes/bulk-delete", response_class=HTMLResponse)
def bulk_delete_notes_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    note_ids: list[str] = Form(...),
) -> Response:
    """Soft-delete selected notes and refresh the page."""
    templates = get_templates()
    try:
        note_service.bulk_delete(note_ids)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    return Response(status_code=200, headers={"HX-Redirect": "/"})


@router.post("/ui/notes/{note_id}", response_class=HTMLResponse)
def update_note_htmx_legacy(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    title: str = Form(...),
    body: str = Form(""),
    is_private: bool = Form(False),
) -> HTMLResponse:
    """Legacy BL-02 endpoint retained for compatibility; delegates to editor route."""
    return update_note_editor_panel(
        request=request,
        note_id=note_id,
        note_service=note_service,
        title=title,
        body=body,
        is_private=is_private,
    )
