# Requirements

## Change Control Addendum (2026-05-04)

Course requirement update: AstraNotes must ship as a web-based multi-user application.

- Active delivery mode: browser-based client + server API + shared persistent store.
- Superseded assumption: single-user desktop-only runtime.
- Existing REQ/NFR/SRG/SMR IDs remain valid unless explicitly superseded below.

### New Web and Multi-User Requirements

- **WEB-01 [MVP]**: The system shall require authenticated user accounts for all note operations.
- **WEB-02 [MVP]**: All note reads/writes shall be scoped to the authenticated user identity; users shall not access other users' notes.
- **WEB-03 [MVP]**: The system shall expose HTTP JSON APIs for create, edit, delete, list, search, and restore operations.
- **WEB-04 [MVP]**: The web client shall consume only public API endpoints and shall not access storage/security internals directly.
- **WEB-05 [MVP]**: Session authentication shall expire after inactivity and require re-authentication.
- **WEB-06 [MVP]**: API endpoints shall enforce authorization checks server-side for every request.
- **WEB-07 [MVP]**: Server-side storage shall support concurrent multi-user access with transactional integrity.
- **WEB-08 [MVP]**: Deployment shall support at least one shared persistent environment for instructor/demo review.

### Authentication and Session Architecture Decisions (Locked)

- **WEB-09 [MVP]**: The system shall implement a persistent `User` account model stored in the database with mandatory fields: `user_id` (unique identifier), `email` (unique, for login), `password_hash` (bcrypt/Argon2 hash of login password), `created_at`, and `is_active` (boolean flag for account suspension). All note operations, sessions, and audit entries shall link back to `user_id` to enforce per-user data isolation.
- **WEB-10 [MVP]**: Session authentication shall use a database-backed server-side session store with the following behavior: (1) login creates a session record with `session_id`, `user_id`, `created_at`, `last_activity_at`, `expires_at`, `is_revoked`, `ip_address`, and `user_agent`; (2) logout invalidates only the current session; (3) idle timeout after 30 minutes of inactivity; (4) absolute maximum session lifetime of 7 days; (5) sessions are represented as secure HttpOnly cookies and checked on every authenticated request; (6) remember-me is not supported in v1. This strategy enables reliable logout, multi-device transparency, auditability, and forced re-authentication after expiration.
- **WEB-11 [MVP]**: Login authentication and private-note encryption shall use separate secrets derived by different cryptographic algorithms: (1) Login password is hashed with bcrypt or Argon2 for account authentication; (2) Private-note passphrase is a 4-digit numeric PIN (0000–9999) derived into an encryption key using PBKDF2-HMAC-SHA256 with a minimum iteration count of 100,000, a randomly generated 16-byte salt, and 256-bit output (per SRG-26); (3) Users can change their login password without invalidating encrypted notes; (4) Changing login password does not require re-encrypting note content because the passphrase is independent.

### Superseded / Reframed Items

- **NFR-06 to NFR-09** are reframed from local desktop measurements to server/API measurements.
- **NFR-10** is reframed from desktop keyboard-only to browser accessibility coverage.
- **NFR-11 / NFR-17 / NFR-18** remain non-blocking [Post-MVP] unless mobile web is explicitly required by the course rubric.

### Approved Implementation Profile (Pre-Scaffolding Decision Lock)

- Backend framework: FastAPI
- Frontend rendering: Jinja2 templates + HTMX partial updates
- Persistence: SQLite for course delivery with PostgreSQL-ready schema and migrations
- Authentication/session: server-side sessions with secure HttpOnly cookies and CSRF protection on write operations

## Functional Requirements

- Create, edit, delete notes.
- Support Markdown rendering.
- Browser-based access on modern desktop browsers.
- Multi-user account support with per-user data isolation.

## Non-Functional Requirements

- **Performance**: Fast load times for <100 notes.
- **Security**: Encrypt sensitive notes.
- **Scalability**: MVP with SQLite; PostgreSQL migration path retained.

## Original Non-Functional Requirements

1. The app shall support concurrent connections for 100 users.
2. The app shall support local create, update, and read operations in under 120 ms for fewer than 5,000 notes.
3. The app shall provide a modern UI with keyboard-first editing.
4. The architecture shall separate UI, security, and storage concerns so that independent quality assurance testing can be performed.

