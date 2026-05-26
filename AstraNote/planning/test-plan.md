# Test Plan — AstraNotes MVP

**Version**: 1.0  
**Date**: 2026-05-11  
**Covers**: All MVP backlog items (BL-01–BL-13, BL-21, BL-22) mapped to REQ-01–27, NFR-01–18 (MVP-applicable), SRG MVP requirements, SMR-01–SMR-12, WEB-01–WEB-11

---

## 1. Test Strategy

### Guiding Principles
- Tests are organized by layer: unit tests validate a single component in isolation; integration tests validate two or more collaborating components; security tests validate cryptographic and access-control correctness.
- Each test layer maps back to at least one requirement.
- No test may depend on a real file system or real crypto backend to validate business logic (NFR-14).
- Tests must be runnable with `pytest` from the workspace root.

### Test Layers

| Layer | What It Tests | Doubles Used | Requirement |
|---|---|---|---|
| Unit — Service | NoteService business rules | Fake in-memory NoteRepository | NFR-14, NFR-15 |
| Unit — Repository | SqlNoteRepository persistence (SQLite) | Real temp SQLite DB file (pytest tmp_path) | NFR-15 |
| Unit — Security | KeyDerivationService, UnlockSessionManager, SecureNote | None (crypto correctness tested directly) | SRG-26, SRG-22–24 |
| Integration | Full request flows end-to-end through service + real repo | Real temp SQLite DB | NFR-15 |
| Security validation | Plaintext allowlist, lockout persistence, anti-enumeration | Real temp files | SRG-01, SRG-19, SRG-23, SRG-24, SRG-25 |
| Performance | API latency at 100 / 1,000 / 5,000 notes per account | Real temp SQLite DB | NFR-06, NFR-07, NFR-08, NFR-09 |

---

## 2. Unit Tests — NoteService (with Fake Repository)

### TP-U01 — Create note: valid input
- **Requirement**: REQ-01, REQ-04
- **Input**: title="Meeting Notes", body="Agenda items"
- **Expected**: Note saved with unique note_id, correct created_at, note appears in list

### TP-U02 — Create note: title validation rejects symbols
- **Requirement**: REQ-02
- **Input**: title="Note@Title"
- **Expected**: Returns VALIDATION_ERROR, no note created

### TP-U03 — Create note: title empty after trim
- **Requirement**: REQ-02
- **Status**: ✅ Implemented (`test_create_note_rejects_empty_title_after_trim`)
- **Input**: title="   "
- **Expected**: Returns VALIDATION_ERROR

### TP-U04 — Create note: title exceeds 255 characters
- **Requirement**: REQ-02
- **Status**: ✅ Implemented (`test_create_note_rejects_title_above_max_length`)
- **Input**: title = "A" * 256
- **Expected**: Returns VALIDATION_ERROR

### TP-U05 — Create note: body exceeds 10,000 characters
- **Requirement**: REQ-02
- **Input**: body = "x" * 10001
- **Expected**: Returns VALIDATION_ERROR

### TP-U06 — Create note: duplicate title auto-suffix
- **Requirement**: REQ-03
- **Setup**: Note with title "Plan" already exists
- **Input**: title="Plan"
- **Expected**: New note saved with title "Plan1"

### TP-U07 — Create note: duplicate title suffix increments correctly
- **Requirement**: REQ-03
- **Setup**: Notes "Plan" and "Plan1" exist
- **Input**: title="Plan"
- **Expected**: New note saved as "Plan2"

### TP-U08 — Edit note: success, preserves note_id and created_at
- **Requirement**: REQ-05, REQ-08
- **Expected**: updated_at changes, note_id and created_at unchanged

### TP-U09 — Edit note: duplicate title excludes self
- **Requirement**: REQ-07
- **Setup**: Only note "Work" exists
- **Input**: Edit "Work" → title stays "Work"
- **Expected**: Save succeeds with same title, no suffix added

### TP-U10 — Edit note: duplicate title with other note
- **Requirement**: REQ-07
- **Setup**: "Work" and "Work1" exist; editing a third note to "Work"
- **Expected**: Saved as "Work2"

