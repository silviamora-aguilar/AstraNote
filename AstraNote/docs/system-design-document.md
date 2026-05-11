# System Design Document — AstraNotes

## 1. Purpose

This document captures the target system design for AstraNotes at the current approved baseline: web-based, multi-user, FastAPI backend, Jinja2 + HTMX frontend, SQLite persistence with PostgreSQL-ready migration discipline, and server-side sessions.

## 2. Design Scope

This design document covers:

- architecture structure,
- data design,
- security design,
- deployment shape,
- UML/document relationships,
- engineering risks,
- readiness implications before implementation.

## 3. Architecture Summary

AstraNotes uses a three-tier architecture:

- Web UI tier: Jinja2-rendered HTML with HTMX-driven dynamic updates
- API/Service tier: FastAPI route handlers and business services
- Data/Security tier: SQL-backed repository, audit/state persistence, encryption, unlock/session handling

This separation is required to preserve testability, ownership enforcement, and backend replaceability.

## 4. Runtime Architecture

### Web UI Tier
- Serves browser pages and partial UI fragments
- Uses HTMX to issue endpoint calls for search, note mutations, and partial page refreshes
- Does not import repository or crypto implementations directly

### API/Service Tier
- FastAPI route layer exposes protected endpoints
- AuthService resolves current authenticated user/session
- NoteService enforces validation, duplicate title rules, capacity limits, and ownership-aware note operations
- ResultError standardizes user-safe failures

### Data/Security Tier
- SqlNoteRepository stores notes, soft-delete state, audit records, user/session data, and security-state records
- KeyDerivationService derives keys for private-note protection
- SecureNote performs authenticated encryption/decryption for sensitive content
- UnlockSessionManager handles private-note unlock timeout and lockout logic

## 5. Data Design

### Core Entities

#### User
- user_id
- username/email
- password_hash
- created_at
- status flags

#### Session
- session_id
- user_id
- created_at
- last_active_at
- expires_at
- csrf_token / equivalent anti-forgery state

#### Note
- note_id
- owner_user_id
- title_encrypted
- body_encrypted
- is_private
- is_deleted
- created_at
- updated_at
- deleted_at
- version

#### AuditEntry
- audit_id
- actor_user_id
- action_type
- note_id
- timestamp_utc
- outcome
- correlation_id

#### SecurityState
- user_id or scoped unlock context
- failed_attempt_count
- lockout_expires_at
- inactivity_expires_at

### Persistence Strategy

- Use SQLite for course delivery and local development
- Use SQLAlchemy models and Alembic migrations from the start
- Keep schema PostgreSQL-ready through portable types and migration discipline
- Treat owner_user_id as mandatory for all note queries and mutations

## 6. Security Design

### Authentication and Session Management
- Server-side sessions with secure HttpOnly cookies
- SameSite configured conservatively
- CSRF protection on state-changing endpoints
- Idle timeout enforced server-side

### Authorization
- Every protected endpoint resolves authenticated identity first
- Every note access is scoped by owner_user_id
- Unauthorized access returns safe denial without leaking ownership information

### Private-Note Security
- Private note content encrypted at rest
- Passphrase-derived key material handled only in memory for unlock window
- Lockout and backoff persisted across restarts
- Wrong passphrase and internal failure paths return equivalent user-facing errors

### Logging and Audit
- Diagnostic logs exclude note plaintext
- Audit records exclude private note content and store only metadata/fingerprints

## 7. Deployment Shape

### MVP Deployment
- Single FastAPI application process
- Shared SQLite database / persistence artifact
- Shared persistent environment for instructor review
- Browser clients access one hosted application endpoint

### Future Deployment Path
- Replace SQLite with PostgreSQL without UI changes
- Add stronger environment isolation, external secret management, and cloud-native hosting later if required

## 8. UML and Design Artifact Relationship

The authoritative narrative design now lives across:

- [docs/architecture.md](./architecture.md)
- [docs/decisions.md](./decisions.md)
- this system design document

Lucid diagrams must be updated in a follow-up pass to reflect:

- AuthService and SessionRepository concepts
- SqlNoteRepository replacing desktop/local JSON assumptions
- Web UI to API boundary
- shared deployment node and persistent environment assumptions

## 9. Key Risks

### Delivery Risks
- New developer ramp-up on web architecture concepts
- scope expansion through UI polish or excessive framework work
- authentication/session bugs affecting milestone velocity

### Technical Risks
- inconsistent handling of owner_user_id across repository/service paths
- partial drift between planning docs and Lucid diagrams until diagram refresh is completed
- over-coupling template/UI logic to storage details

### Security Risks
- missing CSRF protection on HTMX write flows
- plaintext leakage into logs or audit paths
- weak session invalidation or inactivity enforcement

## 10. Engineering Readiness Summary

### Ready
- scope track selected and documented
- framework, frontend rendering, persistence, and auth/session decisions approved
- requirements, user stories, backlog, traceability, tests, sprint plans, release gates, and customer acceptance synchronized

### Still Pending Before Full Confidence
- Lucid diagrams need refresh to match the current baseline
- scaffolding has not yet been fully built around the approved architecture
- test suite files and implementation evidence still need to be created

## 11. Recommendation

The project is architecturally ready to begin development scaffolding. The most sensible next move is to scaffold around the approved decisions rather than reopening architecture choices. The only notable documentation follow-up still pending is Lucid diagram realignment.