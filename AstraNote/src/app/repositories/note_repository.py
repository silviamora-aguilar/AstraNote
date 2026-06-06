"""Abstract repository contract for note persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from src.app.models.note import Note


class NoteRepositoryError(RuntimeError):
    """Repository-level error raised when persistence fails."""


class NoteRepositoryCapacityError(NoteRepositoryError):
    """Repository-level error raised when note capacity is reached."""


class NoteRepositoryNotFoundError(NoteRepositoryError):
    """Repository-level error raised when a note cannot be found."""


class NoteRepository(ABC):
    """Persistence contract for note operations."""

    @abstractmethod
    def create_note_atomic(
        self,
        title: str,
        body: str,
        is_private: bool,
        max_notes: int,
    ) -> Note:
        """Create a note in one transaction including capacity and title allocation."""

    @abstractmethod
    def save(self, note: Note) -> Note:
        """Persist a new note."""

    @abstractmethod
    def update_note_atomic(
        self,
        note_id: str,
        title: str,
        body: str,
        is_private: bool,
    ) -> Note:
        """Update title/body in one transaction with duplicate-title handling."""

    @abstractmethod
    def get(self, note_id: str) -> Note | None:
        """Get a note by id if it exists."""

    @abstractmethod
    def list(self) -> List[Note]:
        """List active notes."""

    @abstractmethod
    def search(self, query: str) -> List[Note]:
        """Search notes by query."""

    def list_deleted(self) -> List[Note]:
        """List soft-deleted notes when supported by the implementation."""
        return []

    def hard_delete(self, note_id: str) -> bool:
        """Permanently delete a note when supported by the implementation."""
        return False

    def purge_soft_deleted_older_than(self, retention_days: int) -> int:
        """Purge expired deleted notes when supported by the implementation."""
        return 0

    def rotate_private_pin(self, old_pin: str, new_pin: str) -> int:
        """Re-encrypt private-note data after an app PIN change when supported."""
        return 0

    @abstractmethod
    def soft_delete(self, note_id: str) -> bool:
        """Soft delete a note by id."""

    @abstractmethod
    def restore(self, note_id: str) -> bool:
        """Restore a soft-deleted note by id."""

    @abstractmethod
    def count_active_notes(self) -> int:
        """Count non-deleted notes."""

    @abstractmethod
    def title_exists(self, title: str) -> bool:
        """Return whether an active note title already exists."""
