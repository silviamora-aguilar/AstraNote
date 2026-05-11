# Sprint 1 Plan (AstraNotes)

## Sprint Goal
Deliver a working web multi-user note-taking core: authenticated create, edit, delete, list, and search with owner-scoped persistence, validation, soft-delete, audit logging, and architecture boundaries enforced. Advanced privacy/security hardening remains in Sprint 2.

## Duration
2 weeks

## Scope — Sprint 1 Backlog Items

### BL-01 · Create Note (REQ-01, REQ-02, REQ-03, REQ-04)
**Tasks:**
- S1-01: Define `Note` data class with fields: `note_id`, `title`, `body`, `is_private`, `is_deleted`, `created_at`, `updated_at`, `deleted_at`
- S1-02: Implement `NoteRepository` abstract interface (`save`, `get`, `list`, `search`, `soft_delete`, `restore`)
- S1-03: Implement `SqlNoteRepository.save()` with transactional commit/rollback and SRG-25 plaintext field enforcement
- S1-04: Implement `NoteService.create()` with title validation (REQ-02), duplicate-title suffix (REQ-03), capacity check (REQ-23/24), unique ID + timestamps (REQ-04)
- S1-05: Wire web create-note form (Jinja2 + HTMX) to `NoteService.create()` via protected endpoint

**Exit criteria:** Creates a note, persists to SQLite store, title constraints enforced, duplicate auto-suffix works, rejects at 10,000-note limit.

---

### BL-02 · Edit Note (REQ-05, REQ-06, REQ-07, REQ-08)
**Tasks:**
- S1-06: Implement `NoteService.update()` with same title validation as REQ-02, self-exclusion duplicate check (REQ-07), and updated_at refresh (REQ-08)
- S1-07: Implement `SqlNoteRepository` update path with transaction boundary
- S1-08: Wire web edit-note form to `NoteService.update()` via protected endpoint

**Exit criteria:** Edits persist, original `note_id` and `created_at` preserved, `updated_at` updated, duplicate check excludes current note.

---

### BL-03 · Delete Note (REQ-09, REQ-10, REQ-11, SRG-10, SRG-11, SRG-13)
**Tasks:**
- S1-09: Implement deletion confirmation step in UI (REQ-09) showing note title and "cannot be undone" message
- S1-10: Implement `NoteService.delete()` as soft delete — set `is_deleted=True`, record `deleted_at` (SRG-10)
- S1-11: Implement `SqlNoteRepository.soft_delete()` with transaction safety
- S1-12: Implement `NoteService.restore()` — undelete within 30-day window, preserve original ID and version history, create audit entry (SRG-13)
- S1-13: Ensure soft-deleted notes excluded from `list()` and `search()` results (SRG-11)

**Exit criteria:** Delete soft-deletes note, removed from list/search, restorable within 30 days; failed delete leaves note intact (REQ-10).

---

### BL-04 · List Notes (REQ-12, REQ-13, REQ-14)
**Tasks:**
- S1-14: Implement `NoteService.list()` returning notes sorted newest-first, excluding soft-deleted
- S1-15: Implement UI list view: 60-char title truncation with ellipsis, date formatted as "Month DD, YYYY" (REQ-12)
- S1-16: Implement empty-state message: "No notes yet. Create your first note." (REQ-13)
- S1-17: Ensure list refreshes after create, edit, delete (REQ-14)

**Exit criteria:** List shows notes newest-first, titles truncated, correct date format, refreshes on all mutations, shows empty state when empty.

---

### BL-05 · Search Notes (REQ-15, REQ-16)
**Tasks:**
- S1-18: Implement `NoteService.search()` — case-insensitive substring match on title and body, minimum 1 non-whitespace character
- S1-19: Implement search edge cases: whitespace-only → show full list; no results → "No notes match your search."; no notes + search → empty state message (REQ-16)
- S1-20: Wire UI search bar to `NoteService.search()`

**Exit criteria:** Search filters correctly, special characters treated as literals, each edge case shows correct feedback message.

---

### BL-12 · Architecture Boundaries and Testability (NFR-13, NFR-14, NFR-15, NFR-16)
**Tasks:**
- S1-21: Enforce that web UI module imports only service/API layer — no direct imports of repository or crypto classes
- S1-22: Define `KeyDerivationService` abstract interface (implementation in Sprint 2)
- S1-23: Write unit tests for `NoteService` using a fake/in-memory `NoteRepository` test double (NFR-14)
- S1-24: Write unit tests for `SqlNoteRepository` persistence behavior independently of UI or service logic (NFR-15)
- S1-25: Add a linter/import-boundary check (e.g., enforce via test or CI rule) to catch direct UI → storage coupling (NFR-13)

**Exit criteria:** Unit tests pass for service and storage layers independently; UI code has no direct storage/crypto imports; backend can be swapped without UI changes.

---

