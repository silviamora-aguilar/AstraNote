# Release Gates — AstraNotes MVP

**Version**: 1.1  
**Date**: 2026-06-01

A release gate is a mandatory pass/fail check that must be satisfied before any code is shipped. Every item below must be ✅ before an MVP release is cut. No exceptions.

---

## Gate 1 — Functional Completeness

All MVP backlog items must be complete and verified:

| Item | Requirement Coverage | Status |
|---|---|---|
| BL-01: Create note | REQ-01–04 | ✅ |
| BL-02: Edit note | REQ-05–08 | ✅ |
| BL-03: Delete note | REQ-09–11 + SRG-10, 11, 13 | ✅ (SRG-13 restore deferred to BL-13 Security Stack) |
| BL-03.1: Bulk delete selected notes (extension) | REQ-09–11 (multi-select UX extension) | ✅ |
| BL-04: List notes | REQ-12–14 | ✅ |
| BL-05: Search | REQ-15–16 | ✅ |
| BL-06: Lists in notes | REQ-17–19 | ✅ |
| BL-07: Text formatting | REQ-20–22 | ✅ |
| BL-08: Note capacity | REQ-23–24 | ✅ |
| BL-09: Privacy state and preview suppression | REQ-25–27 | ✅ |
| BL-10: Performance verification | NFR-06–09 | ☐ |
| BL-12: Architecture boundaries | NFR-13–16 | ☐ |
| BL-13: Security stack | SRG-01, 02, 04, 05, 07, 08, 10, 11, 13–26 | ☐ |
| BL-21: Serviceability/manageability | SMR-01–12 | ☐ |
| BL-22: Web multi-user foundation | WEB-01–08 | ☐ |

---

## Gate 2 — All Tests Pass

All test suites must pass with zero failures:

| Suite | File | Status |
|---|---|---|
| Unit — NoteService | tests/unit/test_note_service.py | ☐ |
| Unit — SqlNoteRepository | tests/unit/test_sql_repository.py | ☐ |
| Unit — Security Layer | tests/unit/test_security.py | ☐ |
| Integration | tests/integration/test_flows.py | ☐ |
| Security Validation | tests/security/test_security_validation.py | ☐ |
| Performance | tests/performance/test_performance.py | ☐ |
| Web Multi-User | tests/integration/test_web_multi_user.py | ☐ |

No test may be skipped or marked `xfail` without an approved written justification.

---

## Gate 3 — Security Requirements Verified

Each item must be individually verified and checked off by the developer before release:

| Check | Requirement | Verification Method | Status |
|---|---|---|---|
| Persistence store contains no plaintext title/body/version_content | SRG-25 | TP-SV01: inspect raw persisted record post-write | ☐ |
| Audit log contains no plaintext private note content | SRG-07 | TP-SV02: parse audit-log.jsonl | ☐ |
| Lockout state persists across app restart | SRG-23 | TP-SV03: reinitialize from security-state.json | ☐ |
| Wrong passphrase and internal error responses are identical | SRG-24 | TP-S13, TP-SV04 | ☐ |
| Raw passphrase absent from all persisted files | SRG-26 | TP-SV05: grep data files | ☐ |
| Encryption uses AES-256-GCM or ChaCha20-Poly1305 | SRG-01 | Code review of SecureNote implementation | ☐ |
| PBKDF2-HMAC-SHA256 ≥ 260,000 iterations confirmed in code | SRG-26 | Code review + TP-S01 | ☐ |
| No content-transmitting feature ships without TLS confirmed | SRG-17 | Code review: confirm no network path exists in MVP; if one exists, TLS 1.2+ must be verified | ☐ |
| Session cookie security flags and CSRF enforcement active on write endpoints | WEB-05, WEB-06 | TP-W07 + endpoint security tests | ☐ |

---

## Gate 4 — Performance Benchmarks Met

Measured at the service boundary (NFR-08), with 5,000-note dataset:

| Metric | Target | Measured | Status |
|---|---|---|---|
| Read p95 latency | ≤ 120 ms | — | ☐ |
| Write p95 latency | ≤ 180 ms | — | ☐ |
| All operations p99 latency | ≤ 300 ms | — | ☐ |
| Write success returned only after storage commit | Verified | — | ☐ |

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
| Owner scoping enforced for all note reads/writes (WEB-02, WEB-06) | ☐ |

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

- ✅ Ready to begin **BL-10 Performance verification**.
- Remaining gate-critical work is measurement evidence for NFR-06 through NFR-09 latency/durability targets.