## Enhanced Non-Functional Requirements

### Concurrency and Reliability
- **NFR-01**: The system shall support 100 concurrently active user sessions in a single deployment instance.
- **NFR-02**: A session shall be counted as active when it issues at least one request every 10 seconds during a continuous 5-minute test window. The concurrency test workload shall be 70% read operations (list, search, open), 20% update operations (edit), and 10% create operations.
- **NFR-03**: Under NFR-02 workload and with a dataset of up to 5,000 notes, measured latency targets shall be p95 <= 120 ms for read operations, p95 <= 180 ms for create/update operations, and p99 <= 300 ms for all operations.
- **NFR-04**: When concurrent edits target the same note, the system shall enforce optimistic concurrency using a note version field. A stale write shall be rejected with a conflict response and shall not overwrite newer data.
- **NFR-05**: For load above 100 active sessions, the system may throttle new requests, but shall not corrupt stored notes. During NFR-02 test conditions, non-user-cancelled request failures shall be <= 1%.

### Web Operation Performance
- **NFR-06**: In web deployment mode, the system shall support a dataset of up to 5,000 notes per user account.
- **NFR-07**: With up to 5,000 notes for the active account, operation latency targets shall be p95 <= 120 ms for read operations (open, list, search), p95 <= 180 ms for create/update operations, and p99 <= 300 ms for all API operations measured at the service boundary.
- **NFR-08**: API latency measurements shall be recorded at the server service boundary from request entry to durable storage commit, excluding browser rendering time.
- **NFR-09**: For create and update API operations, successful completion shall guarantee durable persistence before success is returned.

### Keyboard-First UX
- **NFR-10**: On desktop web browsers, the UI shall support keyboard-only completion of core workflows: create note, open note, edit title/body, save, search, navigate note list, toggle checklist items, and delete with confirmation.
- **NFR-11 [Post-MVP]**: On mobile platforms, the same core workflows shall be completable using touch-only interaction without requiring a hardware keyboard.
- **NFR-12**: Every interactive control in core workflows shall be reachable by the primary input model of the platform (tab navigation on keyboard-capable platforms; touch interaction on mobile) and shall provide a clear visible active/focus indicator.
- **NFR-17 [Post-MVP]**: Interactive touch controls on mobile shall provide touch targets of at least 44x44 CSS pixels for primary actions in core workflows.
- **NFR-18 [Post-MVP]**: Any keyboard shortcut action on desktop shall have an equivalent accessible touch action on mobile.

### Architecture Separation and Testability
- **NFR-13**: The system shall enforce dependency boundaries that prevent direct coupling between UI and storage/security implementations, so that security and storage components can be replaced or tested independently without UI code changes.
- **NFR-14**: Storage and security capabilities shall be accessed through explicit interfaces that support test doubles, so UI and service logic can be tested without real file I/O or cryptographic backends.
- **NFR-15**: The system shall include automated tests that independently validate UI workflow logic, security policy enforcement, and storage persistence behavior.
- **NFR-16**: Replacing the storage backend implementation (for example, SQLite to PostgreSQL) shall not require changes to UI module code.

## Original Security, Reliability, and Governance Requirements

1. The system shall support per-note encryption.
2. Notes marked as private shall be encrypted at rest and in transit.
3. All note operations shall be logged for audit with user, action, timestamp, and delta.
4. Version and history immutable records shall include hashes.
5. The system shall support soft delete with 30-day retention by default.
6. The system shall handle invalid save, load, or delete operations gracefully and report clear errors instead of crashing.

## Enhanced Security, Reliability, and Governance Requirements

Scope tags: [MVP] = target for quarter delivery, [Post-MVP] = planned hardening after MVP.

### Data Protection
- **SRG-01 [MVP]**: All notes shall be encrypted at rest with authenticated encryption (AES-256-GCM or ChaCha20-Poly1305). At minimum, note title, note body, and note content versions shall be encrypted and shall never be written to persistent storage in plaintext; only minimal non-sensitive metadata required for indexing and lifecycle management may remain unencrypted.
- **SRG-02 [MVP]**: For notes marked as private, encryption at rest shall include title, body, and private-note content versions; only minimal non-sensitive metadata required for indexing and lifecycle management may remain unencrypted.
- **SRG-03 [Post-MVP]**: Each note shall be encrypted independently using a unique per-note data encryption key; compromise of one note key shall not expose plaintext of other notes.
- **SRG-04 [MVP]**: Any network transmission containing note content (including sync, backup, restore, and export/import APIs) shall use TLS 1.2 or higher; note content shall not be transmitted over unencrypted channels.
- **SRG-17 [MVP]**: No feature that transmits note content may be released unless SRG-04 transport encryption requirements are satisfied.

