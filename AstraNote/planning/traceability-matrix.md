# Requirements Traceability Matrix

**Project**: AstraNotes  
**Last Updated**: 2026-05-11  
**Total Requirements**: 94 (REQ-01–REQ-27, NFR-01–NFR-18, SRG-01–SRG-26, SMR-01–SMR-12, WEB-01–WEB-11)  
**UML Source**: Lucid document `83846df4-c365-4466-83ae-ea4703514eca`, Page 2 (`C0fSJIjDhK~F`)

## Legend

| Status | Meaning |
|---|---|
| ✅ Fully Traced | Evidence in ≥2 diagram types; clearly represented |
| ⚠️ Partially Traced | Evidence in 1 diagram type only, or only implied |
| ❌ Weakly Traced | No direct diagram representation; relies on doc/test artifacts |

---

## Functional Requirements (REQ-01–REQ-27)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| REQ-01 | Create note with title and body | `Note`, `NoteService.create()` | UC: Create Note | — | ✅ Fully Traced | |
| REQ-02 | Title/body validation rules | `Note` (title, body fields) | UC: Create Note | — | ⚠️ Partially Traced | Validation logic not shown in diagrams; needs unit tests |
| REQ-03 | Duplicate title auto-suffix | `NoteService` | UC: Create Note | — | ⚠️ Partially Traced | Suffix logic implied in service; not explicitly modeled |
| REQ-04 | Unique ID + timestamp + persist | `Note` (id, created_at), `SqlNoteRepository` | UC: Create Note | Shared DB persistence artifact | ✅ Fully Traced | |
| REQ-05 | Edit title and/or body | `Note`, `NoteService.update()` | UC: Edit Note | — | ✅ Fully Traced | |
| REQ-06 | Edit title/body validation | `Note` | UC: Edit Note | — | ⚠️ Partially Traced | Same as REQ-02; validation not diagrammed |
| REQ-07 | Duplicate title on edit (self-exclude) | `NoteService` | UC: Edit Note | — | ⚠️ Partially Traced | Self-exclusion logic implied but not explicit |
| REQ-08 | Edit persistence (keep id/created_at, update updated_at) | `Note` (updated_at), `SqlNoteRepository` | Activity: Save note changes | Shared DB persistence artifact | ✅ Fully Traced | |
| REQ-09 | Delete confirmation prompt | — | UC: Delete Note | — | ⚠️ Partially Traced | Confirmation step not shown in activity diagram |
| REQ-10 | Atomic delete with error fallback | `NoteRepository`, `ResultError` | UC: Delete Note | — | ✅ Fully Traced | |
| REQ-11 | List updates after delete; empty state | `NoteService` | UC: Delete Note, UC: List Notes | — | ⚠️ Partially Traced | Empty state behavior not modeled |
| REQ-12 | List display: newest first, 60-char truncation, date format | `Note` (title, created_at) | UC: List Notes | — | ⚠️ Partially Traced | Truncation and date format are UX details not in diagrams |
| REQ-13 | Empty state message when no notes | — | UC: List Notes | — | ⚠️ Partially Traced | Empty state only referenced in use case label |
| REQ-14 | List auto-refresh after CRUD | `NoteService` | UC: List Notes | — | ⚠️ Partially Traced | Refresh trigger not shown as explicit flow |
| REQ-15 | Search by title/body, case-insensitive | `NoteService.search()` | UC: Search Notes | — | ✅ Fully Traced | |
| REQ-16 | Search edge cases: empty/whitespace/no results | `NoteService` | UC: Search Notes | — | ⚠️ Partially Traced | Edge-case branches not shown in activity diagram |
| REQ-17 | Bullet and checkbox lists in body | `Note` (body) | UC: Edit Note | — | ⚠️ Partially Traced | List rendering not in diagrams; UI-layer detail |
| REQ-18 | List persistence and render after reopen | `SqlNoteRepository` | — | Shared DB persistence artifact | ⚠️ Partially Traced | Rendering consistency is a UI-layer concern |
| REQ-19 | Checkbox toggle + immediate persist | `Note`, `NoteService` | UC: Edit Note | — | ⚠️ Partially Traced | Immediate persist not shown explicitly |
| REQ-20 | Bold/italic/underline formatting | `Note` (body) | UC: Edit Note | — | ⚠️ Partially Traced | Formatting tools are UI-layer; not in architecture diagrams |
| REQ-21 | Formatting safety (no title modification, no data loss) | `Note` | UC: Edit Note | — | ⚠️ Partially Traced | Safety rules not explicitly modeled |
| REQ-22 | Formatting storage rules (Markdown markers) | `Note` (body storage) | — | Shared DB persistence artifact | ⚠️ Partially Traced | Storage format is impl detail; needs UX spec |
| REQ-23 | Max 10,000 notes | `NoteService` | UC: Create Note | — | ⚠️ Partially Traced | Capacity check logic implied in service |
| REQ-24 | Limit-reached blocking behavior + message | `NoteService`, `ResultError` | UC: Create Note | — | ⚠️ Partially Traced | Exact error message is a UX detail |
| REQ-25 | Private toggle per note | `Note` (is_private), `SecureNote` | UC: Mark Private | — | ✅ Fully Traced | |
| REQ-26 | Private status persisted + visually indicated | `Note` (is_private), `SqlNoteRepository` | UC: Mark Private | Shared DB persistence artifact | ✅ Fully Traced | |
| REQ-27 | Private notes hide body preview | `SecureNote` | UC: Mark Private, UC: Search Notes | — | ✅ Fully Traced | |

