# Storage Design Notes

## Current MVP Storage Baseline

AstraNotes MVP uses local SQLite persistence through SQLAlchemy. The active backend is `SqlNoteRepository`; legacy file-per-note JSON storage is not the current implementation.

## Storage Goals (Implemented)

- Reliable local persistence for single-user localhost workflows.
- Encrypted-at-rest note content for both private and non-private notes.
- Soft delete and trash retention behavior with automatic expiry purge.
- Audit and diagnostic logging without plaintext note leakage.

## Primary Persistence Artifacts

| Artifact | Location | Purpose |
|---|---|---|
| SQLite DB (`astranote.db`) | Configured data directory | Primary note store |
| Audit log (`audit-log.jsonl`) | Configured data directory | Append-only audit trail |
| Diagnostic log (`astranote.log`) | Configured data directory | Runtime diagnostics |
| Runtime config (`config.json`) | Configured data directory | Supported settings and PIN token metadata |

Default data directory is OS-specific via `ConfigService`, and can be overridden with `ASTRANOTE_DATA_DIR` or `ASTRANOTE_CONFIG_PATH`.

## Note Record Shape (SQLite)

The repository persists note rows with these fields:

- `note_id` (PK)
- `title` (encrypted payload string)
- `body` (encrypted payload string)
- `is_private` (bool)
- `pin_salt` (nullable; required for private-note decryption key derivation)
- `is_deleted` (bool)
- `created_at`
- `updated_at`
- `deleted_at` (nullable)

Constraint behavior:

- Unique title constraint for active/deleted state: `(title, is_deleted)`.
- Write serialization lock in repository for duplicate-title-safe create/update under concurrent local requests.

## Encryption-at-Rest Design

- `CryptoService` encrypts `title` and `body` before persistence.
- Public note fields are encrypted with a master-derived key.
- Private note fields are encrypted with a PIN-derived key per-note salt.
- PBKDF2-HMAC-SHA256 is used with 260,000 iterations.
- Encryption format is encoded as versioned payload text (`enc:v1:...`).
- Legacy plaintext read fallback exists only to avoid data loss on pre-encryption local stores.

## Lifecycle and Retention Behavior

- Delete is soft delete (`is_deleted=true`, `deleted_at` set).
- Trash view operates on soft-deleted rows.
- Retention window is 15 days.
- Expired soft-deleted rows are purged by service-level purge calls during list/search flows.

## Startup and Integrity Guardrails

- `AppStartup` verifies data directory existence/writability.
- Startup verifies SQLite store readability/structural validity.
- On startup verification failure, app fails fast with a clear error instead of launching partially.

## Scope Notes

Not part of current MVP storage design:

- Multi-user owner scoping columns and account/session tables.
- External DB migration tooling requirement (schema is currently bootstrapped by repository initialization and compatibility column checks).
- Cloud sync or remote storage adapters.