### TP-U10b — Edit note: rejects empty title after trim
- **Requirement**: REQ-06
- **Status**: ✅ Implemented (`test_update_note_rejects_empty_title_after_trim`)
- **Input**: Edit existing note with title="   "
- **Expected**: Returns VALIDATION_ERROR, note not changed

### TP-U10c — Edit note: rejects title above 255 characters
- **Requirement**: REQ-06
- **Status**: ✅ Implemented (`test_update_note_rejects_title_above_max_length`)
- **Input**: Edit existing note with title = "A" * 256
- **Expected**: Returns VALIDATION_ERROR, note not changed

### TP-U11 — Delete note: soft delete sets is_deleted and deleted_at
- **Requirement**: REQ-09, REQ-10, SRG-10
- **Expected**: Note is_deleted=True, deleted_at set, note excluded from list() and search()

### TP-U12 — Delete note: soft-deleted note excluded from list
- **Requirement**: REQ-11, SRG-11
- **Expected**: list() returns only non-deleted notes

### TP-U13 — Delete note: soft-deleted note excluded from search
- **Requirement**: REQ-11, SRG-11
- **Expected**: search() returns only non-deleted notes

### TP-U14 — List notes: sorted newest first
- **Requirement**: REQ-12
- **Status**: ✅ Implemented
- **Expected**: Notes returned in created_at descending order

### TP-U15 — List notes: empty list returns empty result
- **Requirement**: REQ-13
- **Status**: ✅ Implemented
- **Expected**: list() returns empty list (not error)

### TP-U16 — List notes: refreshes after create/edit/delete
- **Requirement**: REQ-14
- **Status**: ✅ Implemented
- **Expected**: Each mutation is immediately visible in next list() call

### TP-U17 — Search: case-insensitive match on title
- **Requirement**: REQ-15
- **Input**: query="meeting", note title="Meeting Notes"
- **Expected**: Note returned

### TP-U18 — Search: case-insensitive match on body
- **Requirement**: REQ-15
- **Expected**: Match found in body content

### TP-U19 — Search: special characters treated as literal
- **Requirement**: REQ-15
- **Input**: query="note@work"
- **Expected**: No error, returns matching notes or empty list

### TP-U20 — Search: whitespace-only query returns full list
- **Requirement**: REQ-16
- **Input**: query="   "
- **Expected**: Full note list returned (same as no search filter)

### TP-U21 — Search: no results returns empty list
- **Requirement**: REQ-16
- **Expected**: Empty list, no error

### TP-U22 — Capacity: create blocked at 10,000 notes
- **Requirement**: REQ-23, REQ-24
- **Setup**: 10,000 notes exist
- **Expected**: Returns CAPACITY_EXCEEDED, no note created

### TP-U23 — Capacity: duplicate-title suffix blocked at limit
- **Requirement**: REQ-24
- **Setup**: 10,000 notes, title "Plan" already exists
- **Input**: title="Plan"
- **Expected**: Returns CAPACITY_EXCEEDED (suffix would add a note)

### TP-U24 — Restore: within window restores note
- **Requirement**: SRG-13
- **Setup**: Note soft-deleted, deleted_at < 30 days ago
- **Expected**: is_deleted=False, audit entry created, note visible in list

### TP-U25 — Restore: outside window rejected
- **Requirement**: SRG-11, SRG-13
- **Setup**: deleted_at > 30 days ago
- **Expected**: Returns error, note remains inaccessible

---

## 3. Unit Tests — User Account and Authentication

### TP-A01 — User signup: valid email and password hash
- **Requirement**: WEB-09
- **Input**: email="user@example.com", password="Str0ng!Pass"
- **Expected**: User created with unique user_id, email, password_hash (bcrypt), created_at, is_active=True

### TP-A02 — User signup: duplicate email rejected
- **Requirement**: WEB-09
- **Setup**: User with email="user@example.com" exists
- **Input**: Try to create another user with same email
- **Expected**: Returns EMAIL_DUPLICATE error, no user created