### Private Note Access Control
- **SRG-18 [MVP]**: Viewing or decrypting a private note shall require successful private-note unlock authentication using a user-defined app passphrase.
- **SRG-19 [MVP]**: Private note content shall remain hidden until unlock authentication succeeds; failed authentication shall not reveal any private title/body/version plaintext.
- **SRG-20 [MVP]**: Unlock authentication shall be required at least once per app session before any private note can be opened.
- **SRG-21 [MVP]**: After 15 minutes of inactivity, private-note unlock state shall expire and re-authentication shall be required.
- **SRG-22 [MVP]**: Failed unlock attempts shall return clear error messages, shall not crash the app, and shall apply rate limiting after 5 consecutive failures.
- **SRG-23 [MVP]**: After 5 consecutive failed unlock attempts within a single session, the private-note unlock mechanism shall enter a locked-out state for a minimum of 5 minutes. Each subsequent lockout period shall double (exponential backoff). The lockout state, attempt count, and expiry timestamp shall persist across app restarts.
- **SRG-24 [MVP]**: Unlock error responses shall be identical in content and timing regardless of whether the failure is caused by a wrong passphrase or an internal error, preventing enumeration of failure cause.

### Metadata Minimization
- **SRG-25 [MVP]**: The only fields permitted to remain unencrypted in local storage are: `note_id`, `created_at`, `updated_at`, `is_private` (boolean), `is_deleted` (boolean), and `deleted_at`. All other note fields—including `title`, `body`, and `version_content`—shall be encrypted at rest per SRG-01. Any future addition of a plaintext field requires explicit update to this allowlist in requirements before implementation.

### Key Management
- **SRG-26 [MVP]**: The encryption key used for private notes shall be derived from the user passphrase using PBKDF2-HMAC-SHA256 with a minimum iteration count of 260,000, a randomly generated 16-byte salt stored alongside the derived key material, and a 256-bit output key. The raw passphrase shall never be stored or logged. The derived key shall be held only in memory for the duration of the unlocked session.

### Auditability and Integrity
- **SRG-05 [MVP]**: Create, read, update, delete, restore, and export operations shall generate audit log entries containing actor identity, action type, note ID, UTC timestamp, operation outcome, and request correlation ID.
- **SRG-06 [Post-MVP]**: Audit logs shall be append-only and tamper-evident using SHA-256 hash chaining where each entry stores the hash of the previous entry.
- **SRG-07 [MVP]**: Audit entries shall not store plaintext private note content; change details shall be limited to metadata and content fingerprints.
- **SRG-08 [MVP]**: Note version history shall be immutable; updates shall create new version records and shall not modify prior stored versions.
- **SRG-09 [Post-MVP]**: Each stored note version shall include a SHA-256 content hash. Hash verification failures shall raise integrity errors, block further writes to affected records, and preserve existing data unchanged.

### Retention and Recovery
- **SRG-10 [MVP]**: Deleting a note shall perform a soft delete by default, retaining recoverable metadata and content for 30 calendar days.
- **SRG-11 [MVP]**: Soft-deleted notes shall be excluded from default list and search results, and shall be restorable only within the retention window.
- **SRG-12 [Post-MVP]**: At retention expiry, soft-deleted notes shall be permanently purged within 24 hours unless an explicit policy override is configured.
- **SRG-13 [MVP]**: Restore operations shall preserve original note ID, maintain version history continuity, and create an audit entry for restore action.

### Failure Handling
- **SRG-14 [MVP]**: Invalid save, load, or delete operations (including malformed input, missing records, permission denial, and integrity check failures) shall return structured errors with machine-readable codes and user-safe messages, and shall not crash the application.
- **SRG-15 [MVP]**: On failed save, load, delete, or restore operations, the system shall preserve pre-operation data state and prevent partial writes via atomic commit/rollback behavior.
- **SRG-16 [MVP]**: Repeated identical invalid requests shall produce consistent error codes and shall not create duplicate side effects in storage or audit logs.

