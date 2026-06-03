"""SQLite-backed repository implementation for notes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    Text,
    UniqueConstraint,
    and_,
    create_engine,
    func,
    inspect,
    select,
    text,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import NullPool

from src.app.models.note import Note
from src.app.repositories.note_repository import (
    NoteRepository,
    NoteRepositoryCapacityError,
    NoteRepositoryError,
    NoteRepositoryNotFoundError,
)
from src.app.security import CryptoService


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
    pin_salt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SqlNoteRepository(NoteRepository):
    """SQLite-backed NoteRepository implementation."""

    def __init__(
        self,
        database_url: str = "sqlite:///./data/astranote.db",
        crypto_service: CryptoService | None = None,
    ) -> None:
        if database_url.startswith("sqlite:///./"):
            db_rel_path = database_url.removeprefix("sqlite:///./")
            Path(db_rel_path).parent.mkdir(parents=True, exist_ok=True)

        engine_kwargs = {"future": True}
        if database_url.startswith("sqlite:///"):
            engine_kwargs["poolclass"] = NullPool

        self.engine = create_engine(database_url, **engine_kwargs)
        self._session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        self._crypto = crypto_service or CryptoService()
        Base.metadata.create_all(self.engine)
        self._ensure_security_columns()

    def _ensure_security_columns(self) -> None:
        """Add security columns for existing local databases without migrations."""
        with self.engine.connect() as conn:
            inspector = inspect(conn)
            columns = {col["name"] for col in inspector.get_columns("notes")}
        alter_stmts: list[str] = []

        if "pin_salt" not in columns:
            alter_stmts.append("ALTER TABLE notes ADD COLUMN pin_salt VARCHAR(64)")

        if not alter_stmts:
            return

        with self.engine.begin() as conn:
            for stmt in alter_stmts:
                conn.execute(text(stmt))

    def _encrypt_title_body(self, title: str, body: str, is_private: bool, pin_salt: str | None) -> tuple[str, str, str | None]:
        if is_private:
            effective_salt = pin_salt or self._crypto.new_pin_salt()
            return (
                self._crypto.encrypt_private(title, effective_salt),
                self._crypto.encrypt_private(body, effective_salt),
                effective_salt,
            )

        return (
            self._crypto.encrypt_public(title),
            self._crypto.encrypt_public(body),
            None,
        )

    def _decrypt_title_body(self, record: NoteRecord) -> tuple[str, str]:
        if record.is_private and record.pin_salt:
            title = self._crypto.decrypt_private(record.title, record.pin_salt)
            body = self._crypto.decrypt_private(record.body, record.pin_salt)
            return title, body

        title = self._crypto.decrypt_public(record.title)
        body = self._crypto.decrypt_public(record.body)
        return title, body

    def _to_domain(self, record: NoteRecord) -> Note:
        title, body = self._decrypt_title_body(record)
        return Note(
            note_id=record.note_id,
            title=title,
            body=body,
            is_private=record.is_private,
            is_deleted=record.is_deleted,
            created_at=record.created_at,
            updated_at=record.updated_at,
            deleted_at=record.deleted_at,
        )

    def _list_active_records(self, session) -> list[NoteRecord]:
        stmt = (
            select(NoteRecord)
            .where(NoteRecord.is_deleted.is_(False))
            .order_by(NoteRecord.created_at.desc())
        )
        return list(session.scalars(stmt).all())

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
                        active_records = self._list_active_records(session)
                        active_count = len(active_records)
                        if active_count >= max_notes:
                            raise NoteRepositoryCapacityError("capacity reached")

                        candidate = title
                        suffix = 1
                        while True:
                            if not any(self._to_domain(record).title == candidate for record in active_records):
                                break
                            candidate = f"{title}{suffix}"
                            suffix += 1

                        note = Note.new(title=candidate, body=body, is_private=is_private)
                        encrypted_title, encrypted_body, pin_salt = self._encrypt_title_body(
                            title=note.title,
                            body=note.body,
                            is_private=note.is_private,
                            pin_salt=None,
                        )
                        session.add(
                            NoteRecord(
                                note_id=note.note_id,
                                title=encrypted_title,
                                body=encrypted_body,
                                is_private=note.is_private,
                                pin_salt=pin_salt,
                                is_deleted=note.is_deleted,
                                created_at=note.created_at,
                                updated_at=note.updated_at,
                                deleted_at=note.deleted_at,
                            )
                        )
                    return note
                except NoteRepositoryCapacityError:
                    raise
                except SQLAlchemyError as exc:
                    raise NoteRepositoryError("Failed to persist note") from exc

        raise NoteRepositoryError("Failed to persist note after concurrent title conflicts")

    def save(self, note: Note) -> Note:
        encrypted_title, encrypted_body, pin_salt = self._encrypt_title_body(
            title=note.title,
            body=note.body,
            is_private=note.is_private,
            pin_salt=None,
        )
        record = NoteRecord(
            note_id=note.note_id,
            title=encrypted_title,
            body=encrypted_body,
            is_private=note.is_private,
            pin_salt=pin_salt,
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

                        active_records = [r for r in self._list_active_records(session) if r.note_id != note_id]

                        candidate = title
                        suffix = 1
                        while True:
                            if not any(self._to_domain(active_record).title == candidate for active_record in active_records):
                                break
                            candidate = f"{title}{suffix}"
                            suffix += 1

                        encrypted_title, encrypted_body, pin_salt = self._encrypt_title_body(
                            title=candidate,
                            body=body,
                            is_private=is_private,
                            pin_salt=record.pin_salt,
                        )
                        record.title = encrypted_title
                        record.body = encrypted_body
                        record.is_private = is_private
                        record.pin_salt = pin_salt
                        record.updated_at = datetime.now(timezone.utc)

                    session.refresh(record)
                    return self._to_domain(record)
                except NoteRepositoryNotFoundError:
                    raise
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
        normalized_query = query.lower()
        with self._session_factory() as session:
            records = self._list_active_records(session)
            matched: list[Note] = []
            for record in records:
                note = self._to_domain(record)
                if normalized_query in note.title.lower() or normalized_query in note.body.lower():
                    matched.append(note)
            return matched

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
        with self._session_factory() as session:
            try:
                with session.begin():
                    record = session.get(NoteRecord, note_id)
                    if record is None or not record.is_deleted:
                        return False
                    record.is_deleted = False
                    record.deleted_at = None
                    record.updated_at = datetime.now(timezone.utc)
                return True
            except SQLAlchemyError as exc:
                raise NoteRepositoryError("Failed to restore note") from exc

    def list_deleted(self) -> list[Note]:
        with self._session_factory() as session:
            stmt = (
                select(NoteRecord)
                .where(NoteRecord.is_deleted.is_(True))
                .order_by(NoteRecord.deleted_at.desc().nullslast(), NoteRecord.created_at.desc())
            )
            records = session.scalars(stmt).all()
            return [self._to_domain(record) for record in records]

    def hard_delete(self, note_id: str) -> bool:
        with self._session_factory() as session:
            try:
                with session.begin():
                    record = session.get(NoteRecord, note_id)
                    if record is None:
                        return False
                    session.delete(record)
                return True
            except SQLAlchemyError as exc:
                raise NoteRepositoryError("Failed to permanently delete note") from exc

    def purge_soft_deleted_older_than(self, retention_days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        with self._session_factory() as session:
            try:
                with session.begin():
                    stmt = (
                        select(NoteRecord)
                        .where(
                            and_(
                                NoteRecord.is_deleted.is_(True),
                                NoteRecord.deleted_at.is_not(None),
                                NoteRecord.deleted_at < cutoff,
                            )
                        )
                    )
                    records = list(session.scalars(stmt).all())
                    for record in records:
                        session.delete(record)
                return len(records)
            except SQLAlchemyError as exc:
                raise NoteRepositoryError("Failed to purge expired deleted notes") from exc

    def count_active_notes(self) -> int:
        with self._session_factory() as session:
            stmt = select(func.count()).select_from(NoteRecord).where(NoteRecord.is_deleted.is_(False))
            count = session.scalar(stmt)
            return int(count or 0)

    def title_exists(self, title: str) -> bool:
        with self._session_factory() as session:
            records = self._list_active_records(session)
            return any(self._to_domain(record).title == title for record in records)

    def rotate_private_pin(self, old_pin: str, new_pin: str) -> int:
        """Re-encrypt private note fields when app-level PIN changes."""
        if not self._crypto.validate_pin_format(old_pin) or not self._crypto.validate_pin_format(new_pin):
            raise NoteRepositoryError("Failed to rotate private note PIN")

        updated_count = 0
        with self._session_factory() as session:
            try:
                with session.begin():
                    stmt = select(NoteRecord).where(
                        and_(NoteRecord.is_private.is_(True), NoteRecord.pin_salt.is_not(None))
                    )
                    records = list(session.scalars(stmt).all())
                    for record in records:
                        if not record.pin_salt:
                            continue
                        plaintext_title = self._crypto.decrypt_private_with_pin(record.title, record.pin_salt, old_pin)
                        plaintext_body = self._crypto.decrypt_private_with_pin(record.body, record.pin_salt, old_pin)
                        record.title = self._crypto.encrypt_private_with_pin(plaintext_title, record.pin_salt, new_pin)
                        record.body = self._crypto.encrypt_private_with_pin(plaintext_body, record.pin_salt, new_pin)
                        updated_count += 1
            except Exception as exc:
                raise NoteRepositoryError("Failed to rotate private note PIN") from exc
        return updated_count