### TP-A03 — User login: valid password
- **Requirement**: WEB-09, WEB-10
- **Setup**: User exists with password_hash of "MyPassword123"
- **Input**: Login attempt with password="MyPassword123"
- **Expected**: Session created, secure HttpOnly cookie returned

### TP-A04 — User login: invalid password rejected
- **Requirement**: WEB-09
- **Input**: Password does not match stored hash
- **Expected**: Returns AUTH_FAIL, no session created

### TP-A05 — Session creation: stores user_id, created_at, expires_at
- **Requirement**: WEB-10
- **Expected**: Session record has session_id (unique), user_id, created_at, last_activity_at, expires_at (30 days in future), is_revoked=False, ip_address, user_agent

### TP-A06 — Session logout: current session marked revoked
- **Requirement**: WEB-10
- **Setup**: User has active session
- **Input**: Logout request
- **Expected**: Session marked is_revoked=True, cookie invalidated, user must log in again

### TP-A07 — Session logout: other sessions remain active
- **Requirement**: WEB-10
- **Setup**: User has two active sessions (two browsers)
- **Input**: Logout from session A
- **Expected**: Session A is revoked; session B remains active and usable

### TP-A08 — Session idle timeout: 30 minutes
- **Requirement**: WEB-10
- **Setup**: Session with last_activity_at = 31 minutes ago
- **Input**: Authenticated request with that session
- **Expected**: Session expired, request rejected, user must log in again

### TP-A09 — Session absolute timeout: 7 days
- **Requirement**: WEB-10
- **Setup**: Session with created_at = 7 days + 1 minute ago, but last_activity_at < 30 minutes ago
- **Input**: Authenticated request
- **Expected**: Session expired, user must log in again

### TP-A10 — Passphrase unlock: valid 4-digit PIN
- **Requirement**: WEB-11, SRG-26
- **Setup**: Private note with passphrase_salt and encrypted body
- **Input**: Unlock attempt with passphrase="1234"
- **Expected**: Passphrase derived via PBKDF2-HMAC-SHA256 (≥100,000 iterations), key matches encrypted body, unlock succeeds

### TP-A11 — Passphrase unlock: invalid PIN rejected
- **Requirement**: WEB-11
- **Input**: Unlock with passphrase="0000" when correct is "1234"
- **Expected**: Decryption fails, unlock rejected without revealing plaintext

### TP-A12 — Passphrase 4-digit format enforced
- **Requirement**: WEB-11
- **Input**: Passphrase="12345" (5 digits) or "abc" (non-numeric)
- **Expected**: Returns INVALID_PASSPHRASE_FORMAT

### TP-A13 — Password change: does not require re-encrypting notes
- **Requirement**: WEB-11
- **Setup**: User has private notes encrypted with passphrase_salt and ciphertext
- **Input**: Change login password, then decrypt a private note with same passphrase
- **Expected**: Private note decrypts successfully; encrypted content and salt unchanged

### TP-A14 — Session cookie is HttpOnly and Secure
- **Requirement**: WEB-10
- **Expected**: Cookie set with HttpOnly=True, Secure=True, SameSite=Strict

---

### TP-U26 — Restore: preserves note_id and version history
- **Requirement**: SRG-13
- **Expected**: note_id unchanged after restore

### TP-U27 — Error handling: save failure does not corrupt state
- **Requirement**: SRG-14, SRG-15
- **Setup**: Fake repo raises save error
- **Expected**: ResultError returned, no partial state change

### TP-U28 — Error handling: repeated invalid requests return consistent code
- **Requirement**: SRG-16
- **Expected**: Same error code on each retry

### TP-U29 — Audit: create generates audit entry with required fields
- **Requirement**: SRG-05
- **Expected**: AuditEntry has actor, action, note_id, UTC timestamp, outcome, correlation_id

### TP-U30 — Audit: private note content absent from audit entry
- **Requirement**: SRG-07
- **Expected**: AuditEntry does not contain plaintext title or body

### TP-U31 — Optimistic concurrency: stale version rejected
- **Requirement**: NFR-04
- **Setup**: Note at version N, edit submitted with version N-1
- **Expected**: Returns STALE_VERSION, note content unchanged

