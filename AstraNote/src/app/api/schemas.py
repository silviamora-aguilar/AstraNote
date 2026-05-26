"""Request and response schemas for note routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CreateNoteRequest(BaseModel):
    """Request model for creating a new note."""

    title: str
    body: str = ""
    is_private: bool = False


class CreateNoteResponse(BaseModel):
    """Response model for created notes."""

    note_id: str
    title: str
    body: str
    is_private: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class UpdateNoteRequest(BaseModel):
    """Request model for editing an existing note."""

    title: str
    body: str = ""
    is_private: bool = False


class UpdateNoteResponse(BaseModel):
    """Response model for edited notes."""

    note_id: str
    title: str
    body: str
    is_private: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class SearchNoteResponse(BaseModel):
    """Response model for note search result items."""

    note_id: str
    title: str
    body: str
    is_private: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class BulkDeleteNotesRequest(BaseModel):
    """Request model for deleting multiple notes."""

    note_ids: list[str]


class BulkDeleteNotesResponse(BaseModel):
    """Response model for a bulk delete operation."""

    deleted_count: int
