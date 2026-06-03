# Requirements Traceability Matrix

**Project**: AstraNotes  
**Last Updated**: 2026-06-03  
**Total Requirements**: 99 (REQ-01–REQ-30, NFR-01–NFR-18, SRG-01–SRG-28, SMR-01–SMR-12, WEB-01–WEB-11)  
**UML Source**: Lucid document `83846df4-c365-4466-83ae-ea4703514eca`, Page 2 (`C0fSJIjDhK~F`)

## Legend

| Status | Meaning |
|---|---|
| ✅ Fully Traced | Evidence in ≥2 diagram types; clearly represented |
| ⚠️ Partially Traced | Evidence in 1 diagram type only, or only implied |
| ❌ Weakly Traced | No direct diagram representation; relies on doc/test artifacts |

---

## Functional Requirements (REQ-01–REQ-30)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| REQ-01 | Create note with title and body | `Note`, `NoteService.create()` | UC: Create Note | FastAPI + HTMX create flow (`/api/notes`, `/ui/notes`) | ✅ Fully Traced | BL-01 implemented with integration tests for API and UI routes |
| REQ-02 | Title/body validation rules | `Note` (title, body fields), `NoteService` validators | UC: Create Note | — | ⚠️ Partially Traced | Implemented with Unicode letter support and explicit punctuation allowlist including `¿` and `¡`; validation branches are not yet diagrammed in UML |
| REQ-03 | Duplicate title auto-suffix | `NoteService`, `SqlNoteRepository.create_note_atomic()` | UC: Create Note | SQLite unique constraint + retry-on-conflict | ⚠️ Partially Traced | Implemented; explicit suffix branch is not yet shown in UML |
| REQ-04 | Unique ID + timestamp + persist | `Note` (id, created_at), `SqlNoteRepository` | UC: Create Note | Shared DB persistence artifact | ✅ Fully Traced | Implemented in BL-01 repository + route integration tests |
| REQ-05 | Edit title and/or body | `Note`, `NoteService.update()` | UC: Edit Note | — | ✅ Fully Traced | |
| REQ-06 | Edit title/body validation | `Note` | UC: Edit Note | — | ⚠️ Partially Traced | Implemented; edit validation branches are not yet diagrammed in UML |
| REQ-07 | Duplicate title on edit (self-exclude) | `NoteService` | UC: Edit Note | — | ⚠️ Partially Traced | Implemented in service logic; self-exclusion flow is not yet explicit in UML |
| REQ-08 | Edit persistence (keep id/created_at, update updated_at) | `Note` (updated_at), `SqlNoteRepository` | Activity: Save note changes | Shared DB persistence artifact | ✅ Fully Traced | |
| REQ-09 | Delete confirmation prompt (move to Trash) | — | UC: Delete Note | — | ⚠️ Partially Traced | Implemented UI copy and confirm flow for move-to-trash; UML activity wording update pending |
| REQ-10 | Atomic soft-delete with error fallback | `NoteRepository`, `ResultError` | UC: Delete Note | — | ✅ Fully Traced | |
| REQ-11 | List updates after delete; empty state | `NoteService` | UC: Delete Note, UC: List Notes | — | ⚠️ Partially Traced | Implemented behavior; empty-state handling is not yet modeled in UML |
| REQ-12 | List display: newest first, 40-char server-side truncation with hover tooltip; editor shows Modified timestamp; body preview uses first non-empty line with formatting-preserving render | `Note` (title, created_at, updated_at) | UC: List Notes | — | ⚠️ Partially Traced | Implemented. Truncation revised to 40 chars (BL-04 UI Alignment). Full title in storage; hover tooltip via CSS `data-full-title`; preview now renders first non-empty line with checklist/bullet/inline formatting. UML artifact update pending. |
| REQ-13 | Empty state message when no notes | — | UC: List Notes | — | ⚠️ Partially Traced | Pending UML detail: explicit empty-state message flow |
| REQ-14 | List auto-refresh after CRUD | `NoteService`, `notes_ui.py` create/search routes | UC: List Notes | HTMX partial refresh + create-from-trash redirect to active results | ⚠️ Partially Traced | Implemented behavior including create-from-trash return to active view; explicit refresh trigger flow still pending in UML |
| REQ-15 | Search by title/body, case-insensitive | `NoteService.search()`, `SqlNoteRepository.search()`, `/api/notes/search`, `/ui/notes/search` | UC: Search Notes | API + HTMX partial route (`#notes-results`) | ✅ Fully Traced | Implemented with integration tests for API and UI live filtering |
| REQ-16 | Search edge cases: empty/whitespace/no results | `NoteService.search()` normalization, UI search context builder | UC: Search Notes | HTMX partial messaging for empty/no-match states | ⚠️ Partially Traced | Implemented with tests; UML activity branches for search edge states are still pending |
| REQ-17 | Bullet and checkbox lists in body | `Note` (body), `editor_panel.html` checklist controls | UC: Edit Note | HTMX editor flow (`/ui/notes/{id}/editor`) | ⚠️ Partially Traced | Implemented in BL-06 with integration tests; UML list-edit branch detail still pending |
| REQ-18 | List persistence and render after reopen | `SqlNoteRepository`, `NoteService.update()` | UC: Edit Note | Shared DB persistence artifact | ⚠️ Partially Traced | Persistence and reopen consistency validated in BL-06 tests; UML render-state detail still pending |
| REQ-19 | Checkbox toggle + immediate persist | `NoteService.toggle_checklist_item()`, `/ui/notes/{id}/checklist-toggle` | UC: Edit Note | HTMX toggle route + persisted SQLite update path | ⚠️ Partially Traced | Immediate persist implemented and tested in BL-06; UML toggle branch remains to be added |
| REQ-20 | Bold/italic/underline formatting | `create_panel.html`, `editor_panel.html`, `applyBodyFormat()` JS | UC: Edit Note | HTMX create/editor body toolbar actions | ⚠️ Partially Traced | Implemented in BL-07 with integration evidence; UML formatting-action branch still pending |
| REQ-21 | Formatting safety (no title modification, no data loss) | `applyBodyFormat()` body-only scope, `NoteService.update()` | UC: Edit Note | API/update integration tests for combined markers | ⚠️ Partially Traced | Implemented and tested for body-only formatting and marker preservation; UML safety constraints still pending |
| REQ-22 | Formatting storage rules (Markdown markers) | `Note` (body storage), update routes | — | Shared DB persistence artifact | ⚠️ Partially Traced | Bold/italic stored as Markdown markers and underline as `<u>...</u>`; UML/storage-rule annotation still pending |
| REQ-23 | Max 10,000 notes | `NoteService`, `SqlNoteRepository.create_note_atomic()` | UC: Create Note | SQLite transaction boundary | ⚠️ Partially Traced | Implemented enforcement; pending verification artifact for load/concurrency target |
| REQ-24 | Limit-reached blocking behavior + message | `NoteService`, `ResultError` | UC: Create Note | API/HTMX error mapping layer | ⚠️ Partially Traced | Implemented error path; pending UX copy standardization artifact |
| REQ-25 | Private toggle per note | `Note` (is_private), `SecureNote` | UC: Mark Private | — | ✅ Fully Traced | |
| REQ-26 | Private status persisted + visually indicated | `Note` (is_private), `SqlNoteRepository` | UC: Mark Private | Shared DB persistence artifact | ✅ Fully Traced | |
| REQ-27 | Private notes hide body preview | `SecureNote` | UC: Mark Private, UC: Search Notes | — | ✅ Fully Traced | |
| REQ-28 | English/Spanish interface toggle for UI text only | UI localization dictionary module (planned), template text keys | UC: Switch interface language | Web UI node | ⚠️ Partially Traced | MVP scope approved in pivot; implementation and tests pending |
| REQ-29 | Nested bullet/checklist lists up to 3 levels [Post-MVP] | Editor list model (planned) | UC: Edit Note (nested list branch) | — | ❌ Weakly Traced | Deferred to Post-MVP under pivot |
| REQ-30 | Image paste in note body [Post-MVP] | Media/content sanitizer module (planned) | UC: Edit Note (paste image flow) | Storage/media artifact | ❌ Weakly Traced | Deferred to Post-MVP under pivot |