---

## 3. Unit Tests — SqlNoteRepository (SQLite)

### TP-R01 — Save and retrieve round-trip
- **Expected**: Saved note recoverable with all fields intact via get()

### TP-R02 — Transactional write atomicity
- **Expected**: database transaction is not partially committed if process interrupted during write

### TP-R03 — SRG-25 plaintext allowlist enforced in storage
- **Requirement**: SRG-25
- **Expected**: Stored records do not expose plaintext `title`, `body`, or `version_content`

### TP-R04 — list() excludes soft-deleted notes
- **Requirement**: SRG-11
- **Expected**: Only active notes returned from repository query

### TP-R05 — restore() within retention window
- **Expected**: Note restored, deleted_at cleared or preserved, is_deleted=False

### TP-R06 — Failed write leaves file unchanged
- **Requirement**: SRG-15
- **Expected**: Pre-op data remains unchanged on write failure

---

## 4. Unit Tests — Security Layer

### TP-S01 — KeyDerivationService: deterministic for same passphrase + salt
- **Requirement**: SRG-26
- **Expected**: Same passphrase + salt always produces same 256-bit key

### TP-S02 — KeyDerivationService: different salt produces different key
- **Expected**: Key changes when salt changes (passphrase same)

### TP-S03 — KeyDerivationService: raw passphrase not in returned output
- **Expected**: Returned object has no passphrase attribute

### TP-S04 — SecureNote: encrypt then decrypt returns original plaintext
- **Requirement**: SRG-01
- **Expected**: Round-trip restores title and body exactly

### TP-S05 — SecureNote: ciphertext is not plaintext
- **Expected**: Encrypted bytes do not contain raw title or body string

### TP-S06 — UnlockSessionManager: first access requires authentication
- **Requirement**: SRG-20
- **Expected**: is_unlocked() returns False before authentication

### TP-S07 — UnlockSessionManager: correct passphrase unlocks session
- **Requirement**: SRG-18
- **Expected**: is_unlocked() returns True after authenticate() with correct passphrase

### TP-S08 — UnlockSessionManager: wrong passphrase denied
- **Requirement**: SRG-18, SRG-19
- **Expected**: authenticate() returns failure; is_unlocked() stays False

### TP-S09 — UnlockSessionManager: session expires after 15 min inactivity
- **Requirement**: SRG-21
- **Setup**: Advance clock by 16 minutes without activity
- **Expected**: is_unlocked() returns False; next access re-prompts

### TP-S10 — UnlockSessionManager: 5 failures trigger lockout
- **Requirement**: SRG-22, SRG-23
- **Expected**: After 5 failures, unlock returns lockout error with remaining time

### TP-S11 — UnlockSessionManager: lockout doubles on subsequent lockout
- **Requirement**: SRG-23
- **Expected**: First lockout 5 min, second 10 min, third 20 min

### TP-S12 — UnlockSessionManager: lockout persists across simulated restart
- **Requirement**: SRG-23
- **Setup**: Write security-state.json with active lockout, instantiate new UnlockSessionManager
- **Expected**: Lockout still active, expiry matches stored timestamp

### TP-S13 — Anti-enumeration: wrong passphrase and internal error return identical message
- **Requirement**: SRG-24
- **Expected**: Error message strings are identical for both failure types

### TP-S14 — Private note content hidden before authentication
- **Requirement**: SRG-19
- **Expected**: SecureNote.get_content() raises or returns None if session not unlocked

---

## 5. Integration Tests

### TP-I01 — Full create → list → open → edit → list round-trip
- **Expected**: Note visible after create; edit persists; updated_at reflects change

### TP-I02 — Full create → soft delete → list excludes note → restore → list includes note
- **Expected**: Soft delete works end-to-end with correct audit entries at each step

### TP-I03 — Search finds note by title after create
- **Expected**: Created note discoverable via title text search

### TP-I04 — Search finds note by body after create
- **Expected**: Created note discoverable via body text search