---

## Non-Functional Requirements (NFR-01–NFR-18)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| NFR-01 | 100 concurrent user sessions | — | — | — | ❌ Weakly Traced | Concurrency target needs dedicated load-test evidence artifact |
| NFR-02 | Active session definition and workload mix | — | — | — | ❌ Weakly Traced | Test definition only; no UML representation appropriate |
| NFR-03 | Concurrency latency targets (p95/p99) | — | — | — | ❌ Weakly Traced | Performance target; no UML representation; needs NFR Verification Plan |
| NFR-04 | Optimistic concurrency / version field | `Note` (version), `ResultError` (STALE_VERSION) | Activity: conflict/save error branch | — | ✅ Fully Traced | |
| NFR-05 | Overload throttle; ≤1% failure rate | — | — | — | ❌ Weakly Traced | Overload policy; no UML representation; needs NFR Verification Plan |
| NFR-06 | Web mode: up to 5,000 notes per account | `SqlNoteRepository` (planned), owner scoping | — | Shared DB node | ⚠️ Partially Traced | SQL repository and per-account data shape not yet in UML export |
| NFR-07 | API latency targets (p95/p99) | — | — | API runtime node | ❌ Weakly Traced | Performance target; needs NFR verification benchmark evidence |
| NFR-08 | API measurement boundary | — | — | — | ❌ Weakly Traced | Test methodology definition only |
| NFR-09 | API write durability before success | `NoteRepository` (persist contract) | Activity: save/commit branch | — | ⚠️ Partially Traced | Durability guarantee implied by repository contract |
| NFR-10 | Browser keyboard-only workflows | — | UC: (all core use cases) | Web UI node | ⚠️ Partially Traced | Input model is UI concern; not modeled in architecture diagrams |
| NFR-11 | Mobile touch-only workflows [Post-MVP] | — | — | — | ❌ Weakly Traced | Explicitly Post-MVP for current course scope |
| NFR-12 | Tab/touch reachability + focus indicator | — | — | — | ❌ Weakly Traced | UI accessibility detail; no UML representation |
| NFR-13 | UI/storage/security dependency separation | `NoteRepository` (interface), `NoteService`, `SqlNoteRepository` | — | AstraNotes Application | ✅ Fully Traced | |
| NFR-14 | Interface-based testability (test doubles) | `NoteRepository` (interface), `KeyDerivationService` | — | — | ✅ Fully Traced | |
| NFR-15 | Automated tests for UI/security/storage | — | — | — | ❌ Weakly Traced | No test artifact in UML; needs companion test plan |
| NFR-16 | Storage backend replaceability | `NoteRepository` (interface), `SqlNoteRepository` | — | — | ✅ Fully Traced | |
| NFR-17 | Mobile touch target ≥44×44px [Post-MVP] | — | — | — | ❌ Weakly Traced | Explicitly Post-MVP for current course scope |
| NFR-18 | Desktop shortcut equivalence on mobile [Post-MVP] | — | — | — | ❌ Weakly Traced | Explicitly Post-MVP for current course scope |

