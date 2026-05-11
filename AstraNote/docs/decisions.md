# Architectural Decisions

## GithubIssues + Project for management

- **Decision**: Github Issues + Github Project. 
- **Rationale**: Fast, easy, links to PR. Experience to be gained by using github.
- **Trade-offs**: Not as friendly for non-tehcnical people to access 
- **AI Prompt Influence**: Used AI to explore options and confirm github issues as starting point.
- **Alternatives considered**:Jira tracking (too much overhead for 1 person)

TODO: Create Github Project and link issues.

## JSON for MVP Storage

- **Decision**: Single `notes.json` file for all notes (not per-note files).
- **Rationale**: A single file simplifies atomic write semantics (write to temp → rename replaces the file atomically), avoids index/data split consistency problems, and aligns with the deployment diagram artifact `/data/notes.json` and the SRG-25 plaintext allowlist design. Per-note files with a separate `index.json` (as explored in `storage_design.md`) were rejected for MVP because two-file atomicity is harder to implement correctly without a database.
- **Storage shape**: `notes.json` is a JSON array of note objects. Only the SRG-25 allowlist fields (`note_id`, `created_at`, `updated_at`, `is_private`, `is_deleted`, `deleted_at`) are stored in plaintext; `title`, `body`, and `version_content` are always encrypted.
- **Trade-offs**: Entire file must be read/written on every operation — acceptable for ≤5,000 notes (NFR-06). For higher scale, replace `JsonNoteRepository` with a SQLite backend without changing `NoteService` or UI code (NFR-16).
- **AI Prompt Influence**: Used AI to explore options and confirm JSON as starting point.
- **Alternatives considered**: SQLite, ORM, Key-value store, Hybrid JSON + index, per-note file + index (see `storage_decision_map.md`)

## Persistence Backend

- **Decision**: SQLite for development and course delivery; PostgreSQL-ready schema design from day one.
- **Rationale**: SQLite requires zero installation and no separate server, eliminating infrastructure ramp-up time. Writing PostgreSQL-ready code (UUID keys, Alembic migrations, standard SQL column types via SQLAlchemy) means switching to PostgreSQL requires only a one-line connection string change — no model rewrites.
- **Architecture impact**: `SqlNoteRepository` uses SQLAlchemy ORM with Alembic for schema migrations. No raw SQL strings. All queries scoped by `owner_user_id` for multi-user isolation.
- **Trade-offs**: SQLite handles concurrent writes poorly at scale; acceptable for a course demo with a small number of users. PostgreSQL can be substituted before final demo if infrastructure signal matters for grading.
- **Alternatives considered**: PostgreSQL (production-grade but requires server setup and management overhead for a first project), MySQL (similar overhead to PostgreSQL, no advantage here), MongoDB (incompatible with SQLAlchemy and harder to model owned relationships).

## Course Pivot: Web-Based Multi-User Delivery

- **Decision**: Delivery target is now web-based multi-user architecture. Desktop-only assumptions are deprecated for scaffolding.
- **Rationale**: Updated course constraints require browser-accessible workflows and concurrent users in a shared deployment.
- **Architecture impact**: Keep three-tier boundaries, but swap desktop UI for Web UI + HTTP API boundary. All note operations must be authenticated and user-scoped.
- **Storage impact**: Prefer a server-side transactional backend (`SqlNoteRepository`) for multi-user correctness. Existing JSON design remains useful for local prototyping and tests.
- **Security impact**: Existing SRG requirements remain in force; add server-side authn/authz enforcement for every API request.
- **Trade-offs**: Slightly higher initial complexity (auth, API contracts, deployment), but aligns implementation with grading rubric and future extensibility.
- **Alternatives considered**: Keep desktop MVP and defer web migration (rejected due to rubric change).

## Backend Framework Selection

- **Decision**: Use FastAPI as the backend framework for the web multi-user MVP.
- **Rationale**: FastAPI provides built-in request/response validation, automatic OpenAPI docs for demo/review, and a clean API-first model that fits the three-tier architecture.
- **Architecture impact**: API handlers will remain thin and delegate to service-layer use cases; storage/security logic stays behind interfaces.
- **Trade-offs**: Slightly steeper learning curve than Flask and more initial structure, but better long-term maintainability and clearer contracts.
- **Alternatives considered**: Flask (simpler but more manual wiring), Django (feature-rich but heavier than needed for this MVP).

## Frontend Rendering Strategy

- **Decision**: Jinja2 server-side templates + HTMX for dynamic behavior.
- **Rationale**: Keeps the entire codebase in Python/HTML with no separate JavaScript framework. HTMX adds live search, instant updates, and dynamic interactions via HTML attributes — no JavaScript written by the developer. Produces a modern-feeling UI without the React/Vue learning overhead.
- **Architecture impact**: FastAPI serves both HTML pages (via Jinja2 `TemplateResponse`) and JSON endpoints. HTMX uses `hx-get`, `hx-post`, `hx-target` attributes to swap page fragments. No separate frontend build toolchain (no npm, no Node.js, no webpack).
- **Trade-offs**: Less portable than a pure API + SPA architecture; adding a native mobile app later would require adding JSON API endpoints alongside the template routes. Acceptable for course scope.
- **Alternatives considered**: React SPA (too high learning curve for a beginner in one quarter), vanilla JS sprinkles (viable but less expressive than HTMX for partial page updates), Django templates (would require switching backend framework).