## Serviceability and Manageability Requirements

Scope: All SMR requirements are [MVP] unless explicitly marked otherwise. These requirements govern the three-tier architecture (UI tier, Service/Business-Logic tier, Storage/Security tier) as an independently operable system.

### Diagnostic Logging
- **SMR-01 [MVP]**: The application shall write diagnostic (non-audit) log entries to a rotating log file located in the application data directory. Each log entry shall include: UTC timestamp, severity level (DEBUG / INFO / WARNING / ERROR), originating tier (UI / Service / Storage / Security), a correlation ID linking the entry to the triggering operation, and a message string. The log file shall rotate when it exceeds 5 MB, retaining the two most recent rotated files.
- **SMR-02 [MVP]**: The active log level shall be configurable in `config.json` under the key `log_level` (values: DEBUG, INFO, WARNING, ERROR). The default level shall be INFO. Changing the log level shall take effect without restarting the application.
- **SMR-03 [MVP]**: Log entries shall never contain plaintext note content (title, body, or private-note fields). Diagnostic context for note operations shall be limited to `note_id` and operation type.

### Error Propagation and Tier Accountability
- **SMR-04 [MVP]**: All errors originating in the Storage tier or Security tier shall be wrapped in a `ResultError` that includes a `source_tier` field (values: `storage`, `security`, `service`, `ui`) before being returned to the Service tier. The UI tier shall not receive raw storage or crypto exceptions.
- **SMR-05 [MVP]**: The UI tier shall render a user-safe error state for every `ResultError` it receives, without exposing machine-readable codes or stack traces to the user. The machine-readable code shall be available in the diagnostic log at WARNING or ERROR level.

### Startup Integrity and Data Directory Management
- **SMR-06 [MVP]**: On application startup, the application shall verify that the data directory exists and is writable. If the directory does not exist, the application shall create it with appropriate permissions before proceeding. If the directory is not writable, the application shall display a clear startup error and refuse to launch rather than operating in a partially functional state.
- **SMR-07 [MVP]**: On startup, the application shall verify that the primary persistence store is readable and structurally valid (SQLite file present/creatable and schema readable). If the store is unreadable or structurally invalid, the application shall log the error with ERROR severity, preserve the original artifact for recovery (`astranotes.db.corrupt.<UTC timestamp>`), initialize a fresh store, and display a user-visible warning.
- **SMR-08 [MVP]**: The storage schema shall include explicit migration/version tracking (for example, Alembic revision history). The application shall reject startup writes if stored schema version is higher than the application's supported version, logging the mismatch at ERROR severity and refusing to write.

### Configuration Management
- **SMR-09 [MVP]**: Application configuration shall be stored in `config.json` in the data directory. The application shall define a fixed set of supported configuration keys with documented defaults. Unknown keys in `config.json` shall be silently ignored (forward compatibility). Missing keys shall fall back to their documented defaults (backward compatibility). Config values shall be validated on load; invalid values shall fall back to defaults and log a WARNING.
- **SMR-10 [MVP]**: The following configuration keys shall be supported at MVP: `log_level` (default: "INFO"), `data_dir` (default: platform-appropriate app data directory), `inactivity_timeout_minutes` (default: 15, maps to SRG-21), `max_notes` (default: 10000, maps to REQ-23).

### Application Identity and Graceful Shutdown
- **SMR-11 [MVP]**: The application shall embed a version string (semantic version, e.g., "1.0.0") accessible at runtime. The version shall be displayed in an About or Help surface in the UI. The version shall also be written to the startup diagnostic log at INFO level.
- **SMR-12 [MVP]**: On graceful shutdown (user closes app, OS signals clean exit), any in-progress storage write shall be allowed to complete before the process exits. The application shall not terminate mid-write in response to a graceful shutdown signal.

## MVP Specs

- Basic CRUD operations.
- JSON file storage.
- No sync initially.

## Original Early-Stage Requirements