---

## Security, Reliability & Governance Requirements (SRG-01–SRG-26)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| SRG-01 | All notes encrypted at rest (AES-256-GCM / ChaCha20-Poly1305) | `SecureNote`, `KeyDerivationService` | — | Crypto Runtime library node | ✅ Fully Traced | |
| SRG-02 | Private note encryption scope | `SecureNote`, `KeyDerivationService` | UC: Mark Private | Crypto Runtime library node | ✅ Fully Traced | |
| SRG-03 | Per-note key isolation [Post-MVP] | — | — | — | ❌ Weakly Traced | Intentionally Post-MVP; no current diagram representation needed |
| SRG-04 | TLS 1.2+ for data in transit | — | — | Deployment constraint note (TLS requirement) | ⚠️ Partially Traced | MVP is local-only; TLS constraint captured in deployment note |
| SRG-05 | Audit log: all CRUD operations | `AuditEntry`, `NoteService` | UC: (all CRUD use cases) | /data/audit-log.jsonl artifact | ✅ Fully Traced | |
| SRG-06 | Tamper-evident audit hash chain [Post-MVP] | — | — | — | ❌ Weakly Traced | Intentionally Post-MVP; no current diagram representation needed |
| SRG-07 | Audit privacy: no plaintext private content | `AuditEntry` | — | /data/audit-log.jsonl artifact | ✅ Fully Traced | |
| SRG-08 | Immutable version records | `VersionHistory`, `NoteVersion` | — | — | ✅ Fully Traced | |
| SRG-09 | Version SHA-256 hash validation [Post-MVP] | — | — | — | ❌ Weakly Traced | Intentionally Post-MVP; no current diagram representation needed |
| SRG-10 | Soft delete: 30-day retention | `Note` (is_deleted, deleted_at) | UC: Delete Note | Shared DB persistence artifact | ✅ Fully Traced | |
| SRG-11 | Soft-deleted notes excluded from list/search; restorable in window | `NoteService`, `NoteRepository` | UC: Delete Note, UC: List Notes | — | ✅ Fully Traced | |
| SRG-12 | Retention expiry purge [Post-MVP] | — | — | — | ❌ Weakly Traced | Intentionally Post-MVP |
| SRG-13 | Restore: preserve ID, history, audit entry | `NoteService`, `VersionHistory`, `AuditEntry` | — | — | ✅ Fully Traced | |
| SRG-14 | Structured error handling (no crashes) | `ResultError` | Activity: save error branch | — | ✅ Fully Traced | |
| SRG-15 | Atomic commit/rollback on failure | `NoteRepository` (persist contract), `ResultError` | Activity: save error branch | — | ✅ Fully Traced | |
| SRG-16 | Consistent error codes on repeated invalid requests | `ResultError` | — | — | ⚠️ Partially Traced | Idempotent error behavior implied by ResultError; not flow-diagrammed |
| SRG-17 | TLS release gate (no content transmission without SRG-04) | — | — | Deployment constraint note | ⚠️ Partially Traced | Gate is a process control; captured in deployment constraint note |
| SRG-18 | Passphrase unlock required for private notes | `UnlockSessionManager`, `KeyDerivationService` | Activity: Prompt passphrase → validate | — | ✅ Fully Traced | |
| SRG-19 | Private content hidden until auth succeeds | `SecureNote`, `UnlockSessionManager` | Activity: Passphrase valid? decision | — | ✅ Fully Traced | |
| SRG-20 | Unlock required once per session | `UnlockSessionManager` | Activity: passphrase flow | — | ✅ Fully Traced | |
| SRG-21 | 15-min inactivity → unlock expiry | `UnlockSessionManager` | Activity: Session inactive >15 min? branch | — | ✅ Fully Traced | |
| SRG-22 | Rate limiting after 5 failed unlock attempts | `UnlockSessionManager` | Activity: Failed attempts ≥5? decision | — | ✅ Fully Traced | |
| SRG-23 | Lockout + exponential backoff; persists across restarts | `UnlockSessionManager` | Activity: lockout state node | /data/security-state.json artifact | ✅ Fully Traced | |
| SRG-24 | Anti-enumeration: identical error for wrong passphrase and internal error | `UnlockSessionManager` | Activity: constraint note (indistinguishable errors) | — | ✅ Fully Traced | |
| SRG-25 | Plaintext metadata allowlist | `Note` (field list), `SqlNoteRepository` | — | Shared DB persistence artifact | ✅ Fully Traced | |
| SRG-26 | PBKDF2-HMAC-SHA256 key derivation (≥260k iterations) | `KeyDerivationService` | — | Key Derivation library node | ✅ Fully Traced | |

