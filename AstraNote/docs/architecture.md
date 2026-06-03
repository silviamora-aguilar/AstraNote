# Architecture

## High-Level Design

AstraNotes is a web-based multi-user note-taking system with a strict three-tier architecture: Web UI, API/Service, and Data/Security. Tier boundaries are enforced through explicit interfaces so each tier can be tested and evolved independently (NFR-13, NFR-14, NFR-16).

## Layer Overview

```
┌─────────────────────────────┐
│      Web UI Layer           │  Browser client (HTML/CSS/JS)
└────────────┬────────────────┘
          │ HTTPS + JSON API
┌────────────▼────────────────┐
│      API / Service Layer    │  Auth, NoteService, validation,
│                             │  concurrency checks, audit orchestration
└──────┬──────────────┬───────┘
    │              │
┌──────▼──────┐  ┌────▼────────────────┐
│ Data Layer  │  │   Security Layer    │
│             │  │                     │
│ NoteRepo    │  │  KeyDerivationSvc   │
│ (interface) │  │  UnlockSessionMgr   │
│     ▲       │  │  SecureNote         │
│     │       │  └─────────────────────┘
│ Sql/Json    │
│ Repository  │  → notes (tenant/user scoped)
│             │  → audit_log
│             │  → security_state
│             │  → users / sessions
└─────────────┘
```

## Key Components

### NoteRepository (interface)
Abstract interface for all storage operations. Concrete implementations (e.g., `SqlNoteRepository` or `JsonNoteRepository`) depend on this interface, never on UI code. Enables test doubles and backend swap (NFR-14, NFR-16).

```python
class NoteRepository:
    def save(self, user_id: str, note: Note) -> Result: ...
    def get(self, user_id: str, note_id: str) -> Result: ...
    def list(self, user_id: str) -> Result: ...
    def search(self, user_id: str, query: str) -> Result: ...
    def soft_delete(self, user_id: str, note_id: str) -> Result: ...
    def restore(self, user_id: str, note_id: str) -> Result: ...
```

### NoteService
Orchestrates all business rules: validation (REQ-02, REQ-06), duplicate-title handling (REQ-03, REQ-07), capacity enforcement (REQ-23, REQ-24), concurrency version check (NFR-04), per-user authorization boundaries, audit log entry creation (SRG-05), and delegation to `NoteRepository`.

### JsonNoteRepository
Concrete `NoteRepository` implementation backed by a single `notes.json` file. All writes are atomic (write to temp → rename). Enforces the SRG-25 plaintext allowlist: only `note_id`, `created_at`, `updated_at`, `is_private`, `is_deleted`, `deleted_at` are stored in plaintext; `title`, `body`, and `version_content` are always encrypted.

### SqlNoteRepository (target for web multi-user)
Primary repository for web deployment. Stores notes scoped by `owner_user_id` and enforces tenant/user-level filtering for every read/write operation. Supports concurrent users, transactional writes, and per-request consistency boundaries.

### SecureNote
Wraps encrypted note content. Responsible for encryption/decryption using the session key provided by `KeyDerivationService`. Private note content is never passed to any layer in plaintext unless the session is unlocked.

### KeyDerivationService
Derives encryption keys from user passphrase via PBKDF2-HMAC-SHA256 (≥260,000 iterations, 16-byte random salt, 256-bit output key). Raw passphrase is never stored (SRG-26).

### UnlockSessionManager
Manages per-note unlock state. Enforces: session-scoped unlock (SRG-20), 15-minute inactivity expiry (SRG-21), 5-failure rate limiting (SRG-22), exponential-backoff lockout during the active app session (SRG-23), and anti-enumeration uniform error responses (SRG-24). State is kept in memory and resets on app restart.

### AuthService (web-only)
Authenticates users, issues sessions/tokens, and supplies authenticated `user_id` context to all service operations. All note and audit operations require authenticated identity.

### ResultError
Structured error type returned by all service and repository operations. Contains a machine-readable code and user-safe message (SRG-14). Used to signal STALE_VERSION, SAVE_ERROR, NOT_FOUND, CAPACITY_EXCEEDED, and so on.

### AuditEntry
Immutable record written to `/data/audit-log.jsonl` for every CRUD, restore, and export operation. Contains actor identity, action type, note_id, UTC timestamp, outcome, and correlation ID (SRG-05). Never contains plaintext private note content (SRG-07).

### VersionHistory / NoteVersion
Immutable version records. Each edit creates a new `NoteVersion`; prior versions are never modified (SRG-08).

## Data Files

| File | Purpose | Plaintext fields |
|---|---|---|
| `notes` table / collection | Notes (active + soft-deleted), scoped per user | allowlist metadata only in plaintext |
| `audit_log` table / stream | Append-only audit records | No private note content |
| `security_state` table | Lockout state, attempt count, expiry | Non-sensitive security metadata |
| `users` + `sessions` | Authentication identity/session state | No plaintext passphrases |
| `config` | App configuration | Non-sensitive settings |

## Dependency Rules

- Web UI may only call API endpoints — never storage or crypto classes directly.
- API handlers may call `NoteService` and `AuthService` only.
- `NoteService` depends on `NoteRepository` (interface) and `UnlockSessionManager` — never on concrete storage classes.
- `SqlNoteRepository`/`JsonNoteRepository` and `KeyDerivationService` have no upstream UI dependencies.
- This ensures security and storage components are independently testable and replaceable.
