"""Unit tests for BL-01 note creation rules."""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest

from src.app.models.note import Note
from src.app.repositories.note_repository import (
    NoteRepository,
    NoteRepositoryCapacityError,
    NoteRepositoryNotFoundError,
)
from src.app.services.note_service import (
    CAPACITY_ERROR_MESSAGE,
    NoteCapacityError,
    NoteNotFoundError,
    NoteService,
    NoteValidationError,
)


class FakeNoteRepository(NoteRepository):
    """In-memory fake repository for NoteService unit tests."""

    def __init__(self) -> None:
        self.notes: list[Note] = []

    def create_note_atomic(
        self,
        title: str,
        body: str,
        is_private: bool,
        max_notes: int,
    ) -> Note:
        active_count = self.count_active_notes()
        if active_count >= max_notes:
            raise NoteRepositoryCapacityError("capacity reached")

        candidate = title
        suffix = 1
        while self.title_exists(candidate):
            candidate = f"{title}{suffix}"
            suffix += 1

        note = Note.new(title=candidate, body=body, is_private=is_private)
        self.notes.append(note)
        return note

    def save(self, note: Note) -> Note:
        self.notes.append(note)
        return note

    def update_note_atomic(
        self,
        note_id: str,
        title: str,
        body: str,
        is_private: bool,
    ) -> Note:
        note = self.get(note_id)
        if note is None or note.is_deleted:
            raise NoteRepositoryNotFoundError("note not found")

        candidate = title
        suffix = 1
        while self.title_exists_for_other(candidate, note_id):
            candidate = f"{title}{suffix}"
            suffix += 1

        note.title = candidate
        note.body = body
        note.is_private = is_private
        note.updated_at = datetime.now(timezone.utc)
        return note

    def get(self, note_id: str) -> Note | None:
        for note in self.notes:
            if note.note_id == note_id:
                return note
        return None

    def list(self) -> list[Note]:
        return [note for note in self.notes if not note.is_deleted]

    def search(self, query: str) -> list[Note]:
        lowered = query.lower()
        return [
            note
            for note in self.notes
            if not note.is_deleted and (lowered in note.title.lower() or lowered in note.body.lower())
        ]

    def soft_delete(self, note_id: str) -> bool:
        raise NotImplementedError

    def restore(self, note_id: str) -> bool:
        raise NotImplementedError

    def count_active_notes(self) -> int:
        return len([note for note in self.notes if not note.is_deleted])

    def title_exists(self, title: str) -> bool:
        return any(note.title == title and not note.is_deleted for note in self.notes)

    def title_exists_for_other(self, title: str, note_id: str) -> bool:
        return any(
            note.title == title and note.note_id != note_id and not note.is_deleted
            for note in self.notes
        )


@pytest.mark.unit
def test_create_note_persists_and_sets_generated_id_and_timestamps() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    note = service.create(title='My First Note', body='hello')

    assert note.note_id
    assert note.title == 'My First Note'
    assert note.body == 'hello'
    assert note.created_at == note.updated_at
    assert repo.get(note.note_id) is not None


@pytest.mark.unit
def test_create_note_applies_duplicate_title_suffix() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    first = service.create(title='Title', body='a')
    second = service.create(title='Title', body='b')
    third = service.create(title='Title', body='c')

    assert first.title == 'Title'
    assert second.title == 'Title1'
    assert third.title == 'Title2'


@pytest.mark.unit
def test_create_note_rejects_symbol_in_title() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteValidationError, match='unsupported symbols'):
        service.create(title='bad<title')


@pytest.mark.unit
def test_create_note_rejects_empty_title_after_trim() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteValidationError, match='Title is required'):
        service.create(title='   ')


@pytest.mark.unit
def test_create_note_rejects_title_above_max_length() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteValidationError, match='Title must be 1-255 characters'):
        service.create(title='a' * 256)


@pytest.mark.unit
def test_create_note_rejects_title_with_newline() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteValidationError, match='newlines'):
        service.create(title='line1\nline2')


@pytest.mark.unit
def test_create_note_rejects_body_above_limit() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteValidationError, match='0-10000'):
        service.create(title='Valid Title', body='a' * 10001)


@pytest.mark.unit
def test_create_note_accepts_spanish_accented_letters_in_title() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    note = service.create(title='Pañuelos de muñeca')
    assert note.title == 'Pañuelos de muñeca'


@pytest.mark.unit
def test_create_note_accepts_spanish_inverted_punctuation_in_title() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    note = service.create(title='¿Qué tal?')
    assert note.title == '¿Qué tal?'


