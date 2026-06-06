"""BL-10 performance verification tests for NFR-06 through NFR-09."""

from __future__ import annotations

import math
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.app.dependencies import get_note_repository, get_note_service
from src.app.repositories.sql_note_repository import SqlNoteRepository
from src.app.services import NoteService
from src.main import app

DATASET_SIZE = 5_000
READ_P95_TARGET_MS = 120.0
WRITE_P95_TARGET_MS = 180.0
ALL_OPS_P99_TARGET_MS = 300.0


@pytest.fixture(scope="module")
def performance_client() -> TestClient:
    """Provide a TestClient bound to a dedicated BL-10 SQLite database."""
    db_path = Path("data") / "astranote_bl10_performance.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}")
    service = NoteService(repository)

    app.dependency_overrides[get_note_repository] = lambda: repository
    app.dependency_overrides[get_note_service] = lambda: service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    repository.engine.dispose()
    if db_path.exists():
        db_path.unlink()


def _percentile(values_ms: list[float], percentile: float) -> float:
    """Compute percentile using nearest-rank after sorting."""
    if not values_ms:
        raise ValueError("Cannot compute percentile of empty sample")

    ordered = sorted(values_ms)
    rank = max(1, math.ceil((percentile / 100.0) * len(ordered)))
    return ordered[rank - 1]


def _seed_dataset(client: TestClient, size: int) -> list[str]:
    """Create notes through API to include end-to-end write path in setup."""
    note_ids: list[str] = []
    for i in range(size):
        response = client.post(
            "/api/notes",
            json={
                "title": f"BL10 Seed {i:05d}",
                "body": f"performance seed body {i}",
                "is_private": False,
            },
        )
        assert response.status_code == 201, response.text
        note_ids.append(response.json()["note_id"])
    return note_ids


@pytest.mark.performance
@pytest.mark.slow
def test_bl10_performance_gate_nfr06_to_nfr09(performance_client: TestClient) -> None:
    """Validate BL-10 latency and durable write semantics at service boundary."""
    note_ids = _seed_dataset(performance_client, DATASET_SIZE)

    read_latencies: list[float] = []
    write_latencies: list[float] = []
    all_op_latencies: list[float] = []

    read_queries = [
        "BL10 Seed",
        "body 42",
        "body 777",
        "body 2048",
        "body 4096",
        "",
    ]

    # Read samples: API read boundary only (search + list via empty-query search).
    for i in range(80):
        query = read_queries[i % len(read_queries)]
        started = time.perf_counter()
        response = performance_client.get("/api/notes/search", params={"q": query})
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        assert response.status_code == 200, response.text
        read_latencies.append(elapsed_ms)
        all_op_latencies.append(elapsed_ms)

    # Write samples: update existing notes and then verify persisted state via read-back.
    for i, note_id in enumerate(note_ids[:60]):
        updated_body = f"durability-check-{i}"
        started = time.perf_counter()
        response = performance_client.put(
            f"/api/notes/{note_id}",
            json={
                "title": f"BL10 Seed {i:05d}",
                "body": updated_body,
                "is_private": False,
            },
        )
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        assert response.status_code == 200, response.text

        # NFR-09 durability check: successful write must be visible immediately
        # after success returns.
        verify = performance_client.get(
            "/api/notes/search",
            params={"q": updated_body},
        )
        assert verify.status_code == 200, verify.text
        bodies = [row["body"] for row in verify.json()]
        assert updated_body in bodies

        write_latencies.append(elapsed_ms)
        all_op_latencies.append(elapsed_ms)

    read_p95 = _percentile(read_latencies, 95.0)
    write_p95 = _percentile(write_latencies, 95.0)
    all_ops_p99 = _percentile(all_op_latencies, 99.0)

    print(
        (
            f"BL10_METRICS read_p95_ms={read_p95:.2f} "
            f"write_p95_ms={write_p95:.2f} all_ops_p99_ms={all_ops_p99:.2f} "
            f"dataset_size={DATASET_SIZE}"
        )
    )

    assert (
        read_p95 <= READ_P95_TARGET_MS
    ), f"Read p95 {read_p95:.2f} ms exceeds {READ_P95_TARGET_MS:.2f} ms"
    assert (
        write_p95 <= WRITE_P95_TARGET_MS
    ), f"Write p95 {write_p95:.2f} ms exceeds {WRITE_P95_TARGET_MS:.2f} ms"
    assert (
        all_ops_p99 <= ALL_OPS_P99_TARGET_MS
    ), f"All-ops p99 {all_ops_p99:.2f} ms exceeds {ALL_OPS_P99_TARGET_MS:.2f} ms"
