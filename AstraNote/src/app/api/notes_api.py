"""JSON API routes for note operations."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.app.api.error_mapping import map_note_error_message, map_note_error_status
from src.app.api.schemas import (
    BulkDeleteNotesRequest,
    BulkDeleteNotesResponse,
    CreateNoteRequest,
    CreateNoteResponse,
    SearchNoteResponse,
    UpdateNoteRequest,
    UpdateNoteResponse,
)
from src.app.dependencies import get_note_service
from src.app.services import NoteService


router = APIRouter(prefix="/api/notes", tags=["notes-api"])


@router.get("/search", response_model=list[SearchNoteResponse])
def search_notes(
    note_service: Annotated[NoteService, Depends(get_note_service)],
    q: str = Query(default=""),
) -> list[SearchNoteResponse]:
    """Search notes by title/body with case-insensitive matching."""
    try:
        notes = note_service.search(q)
    except Exception as exc:
        raise HTTPException(
            status_code=map_note_error_status(exc),
            detail=map_note_error_message(exc),
        ) from exc

    return [
        SearchNoteResponse(
            note_id=note.note_id,
            title=note.title,
            body=note.body,
            is_private=note.is_private,
            is_deleted=note.is_deleted,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        for note in notes
    ]


@router.post("", response_model=CreateNoteResponse, status_code=201)
def create_note(
    payload: CreateNoteRequest,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> CreateNoteResponse:
    """Create a note using BL-01 validation and persistence rules."""
    try:
        note = note_service.create(
            title=payload.title,
            body=payload.body,
            is_private=payload.is_private,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=map_note_error_status(exc),
            detail=map_note_error_message(exc),
        ) from exc

    return CreateNoteResponse(
        note_id=note.note_id,
        title=note.title,
        body=note.body,
        is_private=note.is_private,
        is_deleted=note.is_deleted,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> None:
    """Soft-delete a note by id."""
    try:
        note_service.delete(note_id)
    except Exception as exc:
        raise HTTPException(
            status_code=map_note_error_status(exc),
            detail=map_note_error_message(exc),
        ) from exc


@router.post("/bulk-delete", response_model=BulkDeleteNotesResponse)
def bulk_delete_notes(
    payload: BulkDeleteNotesRequest,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> BulkDeleteNotesResponse:
    """Soft-delete multiple notes in one request."""
    try:
        deleted_count = note_service.bulk_delete(payload.note_ids)
    except Exception as exc:
        raise HTTPException(
            status_code=map_note_error_status(exc),
            detail=map_note_error_message(exc),
        ) from exc

    return BulkDeleteNotesResponse(deleted_count=deleted_count)


@router.put("/{note_id}", response_model=UpdateNoteResponse)
def update_note(
    note_id: str,
    payload: UpdateNoteRequest,
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> UpdateNoteResponse:
    """Edit an existing note using BL-02 validation and persistence rules."""
    try:
        note = note_service.update(
            note_id=note_id,
            title=payload.title,
            body=payload.body,
            is_private=payload.is_private,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=map_note_error_status(exc),
            detail=map_note_error_message(exc),
        ) from exc

    return UpdateNoteResponse(
        note_id=note.note_id,
        title=note.title,
        body=note.body,
        is_private=note.is_private,
        is_deleted=note.is_deleted,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