### TP-I05 — Private note: encrypted at rest, hidden in list/search, accessible after unlock
- **Requirement**: SRG-01, SRG-02, REQ-27, SRG-18
- **Expected**: At-rest storage has no plaintext title/body; list/search suppresses preview; unlock + open succeeds

### TP-I06 — Audit log entries written for create, update, delete, restore
- **Requirement**: SRG-05
- **Expected**: audit-log.jsonl has one entry per operation with required fields

### TP-I07 — Concurrent edit conflict: stale version rejected end-to-end
- **Requirement**: NFR-04
- **Expected**: STALE_VERSION returned; winning version preserved intact

---

## 6. Security Validation Tests

### TP-SV01 — Storage plaintext allowlist: no sensitive fields unencrypted
- **Requirement**: SRG-25
- **Method**: Write a note, inspect raw persisted record, assert sensitive fields are encrypted-at-rest

### TP-SV02 — Audit log contains no plaintext private note content
- **Requirement**: SRG-07
- **Method**: Create + edit private note, parse audit-log.jsonl, assert no note body text present

### TP-SV03 — Lockout state survives process restart
- **Requirement**: SRG-23
- **Method**: Trigger lockout, reinitialize manager from security-state.json, assert still locked

### TP-SV04 — Unlock error messages identical for wrong passphrase vs. internal error
- **Requirement**: SRG-24
- **Method**: Compare error message strings for both failure types

### TP-SV05 — Raw passphrase not present in any persisted file
- **Requirement**: SRG-26
- **Method**: After passphrase setup, grep all data files for passphrase string

---

## 7. Performance Tests

### TP-P01 — Read p95 ≤ 120 ms at 5,000 notes
- **Requirement**: NFR-07
- **Method**: Load 5,000-note dataset; measure list() latency over 100 iterations at service boundary

### TP-P02 — Write p95 ≤ 180 ms at 5,000 notes
- **Requirement**: NFR-07
- **Method**: Measure create() latency over 100 iterations, dataset at 5,000 notes

### TP-P03 — p99 ≤ 300 ms for all operations at 5,000 notes
- **Requirement**: NFR-07

### TP-P04 — Latency measured at service boundary, excluding UI render
- **Requirement**: NFR-08
- **Method**: Timer wraps only service call; UI component (if any) excluded

### TP-P05 — Durable write: success returned only after storage commit
- **Requirement**: NFR-09
- **Method**: After successful save, verify record committed in SQLite before asserting success

---

## 8. Requirement → Test Coverage Map