## Authentication and Session Strategy

- **Decision**: Use server-side sessions with secure HttpOnly cookies.
- **Rationale**: Lowest implementation risk for a first web project while satisfying course security requirements. Sessions are revocable immediately, inactivity timeout is enforced centrally, and no sensitive identity payload is exposed to browser JavaScript.
- **Architecture impact**: Add `AuthService` and `SessionRepository` abstractions. The browser stores only a random session identifier cookie; authoritative session state lives server-side in the database and is checked on every authenticated request.
- **Security controls**: Enable `HttpOnly`, `Secure`, and `SameSite` cookie settings; enforce CSRF tokens for all state-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`); enforce server-side idle timeout (default 15 minutes) aligned with SRG-21.
- **Trade-offs**: Requires server-side session storage and lookup per request. Horizontal scale requires shared session storage (acceptable for course scope).
- **Alternatives considered**: JWT access tokens (more complex revocation/idle timeout behavior), OAuth-only third-party login (additional integration overhead).

## User Model

- **Decision**: Implement a real persistent `User` model stored in the database. Minimal fields: `user_id`, `email`, `password_hash`, `created_at`, `is_active`.
- **Rationale**: Essential for a multi-user web app. Enables repeat login/logout, note ownership across sessions, per-user audit trails, and session invalidation without deleting the user.
- **Architecture impact**: Add `User` table as the root entity. Link `Note.owner_user_id`, `Session.user_id`, and `AuditEntry.actor_user_id` back to `User`. All API endpoints enforce owner-scoped access.
- **Trade-offs**: Requires user signup/account management UI and database schema for user metadata. Minimal footprint for v1.
- **Alternatives considered**: Stateless single-user per browser (rejected — incompatible with course multi-user requirement), hard-coded users (rejected — no scalability or signup UX).

## Session Storage and Behavior

- **Decision**: Database-backed server-side sessions with the following behavior:
  - **Session storage**: `sessions` table with fields `session_id`, `user_id`, `created_at`, `last_activity_at`, `expires_at`, `is_revoked`, `ip_address`, `user_agent`.
  - **Logout scope**: Current session only. Logging out invalidates only the active browser session; other devices remain logged in.
  - **Idle timeout**: 30 minutes. After 30 minutes of inactivity, session expires and user must re-authenticate.
  - **Absolute max session lifetime**: 7 days. Even with constant activity, a session expires after 7 days and requires fresh login.
  - **Remember me**: Not in v1. Every login requires a password entry. Can be added in v2 if user research shows demand.
- **Rationale**: Database-backed sessions enable reliable logout, multi-device support, auditability, and forced expiration. Reasonable security defaults without over-complicating v1 scope.
- **Trade-offs**: Each session check requires a database query. Acceptable for course scope and single server. Can optimize with Redis caching before production scale.
- **Alternatives considered**: In-memory sessions (simplest but loses sessions on app restart), signed cookies (weaker logout semantics).

## Password Hashing vs. Note Passphrase Derivation

- **Decision**: Login password and private note passphrase are completely separate secrets.
  - **Login password**: Strong account credential, hashed with bcrypt or Argon2, enforced by account security policy (e.g., 12+ chars, complexity rules).
  - **Private note passphrase**: 4-digit numerical PIN (0000–9999), derived into an encryption key with PBKDF2-HMAC-SHA256 (100,000+ iterations, SHA256).
- **Rationale**: 
  - Separates account security from note encryption strength. Login password controls account access; passphrase controls individual note locks.
  - 4-digit PIN is simple and memorable (users are familiar from ATMs, phone locks, etc.).
  - PBKDF2 with high iteration count derives a strong encryption key from the weak passphrase. A 4-digit PIN stretched to AES-256-GCM is no longer weak for the purpose of encrypting a single note.
  - Users can change login password without invalidating encrypted notes.
  - Allows weak per-note passphrases without weakening account security.
- **Architecture impact**: 
  - `User.password_hash` stores the bcrypt/Argon2 hash of the login password.
  - `SecureNote.passphrase_salt` and `SecureNote.ciphertext` store the salt and encrypted body. Passphrase is derived on unlock only; never stored plaintext or hashed.
  - `KeyDerivationService` uses PBKDF2-HMAC-SHA256 with 100,000+ iterations to derive AES-256-GCM key from the 4-digit PIN + salt.
- **Trade-offs**: Users manage two secrets, but they are radically different in mental load (account password vs. 4-digit PIN). The separation simplifies password rotation and future note-sharing features.
- **Security note**: A 4-digit space (10,000 possible values) is small, so the salt and high iteration count are critical. Never use these passphrases without a strong key derivation function.
- **Alternatives considered**: Single password for both (coupling security policies), no per-note encryption (weaker security baseline).