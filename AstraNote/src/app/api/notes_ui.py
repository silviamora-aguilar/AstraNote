"""Server-rendered UI routes for notes pages and HTMX partial updates."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, Response
from cryptography.exceptions import InvalidTag

from src.app.api.error_mapping import map_note_error_message, map_note_error_status
from src.app.dependencies import (
    get_crypto_service,
    get_note_repository,
    get_note_service,
    get_pin_settings_manager,
    get_templates,
    get_unlock_session_manager,
)
from src.app.repositories import SqlNoteRepository
from src.app.security import CryptoService, PinSettingsManager, UnlockSessionManager
from src.app.presentation import render_note_body_html
from src.app.presentation.localization import get_ui_strings, resolve_ui_language
from src.app.services import NoteService


router = APIRouter(tags=["notes-ui"])


PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
CHECKLIST_LINE_RE = re.compile(r"^\s*[-*+]\s+\[( |x|X)\]\s+(.*)$")
UNICODE_CHECKLIST_LINE_RE = re.compile(r"^\s*(☐|☑)\s+(.*)$")


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
    return updated_at_pacific.strftime("%B %d, %Y %I:%M %p %Z")


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


def _resolve_lang(request: Request) -> str:
    return resolve_ui_language(
        request.query_params.get("lang"),
        request.cookies.get("astranote_ui_lang"),
    )


def _ui_context(request: Request) -> dict:
    lang = _resolve_lang(request)
    return {"lang": lang, "i18n": get_ui_strings(lang)}


def _build_search_context(note_service: NoteService, query: str, i18n: dict[str, str]) -> dict:
    """Prepare list-group and empty-state context for BL-05 search rendering."""
    all_notes = note_service.list_notes()
    normalized_query = (query or "").strip()
    notes = note_service.search(normalized_query)

    empty_state_message = None
    if not notes:
        if not all_notes:
            empty_state_message = i18n["search_empty_no_notes"]
        elif normalized_query:
            empty_state_message = i18n["search_empty_no_match"]

    return {
        "notes": notes,
        "note_count": len(notes),
        "search_query": normalized_query,
        "view_mode": "active",
        "trash_mode": False,
        "empty_state_message": empty_state_message,
        **_build_note_groups(notes),
    }


def _build_trash_context(note_service: NoteService, query: str, i18n: dict[str, str]) -> dict:
    """Prepare trash-list context with soft-deleted notes only."""
    normalized_query = (query or "").strip()
    notes = note_service.search_trash(normalized_query)

    empty_state_message = None
    if not notes:
        if normalized_query:
            empty_state_message = i18n["trash_empty_no_match"]
        else:
            empty_state_message = i18n["trash_empty"]

    return {
        "notes": notes,
        "note_count": len(notes),
        "search_query": normalized_query,
        "view_mode": "trash",
        "trash_mode": True,
        "empty_state_message": empty_state_message,
        "today_notes": [],
        "recent_notes": [],
        "last_month_notes": [],
        "last_month_label": "",
        "this_year_label": "",
        "this_year_notes": [],
    }


def _extract_checklist_items(body: str) -> list[dict]:
    """Extract checklist lines from note body in display order."""
    items: list[dict] = []
    for line in (body or "").split("\n"):
        match = CHECKLIST_LINE_RE.match(line)
        unicode_match = UNICODE_CHECKLIST_LINE_RE.match(line)
        if match is not None:
            items.append(
                {
                    "index": len(items),
                    "checked": match.group(1).lower() == "x",
                    "label": match.group(2).strip(),
                }
            )
            continue
        if unicode_match is not None:
            items.append(
                {
                    "index": len(items),
                    "checked": unicode_match.group(1) == "☑",
                    "label": unicode_match.group(2).strip(),
                }
            )
    return items


def _render_unlock_panel(
    request: Request,
    note,
    unlock_error: str | None = None,
    unlock_post_url: str | None = None,
) -> HTMLResponse:
    templates = get_templates()
    context = _ui_context(request)
    return templates.TemplateResponse(
        request,
        "partials/private_unlock_panel.html",
        {
            "note": note,
            "unlock_error_message": unlock_error,
            "unlock_post_url": unlock_post_url,
            **context,
        },
        status_code=200,
    )


def _render_pin_settings_panel(
    request: Request,
    *,
    error_message: str | None = None,
    success_message: str | None = None,
    verified_current_pin: str | None = None,
    pin_update_completed: bool = False,
) -> HTMLResponse:
    templates = get_templates()
    context = _ui_context(request)
    return templates.TemplateResponse(
        request,
        "partials/pin_settings_panel.html",
        {
            "pin_error_message": error_message,
            "pin_success_message": success_message,
            "pin_verified": bool(verified_current_pin),
            "verified_current_pin": verified_current_pin or "",
            "pin_update_completed": pin_update_completed,
            **context,
        },
        status_code=200,
    )


@router.get("/", response_class=HTMLResponse)
def notes_page(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    view: str = Query(default="active"),
) -> HTMLResponse:
    """Render initial notes page with create form and notes list."""
    templates = get_templates()
    context = _ui_context(request)
    i18n = context["i18n"]
    try:
        if view == "trash":
            search_context = _build_trash_context(note_service, "", i18n)
        else:
            search_context = _build_search_context(note_service, "", i18n)
    except InvalidTag:
        response = templates.TemplateResponse(
            request,
            "index.html",
            {
                "error_message": i18n["pin_data_decrypt_warning"],
                "view_mode": "active",
                "trash_mode": False,
                "notes": [],
                "note_count": 0,
                "search_query": "",
                "empty_state_message": i18n["pin_data_hidden_warning"],
                "today_notes": [],
                "recent_notes": [],
                "last_month_notes": [],
                "last_month_label": datetime.now(timezone.utc).strftime("%B %Y"),
                "this_year_label": str(datetime.now(timezone.utc).year),
                "this_year_notes": [],
                **context,
            },
            status_code=200,
        )
        response.set_cookie("astranote_ui_lang", context["lang"], samesite="lax")
        return response

    response = templates.TemplateResponse(
        request,
        "index.html",
        {
            "error_message": None,
            **search_context,
            **context,
        },
    )
    response.set_cookie("astranote_ui_lang", context["lang"], samesite="lax")
    return response


@router.get("/ui/notes/search", response_class=HTMLResponse)
def search_notes_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    query: str = Query(default=""),
    view: str = Query(default="active"),
) -> HTMLResponse:
    """Return filtered note-list markup for BL-05 live search."""
    templates = get_templates()
    context = _ui_context(request)
    i18n = context["i18n"]
    if view == "trash":
        search_context = _build_trash_context(note_service, query, i18n)
    else:
        search_context = _build_search_context(note_service, query, i18n)
    return templates.TemplateResponse(
        request,
        "partials/note_list_results.html",
        {**search_context, **context},
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
        {
            "note": note,
            "selected_note_id": None,
            "oob_swap": False,
            **_ui_context(request),
        },
        status_code=201,
    )


@router.get("/ui/notes/{note_id}/editor", response_class=HTMLResponse)
def get_note_editor_panel(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
    include_oob: bool = Query(default=True),
) -> HTMLResponse:
    """Load a selected note into the dedicated editor panel."""
    templates = get_templates()
    note = note_service.get_note(note_id)
    if note is None:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": _ui_context(request)["i18n"]["note_not_found"]},
            status_code=404,
        )

    if note.is_private and not unlock_manager.is_unlocked(note.note_id):
        return _render_unlock_panel(request, note)

    return templates.TemplateResponse(
        request,
        "partials/editor_panel.html",
        {
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "checklist_items": _extract_checklist_items(note.body),
            "edit_error_message": None,
            "oob_note": note if include_oob else None,
            "selected_note_id": note.note_id,
            **_ui_context(request),
        },
        status_code=200,
    )


@router.get("/ui/notes/{note_id}/trash-viewer", response_class=HTMLResponse)
def get_trashed_note_viewer_panel(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
) -> HTMLResponse:
    """Load a trashed note into a read-only viewer panel."""
    templates = get_templates()
    note = note_service.get_note_any(note_id)
    if note is None or not note.is_deleted:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": _ui_context(request)["i18n"]["note_not_found"]},
            status_code=404,
        )

    if note.is_private and not unlock_manager.is_unlocked(note.note_id):
        return _render_unlock_panel(
            request,
            note,
            unlock_post_url=f"/ui/notes/{note.note_id}/unlock?view=trash",
        )

    return templates.TemplateResponse(
        request,
        "partials/trashed_note_panel.html",
        {
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "deleted_display": _format_modified_pacific(note.deleted_at) if note.deleted_at else "Recently",
            "rendered_body_html": render_note_body_html(note.body or ""),
            **_ui_context(request),
        },
        status_code=200,
    )


@router.post("/ui/notes/{note_id}/editor", response_class=HTMLResponse)
def update_note_editor_panel(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
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
            {"error_message": _ui_context(request)["i18n"]["note_not_found"]},
            status_code=404,
        )

    if existing_note.is_private and not unlock_manager.is_unlocked(existing_note.note_id):
        return _render_unlock_panel(request, existing_note, _ui_context(request)["i18n"]["unlock_wrong_pin"])

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
                "checklist_items": _extract_checklist_items(resolved_body),
                "edit_error_message": map_note_error_message(exc),
                "oob_note": current_note,
                "selected_note_id": current_note.note_id,
                "form_title": title,
                "form_body": resolved_body,
                "form_is_private": is_private,
                **_ui_context(request),
            },
            status_code=200,
        )

    return templates.TemplateResponse(
        request,
        "partials/editor_panel.html",
        {
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "checklist_items": _extract_checklist_items(note.body),
            "edit_error_message": None,
            "oob_note": note,
            "selected_note_id": note.note_id,
            **_ui_context(request),
        },
        status_code=200,
    )


@router.post("/ui/notes/{note_id}/checklist-toggle", response_class=HTMLResponse)
def toggle_checklist_item_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
    line_index: int = Form(...),
    checked: bool = Form(False),
) -> HTMLResponse:
    """Toggle a checklist item and persist state immediately for BL-06."""
    templates = get_templates()
    existing_note = note_service.get_note(note_id)
    if existing_note is None:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": _ui_context(request)["i18n"]["note_not_found"]},
            status_code=404,
        )
    if existing_note.is_private and not unlock_manager.is_unlocked(existing_note.note_id):
        return _render_unlock_panel(request, existing_note, _ui_context(request)["i18n"]["unlock_wrong_pin"])

    try:
        note = note_service.toggle_checklist_item(note_id=note_id, line_index=line_index, checked=checked)
    except Exception as exc:
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
            "note": note,
            "created_display": _format_created_pacific(note.created_at),
            "modified_display": _format_modified_pacific(note.updated_at),
            "checklist_items": _extract_checklist_items(note.body),
            "edit_error_message": None,
            "oob_note": note,
            "selected_note_id": note.note_id,
            **_ui_context(request),
        },
        status_code=200,
    )


@router.post("/ui/notes/{note_id}/unlock", response_class=HTMLResponse)
def unlock_private_note_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
    view: str = Query(default="active"),
    pin: str = Form(...),
) -> HTMLResponse:
    """Unlock a private note using the configured 4-digit PIN."""
    note = note_service.get_note(note_id)
    if note is None and view == "trash":
        note = note_service.get_note_any(note_id)
        if note is not None and not note.is_deleted:
            note = None

    if note is None:
        templates = get_templates()
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": _ui_context(request)["i18n"]["note_not_found"]},
            status_code=404,
        )

    if not note.is_private:
        if view == "trash":
            return get_trashed_note_viewer_panel(request, note_id, note_service, unlock_manager)
        return get_note_editor_panel(request, note_id, note_service, unlock_manager)

    unlocked, error_message = unlock_manager.attempt_unlock(note_id, pin)
    if not unlocked:
        unlock_post_url = f"/ui/notes/{note.note_id}/unlock?view=trash" if view == "trash" else None
        return _render_unlock_panel(request, note, _ui_context(request)["i18n"]["unlock_wrong_pin"], unlock_post_url)

    if view == "trash":
        return get_trashed_note_viewer_panel(request, note_id, note_service, unlock_manager)
    return get_note_editor_panel(request, note_id, note_service, unlock_manager)


@router.get("/ui/security/pin", response_class=HTMLResponse)
def get_private_pin_settings_panel(request: Request) -> HTMLResponse:
    """Render app-level private PIN settings panel."""
    return _render_pin_settings_panel(request)


@router.post("/ui/security/pin/verify", response_class=HTMLResponse)
def verify_private_pin_settings_current_pin(
    request: Request,
    pin_settings: Annotated[PinSettingsManager, Depends(get_pin_settings_manager)],
    crypto_service: Annotated[CryptoService, Depends(get_crypto_service)],
    current_pin: str = Form(...),
) -> HTMLResponse:
    """Verify current app-level private PIN before allowing update fields."""
    lang_ctx = _ui_context(request)
    if not crypto_service.validate_pin_format(current_pin):
        return _render_pin_settings_panel(request, error_message=f"{lang_ctx['i18n']['current_pin_label']} must be exactly 4 digits.")

    if not pin_settings.verify_pin(current_pin):
        return _render_pin_settings_panel(request, error_message=f"{lang_ctx['i18n']['current_pin_label']} is incorrect.")

    return _render_pin_settings_panel(
        request,
        success_message=f"{lang_ctx['i18n']['current_pin_label']} verified. Enter a new PIN.",
        verified_current_pin=current_pin,
    )


@router.post("/ui/security/pin", response_class=HTMLResponse)
def update_private_pin_settings(
    request: Request,
    note_repository: Annotated[SqlNoteRepository, Depends(get_note_repository)],
    crypto_service: Annotated[CryptoService, Depends(get_crypto_service)],
    pin_settings: Annotated[PinSettingsManager, Depends(get_pin_settings_manager)],
    unlock_manager: Annotated[UnlockSessionManager, Depends(get_unlock_session_manager)],
    current_pin: str = Form(...),
    new_pin: str = Form(...),
    confirm_pin: str = Form(...),
) -> HTMLResponse:
    """Change app-level private-note PIN and re-encrypt private note data."""
    lang_ctx = _ui_context(request)
    if not crypto_service.validate_pin_format(current_pin):
        return _render_pin_settings_panel(request, error_message=f"{lang_ctx['i18n']['current_pin_label']} is incorrect.")

    active_pin = pin_settings.get_pin()
    effective_current_pin = current_pin
    recovery_message = ""

    if not pin_settings.verify_pin(current_pin):
        try:
            recovered_count = note_repository.rotate_private_pin(old_pin=current_pin, new_pin=active_pin)
        except Exception:
            recovered_count = 0

        if recovered_count <= 0:
            return _render_pin_settings_panel(request, error_message=f"{lang_ctx['i18n']['current_pin_label']} is incorrect.")

        effective_current_pin = active_pin
        unlock_manager.reset_all()
        recovery_message = f"Recovered {recovered_count} private notes from a previous PIN. "

    if not crypto_service.validate_pin_format(new_pin):
        return _render_pin_settings_panel(
            request,
            error_message=f"{lang_ctx['i18n']['new_pin_label']} must be exactly 4 digits.",
            verified_current_pin=effective_current_pin,
        )

    if new_pin != confirm_pin:
        return _render_pin_settings_panel(
            request,
            error_message=f"{lang_ctx['i18n']['new_pin_label']} and confirmation do not match.",
            verified_current_pin=effective_current_pin,
        )

    if effective_current_pin == new_pin:
        if recovery_message:
            return _render_pin_settings_panel(
                request,
                success_message=f"{recovery_message}PIN unchanged.",
                verified_current_pin=effective_current_pin,
            )
        return _render_pin_settings_panel(
            request,
            error_message=f"{lang_ctx['i18n']['new_pin_label']} must be different from {lang_ctx['i18n']['current_pin_label']}.",
            verified_current_pin=effective_current_pin,
        )

    try:
        note_repository.rotate_private_pin(old_pin=effective_current_pin, new_pin=new_pin)
        pin_settings.set_pin(new_pin)
        crypto_service.set_private_pin(new_pin)
        unlock_manager.reset_all()
    except Exception:
        return _render_pin_settings_panel(
            request,
            error_message=f"Unable to update {lang_ctx['i18n']['change_private_pin'].lower()} right now.",
            verified_current_pin=effective_current_pin,
        )

    return _render_pin_settings_panel(
        request,
        success_message=f"{recovery_message}{lang_ctx['i18n']['change_private_pin']} updated.",
        verified_current_pin=new_pin,
        pin_update_completed=True,
    )


@router.delete("/ui/notes/{note_id}", response_class=HTMLResponse)
def delete_note_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> Response:
    """Move a note to trash and redirect the page to reflect the updated list."""
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
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?lang={lang}"})


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
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?lang={lang}"})


@router.post("/ui/notes/{note_id}/restore", response_class=HTMLResponse)
def restore_note_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> Response:
    """Restore a note from trash and keep the user in trash view."""
    templates = get_templates()
    try:
        note_service.restore(note_id)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?view=trash&lang={lang}"})


@router.post("/ui/notes/trash/bulk-restore", response_class=HTMLResponse)
def bulk_restore_notes_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    note_ids: list[str] = Form(...),
) -> Response:
    """Restore selected notes from trash and stay in trash view."""
    templates = get_templates()
    try:
        note_service.bulk_restore(note_ids)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?view=trash&lang={lang}"})


@router.delete("/ui/notes/{note_id}/purge", response_class=HTMLResponse)
def purge_note_htmx(
    request: Request,
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> Response:
    """Permanently delete a note from trash and stay in trash view."""
    templates = get_templates()
    try:
        note_service.permanently_delete(note_id)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?view=trash&lang={lang}"})


@router.post("/ui/notes/trash/bulk-purge", response_class=HTMLResponse)
def bulk_purge_notes_htmx(
    request: Request,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    note_ids: list[str] = Form(...),
) -> Response:
    """Permanently delete selected trashed notes and stay in trash view."""
    templates = get_templates()
    try:
        note_service.bulk_permanently_delete(note_ids)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "partials/error_message.html",
            {"error_message": map_note_error_message(exc)},
            status_code=map_note_error_status(exc),
        )
    lang = _resolve_lang(request)
    return Response(status_code=200, headers={"HX-Redirect": f"/?view=trash&lang={lang}"})


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
