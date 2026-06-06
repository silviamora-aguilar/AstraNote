# Architectural Decisions

## Local-First Single-User Web MVP

- **Decision**: The delivered baseline is a local, single-user browser app running on 127.0.0.1.
- **Rationale**: This keeps the MVP small enough to complete cleanly while still delivering a real web experience for course review.
- **Trade-offs**: Multi-user auth, sharing, and session management are intentionally deferred to Post-MVP.
- **Alternatives considered**: Multi-user delivery for the MVP, which was broader than the completed baseline.

## FastAPI Backend Framework

- **Decision**: Use FastAPI as the backend framework.
- **Rationale**: FastAPI keeps the route layer thin, provides validation, and fits the API + server-rendered UI split used by the project.
- **Architecture impact**: Request handling stays at the route layer while business logic remains in services and repositories.
- **Trade-offs**: More structure than a minimal Flask app, but clearer contracts and better maintainability.
- **Alternatives considered**: Flask and Django.

## Jinja2 + HTMX Rendering Strategy

- **Decision**: Use Jinja2 templates plus HTMX for dynamic behavior.
- **Rationale**: This keeps the front end in Python and HTML, avoids a separate SPA build chain, and supports interactive workflows without heavy JavaScript.
- **Architecture impact**: Server-rendered pages and partial updates share the same backend routes and view model.
- **Trade-offs**: Less decoupled than a pure API + SPA architecture, but much easier to finish and review within course scope.
- **Alternatives considered**: React SPA, vanilla JS, and a full Django template stack.

## SQLite Persistence for the MVP Baseline

- **Decision**: Use SQLite for local persistence in the delivered MVP.
- **Rationale**: SQLite is easy to run, easy to reset, and sufficient for the single-user baseline.
- **Architecture impact**: The repository layer owns atomic writes, soft delete state, and encrypted note payload storage.
- **Trade-offs**: SQLite is not the final answer for scale, but it is the correct answer for the local baseline.
- **Alternatives considered**: PostgreSQL and JSON-file storage.

## Private-Note Encryption and PIN Handling

- **Decision**: Private notes use a separate app-wide 4-digit PIN and encrypted-at-rest content.
- **Rationale**: The PIN is simple enough for the user to remember while still being protected by a strong key-derivation step.
- **Architecture impact**: The crypto layer derives the note key from the PIN and stores only the minimum allowed plaintext metadata.
- **Trade-offs**: The user manages one additional secret, but the model keeps private-note handling understandable and testable.
- **Alternatives considered**: Reusing the login password, or leaving private-note content unencrypted.

## Soft Delete and Trash Retention

- **Decision**: Deletion is soft-delete by default with a Trash view and 15-day retention.
- **Rationale**: The project needs safe recovery from accidental deletion and a clear audit trail.
- **Architecture impact**: Deleted notes retain minimal metadata and can be restored or purged through the service layer.
- **Trade-offs**: More state to manage than hard delete, but better user safety and better reviewability.
- **Alternatives considered**: Immediate hard delete.

## English/Spanish Interface Toggle

- **Decision**: The UI includes a translation toggle for interface text only.
- **Rationale**: This satisfies the localization requirement without changing user-authored note content.
- **Architecture impact**: Template keys and language state are handled at the presentation layer.
- **Trade-offs**: Limited to the core UI vocabulary, but sufficient for the MVP.
- **Alternatives considered**: Full content translation and browser language auto-detection.

## Deferred Post-MVP Decisions

- Multi-user accounts and ownership-scoped sessions remain deferred
- Per-note key isolation remains deferred
- Device sync and real-time collaboration remain deferred
- Mobile accessibility parity remains deferred
