"""SQLite-backed repository implementation for notes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint, and_, create_engine, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src.app.models.note import Note
from src.app.repositories.note_repository import (
    NoteRepository,
    NoteRepositoryCapacityError,
    NoteRepositoryError,
    NoteRepositoryNotFoundError,
)


class Base(DeclarativeBase):
    """Base SQLAlchemy declarative class."""


class NoteRecord(Base):
    """ORM model for note persistence."""

    __tablename__ = "notes"
    __table_args__ = (UniqueConstraint("title", "is_deleted", name="uq_notes_title_is_deleted"),)

    note_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SqlNoteRepository(NoteRepository):
    """SQLite-backed NoteRepository implementation."""

    def __init__(self, database_url: str = "sqlite:///./data/astranote.db") -> None:
        if database_url.startswith("sqlite:///./"):
            db_rel_path = database_url.removeprefix("sqlite:///./")
            Path(db_rel_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(database_url, future=True)
        self._session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        Base.metadata.create_all(self.engine)

    def _to_domain(self, record: NoteRecord) -> Note:
        return Note(
            note_id=record.note_id,
            title=record.title,
            body=record.body,
            is_private=record.is_private,
            is_deleted=record.is_deleted,
            created_at=record.created_at,
            updated_at=record.updated_at,
            deleted_at=record.deleted_at,
        )

    def create_note_atomic(
        self,
        title: str,
        body: str,
        is_private: bool,
        max_notes: int,
    ) -> Note:
        """Atomically enforce capacity and title uniqueness before insert."""
        max_retries = 20
        for _ in range(max_retries):
            with self._session_factory() as session:
                try:
                    with session.begin():
                        count_stmt = select(func.count()).select_from(NoteRecord).where(NoteRecord.is_deleted.is_(False))
                        active_count = int(session.scalar(count_stmt) or 0)
                        if active_count >= max_notes:
                            raise NoteRepositoryCapacityError("capacity reached")

                        candidate = title
                        suffix = 1
                        while True:
                            exists_stmt = (
                                select(NoteRecord.note_id)
                                .where(
                                    and_(
                                        NoteRecord.title == candidate,
                                        NoteRecord.is_deleted.is_(False),
                                    )
                                )
                                .limit(1)
                            )
                            if session.scalar(exists_stmt) is None:
                                break
                            candidate = f"{title}{suffix}"
                            suffix += 1

                        note = Note.new(title=candidate, body=body, is_private=is_private)
                        session.add(
                            NoteRecord(
                                note_id=note.note_id,
                                title=note.title,
                                body=note.body,
                                is_private=note.is_private,
                                is_deleted=note.is_deleted,
                                created_at=note.created_at,
                                updated_at=note.updated_at,
                                deleted_at=note.deleted_at,
                            )
                        )
                    return note
                except NoteRepositoryCapacityError:
                    raise
                except IntegrityError:
                    # Another writer won the same title; retry and recompute suffix.
                    continue
                except SQLAlchemyError as exc:
                    raise NoteRepositoryError("Failed to persist note") from exc

        raise NoteRepositoryError("Failed to persist note after concurrent title conflicts")

    def save(self, note: Note) -> Note:
        record = NoteRecord(
            note_id=note.note_id,
            title=note.title,
            body=note.body,
            is_private=note.is_private,
            is_deleted=note.is_deleted,
            created_at=note.created_at,
            updated_at=note.updated_at,
            deleted_at=note.deleted_at,
        )
        with self._session_factory() as session:
            try:
                session.add(record)
                session.commit()
            except SQLAlchemyError as exc:
                session.rollback()
                raise NoteRepositoryError("Failed to persist note") from exc
        return note

    def update_note_atomic(
        self,
        note_id: str,
        title: str,
        body: str,
        is_private: bool,
    ) -> Note:
        """Atomically update title/body with duplicate-title handling that excludes self."""
        max_retries = 20
        for _ in range(max_retries):
            with self._session_factory() as session:
                try:
                    with session.begin():
                        record = session.get(NoteRecord, note_id)
                        if record is None or record.is_deleted:
                            raise NoteRepositoryNotFoundError("note not found")

                        candidate = title
                        suffix = 1
                        while True:
                            exists_stmt = (
                                select(NoteRecord.note_id)
                                .where(
                                    and_(
                                        NoteRecord.title == candidate,
                                        NoteRecord.is_deleted.is_(False),
                                        NoteRecord.note_id != note_id,
                                    )
                                )
                                .limit(1)
                            )
                            if session.scalar(exists_stmt) is None:
                                break
                            candidate = f"{title}{suffix}"
                            suffix += 1

                        record.title = candidate
                        record.body = body
                        record.is_private = is_private
                        record.updated_at = datetime.now(timezone.utc)

                    session.refresh(record)
                    return self._to_domain(record)
                except NoteRepositoryNotFoundError:
                    raise
                except IntegrityError:
                    # Another writer won the same title; retry and recompute suffix.
                    continue
                except SQLAlchemyError as exc:
                    raise NoteRepositoryError("Failed to update note") from exc

        raise NoteRepositoryError("Failed to update note after concurrent title conflicts")

    def get(self, note_id: str) -> Note | None:
        with self._session_factory() as session:
            record = session.get(NoteRecord, note_id)
            if record is None:
                return None
            return self._to_domain(record)

    def list(self) -> list[Note]:
        with self._session_factory() as session:
            stmt = (
                select(NoteRecord)
                .where(NoteRecord.is_deleted.is_(False))
                .order_by(NoteRecord.created_at.desc())
            )
            records = session.scalars(stmt).all()
            return [self._to_domain(record) for record in records]

    def search(self, query: str) -> list[Note]:
        with self._session_factory() as session:
            escaped_query = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            like_query = f"%{escaped_query}%"
            stmt = (
                select(NoteRecord)
                .where(
                    and_(
                        NoteRecord.is_deleted.is_(False),
                        or_(
                            NoteRecord.title.ilike(like_query, escape="\\"),
                            NoteRecord.body.ilike(like_query, escape="\\"),
                        ),
                    )
                )
                .order_by(NoteRecord.created_at.desc())
            )
            records = session.scalars(stmt).all()
            return [self._to_domain(record) for record in records]

    def soft_delete(self, note_id: str) -> bool:
        with self._session_factory() as session:
            try:
                with session.begin():
                    record = session.get(NoteRecord, note_id)
                    if record is None or record.is_deleted:
                        return False
                    record.is_deleted = True
                    record.deleted_at = datetime.now(timezone.utc)
                return True
            except SQLAlchemyError as exc:
                raise NoteRepositoryError("Failed to delete note") from exc

    def restore(self, note_id: str) -> bool:
        raise NotImplementedError("restore is implemented in BL-03")

    def count_active_notes(self) -> int:
        with self._session_factory() as session:
            stmt = select(func.count()).select_from(NoteRecord).where(NoteRecord.is_deleted.is_(False))
            count = session.scalar(stmt)
            return int(count or 0)

    def title_exists(self, title: str) -> bool:
        with self._session_factory() as session:
            stmt = (
                select(NoteRecord.note_id)
                .where(
                    and_(
                        NoteRecord.title == title,
                        NoteRecord.is_deleted.is_(False),
                    )
                )
                .limit(1)
            )
            return session.scalar(stmt) is not None