### Audit Logging Foundation (SRG-05, SRG-07) — required for BL-01 to BL-03
**Tasks:**
- S1-26: Implement `AuditEntry` data class and `append_audit_entry()` to write to `/data/audit-log.jsonl`
- S1-27: Integrate audit entry creation in `NoteService` for create, update, soft_delete, and restore operations
- S1-28: Verify audit entries contain no plaintext private note content (SRG-07)

---

### BL-21 · Serviceability and Manageability Foundation (SMR-01–SMR-12)
These tasks must be completed in Sprint 1 because logging, config, and startup integrity underpin all other tiers.

**Tasks:**
- S1-32: Implement `AppLogger` — rotating file logger (5 MB / 2 rotated files), structured entries with UTC timestamp, severity, tier (UI/Service/Storage/Security), correlation ID, and message (SMR-01)
- S1-33: Implement `ConfigService` — load `config.json` on startup; apply supported keys (SMR-09, SMR-10); ignore unknown keys; use documented defaults for missing keys; log WARNING for invalid values; expose `get(key)` API to all tiers
- S1-34: Wire `AppLogger` log level to `config.json` `log_level` key; implement live-reload check so log level is respected without restart (SMR-02)
- S1-35: Enforce log privacy guard — add assertion/test that `AppLogger` never accepts note title or body as a message argument; log diagnostic context limited to `note_id` + operation type (SMR-03)
- S1-36: Add `source_tier` field to `ResultError`; update Storage tier and Security tier error paths to set it before returning errors to NoteService (SMR-04)
- S1-37: Implement UI error handler — catch all `ResultError` at the UI layer, display user-safe message, log full detail at WARNING/ERROR level; ensure no machine-readable codes or stack traces reach the user-facing surface (SMR-05)
- S1-38: Implement `AppStartup` sequence: verify data directory exists and is writable → create if absent → refuse launch with clear error if not writable (SMR-06)
- S1-39: Add persistence-integrity check to `AppStartup` / repository init: if store is unreadable/corrupt, rename to `astranotes.db.corrupt.<UTC>`, initialize fresh store, surface user warning (SMR-07)
- S1-40: Add migration/version guard (Alembic revision compatibility) in repository startup path — refuse write if stored schema revision > app-supported revision (SMR-08)
- S1-41: Embed semantic version constant (e.g., `APP_VERSION = "1.0.0"`) in application; log it at INFO on startup; expose it in an About/Help UI surface (SMR-11)
- S1-42: Implement graceful shutdown handler — register OS signal handler (SIGTERM, process stop) that waits for any in-progress repository transaction to complete before exit (SMR-12)

---

### BL-22 · Web Multi-User Foundation (WEB-01–WEB-08)
**Tasks:**
- S1-43: Implement account authentication flow (sign-in/sign-out) with server-side session cookies (WEB-01)
- S1-44: Implement session inactivity timeout (default 15 minutes) with server-side enforcement (WEB-05)
- S1-45: Add CSRF protection to all state-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) (WEB-06)
- S1-46: Add owner scoping (`owner_user_id`) to all note repository queries and mutations (WEB-02)
- S1-47: Expose JSON API routes for create/edit/delete/list/search/restore with stable payload contracts (WEB-03)
- S1-48: Enforce UI-to-API boundary for Jinja2 + HTMX views (WEB-04)
- S1-49: Add transactional multi-user write integration test workload (WEB-07)
- S1-50: Add shared deployment smoke checklist and health endpoint validation (WEB-08)

**Exit criteria:** Authenticated sessions required for note operations, per-user isolation proven by tests, API endpoints operational, CSRF enabled for writes, and deployment smoke check documented.

**Exit criteria:** Diagnostic log written for all operations with required fields; config.json controls log level; corrupt persistence store handled on startup without crash; schema/migration version guard blocks stale writes; app version visible in UI and startup log; shutdown does not interrupt in-flight transaction completion.

---

### ResultError Structured Errors (SRG-14, SRG-15, SRG-16)
**Tasks:**
- S1-29: Implement `ResultError` with machine-readable codes: `NOT_FOUND`, `VALIDATION_ERROR`, `CAPACITY_EXCEEDED`, `STALE_VERSION`, `SAVE_ERROR`
- S1-30: Ensure all `NoteService` and repository operations return `ResultError` on failure rather than raising unhandled exceptions (SRG-14)
- S1-31: Ensure failed operations do not partially persist data — transaction rollback guarantees pre-op state preserved (SRG-15)

---

## Sprint 1 Dependency Order