---

## Web and Multi-User Requirements (WEB-01–WEB-11)

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| WEB-01 | Authenticated account required for note operations | `AuthService`, `SessionRepository` (planned) | UC: Login, UC: Access Notes | Shared deployment node | ⚠️ Partially Traced | Auth classes not yet present in UML export |
| WEB-02 | Per-user data isolation (owner-scoped reads/writes) | `SqlNoteRepository` owner scoping | UC: List Notes, UC: Edit Note | Shared DB node | ⚠️ Partially Traced | Owner scoping not yet rendered in current class diagram |
| WEB-03 | JSON APIs for create/edit/delete/list/search/restore | FastAPI route layer (planned) | Activity: API request/response flows | API runtime node | ⚠️ Partially Traced | API endpoints not yet represented in UML artifacts |
| WEB-04 | Web client consumes public APIs only | UI → API boundary rule | UC: all note workflows via API | — | ⚠️ Partially Traced | Boundary captured in requirements/ADR, not yet diagrammed |
| WEB-05 | Session expires after inactivity | `SessionRepository`, inactivity timeout policy | Activity: session timeout and re-auth path | — | ⚠️ Partially Traced | Session timeout flow not yet in activity diagrams |
| WEB-06 | Server-side authorization check on every API | `AuthService`, route-level dependency checks | Activity: authorize before mutate | — | ⚠️ Partially Traced | Endpoint guard pattern not yet in UML |
| WEB-07 | Transactional multi-user storage integrity | `SqlNoteRepository`, DB transaction boundary | Activity: commit/rollback | Shared DB node | ⚠️ Partially Traced | Transaction handling implied; implementation diagram pending |
| WEB-08 | Shared persistent demo environment | Deployment config + persistence volume | UC: reviewer access | Shared deployment endpoint | ❌ Weakly Traced | Requires deployment architecture artifact and runbook |
| WEB-09 | Persistent User model with required fields | `User` table: user_id, email, password_hash, created_at, is_active | UC: Signup, UC: Login | Database schema artifact | ⚠️ Partially Traced | User model design document included in ADR; schema diagram pending |
| WEB-10 | Database-backed session store with timeouts | `Session` table: session_id, user_id, created_at, last_activity_at, expires_at, is_revoked, ip_address, user_agent; 30-min idle timeout, 7-day absolute timeout | Activity: login → session create; logout → session revoke; timeout check | Database schema artifact | ⚠️ Partially Traced | Session lifecycle design documented in ADR; sequence diagram pending |
| WEB-11 | Separate login password and note passphrase | `User.password_hash` (bcrypt/Argon2); `Note.passphrase_salt` + PBKDF2 (4-digit PIN) | Activity: login hashes password; unlock derives key from passphrase | Crypto policy artifact | ⚠️ Partially Traced | Separation rationale in ADR; cryptographic flow diagram pending |

