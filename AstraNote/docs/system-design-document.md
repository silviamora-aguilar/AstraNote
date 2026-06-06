# System Design Document - AstraNotes

## 1. Purpose

This document describes the implemented MVP system design for AstraNotes as delivered: local single-user web app, FastAPI backend, Jinja2 + HTMX UI, SQLite persistence, encrypted-at-rest note content, and PIN-gated private note workflows.

## 2. Design Scope

This document covers implemented MVP behavior for:

- architecture structure,
- persistence and runtime data,
- private-note security controls,
- local deployment shape,
- current risks and Post-MVP boundaries.

## 3. Architecture Summary

AstraNotes is organized into three tiers:

- Web UI tier: server-rendered templates and HTMX partial updates.
- API/Service tier: FastAPI routes, NoteService, PrivateNoteService, error mapping.
- Data/Security tier: SqlNoteRepository, CryptoService, unlock/PIN managers, audit and runtime logging.

Current runtime target is localhost use (127.0.0.1), not multi-user hosted deployment.

## 4. Runtime Design

### 4.1 Web UI Tier

- Uses Jinja2 templates in `src/app/templates`.
- Uses HTMX for partial refreshes (list/search/editor/trash interactions).
- Uses UI routes in `src/app/api/notes_ui.py`.

### 4.2 API/Service Tier

- JSON endpoints in `src/app/api/notes_api.py`.
- `NoteService` applies validation, duplicate-title allocation, soft delete, restore, purge, and capacity guardrails.
- `PrivateNoteService` handles unlock and PIN-change workflows.
- `error_mapping.py` provides stable user-safe error mapping for UI and API responses.

### 4.3 Data/Security Tier

- `SqlNoteRepository` persists notes in SQLite and handles transactional CRUD/restore/purge operations.
- `CryptoService` encrypts note title/body payloads and derives keys with PBKDF2-HMAC-SHA256.
- `UnlockSessionManager` enforces unlock timeout, failed-attempt throttling, and lockout backoff in memory.
- `PinSettingsManager` persists app-level PIN token metadata via config.
- `AuditLogger` writes append-only audit events (`audit-log.jsonl`).

### 4.4 Runtime/Startup Tier

- `ConfigService` validates supported keys and defaults.
- `AppStartup` ensures writable data directory and verifies store readability at startup.
- `AppLogger` writes diagnostic logs to rotating log file.

## 5. Data Design

### 5.1 Note Persistence Entity

SQLite `notes` table fields used by MVP:

- `note_id`,
- `title` (encrypted),
- `body` (encrypted),
- `is_private`,
- `pin_salt`,
- `is_deleted`,
- `created_at`,
- `updated_at`,
- `deleted_at`.

### 5.2 Supporting Runtime Data

- `audit-log.jsonl` for audit events.
- `astranote.log` for diagnostics.
- `config.json` for supported runtime configuration and PIN token metadata.

### 5.3 Data Integrity Behavior

- Duplicate-title-safe create/update with serialized title allocation.
- Soft delete retention with service-triggered purge after 15 days.
- Startup fail-fast if storage cannot be opened safely.

## 6. Security Design (MVP)

### 6.1 At-Rest Encryption

- Note title/body values are encrypted before persistence.
- Private-note encryption uses PIN-derived keying with per-note salt.
- Public note encryption uses master-secret-derived keying.

### 6.2 Private Note Access Controls

- Unlock required before private note content is shown.
- Unlock timeout defaults to 15 minutes of inactivity.
- Lockout begins after repeated failed attempts and backs off exponentially.
- Unlock/lockout state is process-memory scoped in MVP (resets on app restart).

### 6.3 Logging Privacy

- Audit logs exclude plaintext note content.
- Diagnostic logs are designed to avoid plaintext note body/title leakage.

## 7. Deployment Shape (MVP)

- Single FastAPI process.
- Local SQLite database in app data directory.
- Local browser access via localhost.
- No active account/session multi-user model in MVP runtime.

## 8. Post-MVP Boundaries

Deferred capabilities include:

- multi-user accounts and server-side authenticated sessions,
- non-local deployment hardening and transport-security rollout,
- expanded migration/version governance beyond current startup compatibility checks,
- mobile/hosted environment parity targets.

## 9. Risks and Maintenance Notes

- Documentation/diagram drift remains a risk when requirements change quickly.
- Encryption format compatibility must be preserved during future storage migrations.
- Any move to hosted deployment requires revisiting auth/session and transport assumptions.

## 10. Current Readiness Statement

The MVP is implemented and runnable for local single-user review. Core architecture and storage/security decisions are reflected in source and tests. Primary follow-up work is Post-MVP scope delivery and Lucid artifact refresh to mirror this baseline exactly.