```
S1-01 (Note model) → S1-02 (NoteRepository interface)
  → S1-03 (SqlNoteRepository.save)
    → S1-04 (NoteService.create)  → S1-05 (UI create)
    → S1-06 (NoteService.update)  → S1-08 (UI edit)
    → S1-10 (NoteService.delete)  → S1-09 (UI confirm) + S1-12 (restore)
  → S1-14 (NoteService.list)      → S1-15–S1-17 (UI list)
  → S1-18 (NoteService.search)    → S1-19–S1-20 (UI search)
S1-26 (AuditEntry) → S1-27 (integrate into NoteService)
S1-29 (ResultError) → all NoteService methods
S1-43 (auth/session) → S1-46 (owner scoping) → all protected note routes
S1-21–S1-25 (boundaries + tests) — run in parallel with above
```

## Sprint 1 Exit Criteria
- All tasks S1-01 through S1-31 complete
- All tasks S1-43 through S1-50 complete
- Unit tests pass for NoteService (with fake repo) and SqlNoteRepository (with temp DB)
- Integration test: full create → edit → list → search → soft-delete → restore round-trip passes
- Persistence layer contains no plaintext title or body fields
- Audit log written for all operations
- No unhandled exceptions on any invalid input scenario

---

# Sprint 2 Plan (AstraNotes)

## Sprint Goal
Deliver authoring features (lists, formatting, capacity) and the full private-note security stack (passphrase unlock, encryption at rest, lockout, session expiry).

## Duration
2 weeks

## Scope — Sprint 2 Backlog Items

### BL-06 · Lists in Notes (REQ-17, REQ-18, REQ-19)
**Tasks:**
- S2-01: Implement bullet list and checkbox list insertion and editing in note body
- S2-02: Persist list Markdown in SQLite store; verify render-after-reopen consistency (REQ-18)
- S2-03: Implement checkbox toggle with immediate persist (REQ-19)

---

### BL-07 · Text Formatting (REQ-20, REQ-21, REQ-22)
**Tasks:**
- S2-04: Implement bold/italic/underline on selected body text; disable for title (REQ-21)
- S2-05: Verify bold/italic stored as Markdown markers; underline stored in one consistent format (REQ-22)
- S2-06: Verify combined formats don't corrupt surrounding text (REQ-21)

---

### BL-08 · Note Capacity (REQ-23, REQ-24)
**Tasks:**
- S2-07: Verify capacity check already implemented in Sprint 1 (S1-04); validate exact message: "Note limit reached (10,000). Delete notes to create a new one."
- S2-08: Test duplicate-title suffix is also blocked at 10,000 notes (REQ-24)

---

### BL-09 · Note Privacy State and Preview Suppression (REQ-25, REQ-26, REQ-27)
**Tasks:**
- S2-09: Implement per-note private toggle; persist `is_private` in storage (REQ-25, REQ-26)
- S2-10: Show private indicator in list view (REQ-26)
- S2-11: Suppress body preview for private notes in list and search results (REQ-27)

---

### BL-13 · MVP Security Stack (SRG-01, SRG-02, SRG-04, SRG-18–SRG-26)
**Tasks:**
- S2-12: Implement `KeyDerivationService` — PBKDF2-HMAC-SHA256, ≥260,000 iterations, 16-byte random salt, 256-bit output key; raw passphrase never stored or logged (SRG-26)
- S2-13: Implement `SecureNote` encryption/decryption using AES-256-GCM; encrypt `title`, `body`, `version_content` before any write (SRG-01, SRG-02)
- S2-14: Validate SRG-25 plaintext allowlist: verify persisted records contain no plaintext `title`, `body`, or `version_content`
- S2-15: Implement `UnlockSessionManager` — session-scoped unlock (SRG-20), 15-min inactivity expiry (SRG-21)
- S2-16: Implement 5-consecutive-failure rate limiting and exponential-backoff lockout (min 5 min, doubling); persist lockout state + expiry to `security-state.json` across restarts (SRG-22, SRG-23)
- S2-17: Implement anti-enumeration: identical error message and response timing for wrong passphrase and internal error (SRG-24)
- S2-18: Gate content-transmitting features on SRG-04 TLS compliance (SRG-17) — add release gate check (see `release-gates.md`)
- S2-19: Write security unit tests: encryption round-trip, passphrase wrong → no plaintext exposed (SRG-19), lockout persistence, timeout expiry

---

### BL-10 · Performance Verification Harness (NFR-06, NFR-07, NFR-08, NFR-09)
**Tasks:**
- S2-20: Implement benchmark test measuring p95/p99 read and write latency at 100, 1,000, and 5,000 notes
- S2-21: Verify measurement boundary: service invocation → storage commit, excluding UI render (NFR-08)
- S2-22: Verify write-before-success: successful save confirmed durable before returning (NFR-09)

---

## Sprint 2 Exit Criteria
- All Sprint 2 tasks complete
- Encryption verified: no plaintext title/body in persistence store after any write
- Lockout and session expiry work across simulated app restarts
- Anti-enumeration: wrong-passphrase and internal-error responses are identical in content
- Performance benchmarks at 5,000 notes meet NFR-07 targets
- Full regression: all Sprint 1 tests continue to pass