---

## Summary

| Status | Count |
|---|---|
| ✅ Fully Traced | 26 |
| ⚠️ Partially Traced | 41 |
| ❌ Weakly Traced | 15 |
| ➕ SMR — Pending Diagrams | 12 |
| **Total** | **91** |

---

## Serviceability and Manageability Requirements (SMR-01–SMR-12)

> These requirements were added to support the 3-tier GUI architecture. UML diagram coverage will be added in the UML gap-resolution session.

| Req ID | Short Description | Class / Object Evidence | Use Case / Activity Evidence | Deployment Evidence | Status | Gap Note |
|---|---|---|---|---|---|---|
| SMR-01 | Rotating diagnostic log file with tier, timestamp, severity, correlation ID | `AppLogger` (to be added to class diagram) | — | AstraNotes Application node | ⚠️ Partially Traced | Logger class not yet in UML; deployment node covers runtime |
| SMR-02 | Log level configurable in config.json; live reload | `AppLogger`, `ConfigService` | — | /data/config.json artifact | ⚠️ Partially Traced | ConfigService not yet in class diagram |
| SMR-03 | Log entries never contain note plaintext | `AppLogger` | — | — | ⚠️ Partially Traced | Privacy constraint on logger; needs class diagram note |
| SMR-04 | ResultError includes source_tier; raw exceptions never reach UI | `ResultError` (source_tier field) | — | — | ⚠️ Partially Traced | ResultError in class diagram; source_tier field to be added |
| SMR-05 | UI renders user-safe error state; no codes/traces shown to user | UI tier (to be modeled) | Activity: error branch rendering | — | ❌ Weakly Traced | No UI-tier class in current class diagram |
| SMR-06 | Startup: verify/create data directory; refuse launch if not writable | `AppStartup` (to be added) | — | Local File System node | ⚠️ Partially Traced | Startup class not yet modeled; deployment covers file system |
| SMR-07 | Startup: corrupt/unreadable persistence store preserved + fresh store initialized + user warning | `SqlNoteRepository` startup path | — | Shared DB artifact | ⚠️ Partially Traced | Startup recovery flow not yet diagrammed |
| SMR-08 | Schema migration version guard; refuse write if stored version > app version | `SqlNoteRepository`, migration metadata | — | DB migration metadata artifact | ⚠️ Partially Traced | Migration-version guard not yet in class diagram |
| SMR-09 | config.json: unknown keys ignored, missing keys use defaults, invalid values → WARNING | `ConfigService` (to be added) | — | /data/config.json artifact | ⚠️ Partially Traced | ConfigService not yet modeled |
| SMR-10 | Four supported config keys: log_level, data_dir, inactivity_timeout_minutes, max_notes | `ConfigService` | — | /data/config.json artifact | ⚠️ Partially Traced | Configuration keys drive SRG-21 and REQ-23 behavior |
| SMR-11 | Semantic version embedded in app, shown in About UI, logged on startup | `AppVersion` / version constant | — | AstraNotes Application node | ⚠️ Partially Traced | Version not yet in class diagram |
| SMR-12 | Graceful shutdown: in-progress writes complete before process exits | `SqlNoteRepository` (transaction guard) | — | AstraNotes Application node | ⚠️ Partially Traced | Shutdown behavior not yet in activity diagram |

### Weakly Traced — Root Cause Groups

| Group | Requirements | Recommended Artifact |
|---|---|---|
| Concurrency / performance targets | NFR-01, NFR-02, NFR-03, NFR-05, NFR-07, NFR-08 | NFR Verification Plan (`nfr-verification-plan.md`) |
| Mobile / accessibility (out of MVP scope) | NFR-11, NFR-12, NFR-17, NFR-18 | Explicitly mark Post-MVP in requirements; note in this matrix |
| Automated test coverage | NFR-15 | Test plan / test strategy document |
| Post-MVP security hardening | SRG-03, SRG-06, SRG-09, SRG-12 | Already tagged `[Post-MVP]`; no action needed for MVP |