---

## Non-Functional Requirements (NFR-01–NFR-18)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| NFR-01 | 100 concurrent user sessions | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| NFR-02 | Active session definition and workload mix | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| NFR-03 | Concurrency latency targets (p95/p99) | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| NFR-04 | Optimistic concurrency / version field | `Note` (version), `ResultError` (STALE_VERSION) | Activity: conflict/save error branch | — | ✅ Fully Traced | |
| NFR-05 | Overload throttle; ≤1% failure rate | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| NFR-06 | Web mode: up to 5,000 notes per account | `SqlNoteRepository`, `tests/performance/test_performance.py` (5,000-note seed) | BL-10 performance verification workflow | Shared DB node | ✅ Fully Traced | Verified in BL-10 with dataset size 5,000 |
| NFR-07 | API latency targets (p95/p99) | `tests/performance/test_performance.py` latency assertions | BL-10 benchmark run (read/search + update operations) | API runtime node | ✅ Fully Traced | Measured results: read p95 35.00 ms, write p95 1.34 ms, all-ops p99 35.99 ms |
| NFR-08 | API measurement boundary | `tests/performance/test_performance.py` API-route timing (`/api/notes/search`, `/api/notes/{id}`) | BL-10 service-boundary measurement procedure | API runtime node | ✅ Fully Traced | Browser rendering excluded; request/response boundary timing captured |
| NFR-09 | API write durability before success | `tests/performance/test_performance.py` immediate read-after-success verification | BL-10 durability check on update operations | Shared DB node | ✅ Fully Traced | Immediate read-after-success validation on 60 updates with zero failures |
| NFR-10 | Browser keyboard-only workflows | — | UC: (all core use cases) | Web UI node | ⚠️ Partially Traced | Pending evidence: keyboard-only interaction model and accessibility checks |
| NFR-11 | Mobile touch-only workflows [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| NFR-12 | Tab/touch reachability + focus indicator | — | — | — | ❌ Weakly Traced | Pending artifact: accessibility verification for focus and reachability |
| NFR-13 | UI/storage/security dependency separation | `NoteRepository` (interface), `NoteService`, `SqlNoteRepository` | — | AstraNotes Application | ✅ Fully Traced | |
| NFR-14 | Interface-based testability (test doubles) | `NoteRepository` (interface), `KeyDerivationService` | — | — | ✅ Fully Traced | |
| NFR-15 | Automated tests for UI/security/storage | pytest integration/unit suites (`tests/unit`, `tests/integration`) | Route-layer and service-layer test scenarios | CI test workflow artifact | ⚠️ Partially Traced | Implemented test baseline; pending security-slice test completion |
| NFR-16 | Storage backend replaceability | `NoteRepository` (interface), `SqlNoteRepository` | — | — | ✅ Fully Traced | |
| NFR-17 | Mobile touch target ≥44×44px [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| NFR-18 | Desktop shortcut equivalence on mobile [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |

---

## Security, Reliability & Governance Requirements (SRG-01–SRG-28)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| SRG-01 | All notes encrypted at rest (AES-256-GCM / ChaCha20-Poly1305) | `SecureNote`, `KeyDerivationService` | — | Crypto Runtime library node | ✅ Fully Traced | |
| SRG-02 | Private note encryption scope | `SecureNote`, `KeyDerivationService` | UC: Mark Private | Crypto Runtime library node | ✅ Fully Traced | |
| SRG-03 | Per-note key isolation [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-04 | TLS 1.2+ for data in transit | — | — | Deployment constraint note (TLS requirement) | ⚠️ Partially Traced | Constraint is documented; production TLS verification is pending |
| SRG-05 | Audit log: all CRUD operations | `AuditEntry`, `NoteService` | UC: (all CRUD use cases) | /data/audit-log.jsonl artifact | ✅ Fully Traced | |
| SRG-06 | Tamper-evident audit hash chain [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-07 | Audit privacy: no plaintext private content | `AuditEntry` | — | /data/audit-log.jsonl artifact | ✅ Fully Traced | |
| SRG-08 | Immutable version records | `VersionHistory`, `NoteVersion` | — | — | ✅ Fully Traced | |
| SRG-09 | Version SHA-256 hash validation [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-10 | Soft delete: 15-day retention | `Note` (is_deleted, deleted_at) | UC: Delete Note | Shared DB persistence artifact | ✅ Fully Traced | |
| SRG-11 | Soft-deleted notes excluded from default list/search and managed in Trash view | `NoteService`, `NoteRepository`, `notes_ui.py`, `note_preview.py` | UC: Delete Note, UC: List Notes, UC: Restore Note, UC: Trash Review | UI trash routes (`/?view=trash`, `/ui/notes/{id}/trash-viewer`, `/ui/notes/{id}/trash-unlock`, `/ui/notes/{id}/restore`, `/ui/notes/{id}/purge`) | ✅ Fully Traced | Read-only trash viewer, private-note unlock in trash, and restore/purge are covered by `tests/integration/test_trash_ui.py` |
| SRG-12 | Retention expiry purge (MVP) | `NoteService._purge_expired_deleted_notes()`, `SqlNoteRepository.purge_soft_deleted_older_than()` | Activity: list/search triggers purge path | Shared DB persistence artifact | ✅ Fully Traced | Implemented with 15-day automatic purge and covered by `test_trash_ui.py` |
| SRG-13 | Restore: preserve ID, history, audit entry | `NoteService`, `VersionHistory`, `AuditEntry` | — | — | ✅ Fully Traced | |
| SRG-14 | Structured error handling (no crashes) | `ResultError`, route error mapping module | Activity: save error branch | API and UI route parity tests | ✅ Fully Traced | Implemented shared error mapping with route-level tests |
| SRG-15 | Atomic commit/rollback on failure | `NoteRepository` (persist contract), `SqlNoteRepository.create_note_atomic()` | Activity: save error branch | SQLite transaction and integrity-error retry path | ✅ Fully Traced | Concurrency tests validate conflict-safe create behavior |
| SRG-16 | Consistent error codes on repeated invalid requests | `ResultError` | — | — | ⚠️ Partially Traced | Behavior is implemented in shared error contracts; explicit flow evidence is pending |
| SRG-17 | TLS release gate (no content transmission without SRG-04) | — | — | Deployment constraint note | ⚠️ Partially Traced | Process gate is documented; release-control evidence is pending |
| SRG-18 | PIN unlock required for private notes | `UnlockSessionManager`, `KeyDerivationService` | Activity: Prompt PIN → validate | — | ✅ Fully Traced | |
| SRG-19 | Private content hidden until auth succeeds | `SecureNote`, `UnlockSessionManager` | Activity: PIN valid? decision | — | ✅ Fully Traced | |
| SRG-20 | Unlock required once per session | `UnlockSessionManager` | Activity: PIN flow | — | ✅ Fully Traced | |
| SRG-21 | 15-min inactivity → unlock expiry | `UnlockSessionManager` | Activity: Session inactive >15 min? branch | — | ✅ Fully Traced | |
| SRG-22 | Rate limiting after 5 failed unlock attempts | `UnlockSessionManager` | Activity: Failed attempts ≥5? decision | — | ✅ Fully Traced | |
| SRG-23 | Lockout + exponential backoff; resets on restart | `UnlockSessionManager` | Activity: lockout state node | In-memory session state | ✅ Fully Traced | |
| SRG-24 | Anti-enumeration: identical error for wrong PIN and internal error | `UnlockSessionManager` | Activity: constraint note (indistinguishable errors) | — | ✅ Fully Traced | |
| SRG-25 | Plaintext metadata allowlist | `Note` (field list), `SqlNoteRepository` | — | Shared DB persistence artifact | ✅ Fully Traced | |
| SRG-26 | PBKDF2-HMAC-SHA256 key derivation (≥260k iterations) | `KeyDerivationService` | — | Key Derivation library node | ✅ Fully Traced | |
| SRG-27 | App-wide 4-digit PIN bootstrap (default `1234`) | `PinSettingsManager`, `UnlockSessionManager`, `CryptoService.set_private_pin()` | Activity: unlock prompt validates 4-digit PIN | UI settings + config persistence artifact (`/ui/security/pin`) | ✅ Fully Traced | Implemented with persistent app-wide PIN default and verification flow. Test evidence: TP-U32, TP-U33, TP-I08 (see `planning/test-plan.md`). |
| SRG-28 | In-app PIN change + atomic private-note rotation + keypad UX | `PinSettingsManager`, `SqlNoteRepository.rotate_private_pin()`, `notes_ui.py`, `pin_settings_panel.html`, `pin_input_component.html` | Activity: verify current PIN → reveal new/confirm inputs → rotate private note ciphertext → completion state; unlock via keypad auto-submit | HTMX verify/update routes (`/ui/security/pin/verify`, `/ui/security/pin`) + unlock partials | ✅ Fully Traced | Implemented with rollback-safe rotation, staged verify/update flow, and completion-state rendering. Test evidence: TP-U33, TP-U34, TP-I08, TP-I09, TP-I14 (see `planning/test-plan.md`). |

---

## Web and Multi-User Requirements (WEB-01–WEB-11)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| WEB-01 | Authenticated account required for note operations | `AuthService`, `SessionRepository` (planned) | UC: Login, UC: Access Notes | Shared deployment node | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-02 | Per-user data isolation (owner-scoped reads/writes) | `SqlNoteRepository` owner scoping | UC: List Notes, UC: Edit Note | Shared DB node | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-03 | JSON APIs for create/edit/delete/list/search/restore | FastAPI route layer (BL-01 create implemented) | Activity: API request/response flows | API runtime node | ⚠️ Partially Traced | BL-01 create API is implemented and tested; remaining endpoints are pending |
| WEB-04 | Web client consumes public APIs only | UI → service boundary with API parity contract | UC: all note workflows via API | — | ⚠️ Partially Traced | BL-01 parity is tested; full UI-through-API boundary enforcement is pending |
| WEB-05 | Session expires after inactivity | `SessionRepository`, inactivity timeout policy | Activity: session timeout and re-auth path | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-06 | Server-side authorization check on every API | `AuthService`, route-level dependency checks | Activity: authorize before mutate | — | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-07 | Transactional multi-user storage integrity | `SqlNoteRepository`, DB transaction boundary | Activity: commit/rollback | Shared DB node | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-08 | Shared persistent demo environment | Deployment config + persistence volume | UC: reviewer access | Shared deployment endpoint | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-09 | Persistent User model with required fields | `User` table: user_id, email, password_hash, created_at, is_active | UC: Signup, UC: Login | Database schema artifact | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-10 | Database-backed session store with timeouts | `Session` table: session_id, user_id, created_at, last_activity_at, expires_at, is_revoked, ip_address, user_agent; 30-min idle timeout, 7-day absolute timeout | Activity: login → session create; logout → session revoke; timeout check | Database schema artifact | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |
| WEB-11 | Separate login password and note passphrase | `User.password_hash` (bcrypt/Argon2); `Note.passphrase_salt` + PBKDF2 (4-digit PIN) | Activity: login hashes password; unlock derives key from passphrase | Crypto policy artifact | ❌ Weakly Traced | Deferred to Post-MVP under single-user pivot |

---

## Summary

| Status | Count |
|---|---|
| ✅ Fully Traced | 28 |
| ⚠️ Partially Traced | 43 |
| ❌ Weakly Traced | 16 |
| ➕ SMR — Pending Diagrams | 12 |
| **Total** | **99** |

## BL-01 Residual Tracker (Non-Blocking)

- BL-01 is implementation-complete and may proceed to downstream slices.
- Remaining BL-01 follow-through items are tracked residuals (not blockers for BL-02):
	- UML artifact update for explicit validation and duplicate-suffix branches (REQ-02, REQ-03).
	- Verification artifact for note-capacity/load boundary evidence (REQ-23, NFR-01/03 alignment).
	- Sprint 1 foundation items continue under BL-21 and BL-22 plans.

## BL-02 Residual Tracker (Non-Blocking)

- BL-02 is implementation-complete and release-marked complete.
- Remaining BL-02 follow-through items are tracked residuals (not blockers for BL-03):
	- UML artifact update for edit validation branches (REQ-06).
	- UML artifact update for self-exclusion duplicate-title branch (REQ-07).
	- Cross-artifact reconciliation pass to keep requirement/story/traceability references fully aligned for BL-02.

## BL-03 Residual Tracker (Non-Blocking)

- BL-03 is implementation-complete. All delete infrastructure was already in place: `SqlNoteRepository.soft_delete()`, `NoteService.delete()` / `bulk_delete()`, `DELETE /api/notes/{id}`, `DELETE /ui/notes/{id}`, and delete button in `editor_panel.html`.
- BL-03.1 bulk delete ✅, individual delete ✅.
- SRG-13 restore intentionally deferred to BL-13 Security Stack (requires `VersionHistory`, `AuditEntry`, and encrypt-at-rest layer to be wired first).

## BL-04 Residual Tracker (Non-Blocking)

- BL-04 is implementation-complete and release-marked ✅.
- REQ-12 title truncation revised from 60-char to 40-char server-side cap (37 chars + "…") to fit the two-panel workbench layout; full title is preserved in storage and exposed via hover tooltip.
- BL-04 UI Alignment story added to `user_stories.md` covering: two-panel workbench, draggable resizer with `localStorage` persistence, create/editor right-panel slot, idle placeholder, and HTMX `htmx.process()` dynamic initialization requirement.
- Remaining follow-through items (not blockers for BL-06):
	- UML artifact update for two-panel layout and panel-resizer interaction flow.
	- Cross-artifact reconciliation pass to confirm REQ-12 traceability references reflect the 40-char revision.

## BL-05 Residual Tracker (Non-Blocking)

- BL-05 is implementation-complete and release-marked ✅.
- Implemented artifacts include: `NoteService.search()` normalization, wildcard-literal safe repository matching, JSON API route (`/api/notes/search`), HTMX UI route (`/ui/notes/search`), and hero-toolbar search placement beside Create Note.
- Edge cases covered and verified: whitespace query -> full list, no matches -> "No notes match your search.", no notes -> REQ-13 empty-state message.
- Remaining follow-through items (not blockers for BL-06):
	- UML activity update for search edge-case branches and HTMX partial update path.
	- Optional future enhancement: preserve current selected note highlight across filtered result swaps.

---

## Serviceability and Manageability Requirements (SMR-01–SMR-12)

> These requirements were added to support the 3-tier GUI architecture. UML diagram coverage will be added in the UML gap-resolution session.

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| SMR-01 | Rotating diagnostic log file with tier, timestamp, severity, correlation ID | `AppLogger` (to be added to class diagram) | — | AstraNotes Application node | ⚠️ Partially Traced | Runtime coverage exists; logger class representation in UML is pending |
| SMR-02 | Log level configurable in config.json; live reload | `AppLogger`, `ConfigService` | — | /data/config.json artifact | ⚠️ Partially Traced | Configuration artifact exists; ConfigService class representation in UML is pending |
| SMR-03 | Log entries never contain note plaintext | `AppLogger` | — | — | ⚠️ Partially Traced | Constraint is defined; logger privacy note in UML is pending |
| SMR-04 | ResultError includes source_tier; raw exceptions never reach UI | `ResultError` (source_tier field) | — | — | ⚠️ Partially Traced | ResultError is represented; source_tier field detail in UML is pending |
| SMR-05 | UI renders user-safe error state; no codes/traces shown to user | UI tier (to be modeled) | Activity: error branch rendering | — | ❌ Weakly Traced | Pending artifact: UI-tier model for safe error rendering |
| SMR-06 | Startup: verify/create data directory; refuse launch if not writable | `AppStartup` (to be added) | — | Local File System node | ⚠️ Partially Traced | Deployment evidence exists; startup class representation in UML is pending |
| SMR-07 | Startup: corrupt/unreadable persistence store preserved + fresh store initialized + user warning | `SqlNoteRepository` startup path | — | Shared DB artifact | ⚠️ Partially Traced | Startup recovery behavior is defined; UML flow evidence is pending |
| SMR-08 | Schema migration version guard; refuse write if stored version > app version | `SqlNoteRepository`, migration metadata | — | DB migration metadata artifact | ⚠️ Partially Traced | Migration artifact exists; version-guard detail in UML is pending |
| SMR-09 | config.json: unknown keys ignored, missing keys use defaults, invalid values → WARNING | `ConfigService` (to be added) | — | /data/config.json artifact | ⚠️ Partially Traced | Configuration artifact exists; ConfigService model in UML is pending |
| SMR-10 | Four supported config keys: log_level, data_dir, inactivity_timeout_minutes, max_notes | `ConfigService` | — | /data/config.json artifact | ⚠️ Partially Traced | Defined keys are documented; UML/config flow evidence is pending |
| SMR-11 | Semantic version embedded in app, shown in About UI, logged on startup | `AppVersion` / version constant | — | AstraNotes Application node | ⚠️ Partially Traced | Deployment evidence exists; version model detail in UML is pending |
| SMR-12 | Graceful shutdown: in-progress writes complete before process exits | `SqlNoteRepository` (transaction guard) | — | AstraNotes Application node | ⚠️ Partially Traced | Transaction intent is represented; shutdown-flow activity evidence is pending |

### Weakly Traced — Root Cause Groups

| Group | Requirements | Recommended Artifact |
|---|---|---|
| Concurrency / performance targets | NFR-01, NFR-02, NFR-03, NFR-05, NFR-07, NFR-08 | NFR Verification Plan (`nfr-verification-plan.md`) |
| Mobile / accessibility (out of MVP scope) | NFR-11, NFR-12, NFR-17, NFR-18 | Explicitly mark Post-MVP in requirements; note in this matrix |
| Automated test coverage | NFR-15 | Test plan / test strategy document |
| Post-MVP security hardening | SRG-03, SRG-06, SRG-09, SRG-12 | Already tagged `[Post-MVP]`; no action needed for MVP |
