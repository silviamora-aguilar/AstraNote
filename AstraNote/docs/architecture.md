# Architecture Overview

## MVP Baseline

AstraNotes is implemented as a local, single-user web application running on localhost (127.0.0.1). The delivered MVP uses a three-tier structure with clear boundaries between UI, service logic, and persistence/security components.

## Layer Overview

```
┌──────────────────────────────────────────┐
│              Web UI Layer                │
│  Browser client using Jinja2 + HTMX     │
└──────────────────────┬───────────────────┘
                       │ HTTP on localhost
┌──────────────────────▼───────────────────┐
│         FastAPI Route Layer              │
│  notes_ui.py (HTML) + notes_api.py (JSON)│
└──────────────────────┬───────────────────┘
                       │ service calls
┌──────────────────────▼───────────────────┐
│            Service Layer                 │
│ NoteService + PrivateNoteService +       │
│ route-level error mapping                │
└───────────────┬───────────────┬──────────┘
                │               │
┌───────────────▼────────────┐  │
│ Data Repository Layer      │  │
│ SqlNoteRepository (SQLite) │  │
└────────────────────────────┘  │
                                │
┌───────────────────────────────▼──────────┐
│ Security + Runtime Support Layer         │
│ CryptoService, UnlockSessionManager,     │
│ PinSettingsManager, AuditLogger,         │
│ ConfigService, AppStartup, AppLogger     │
└───────────────────────────────────────────┘
```

## Implemented Components

### Web/UI Layer

- Server-rendered pages and partial updates are handled through Jinja2 templates and HTMX.
- Route modules:
  - `src/app/api/notes_ui.py` for HTML/partial rendering flows.
  - `src/app/api/notes_api.py` for JSON API flows.

### Service Layer

- `NoteService` enforces note-domain rules (validation, duplicate-title suffixing, capacity limits, soft delete, restore, search, and purge behavior).
- `PrivateNoteService` coordinates unlock, lock, and PIN-management workflows.
- Structured route-level error mapping is handled via `src/app/api/error_mapping.py`.

### Data and Security Layer

- `SqlNoteRepository` is the active persistence backend in MVP.
- `CryptoService` encrypts title/body at rest using AES-GCM with PBKDF2-HMAC-SHA256-derived keys.
- `UnlockSessionManager` tracks unlock/lockout state in memory per note (session-scoped for the running process).
- `PinSettingsManager` persists app-level PIN token/version settings.
- `AuditLogger` writes append-only JSONL audit entries.

### Runtime Layer

- `ConfigService` validates runtime config keys and defaults.
- `AppStartup` verifies writable data directory and validates that the SQLite store can be opened before app use.
- `AppLogger` writes rotating diagnostic logs.

## Data Artifacts in MVP

| Artifact | Purpose |
|---|---|
| `astranote.db` | SQLite note persistence |
| `audit-log.jsonl` | Append-only audit events |
| `astranote.log` | Diagnostic runtime logs |
| `config.json` | Runtime config including supported keys and PIN token metadata |

## Dependency Rules (Current)

- UI routes call services, not repository or crypto internals directly.
- Services depend on repository and security gateways/interfaces.
- Repository and security components do not depend on UI template code.
- Shared providers in `src/app/dependencies.py` wire components for both API and UI routes.

## Explicit Post-MVP Items

The following are intentionally not part of the current MVP implementation baseline:

- Multi-user account model and server-side authenticated user sessions.
- Non-local transport hardening flows (beyond localhost exception).
- Shared cloud deployment topology.
