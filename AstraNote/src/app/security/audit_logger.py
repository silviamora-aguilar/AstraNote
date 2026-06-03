"""File-backed audit logging for note operations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(slots=True)
class AuditEntry:
    """Minimal audit record for note operations.

    Content fields (title/body) are intentionally excluded to avoid plaintext leakage.
    """

    actor: str
    action: str
    note_id: str
    timestamp_utc: str
    outcome: str
    correlation_id: str
    error_code: str | None = None


class AuditLogger:
    """Append-only JSONL audit logger."""

    def __init__(self, log_path: Path | str = "data/audit-log.jsonl") -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        actor: str,
        action: str,
        note_id: str,
        outcome: str,
        correlation_id: str | None = None,
        error_code: str | None = None,
    ) -> AuditEntry:
        """Append one audit event and return the created entry."""
        entry = AuditEntry(
            actor=actor,
            action=action,
            note_id=note_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            outcome=outcome,
            correlation_id=correlation_id or str(uuid4()),
            error_code=error_code,
        )
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(entry), ensure_ascii=True))
            handle.write("\n")
        return entry