| Requirement | Tests |
|---|---|
| REQ-01 | TP-U01 |
| REQ-02 | TP-U02, TP-U03, TP-U04, TP-U05 |
| REQ-03 | TP-U06, TP-U07 |
| REQ-04 | TP-U01, TP-R01 |
| REQ-05 | TP-U08 |
| REQ-06 | TP-U08 (validation same as REQ-02) |
| REQ-07 | TP-U09, TP-U10 |
| REQ-08 | TP-U08, TP-I01 |
| REQ-09 | Sprint 2 UI test |
| REQ-10 | TP-U27 |
| REQ-11 | TP-U11, TP-I02 |
| REQ-12 | TP-U14 |
| REQ-13 | TP-U15 |
| REQ-14 | TP-U16, TP-I01 |
| REQ-15 | TP-U17, TP-U18, TP-U19 |
| REQ-16 | TP-U20, TP-U21 |
| REQ-17–19 | Sprint 2 tests |
| REQ-20–22 | Sprint 2 tests |
| REQ-23 | TP-U22 |
| REQ-24 | TP-U22, TP-U23 |
| REQ-25–27 | Sprint 2 + TP-I05 |
| NFR-04 | TP-U31, TP-I07 |
| NFR-06 | TP-P01 |
| NFR-07 | TP-P01, TP-P02, TP-P03 |
| NFR-08 | TP-P04 |
| NFR-09 | TP-P05 |
| NFR-13 | Architecture boundary check (S1-25) |
| NFR-14 | All unit tests use test doubles |
| NFR-15 | Existence of unit + integration + security test suites |
| NFR-16 | Fake repo swapped in all unit tests without service changes |
| SRG-01 | TP-S04, TP-S05, TP-SV01 |
| SRG-02 | TP-I05, TP-SV01 |
| SRG-05 | TP-U29, TP-I06 |
| SRG-07 | TP-U30, TP-SV02 |
| SRG-08 | TP-U08 (version record immutability) |
| SRG-10 | TP-U11 |
| SRG-11 | TP-U12, TP-U13, TP-I02 |
| SRG-13 | TP-U24, TP-U25, TP-U26, TP-I02 |
| SRG-14 | TP-U27 |
| SRG-15 | TP-U27, TP-R06 |
| SRG-16 | TP-U28 |
| SRG-18 | TP-S07, TP-S08 |
| SRG-19 | TP-S08, TP-S14 |
| SRG-20 | TP-S06 |
| SRG-21 | TP-S09 |
| SRG-22 | TP-S10 |
| SRG-23 | TP-S10, TP-S11, TP-S12, TP-SV03 |
| SRG-24 | TP-S13, TP-SV04 |
| SRG-25 | TP-R03, TP-SV01 |
| SRG-26 | TP-S01, TP-S02, TP-S03, TP-SV05 |
| SMR-01 | TP-M01, TP-M02 |
| SMR-02 | TP-M03 |
| SMR-03 | TP-M04 |
| SMR-04 | TP-M05 |
| SMR-05 | TP-M06 |
| SMR-06 | TP-M07 |
| SMR-07 | TP-M08, TP-M09 |
| SMR-08 | TP-M10 |
| SMR-09 | TP-M11, TP-M12 |
| SMR-10 | TP-M13 |
| SMR-11 | TP-M14 |
| SMR-12 | TP-M15 |
| WEB-01 | TP-W01, TP-W02 |
| WEB-02 | TP-W03, TP-W04 |
| WEB-03 | TP-W05 |
| WEB-04 | TP-W06 |
| WEB-05 | TP-W07 |
| WEB-06 | TP-W03, TP-W04 |
| WEB-07 | TP-W08 |
| WEB-08 | TP-W09 |
| WEB-09 | TP-A01, TP-A02, TP-A03, TP-A04 |
| WEB-10 | TP-A05, TP-A06, TP-A07, TP-A08, TP-A09, TP-A14 |
| WEB-11 | TP-A10, TP-A11, TP-A12, TP-A13 |

---

## 9. Serviceability and Manageability Tests

### TP-M01 — Diagnostic log written with all required fields
- **Requirement**: SMR-01
- **Expected**: After any note operation, log file contains an entry with UTC timestamp, severity, tier name, correlation ID, and message string

### TP-M02 — Log file rotates at 5 MB; retains two prior files
- **Requirement**: SMR-01
- **Method**: Write log entries until file exceeds 5 MB; verify rotation and file count ≤ 3 (current + 2 rotated)

### TP-M03 — Log level change in config.json takes effect without restart
- **Requirement**: SMR-02
- **Method**: Set log_level=DEBUG in config.json; perform operation; verify DEBUG entries appear; set log_level=ERROR; verify DEBUG entries no longer appear
- **Expected**: Level change respected without app restart

### TP-M04 — Log entries contain no note plaintext
- **Requirement**: SMR-03
- **Method**: Create a note with a distinctive title and body; grep log file for title and body text
- **Expected**: No title or body text present in any log entry

### TP-M05 — Storage tier error wrapped in ResultError with source_tier
- **Requirement**: SMR-04
- **Setup**: Inject storage failure
- **Expected**: Service layer receives ResultError with source_tier="storage"; no raw exception propagates to UI

### TP-M06 — UI displays user-safe message for ResultError; no code/traceback shown
- **Requirement**: SMR-05
- **Method**: Trigger a SAVE_ERROR; inspect UI error display
- **Expected**: User sees a friendly message; no machine-readable code or stack trace in user-facing output

### TP-M07 — Startup creates data directory if absent
- **Requirement**: SMR-06
- **Method**: Remove data directory; start app
- **Expected**: Data directory created; app launches normally; creation logged at INFO

### TP-M08 — Startup with valid SQLite store proceeds normally
- **Requirement**: SMR-07
- **Expected**: No warnings or recovery actions; notes loaded correctly