1. The app shall allow the user to create a text note with title and body.
2. The app shall allow the user to edit the title and body of an existing note.
3. The app shall allow the user to delete a note, with a confirmation prompt.
4. The app shall display a list of all notes, showing titles and creation dates.
5. The app shall allow the user to search notes by title or body content.
6. The app shall allow users to create lists like bullets or checkbox list.
7. The app shall allow users to control text formatting: bold, underline, italicize.
8. The app shall allow each user to create up to 10,000 notes/files.
9. The app shall allow a user to mark a note as private.

## Enhanced Early-Stage Requirements

### Create Note
- **REQ-01**: The app shall allow the user to create a note with a required title and an optional body.
- **REQ-02**: The note title shall accept Unicode letters, numbers, spaces, and common punctuation (. , - ' "), and shall reject symbols (@ # $ % &) and newlines. Title length shall be 1–255 characters. Body length shall be 0–10,000 characters.
- **REQ-03**: If the entered title already exists, the app shall auto-assign the next available numeric suffix (Title, Title1, Title2, ...).
- **REQ-04**: Each created note shall be assigned a unique ID and creation timestamp, and persisted to server-side storage.

### Edit Note
- **REQ-05**: The app shall allow the user to edit the title and/or body of an existing note.
- **REQ-06**: The edited title shall follow the same validation rules as REQ-02 (required, max 255, Unicode-friendly, no symbols/newlines). Body shall remain optional, max 10,000 characters.
- **REQ-07**: If the edited title conflicts with another existing note, the app shall auto-assign the next available numeric suffix, excluding the current note from the duplicate check.
- **REQ-08**: On successful save, the note shall retain its original ID and created_at timestamp, update its updated_at timestamp, and persist changes to server-side storage.

### Delete Note
- **REQ-09**: The app shall require the user to confirm deletion before a note is removed. The confirmation prompt shall display the note title and state that the action is permanent and cannot be undone.
- **REQ-10**: Upon confirmation, the app shall permanently remove the note from storage atomically. If the delete operation fails, the note shall remain intact and the user shall receive an error message.
- **REQ-11**: After a note is deleted, the app shall update the notes list immediately and display an empty state if no notes remain.

### List Notes
- **REQ-12**: The app shall display all notes in a scrollable list ordered by creation date (newest first), showing each note's title (truncated at 60 characters with ellipsis if longer) and creation date formatted as Month DD, YYYY.
- **REQ-13**: When no notes exist, the app shall display an empty state message prompting the user to create their first note.
- **REQ-14**: The notes list shall refresh automatically after any create, edit, or delete operation to reflect the current state of storage.

### Search Notes
- **REQ-15**: The app shall allow the user to filter notes by entering a query that matches against note titles and body content, case-insensitively. Minimum query length is 1 non-whitespace character. Special characters in the search query are treated as literal text and do not cause errors.
- **REQ-16**: The app shall handle empty, whitespace-only, and no-result search inputs by displaying specific feedback messages in place of the notes list, with no errors or crashes occurring.

### Lists in Notes
- **REQ-17**: The app shall allow the user to create and edit unordered bullet lists and checkbox lists inside the note body.
- **REQ-18**: List content shall be persisted in note storage and rendered consistently after save, close, and reopen. Nested lists deeper than 2 levels are not required for MVP.
- **REQ-19**: The app shall allow the user to toggle checkbox list items between checked and unchecked states, and persist each state change immediately.

### Text Formatting
- **REQ-20**: The app shall allow the user to apply bold, italic, and underline formatting to selected text in the note body.
- **REQ-21**: Formatting actions shall not modify note title content and shall preserve existing surrounding text without data loss when multiple formats are combined.
- **REQ-22**: Bold and italic shall be stored using Markdown-compatible markers, and underline shall be stored using a consistent format supported by the renderer.

### Note Capacity
- **REQ-23**: The app shall allow up to 10,000 notes in a single user data store.
- **REQ-24**: When note count is 10,000, create and duplicate-title-save operations that would add a new note shall be blocked, the existing data shall remain unchanged, and the app shall display: "Note limit reached (10,000). Delete notes to create a new one."

### Note Privacy
- **REQ-25**: The app shall allow the user to mark or unmark any note as private using a per-note toggle.
- **REQ-26**: Private status shall be persisted in storage and visually indicated in the notes list.
- **REQ-27**: Private notes shall hide body preview text in list and search results to prevent accidental on-screen disclosure.