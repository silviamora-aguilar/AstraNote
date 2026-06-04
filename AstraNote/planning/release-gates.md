# Release Gates — AstraNotes MVP

**Version**: 1.4  
**Date**: 2026-06-03

A release gate is a mandatory pass/fail check that must be satisfied before any code is shipped. Every item below must be ✅ before an MVP release is cut. No exceptions.

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
| BL-12: Architecture boundaries | NFR-13–16 | ☐ |
| BL-13: Security stack | SRG-01, 02, 04, 05, 07, 08, 10, 11, 12, 13–26 | ✅ |
| BL-23: Interface localization toggle | REQ-28 | ✅ |
| BL-21: Serviceability/manageability | SMR-01–12 | ☐ |
| BL-22: Web multi-user foundation | WEB-01–11 | Deferred [Post-MVP] |
| BL-24: Nested list depth (3 levels) | REQ-29 | Deferred [Post-MVP] |
| BL-25: Image paste in note body | REQ-30 | Deferred [Post-MVP] |
| BL-26: Concurrency/load verification | NFR-01–05 | Deferred [Post-MVP] |

---

## Gate 2 — All Tests Pass

All test suites must pass with zero failures:

| Suite | File | Status |
|---|---|---|
| Unit — NoteService | tests/unit/test_note_service_create.py, tests/unit/test_note_service_delete.py | ☐ |
| Unit — Repository/Storage | tests/integration/test_create_note_api.py, tests/integration/test_update_note_api.py, tests/integration/test_concurrency_routes.py | ☐ |
| Unit — Security Layer | tests/unit (dedicated security unit suite pending) | ☐ |
| Integration — API/UI flows | tests/integration/test_*_api.py, tests/integration/test_*_ui.py, tests/integration/test_ui_wiring.py | ☐ |
| Security Validation | tests (SRG validation currently distributed; dedicated tests/security/* suite pending) | ☐ |
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
| No direct UI → repository/security imports exist; UI uses API/service boundary only (NFR-13, WEB-04) | ☐ |
| NoteRepository and KeyDerivationService accessed only through interfaces (NFR-14) | ☐ |
| Replacing SqlNoteRepository with a fake in tests requires no UI code changes (NFR-16) | ☐ |
| No unhandled exceptions reachable through any user input path (SRG-14) | ☐ |
| All error responses use ResultError with machine-readable codes (SRG-14) | ☐ |
| All writes use transaction commit/rollback safety (SRG-15) | ☐ |
| Owner scoping enforced for all note reads/writes (WEB-02, WEB-06) | Deferred [Post-MVP] |

---

## Gate 6 — Definition of Done (Per Story)

Before any single story is counted as done, all of the following must be true:

- [ ] All acceptance criteria in user_stories.md for that story pass
- [ ] Unit test(s) covering the story's logic exist and pass
- [ ] No new test failures introduced in any other suite
- [ ] Code reviewed (self-review at minimum for solo project)
- [ ] Relevant requirement IDs referenced in the commit message or PR description
- [ ] traceability-matrix.md updated if story fully satisfies a previously partial/weak requirement

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
Release version: _______________
Date: _______________
Gates 1–7 all passed: ☐ Yes
Open P0/P1 defects: None ☐
Performance results recorded in Gate 4: ☐ Yes
Security checks individually verified in Gate 3: ☐ Yes
Signed off by: _______________
```

---

## Current Delivery Checkpoint (2026-06-01)

### Completed Backlog Slices

- ✅ BL-01 through BL-09 are implemented and reflected in requirement status markers.
- ✅ BL-06/BL-07 UI stabilization completed for list editing behavior (multi-line bullet/checklist formatting, checklist Enter/caret positioning, checklist toggle without forced panel refresh).
- ✅ List preview rendering now uses the first non-empty line and preserves visual formatting for checklist/bullet/inline text.

### Requirement and Implementation Alignment

- ✅ REQ-01 through REQ-27 are implemented in current codebase scope.
- ✅ Recent integration runs passed for BL-02/04/05/06/07/09 behaviors (including preview regressions).

### Readiness for Next BL

- ✅ BL-10 Performance verification completed via `tests/performance/test_performance.py` on dataset size 5,000.
- ✅ Measured evidence captured for NFR-06 through NFR-09 latency/durability targets in Gate 4.

## MVP Scope Adjustment Checkpoint (2026-06-03)

- ✅ BL-11 deferred to Post-MVP for this demo cycle.
- ✅ NFR-10 and NFR-12 moved to Post-MVP scope in `planning/requirements.md`.
- ✅ Current active open implementation gates for MVP are BL-12, BL-21, and BL-23.

## Demo Hardening Checkpoint (2026-06-03)

- ✅ Focused demo regression pack passed (20 tests): private unlock UI, trash flows, private PIN settings UI, create-note API, deterministic error mapping, and PIN settings persistence checks.
- ✅ SRG-16 API evidence added: repeated invalid create requests return stable `X-Error-Code` and no storage mutation (`tests/integration/test_create_note_api.py`).
- ✅ SRG-26 persistence hardening completed: plaintext legacy PIN is migrated to encrypted token on `PinSettingsManager` initialization.
- ✅ Demo scope freeze set: only blocker/security fixes until demo; no net-new feature additions.

## BL-10 Closure Checkpoint (2026-06-02)

- ✅ Branch `bl10-performance` pushed with BL-10 implementation and evidence updates.
- ✅ Full regression suite passed: 93 passed, 0 failed.
- ✅ Requirements and traceability documentation aligned for NFR-06 through NFR-09 completion.
- ✅ Ready to proceed to **BL-11** planning/execution.

## Pivot Baseline Checkpoint (2026-06-02)

- ✅ Scope pivot approved: MVP delivery mode is single-user web on localhost.
- ✅ Completed BL-01 through BL-10 evidence remains accepted and unchanged.
- ✅ Multi-user/auth/session backlog (BL-22, WEB-01..11) is deferred to Post-MVP.
- ✅ MVP adds localization scope (BL-23 / REQ-28).
- ✅ Nested list depth expansion and image paste are deferred to Post-MVP (BL-24, BL-25).
- ✅ SRG-04/SRG-17 clarified: non-local transport must use TLS before release.

## BL-13.1 Trash/PIN UX Checkpoint (2026-06-03)

- ✅ Trash review and recovery UX enhancements merged (read-only trash viewer, private-note unlock in trash, bulk restore/purge flows).
- ✅ Create-from-trash behavior aligned: create action returns user to active results and surfaces the created note.
- ✅ Private PIN settings flow merged with staged current-PIN verification and completion-state success rendering.
- ✅ Planning artifacts updated for this slice: requirements, user stories, traceability matrix, and test plan.
- ℹ️ BL-11 remains open and unchanged (NFR-10, NFR-12 input/accessibility parity).

## BL-13 Security Implementation Checkpoint (2026-06-03)

- ✅ Added append-only audit logger and service integration for create, update, delete, and restore operations.
- ✅ Added unit coverage for SRG-05/SRG-07 audit fields and plaintext non-disclosure.
- ✅ Verified focused BL-13 suite pass: `test_audit_logging`, `test_security_encryption`, `test_unlock_session_manager`, `test_private_unlock_ui`, `test_trash_ui`.
- ✅ Added deterministic error-code mapping for repeated invalid requests (SRG-16) and verified via unit test.
- ✅ Confirmed there is no outbound content-transmitting network path in the MVP codebase (SRG-17 code review evidence).
- ✅ BL-13 gate checks in Gate 3 are complete for current MVP scope.

## BL-23 Localization Checkpoint (2026-06-03)

- ✅ Added English/Spanish UI localization dictionary and route-level language resolution.
- ✅ Added language toggle in the main UI with `lang` propagation across HTMX/fetch routes.
- ✅ Localized UI labels/headings/system helper text across primary notes, trash, unlock, editor, and create flows.
- ✅ Added integration coverage in `tests/integration/test_localization_ui.py` for English default, Spanish toggle, cookie persistence, and Spanish search empty-state messaging.