### TP-M09 — Startup with corrupt SQLite store renames artifact and initializes fresh
- **Requirement**: SMR-07
- **Method**: Corrupt the SQLite store file; start app
- **Expected**: Corrupt file renamed to `astranotes.db.corrupt.<timestamp>`; fresh store initialized; user-visible warning displayed; error logged

### TP-M10 — App refuses write when stored migration version > app-supported version
- **Requirement**: SMR-08
- **Method**: Simulate newer migration revision in store metadata; attempt a create operation
- **Expected**: Write blocked; ERROR logged with version mismatch detail; existing data unchanged

### TP-M11 — Unknown config keys in config.json are silently ignored
- **Requirement**: SMR-09
- **Method**: Add `unknown_key: "foo"` to config.json; start app
- **Expected**: App starts normally; no error; unknown key not used

### TP-M12 — Missing config key uses documented default
- **Requirement**: SMR-09
- **Method**: Remove `log_level` from config.json; start app
- **Expected**: Log level defaults to INFO; no error

### TP-M13 — All four SMR-10 config keys applied at runtime
- **Requirement**: SMR-10
- **Method**: Set each of log_level, data_dir, inactivity_timeout_minutes, max_notes to non-default valid values; verify each takes effect
- **Expected**: log_level changes log verbosity; inactivity_timeout_minutes controls session expiry; max_notes controls capacity limit

### TP-M14 — App version displayed in About UI and logged on startup
- **Requirement**: SMR-11
- **Expected**: Version string in semantic format (e.g., "1.0.0") visible in About surface and present in startup log at INFO level

### TP-M15 — Graceful shutdown waits for in-progress write to complete
- **Requirement**: SMR-12
- **Method**: Trigger a write operation; send graceful shutdown signal mid-write; verify DB transaction is not partially committed
- **Expected**: Write completes atomically before process exits; no corrupted or partially committed data after shutdown

---

## 10. Web and Multi-User Tests

### TP-W01 — Unauthenticated note access is blocked
- **Requirement**: WEB-01
- **Method**: Request protected note route without session cookie
- **Expected**: HTML routes redirect to sign-in; API routes return 401

### TP-W02 — Logout invalidates session immediately
- **Requirement**: WEB-01
- **Method**: Sign in, call logout, retry protected endpoint with old cookie
- **Expected**: Old session denied; user must re-authenticate

### TP-W03 — User cannot read another user's note by ID
- **Requirement**: WEB-02, WEB-06
- **Method**: Create note under User A; request same note ID under User B
- **Expected**: Access denied (404/403 with no ownership disclosure)

### TP-W04 — User cannot mutate another user's note
- **Requirement**: WEB-02, WEB-06
- **Method**: Attempt update/delete by non-owner account
- **Expected**: Mutation blocked; owner data unchanged

### TP-W05 — JSON API contract for core note operations
- **Requirement**: WEB-03
- **Method**: Validate create/edit/delete/list/search/restore endpoints return JSON payloads with stable fields and status codes
- **Expected**: All core operations available and contract-consistent

### TP-W06 — UI calls only API endpoints (no direct repository access)
- **Requirement**: WEB-04
- **Method**: Static architecture check on UI modules for forbidden imports (`repository`, `security` internals)
- **Expected**: No boundary violations

### TP-W07 — Session inactivity timeout requires re-authentication
- **Requirement**: WEB-05
- **Method**: Sign in, wait beyond configured timeout with no activity, call protected route
- **Expected**: Session rejected and re-auth required

### TP-W08 — Concurrent multi-user writes preserve transactional integrity
- **Requirement**: WEB-07
- **Method**: Run concurrent write workload across multiple accounts; force one failing transaction
- **Expected**: Successful writes commit cleanly; failed transaction rolls back with no partial records

### TP-W09 — Shared persistent deployment smoke test
- **Requirement**: WEB-08
- **Method**: Deploy to shared review environment; restart app/service; verify existing data persists and health endpoint responds
- **Expected**: Environment reachable by reviewer and data persists across restart
