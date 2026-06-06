# Requirements Traceability Matrix

**Project**: AstraNotes  
**Last Updated**: 2026-06-05
**Total Requirements**: 100 (REQ-01–REQ-30, NFR-01–NFR-18, SRG-01–SRG-29, SMR-01–SMR-12, WEB-01–WEB-11)
**UML Source**: [AstraNotes MVP UML Set (Class, Object, Use Case, Activity, Deployment)](https://lucid.app/lucidchart/633a4be6-a4d5-4060-a3ce-33c4b0de31da/edit)

## Legend

| Status | Meaning |
|---|---|
| ✅ Fully Traced | Evidence in ≥2 diagram types; clearly represented |
| ⚠️ Partially Traced | Evidence in 1 diagram type only, or only implied |
| ❌ Weakly Traced | No direct diagram representation; relies on doc/test artifacts |

---

## Summary

### MVP Requirements

| Status | Count |
|---|---|
| ✅ Fully Traced | 61 |
| ⚠️ Partially Traced | 10 |
| ❌ Weakly Traced | 0 |
| **Total MVP Requirements** | **30** |

---

## MVP Requirements (In Scope)

> Note: Partially traced MVP items are mostly implementation-detail branches that are already tested and implemented but not explicitly drawn. These are intentionally not expanded in UML to avoid diagram bloat.

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| REQ-01 | Create note with title and body | `Note`, `NoteService.create()` | UC: Create Note | FastAPI + HTMX create flow (`/api/notes`, `/ui/notes`) | ✅ Fully Traced | BL-01 implemented with integration tests for API and UI routes |
| REQ-02 | Title/body validation rules | `Note` (title, body fields), `NoteService` validators | UC: Create Note | — | ⚠️ Partially Traced | Implemented with Unicode letter support and explicit punctuation allowlist including `¿` and `¡`; validation branches are not yet diagrammed in UML |
| REQ-03 | Duplicate title auto-suffix | `NoteService`, `SqlNoteRepository.create_note_atomic()` | UC: Create Note, Activity: duplicate-title auto-suffix branch | SQLite unique constraint + retry-on-conflict | ✅ Fully Traced | Duplicate-title create conflict path is now explicitly represented in use case + activity diagrams. |
| REQ-04 | Unique ID + timestamp + persist | `Note` (id, created_at), `SqlNoteRepository` | UC: Create Note | Shared DB persistence artifact | ✅ Fully Traced | Implemented in BL-01 repository + route integration tests |
| REQ-05 | Edit title and/or body | `Note`, `NoteService.update()` | UC: Update Note | — | ✅ Fully Traced |  |
| REQ-06 | Edit title/body validation | `Note` | UC: Update Note | — | ⚠️ Partially Traced | Implemented; edit validation branches are not yet diagrammed in UML |
| REQ-07 | Duplicate title on edit (self-exclude) | `NoteService` | UC: Update Note, Activity: self-exclude duplicate validation branch | — | ✅ Fully Traced | Update duplicate-title self-exclusion behavior is now explicit in use case + activity diagrams. |
| REQ-08 | Edit persistence (keep id/created_at, update updated_at) | `Note` (updated_at), `SqlNoteRepository` | Activity: Save note changes | Shared DB persistence artifact | ✅ Fully Traced |  |
| REQ-09 | Delete confirmation prompt (move to Trash) | `NoteService.delete()`, `notes_ui.py` delete routes | UC: Delete Note (Soft Delete), Activity: delete branch | Web UI node + API/UI delete routes | ✅ Fully Traced | Confirm flow represented with soft-delete branch and route-level behavior |
| REQ-10 | Atomic soft-delete with error fallback | `NoteRepository`, structured domain error mapping | UC: Delete Note | — | ✅ Fully Traced |  |
| REQ-11 | List updates after delete; empty state | `NoteService` | UC: Delete Note (Soft Delete), UC: List Notes, UC: Restore Note | Notes UI + HTMX refresh flow on list/trash views | ✅ Fully Traced | Delete/list/restore representation now explicit across use case + activity/deployment artifacts |
| REQ-12 | List display: newest first, 40-char server-side truncation with hover tooltip; editor shows Modified timestamp; body preview uses first non-empty line with formatting-preserving render | `Note` (title, created_at, updated_at) | UC: List Notes | — | ⚠️ Partially Traced | Implemented. Truncation revised to 40 chars (BL-04 UI Alignment). Full title in storage; hover tooltip via CSS `data-full-title`; preview now renders first non-empty line with checklist/bullet/inline formatting. UML artifact update pending. |
| REQ-13 | Empty state message when no notes | — | UC: List Notes | — | ⚠️ Partially Traced | Pending UML detail: explicit empty-state message flow |
| REQ-14 | List auto-refresh after CRUD | `NoteService`, `notes_ui.py` create/search/update/delete routes | UC: List Notes, Activity: action-selection -> response flow | HTMX partial refresh + create-from-trash redirect to active results | ✅ Fully Traced | CRUD response-to-list refresh flow now represented in use case/activity/deployment set |
| REQ-15 | Search by title/body, case-insensitive | `NoteService.search()`, `SqlNoteRepository.search()`, `/api/notes/search`, `/ui/notes/search` | UC: Search Notes | API + HTMX partial route (`#notes-results`) | ✅ Fully Traced | Implemented with integration tests for API and UI live filtering |
| REQ-16 | Search edge cases: empty/whitespace/no results | `NoteService.search()` normalization, UI search context builder | UC: Search Notes, Activity: edge-case search branches | HTMX partial messaging for empty/no-match states | ✅ Fully Traced | Empty/whitespace/no-results search branches are now explicit in activity flow and linked to search use case. |
| REQ-17 | Bullet and checkbox lists in body | `Note` (body), `editor_panel.html` checklist controls | UC: Update Note, UC: Toggle Checklist Item | HTMX editor flow (`/ui/notes/{id}/editor`) | ✅ Fully Traced | List-edit behavior now represented explicitly via Update + Toggle Checklist use cases |
| REQ-18 | List persistence and render after reopen | `SqlNoteRepository`, `NoteService.update()` | UC: Update Note, UC: List Notes | Shared DB persistence artifact (`data/astranotes.db`) | ✅ Fully Traced | Persistence + reopen/list representation now present across class/use case/deployment evidence |
| REQ-19 | Checkbox toggle + immediate persist | `NoteService.toggle_checklist_item()`, `/ui/notes/{id}/checklist-toggle` | UC: Toggle Checklist Item, Activity: action-selection toggle branch | HTMX toggle route + persisted SQLite update path | ✅ Fully Traced | Toggle persistence now explicitly represented in use case + activity + deployment artifacts |
| REQ-20 | Bold/italic/underline formatting | `create_panel.html`, `editor_panel.html`, `applyBodyFormat()` JS | UC: Edit Note | HTMX create/editor body toolbar actions | ⚠️ Partially Traced | Implemented in BL-07 with integration evidence; UML formatting-action branch still pending |
| REQ-21 | Formatting safety (no title modification, no data loss) | `applyBodyFormat()` body-only scope, `NoteService.update()` | UC: Edit Note | API/update integration tests for combined markers | ⚠️ Partially Traced | Implemented and tested for body-only formatting and marker preservation; UML safety constraints still pending |
| REQ-22 | Formatting storage rules (Markdown markers) | `Note` (body storage), update routes | — | Shared DB persistence artifact | ⚠️ Partially Traced | Bold/italic stored as Markdown markers and underline as `<u>...</u>`; UML/storage-rule annotation still pending |
| REQ-23 | Max 10,000 notes | `NoteService`, `SqlNoteRepository.create_note_atomic()` | UC: Create Note, Activity: max_notes guard branch | SQLite transaction boundary + deployment max_notes limit guard | ✅ Fully Traced | Capacity guard behavior is now explicit across use case, activity, and deployment artifacts. |
| REQ-24 | Limit-reached blocking behavior + message | `NoteService`, stable machine-readable error mapping | UC: Create Note, Activity: LIMIT_REACHED branch | API/HTMX error mapping layer + deployment LIMIT_REACHED response path | ✅ Fully Traced | Limit-reached blocking and safe response path are now explicit in use case, activity, and deployment diagrams. |
| REQ-25 | Private toggle per note | `Note` (is_private), `PrivateNoteService` | UC: Mark Private | — | ✅ Fully Traced |  |
| REQ-26 | Private status persisted + visually indicated | `Note` (is_private), `SqlNoteRepository` | UC: Mark Private | Shared DB persistence artifact | ✅ Fully Traced |  |
| REQ-27 | Private notes hide body preview | `Note` (is_private), `PrivateNoteService` | UC: Mark Private, UC: Search Notes | — | ✅ Fully Traced |  |
| REQ-28 | English/Spanish interface toggle for UI text only | `src/app/presentation/localization.py`, localized template keys | UC: Switch interface language | Web UI node + HTMX language propagation (`lang` query/cookie) | ✅ Fully Traced | Implemented in BL-23 with integration coverage in `tests/integration/test_localization_ui.py` |
| NFR-06 | Web mode: up to 5,000 notes per account | `SqlNoteRepository`, `tests/performance/test_performance.py` (5,000-note seed) | BL-10 performance verification workflow | Shared DB node | ✅ Fully Traced | Verified in BL-10 with dataset size 5,000 |
| NFR-07 | API latency targets (p95/p99) | `tests/performance/test_performance.py` latency assertions | BL-10 benchmark run (read/search + update operations) | API runtime node | ✅ Fully Traced | Measured results: read p95 35.00 ms, write p95 1.34 ms, all-ops p99 35.99 ms |
| NFR-08 | API measurement boundary | `tests/performance/test_performance.py` API-route timing (`/api/notes/search`, `/api/notes/{id}`) | BL-10 service-boundary measurement procedure | API runtime node | ✅ Fully Traced | Browser rendering excluded; request/response boundary timing captured |
| NFR-09 | API write durability before success | `tests/performance/test_performance.py` immediate read-after-success verification | BL-10 durability check on update operations | Shared DB node | ✅ Fully Traced | Immediate read-after-success validation on 60 updates with zero failures |
| NFR-13 | UI/storage/security dependency separation | `NoteRepository` (interface), `NoteService`, `SqlNoteRepository` | — | AstraNotes Application | ✅ Fully Traced |  |
| NFR-14 | Interface-based testability (test doubles) | `NoteRepository` (interface), `CryptoService` | — | — | ✅ Fully Traced |  |
| NFR-15 | Automated tests for UI/security/storage | pytest integration/unit suites (`tests/unit`, `tests/integration`) | Route-layer and service-layer test scenarios | CI test workflow artifact | ⚠️ Partially Traced | Implemented test baseline; pending security-slice test completion |
| NFR-16 | Storage backend replaceability | `NoteRepository` (interface), `SqlNoteRepository` | — | — | ✅ Fully Traced |  |
| SRG-01 | All notes encrypted at rest (AES-256-GCM / ChaCha20-Poly1305) | `CryptoService`, `SqlNoteRepository` | — | Crypto Runtime library node | ✅ Fully Traced |  |
| SRG-02 | Private note encryption scope | `PrivateNoteService`, `CryptoService` | UC: Mark Private | Crypto Runtime library node | ✅ Fully Traced |  |
| SRG-04.1 | Localhost HTTP permitted for MVP development | — | — | Deployment constraint note (MVP localhost exception) | ✅ Fully Traced | Implemented as the MVP-only localhost HTTP exception |
| SRG-05 | Audit log: all CRUD operations | `AuditEntry`, `NoteService` | UC: Create/Update/Delete/Restore, Activity: post-operation logging | /data/audit-log.json artifact | ✅ Fully Traced |  |
| SRG-07 | Audit privacy: no plaintext private content | `AuditEntry` | — | /data/audit-log.json artifact | ✅ Fully Traced |  |
| SRG-10 | Soft delete: 15-day retention | `Note` (is_deleted, deleted_at) | UC: Delete Note | Shared DB persistence artifact | ✅ Fully Traced |  |
| SRG-11 | Soft-deleted notes excluded from default list/search and managed in Trash view | `NoteService`, `NoteRepository`, `notes_ui.py`, `note_preview.py` | UC: Delete Note, UC: List Notes, UC: Restore Note, UC: Trash Review | UI trash routes (`/?view=trash`, `/ui/notes/{id}/trash-viewer`, `/ui/notes/{id}/trash-unlock`, `/ui/notes/{id}/restore`, `/ui/notes/{id}/purge`) | ✅ Fully Traced | Read-only trash viewer, private-note unlock in trash, and restore/purge are covered by `tests/integration/test_trash_ui.py` |
| SRG-12 | Retention expiry purge (MVP) | `NoteService._purge_expired_deleted_notes()`, `SqlNoteRepository.purge_soft_deleted_older_than()` | Activity: list/search triggers purge path | Shared DB persistence artifact | ✅ Fully Traced | Implemented with 15-day automatic purge and covered by `test_trash_ui.py` |
| SRG-13 | Restore: preserve ID and audit entry | `NoteService`, `AuditEntry` | UC: Restore Note, Activity: restore branch | Shared DB + audit artifact | ✅ Fully Traced | Restore retention/ID preservation/audit entry are covered; version-history continuity is deferred with SRG-08 |
| SRG-14 | Structured error handling (no crashes) | stable domain error mapping, route error mapping module | Activity: save error branch | API and UI route parity tests | ✅ Fully Traced | Implemented shared error mapping with route-level tests |
| SRG-15 | Atomic commit/rollback on failure | `NoteRepository` (persist contract), `SqlNoteRepository.create_note_atomic()` | Activity: save error branch | SQLite transaction and integrity-error retry path | ✅ Fully Traced | Concurrency tests validate conflict-safe create behavior |
| SRG-16 | Consistent error codes on repeated invalid requests | stable domain error mapping, `map_note_error_code()` | Activity: invalid request error branch | API error header evidence (`X-Error-Code`) | ✅ Fully Traced | Implemented with deterministic mapping and validated by unit + API integration coverage (`tests/unit/test_error_mapping.py`, `tests/integration/test_create_note_api.py`) |
| SRG-17 | TLS release gate (no content transmission without SRG-04) | — | — | Deployment constraint note | ✅ Fully Traced | Code review confirms the MVP codebase has no outbound content-transmitting network path |
| SRG-18 | PIN unlock required for private notes | `UnlockSessionManager`, `PrivateNoteService` | Activity: Prompt PIN → validate | — | ✅ Fully Traced |  |
| SRG-19 | Private content hidden until auth succeeds | `PrivateNoteService`, `UnlockSessionManager` | Activity: PIN valid? decision | — | ✅ Fully Traced |  |
| SRG-20 | Unlock required once per session | `UnlockSessionManager` | Activity: PIN flow | — | ✅ Fully Traced |  |
| SRG-21 | 15-min inactivity → unlock expiry | `UnlockSessionManager` | Activity: Session inactive >15 min? branch | — | ✅ Fully Traced |  |
| SRG-22 | Rate limiting after 5 failed unlock attempts | `UnlockSessionManager` | Activity: Failed attempts ≥5? decision | — | ✅ Fully Traced |  |
| SRG-23 | Lockout + exponential backoff; resets on restart | `UnlockSessionManager` | Activity: lockout state node | In-memory session state | ✅ Fully Traced |  |
| SRG-24 | Anti-enumeration: identical error for wrong PIN and internal error | `UnlockSessionManager` | Activity: constraint note (indistinguishable errors) | — | ✅ Fully Traced |  |
| SRG-25 | Plaintext metadata allowlist | `Note` (field list), `SqlNoteRepository` | — | Shared DB persistence artifact | ✅ Fully Traced |  |
| SRG-26 | PBKDF2-HMAC-SHA256 key derivation (≥260k iterations) | `CryptoService` | — | Key Derivation library node | ✅ Fully Traced |  |
| SRG-27 | App-wide 4-digit PIN bootstrap (default `1234`) | `PinSettingsManager`, `UnlockSessionManager`, `CryptoService.set_private_pin()` | Activity: unlock prompt validates 4-digit PIN | UI settings + config persistence artifact (`/ui/security/pin`) | ✅ Fully Traced | Implemented with persistent app-wide PIN default and verification flow. Test evidence: TP-U32, TP-U33, TP-I08 (see `planning/test-plan.md`). |
| SRG-28 | In-app PIN change + atomic private-note rotation + keypad UX | `PinSettingsManager`, `SqlNoteRepository.rotate_private_pin()`, `notes_ui.py`, `pin_settings_panel.html`, `pin_input_component.html` | Activity: verify current PIN → reveal new/confirm inputs → rotate private note ciphertext → completion state; unlock via keypad auto-submit | HTMX verify/update routes (`/ui/security/pin/verify`, `/ui/security/pin`) + unlock partials | ✅ Fully Traced | Implemented with rollback-safe rotation, staged verify/update flow, and completion-state rendering. Test evidence: TP-U33, TP-U34, TP-I08, TP-I09, TP-I14 (see `planning/test-plan.md`). |
| WEB-03 | JSON APIs for create/edit/delete/list/search/restore | FastAPI route layer, note service, repository boundary | Activity: API request/response flows | API runtime node | ✅ Fully Traced | Implemented and exercised by API integration coverage across the note workflows |
| WEB-04 | Web client consumes public APIs only | UI → service boundary with API parity contract | UC: all note workflows via API | — | ✅ Fully Traced | Implemented through the UI/service boundary; UI routes do not couple directly to storage or security internals |
| SMR-01 | Rotating diagnostic log file with tier, timestamp, severity, correlation ID | `AppLogger` | — | AstraNotes Application node | ✅ Fully Traced | Runtime coverage exists and logger class is represented in UML |
| SMR-03 | Log entries never contain note plaintext | `AppLogger` | — | — | ⚠️ Partially Traced | Constraint is defined; logger privacy note in UML is pending |
| SMR-04 | Storage/security errors translated to stable domain errors before UI responses | `error_mapping.py`, domain error types | Activity: error branch rendering with mapping step | Deployment: Error Mapping Layer -> User-Safe Error Response Contract | ✅ Fully Traced | Stable domain-error translation path is now explicitly modeled in activity + deployment diagrams. |
| SMR-05 | UI renders user-safe error state; no codes/traces shown to user | Notes UI (`FT63emqFhc.5`) | Activity: user-safe error rendering branch | Deployment: User-Safe Error Response Contract -> Notes UI | ✅ Fully Traced | UI safe-error rendering constraint is now explicitly represented in activity + deployment diagrams. |
| SMR-06 | Startup: verify/create data directory; refuse launch if not writable | `AppStartup` | Activity: startup bootstrap branch | Local File System node | ✅ Fully Traced | Startup component now represented in deployment/activity artifacts |
| SMR-07 | Startup: unreadable/invalid persistence store triggers clear fail-fast behavior | `SqlNoteRepository` startup path | Activity: startup fail-fast readiness guard branch | Deployment: Startup Readiness Guard with DB readability check | ✅ Fully Traced | Fail-fast startup path is now explicitly represented in activity + deployment diagrams. |
| SMR-09 | config.json: unknown keys ignored, missing keys use defaults, invalid values → WARNING | `ConfigService` | Activity: config load path | /data/config.json artifact | ✅ Fully Traced | ConfigService and config artifact are now represented in deployment/activity artifacts |
| SMR-10 | Four supported config keys: log_level, data_dir, inactivity_timeout_minutes, max_notes | `ConfigService` | Activity: startup config consumption path | /data/config.json artifact | ✅ Fully Traced | Config flow is represented via startup + ConfigService deployment/activity evidence |
| SMR-11 | Semantic version embedded and available in runtime/startup metadata | `APP_VERSION`/application version metadata | — | AstraNotes Application node | ⚠️ Partially Traced | Runtime metadata exists; dedicated About UI exposure deferred |

---

### Post-MVP Requirements Summary

| Status | Count |
|---|---|
| ✅ Fully Traced | 0 |
| ⚠️ Partially Traced | 0 |
| ❌ Weakly Traced | 30 |
| **Total Post-MVP Requirements** | **30** |

---

## Post-MVP Requirements

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| REQ-29 | Nested bullet/checklist lists up to 3 levels [Post-MVP] | Editor list model (planned) | UC: Edit Note (nested list branch) | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| REQ-30 | Image paste in note body [Post-MVP] | Media/content sanitizer module (planned) | UC: Edit Note (paste image flow) | Storage/media artifact | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| NFR-01 | 100 concurrent user sessions | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| NFR-02 | Active session definition and workload mix | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| NFR-03 | Concurrency latency targets (p95/p99) | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| NFR-04 [Post-MVP] | Optimistic concurrency / version field | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP; current MVP does not expose note-version conflict handling |
| NFR-05 | Overload throttle; ≤1% failure rate | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| NFR-10 | Browser keyboard-only workflows [Post-MVP] | — | UC: (all core use cases) | Web UI node | ❌ Weakly Traced | Deferred to Post-MVP for single-user demo timeline; keyboard-only parity evidence intentionally deferred |
| NFR-11 | Mobile touch-only workflows [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| NFR-12 | Tab/touch reachability + focus indicator [Post-MVP] | — | — | — | ❌ Weakly Traced | Deferred to Post-MVP for single-user demo timeline; focus-indicator parity evidence intentionally deferred |
| NFR-17 | Mobile touch target ≥44×44px [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| NFR-18 | Desktop shortcut equivalence on mobile [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-03 | Per-note key isolation [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-04.2 [Post-MVP] | TLS 1.2+ for non-local data in transit | — | — | Deployment constraint note (TLS requirement) | ❌ Weakly Traced | Deferred to Post-MVP; production TLS verification is pending |
| SRG-06 | Tamper-evident audit hash chain [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-08 [Post-MVP] | Immutable version records | — | — | — | ❌ Weakly Traced | Deferred until version-history implementation is activated |
| SRG-09 | Version SHA-256 hash validation [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| SRG-29 | Retention expiry purge [Post-MVP] | — | — | — | ❌ Weakly Traced | Post-MVP scope; coverage intentionally deferred |
| WEB-01 | Authenticated account required for note operations | `AuthService`, `SessionRepository` (planned) | UC: Login, UC: Access Notes | Shared deployment node | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-02 | Per-user data isolation (owner-scoped reads/writes) | `SqlNoteRepository` owner scoping | UC: List Notes, UC: Edit Note | Shared DB node | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-05 | Session expires after inactivity | `SessionRepository`, inactivity timeout policy | Activity: session timeout and re-auth path | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-06 | Server-side authorization check on every API | `AuthService`, route-level dependency checks | Activity: authorize before mutate | — | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-07 | Transactional multi-user storage integrity | `SqlNoteRepository`, DB transaction boundary | Activity: commit/rollback | Shared DB node | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-08 | Shared persistent demo environment | Deployment config + persistence volume | UC: reviewer access | Shared deployment endpoint | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-09 | Persistent User model with required fields | `User` table: user_id, email, password_hash, created_at, is_active | UC: Signup, UC: Login | Database schema artifact | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-10 | Database-backed session store with timeouts | `Session` table: session_id, user_id, created_at, last_activity_at, expires_at, is_revoked, ip_address, user_agent; 30-min idle timeout, 7-day absolute timeout | Activity: login → session create; logout → session revoke; timeout check | Database schema artifact | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| WEB-11 | Separate login password and note passphrase | `User.password_hash` (bcrypt/Argon2); `Note.passphrase_salt` + PBKDF2 (4-digit PIN) | Activity: login hashes password; unlock derives key from passphrase | Crypto policy artifact | ❌ Weakly Traced | Deferred to Post-MVP in the single-user local MVP baseline |
| SMR-02 [Post-MVP] | Log level configurable in config.json; live reload | `AppLogger`, `ConfigService` | — | /data/config.json artifact | ❌ Weakly Traced | Deferred to Post-MVP under localhost MVP scope rebaseline |
| SMR-08 [Post-MVP] | Schema migration version guard; refuse write if stored version > app version | `SqlNoteRepository`, migration metadata | — | DB migration metadata artifact | ❌ Weakly Traced | Deferred to Post-MVP under localhost MVP scope rebaseline |
| SMR-12 [Post-MVP] | Graceful shutdown: in-progress writes complete before process exits | `SqlNoteRepository` (transaction guard) | — | AstraNotes Application node | ❌ Weakly Traced | Deferred to Post-MVP under localhost MVP scope rebaseline |