@pytest.mark.unit
def test_create_note_accepts_spanish_characters_in_body() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    note = service.create(title='Nota', body='Él dijo: ¡Hola! ¿Cómo estás, señor García?')
    assert 'ñ' in note.body
    assert '¡' in note.body
    assert '¿' in note.body


@pytest.mark.unit
def test_create_note_blocks_when_capacity_is_reached() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    for index in range(10_000):
        service.create(title=f'Title {index}')

    with pytest.raises(NoteCapacityError, match=re.escape(CAPACITY_ERROR_MESSAGE)):
        service.create(title='Overflow')


@pytest.mark.unit
def test_list_notes_returns_active_repository_notes() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    created = service.create(title='List Me', body='x')
    notes = service.list_notes()

    assert len(notes) == 1
    assert notes[0].note_id == created.note_id


@pytest.mark.unit
def test_update_note_persists_title_body_and_updates_timestamp() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    created = service.create(title='Original', body='before')
    updated = service.update(note_id=created.note_id, title='Updated', body='after', is_private=True)

    assert updated.note_id == created.note_id
    assert updated.created_at == created.created_at
    assert updated.updated_at > created.created_at
    assert updated.title == 'Updated'
    assert updated.body == 'after'
    assert updated.is_private is True


@pytest.mark.unit
def test_update_note_applies_duplicate_suffix_excluding_current_note() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    existing = service.create(title='Title', body='a')
    target = service.create(title='Another', body='b')

    updated = service.update(note_id=target.note_id, title='Title', body='c', is_private=False)

    assert existing.title == 'Title'
    assert updated.title == 'Title1'


@pytest.mark.unit
def test_update_note_keeps_same_title_without_self_suffix() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    created = service.create(title='Stable', body='a')
    updated = service.update(note_id=created.note_id, title='Stable', body='changed', is_private=False)

    assert updated.title == 'Stable'
    assert updated.body == 'changed'


@pytest.mark.unit
def test_update_note_raises_not_found_for_missing_note() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)

    with pytest.raises(NoteNotFoundError, match='Note not found'):
        service.update(note_id='missing-note-id', title='Any title', body='x')


@pytest.mark.unit
def test_update_note_rejects_invalid_title() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    created = service.create(title='Valid', body='a')

    with pytest.raises(NoteValidationError, match='unsupported symbols'):
        service.update(note_id=created.note_id, title='bad<title', body='x')


@pytest.mark.unit
def test_update_note_rejects_empty_title_after_trim() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    created = service.create(title='Valid', body='a')

    with pytest.raises(NoteValidationError, match='Title is required'):
        service.update(note_id=created.note_id, title='   ', body='x')


@pytest.mark.unit
def test_update_note_rejects_title_above_max_length() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    created = service.create(title='Valid', body='a')

    with pytest.raises(NoteValidationError, match='Title must be 1-255 characters'):
        service.update(note_id=created.note_id, title='a' * 256, body='x')


@pytest.mark.unit
def test_toggle_checklist_item_persists_checked_state_immediately() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    note = service.create(
        title='Checklist',
        body='- [ ] first task\n- [x] second task',
    )

    updated = service.toggle_checklist_item(note.note_id, line_index=0, checked=True)

    assert '- [x] first task' in updated.body
    reloaded = service.get_note(note.note_id)
    assert reloaded is not None
    assert '- [x] first task' in reloaded.body


@pytest.mark.unit
def test_toggle_checklist_item_persists_unchecked_state_immediately() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    note = service.create(title='Checklist', body='- [x] done task')

    updated = service.toggle_checklist_item(note.note_id, line_index=0, checked=False)

    assert updated.body == '- [ ] done task'


@pytest.mark.unit
def test_toggle_checklist_item_rejects_out_of_range_index() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    note = service.create(title='Checklist', body='- [ ] first task')

    with pytest.raises(NoteValidationError, match='out of range'):
        service.toggle_checklist_item(note.note_id, line_index=2, checked=True)


@pytest.mark.unit
def test_toggle_checklist_item_supports_unicode_checkbox_lines() -> None:
    repo = FakeNoteRepository()
    service = NoteService(repo)
    note = service.create(title='Checklist', body='☐ first task\n☑ second task')

    checked = service.toggle_checklist_item(note.note_id, line_index=0, checked=True)
    assert checked.body.split('\n')[0].startswith('☑ ')

    unchecked = service.toggle_checklist_item(note.note_id, line_index=1, checked=False)
    assert unchecked.body.split('\n')[1].startswith('☐ ')
