"""Domain model for notes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class Note:
    """Represents a single note in the domain layer."""

    note_id: str
    title: str
    body: str
    is_private: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def new(cls, title: str, body: str = "", is_private: bool = False) -> "Note":
        """Create a new note with generated id and timestamps."""
        now = datetime.now(timezone.utc)
        return cls(
            note_id=str(uuid4()),
            title=title,
            body=body,
            is_private=is_private,
            is_deleted=False,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
