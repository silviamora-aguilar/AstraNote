# Release Gates — AstraNotes MVP

**Version**: 1.5  
**Date**: 2026-06-05

A release gate is a mandatory pass/fail check that must be satisfied before any code is shipped. Every item below must be ✅ before an MVP release is cut. No exceptions.

## Current Gate Status Snapshot (2026-06-05)

| Gate | Current Status | Notes |
|---|---|---|
| Gate 1 — Functional Completeness | 🟢 Pass | In-scope MVP backlog slices are complete; deferred Post-MVP slices remain explicitly documented. |
| Gate 2 — All Tests Pass | 🟢 Pass | Unit, integration, security, and performance suites for MVP scope are passing. |
| Gate 3 — Security Requirements Verified | 🟢 Pass | In-scope SRG checks have implementation and verification evidence recorded. |
| Gate 4 — Performance Benchmarks Met | 🟢 Pass | NFR-06/07/08/09 benchmark targets are met and measured. |
| Gate 5 — Code Quality and Architecture | 🟢 Pass | Architecture boundaries, error safety, and transaction guarantees are satisfied for MVP scope. |
| Gate 6 — Definition of Done | 🟢 Pass | MVP stories marked done satisfy DoD criteria and traceability alignment. |
| Gate 7 — No Open P0/P1 Defects | 🟢 Pass | No known open P0/P1 defects in active MVP scope. |

---

## Gate 1 — Functional Completeness

All MVP backlog items must be complete and verified:

| Item | Requirement Coverage | Status |
|---|---|---|
| BL-01: Create note | REQ-01–04 | ✅ |
| BL-02: Edit note | REQ-05–08 | ✅ |
| BL-03: Delete note | REQ-09–11 + SRG-10, 11, 13 | ✅ |
| BL-03.1: Bulk delete selected notes (extension) | REQ-09–11 (multi-select UX extension) | ✅ |
| BL-04: List notes | REQ-12–14 | ✅ |
| BL-05: Search | REQ-15–16 | ✅ |
| BL-06: Lists in notes | REQ-17–19 | ✅ |
| BL-07: Text formatting | REQ-20–22 | ✅ |
| BL-08: Note capacity | REQ-23–24 | ✅ |
| BL-09: Privacy state and preview suppression | REQ-25–27 | ✅ |
| BL-10: Performance verification | NFR-06–09 | ✅ |
| BL-11: Input model and accessibility parity | NFR-10, NFR-12 | Deferred [Post-MVP] |
| BL-12: Architecture boundaries | NFR-13–16 | ✅ |
| BL-13: Security stack | SRG-01, 02, 04, 05, 07, 08, 10, 11, 12, 13–26 | ✅ |
| BL-23: Interface localization toggle | REQ-28 | ✅ |
| BL-21: Serviceability/manageability | SMR-01, 03, 04, 05, 06, 07, 09, 10, 11 (SMR-02, 08, 12 deferred [Post-MVP]) | ✅ |
| BL-22: Web multi-user foundation | WEB-01–11 | Deferred [Post-MVP] |
| BL-24: Nested list depth (3 levels) | REQ-29 | Deferred [Post-MVP] |
| BL-25: Image paste in note body | REQ-30 | Deferred [Post-MVP] |
| BL-26: Concurrency/load verification | NFR-01–05 | Deferred [Post-MVP] |

---

## Gate 2 — All Tests Pass

All test suites must pass with zero failures:

| Suite | File | Status |
|---|---|---|
| Unit — NoteService | tests/unit/test_note_service_create.py, tests/unit/test_note_service_delete.py | ✅ |
| Unit — Repository/Storage | tests/integration/test_create_note_api.py, tests/integration/test_update_note_api.py, tests/integration/test_concurrency_routes.py | ✅ |
| Unit — Security Layer | tests/unit/test_security_encryption.py, tests/unit/test_unlock_session_manager.py, tests/unit/test_pin_settings_manager.py, tests/unit/test_private_note_service.py | ✅ |
| Integration — API/UI flows | tests/integration/test_*_api.py, tests/integration/test_*_ui.py, tests/integration/test_ui_wiring.py | ✅ |
| Security Validation | tests/unit/test_audit_logging.py, tests/unit/test_security_encryption.py, tests/integration/test_private_unlock_ui.py, tests/integration/test_trash_ui.py | ✅ |
| Performance | tests/performance/test_performance.py | ✅ |
| Web Multi-User | tests/integration/test_web_multi_user.py | Deferred [Post-MVP] |

No test may be skipped or marked `xfail` without an approved written justification.

---

## Gate 3 — Security Requirements Verified

Each item must be individually verified and checked off by the developer before release:

| Check | Requirement | Verification Method | Status |
|---|---|---|---|
| Persistence store contains no plaintext title/body/version_content | SRG-25 | `tests/unit/test_security_encryption.py` | ✅ |
| Audit log contains no plaintext private note content | SRG-07 | `tests/unit/test_audit_logging.py::test_audit_log_does_not_store_note_plaintext` | ✅ |
| Lockout state resets on app restart | SRG-23 | `tests/unit/test_unlock_session_manager.py::test_unlock_lockout_triggers_after_five_failures_and_does_not_carry_over` | ✅ |
| Wrong passphrase and internal error responses are identical | SRG-24 | `tests/unit/test_unlock_session_manager.py::test_unlock_internal_pin_error_returns_same_user_message` | ✅ |
| Retention-expiry purge removes stale soft-deleted notes | SRG-12 | `tests/integration/test_trash_ui.py::test_trash_notes_older_than_retention_are_purged` | ✅ |
| Raw passphrase absent from all persisted files | SRG-26 | TP-SV05: grep persisted artifacts (`data/config.json`, `data/audit-log.jsonl`, SQLite string probe) | ✅ |
| Encryption uses AES-256-GCM or ChaCha20-Poly1305 | SRG-01 | Code review: `src/app/security/crypto_service.py` uses `AESGCM` for at-rest note encryption | ✅ |
| PBKDF2-HMAC-SHA256 ≥ 260,000 iterations confirmed in code | SRG-26 | Code review + TP-S01: `PBKDF2HMAC(..., iterations=260_000, length=32)` in `crypto_service.py`; storage-token derivation in `pin_settings_manager.py` uses `pbkdf2_hmac(..., 260_000, dklen=32)` | ✅ |
| No content-transmitting feature ships without TLS confirmed | SRG-17 | Code review: no outbound network path exists in MVP codebase | ✅ |
| Session cookie security flags and CSRF enforcement active on write endpoints | WEB-05, WEB-06 | TP-W07 + endpoint security tests | Deferred [Post-MVP] |

---

## Gate 4 — Performance Benchmarks Met

Measured at the service boundary (NFR-08), with 5,000-note dataset:

| Metric | Target | Measured | Status |
|---|---|---|---|
| Read p95 latency | ≤ 120 ms | 35.00 ms | ✅ |
| Write p95 latency | ≤ 180 ms | 1.34 ms | ✅ |
| All operations p99 latency | ≤ 300 ms | 35.99 ms | ✅ |
| Write success returned only after storage commit | Verified | Immediate read-after-success verification on 60 updates (0 failures) | ✅ |

Fill in the **Measured** column with actual benchmark results before checking off.

---

## Gate 5 — Code Quality and Architecture

| Check | Status |
|---|---|
| No direct UI → repository/security imports exist; UI uses API/service boundary only (NFR-13, WEB-04) | ✅ |
| NoteRepository and private-note/runtime dependencies are accessed through interfaces or service/provider boundaries (NFR-14) | ✅ |
| Replacing SqlNoteRepository with a fake in tests requires no UI code changes (NFR-16) | ✅ |
| No unhandled exceptions reachable through any user input path (SRG-14) | ✅ |
| Error responses use stable machine-readable codes with user-safe UI/API mapping (SRG-14, SRG-16) | ✅ |
| All writes use transaction commit/rollback safety (SRG-15) | ✅ |
| Owner scoping enforced for all note reads/writes (WEB-02, WEB-06) | Deferred [Post-MVP] |

---

## Gate 6 — Definition of Done (Per Story)

Before any single story is counted as done, all of the following must be true:

- [x] All acceptance criteria in user_stories.md for that story pass
- [x] Unit test(s) covering the story's logic exist and pass
- [x] No new test failures introduced in any other suite
- [x] Code reviewed (self-review at minimum for solo project)
- [x] Relevant requirement IDs referenced in the commit message or PR description
- [x] traceability-matrix.md updated if story fully satisfies a previously partial/weak requirement

---

## Gate 7 — No Open P0 or P1 Defects

| Priority | Definition | Required State |
|---|---|---|
| P0 | Data loss, data corruption, security bypass, crash on any reachable path | Zero open |
| P1 | Core workflow blocked, incorrect persistence, failed acceptance criterion | Zero open |
| P2 | UI cosmetic, non-critical edge case | May remain open with documented deferral |

---

## Release Sign-Off Checklist

Before cutting a release, confirm all gates above are ✅, then sign off:

```
Release version: 1.1
Date: 2026-06-05
Gates 1–7 all passed: ☑ Yes
Open P0/P1 defects: None ☑
Performance results recorded in Gate 4: ☑ Yes
Security checks individually verified in Gate 3: ☑ Yes
Signed off by: Silvia Mora
```

---

