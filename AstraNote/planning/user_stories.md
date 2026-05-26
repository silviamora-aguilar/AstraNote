# User Stories and Requirements

## Create Note

### REQ-01 — Basic Note Creation
**Requirement**: The app shall allow the user to create a note with a required title and an optional body.

**User Story**: As a user, I want to create a new note so that I can capture ideas quickly.

**Acceptance Criteria**:
- User can enter a title and optional body to create a note.
- Title is required; empty title is rejected with a validation message.
- Body may be empty.
- Saved note appears in the notes list immediately.

### REQ-02 — Title and Body Validation
**Requirement**: The note title shall accept Unicode letters, numbers, spaces, and common punctuation `. , - ' " @ # & : ; ! ? ( ) [ ] / + _`, and shall reject control characters, unsupported symbols, and newlines. Title length shall be 1–255 characters. Body length shall be 0–10,000 characters.

**User Story**: As a user, I want the app to validate my note title so that invalid characters are caught before saving.

**Acceptance Criteria**:
- Title accepts Unicode letters (any language), numbers, spaces, and `. , - ' " @ # & : ; ! ? ( ) [ ] / + _`.
- Title rejects unsupported symbols and newlines with a clear validation message.
- Title exceeding 255 characters is rejected.
- Body exceeding 10,000 characters is rejected.

### REQ-03 — Duplicate Title Handling
**Requirement**: If the entered title already exists, the app shall auto-assign the next available numeric suffix (Title, Title1, Title2, ...).

**User Story**: As a user, I want the app to handle duplicate note titles automatically so that I don't lose a new note because a title already exists.

**Acceptance Criteria**:
- If title is unique, note is saved with that exact title.
- If title already exists, note is auto-renamed to the next available suffix:
  - Note -> next duplicate saves as Note1
  - Note, Note1 -> next duplicate saves as Note2

### REQ-04 — Note Persistence
**Requirement**: Each created note shall be assigned a unique ID and creation timestamp, and persisted to server-side storage.

**User Story**: As a user, I want my notes to be saved reliably so that I can access them after closing the app.

**Acceptance Criteria**:
- Each saved note has a unique ID and created_at timestamp.
- Note data persists across app restarts.
- If persistence fails, the app shows an error and does not save partial or corrupt note data.

## Edit Note

### REQ-05 — Basic Note Editing
**Requirement**: The app shall allow the user to edit the title and/or body of an existing note.

**User Story**: As a user, I want to edit an existing note so that I can update content.

**Acceptance Criteria**:
- User can open an existing note and edit title and/or body.
- Saving without content changes is allowed and does not alter title/body values.
- Edited note appears correctly in the notes list after save.
- If the note no longer exists at save time, show error and do not recreate it.

### REQ-06 — Edit Title and Body Validation
**Requirement**: The edited title shall follow the same validation rules as REQ-02 (required, max 255, Unicode-friendly, common punctuation allowed, no control characters/newlines). Body shall remain optional, max 10,000 characters.

**User Story**: As a user, I want the same title validation rules applied during editing so that my notes stay consistent.

**Acceptance Criteria**:
- Title is required after trimming whitespace; blank title is rejected.
- Title length must be 1–255 characters; body length must be 0–10,000 characters.
- Title validation rules match REQ-02 exactly.

### REQ-07 — Duplicate Title on Edit
**Requirement**: If the edited title conflicts with another existing note, the app shall auto-assign the next available numeric suffix, excluding the current note from the duplicate check.

**User Story**: As a user, I want the app to handle title conflicts during editing automatically so that my edits don't overwrite another note's identity.

**Acceptance Criteria**:
- If edited title is unique, save with that title.
- If edited title conflicts with another note, auto-suffix to next available value.
- Duplicate check excludes the same note ID (no false duplicate on unchanged title).

### REQ-08 — Edit Persistence
**Requirement**: On successful save, the note shall retain its original ID and created_at timestamp, update its updated_at timestamp, and persist changes to server-side storage.

**User Story**: As a user, I want my edits saved reliably so that changes persist after closing the app.

**Acceptance Criteria**:
- On successful edit, note keeps original id and created_at, and updates updated_at.
- If persistence fails, show error and keep previously saved data unchanged.

### BL-02 UI Alignment — Dedicated Editor Workflow
**Requirement**: BL-02 editing UX shall use a dedicated editor panel opened from note-list selection, support private-toggle edits, keep the editor open after save, refresh the selected list item preview, and show created timestamp in Pacific time with automatic PST/PDT labeling.

**User Story**: As a user, I want a stable editor workflow that keeps context while I edit so that saving changes is predictable and list previews stay in sync.

**Acceptance Criteria**:
- Selecting a note from the list opens that note in a dedicated editor panel.
- The editor panel allows changing title, body, and private toggle state in the same save action.
- Saving updates the selected note list item without closing the editor panel.
- The editor shows created timestamp in Pacific time and automatically labels PST or PDT by date.

## Delete Note

### REQ-09 — Delete Confirmation
**Requirement**: The app shall require the user to confirm deletion before a note is removed. The confirmation prompt shall display the note title and state that the action is permanent and cannot be undone.

**User Story**: As a user, I want to be asked to confirm before a note is deleted so that I don't accidentally lose my work.

**Acceptance Criteria**:
- User selects a note and triggers delete.
- Confirmation dialog appears displaying the note title and the message "This cannot be undone."
- If user cancels, the note is not deleted and the list is unchanged.

## Account and Authentication

### WEB-09 — Persistent User Account Model
**Requirement**: The system shall implement a persistent `User` account model stored in the database.

**User Story**: As a multi-user note app, I want to maintain persistent user accounts so that users can sign up, change their login password, and return to the app after closing the browser.

**Acceptance Criteria**:
- User table exists with fields: `user_id`, `email`, `password_hash`, `created_at`, `is_active`.
- `user_id` is unique and immutable.
- `email` is unique (verified at signup and on update to prevent duplicates).
- `password_hash` is bcrypt or Argon2 of the login password, never plaintext.
- `is_active` allows account suspension without deletion.
- All notes, sessions, and audit entries reference `user_id` to enforce ownership.

### WEB-10 — Server-Side Session Management
**Requirement**: The system shall use database-backed server-side sessions with specific timeout and logout behavior.

**User Story**: As a user, I want reliable session management so that I can log out immediately and be confident my session is revoked, and so sessions automatically expire after inactivity or a maximum time.

**Acceptance Criteria**:
- Sessions table exists with fields: `session_id`, `user_id`, `created_at`, `last_activity_at`, `expires_at`, `is_revoked`, `ip_address`, `user_agent`.
- Login creates a session record and returns a secure HttpOnly cookie.
- Logout marks the session `is_revoked = True`, invalidating that device/browser immediately.
- Idle timeout: session expires after 30 minutes of no requests.
- Absolute timeout: session expires after 7 days regardless of activity.
- Other devices/sessions remain active when one session logs out.
- Remember-me is not available in v1.
- Session cookie cannot be accessed by JavaScript and is not transmitted over unencrypted channels.

### WEB-11 — Separate Login Password and Note Passphrase
**Requirement**: Login password and private-note passphrase shall be separate secrets using different cryptographic derivation.

**User Story**: As a user, I want to use a strong account password for login and a simple memorable 4-digit PIN for my private notes, and I want to be able to change my login password without affecting my encrypted notes.

**Acceptance Criteria**:
- Login password is hashed with bcrypt/Argon2 using strong iteration counts.
- Private-note passphrase is a 4-digit numeric PIN (0000–9999).
- Passphrase is derived into an AES-256-GCM key using PBKDF2-HMAC-SHA256 with ≥100,000 iterations and a random 16-byte salt.
- Users can change login password without re-encrypting notes.
- Passphrase is never stored plaintext; only the salt is stored with each encrypted note.
- Changing login password does not affect existing encrypted notes.
- Bulk delete is out of scope for MVP.

### REQ-10 — Delete Execution and Persistence
**Requirement**: Upon confirmation, the app shall permanently remove the note from storage atomically. If the delete operation fails, the note shall remain intact and the user shall receive an error message.

**User Story**: As a user, I want a confirmed deletion to remove the note immediately and permanently so that my storage stays clean.

**Acceptance Criteria**:
- Confirmed deletion removes the note from JSON storage atomically (no partial writes).
- Deleted note is removed from the list immediately.
- If the note no longer exists at delete time, the app shows an error and does not crash.
- If JSON write fails, the note remains intact and user receives an error message.

### REQ-11 — Post-Deletion List Behavior
**Requirement**: After a note is deleted, the app shall update the notes list immediately and display an empty state if no notes remain.

**User Story**: As a user, I want the notes list to update immediately after deletion so that I always see an accurate view of my notes.

**Acceptance Criteria**:
- Notes list refreshes immediately after successful deletion.
- If notes remain, the next note in the list receives focus.
- If the deleted note was the last one, an empty state message is displayed (e.g., "No notes yet. Create your first note.").

### BL-03.1 — Bulk Delete Selected Notes
**Requirement**: The UI shall provide a multi-select mode for the notes list that allows the user to select multiple notes at once and delete them in a single confirmation action.

**User Story**: As a user, I want to select and delete multiple notes at once so that I can clean up my list efficiently without repeating the delete action for each note.

**Acceptance Criteria**:
- User can enter multi-select mode and individually select notes from the list.
- A bulk-delete button is visible when at least one note is selected.
- Confirming bulk delete removes all selected notes and refreshes the list immediately.
- If no notes remain after bulk delete, the empty state message from REQ-13 is shown.
- Deselecting all notes or cancelling exits multi-select mode without deleting anything.
- Bulk-action buttons wrap gracefully at narrower panel widths rather than overflowing.

## List Notes

### REQ-12 — List Display and Format
**Requirement**: The app shall display all notes in a scrollable list ordered by creation date (newest first), showing each note's title (truncated at 40 characters server-side, with ellipsis appended). In the editor panel, under the Created timestamp, the app shall show `Modified: Month DD, YYYY HH:MM PST/PDT`. A body preview shall appear under each title, truncated by CSS single-line ellipsis.

> **Revision note (2026-05-19)**: Truncation cap revised from 60 to 40 characters to fit the two-panel workbench layout determined during BL-04 UI implementation. The full title is preserved in storage and surfaced via instant hover tooltip.

**User Story**: As a user, I want to see all my notes in a clear, ordered list so I can quickly scan and find what I need.

**Acceptance Criteria**:
- All notes displayed in a scrollable list, newest first.
- Each list item shows title truncated server-side at 40 characters (37 chars + "…") with the full title available on hover via tooltip.
- Each list item shows a one-line body preview truncated by CSS ellipsis.
- Editor panel shows `Modified: Month DD, YYYY HH:MM PST/PDT` directly under `Created:`.

### REQ-13 — List Empty State
**Requirement**: When no notes exist, the app shall display an empty state message prompting the user to create their first note.

**User Story**: As a user, I want to see a helpful message when I have no notes so that I am guided to create one.

**Acceptance Criteria**:
- If no notes exist, display: "No notes yet. Create your first note."
- Empty state replaces the list view entirely.
- List transitions to showing notes immediately after first note is created.

### REQ-14 — List Refresh
**Requirement**: The notes list shall refresh automatically after any create, edit, or delete operation to reflect the current state of storage.

**User Story**: As a user, I want the notes list to always reflect the latest state so I never see stale data.

**Acceptance Criteria**:
- List updates immediately after a note is created, edited, or deleted.
- Sort order (newest first) is re-applied after each refresh.

### BL-04 UI Alignment — Two-Panel Workbench Layout
**Requirement**: The desktop workbench shall display a persistent two-panel layout with a resizable notes list on the left and an editor/action panel on the right. The create-note form and the note editor shall share the same right-panel slot. The right panel shall show an idle placeholder when no action is active. The notes list panel shall be resizable via a draggable splitter bar that persists its position across sessions.

**User Story**: As a user, I want a stable two-panel workspace so that browsing my notes and editing or creating them happen side by side without context-switching.

**Acceptance Criteria**:
- Desktop layout always opens with two panels visible: notes list (left) and action panel (right).
- Clicking "Create Note" opens the create form in the right panel slot; selecting a note opens the editor in the same slot.
- Closing the editor or create form returns the right panel to the idle placeholder ("Ready when you are").
- A draggable splitter between panels allows resizing; panel widths persist across page loads via `localStorage`.
- Double-clicking the splitter resets panel widths to the default (360 px notes list).
- Notes list minimum width is 300 px; right panel minimum width is 320 px.
- Note titles in the list are truncated server-side at 40 characters; hovering the title shows the full title via an instant CSS tooltip.
- Note body preview renders as a single line truncated by CSS ellipsis; the full body text is present in the HTML for search and accessibility.
- HTMX partial templates injected dynamically are initialized with `htmx.process()` to ensure attribute bindings activate.

## Search Notes

### REQ-15 — Basic Search
**Requirement**: The app shall allow the user to filter notes by entering a query that matches against note titles and body content, case-insensitively. Minimum query length is 1 non-whitespace character. Special characters in the search query are treated as literal text and do not cause errors.

**User Story**: As a user, I want to search my notes by title or content so I can locate specific information efficiently.

**Acceptance Criteria**:
- Search bar filters notes matching query against title or body (case-insensitive).
- Results update in real-time as user types.
- Minimum query length is 1 non-whitespace character.
- Special characters in search query (e.g., @, #) are treated as literal search text and do not cause errors.
- Clearing the search bar resets to the full note list.

### REQ-16 — Search Edge Cases
**Requirement**: The app shall handle empty, whitespace-only, and no-result search inputs by displaying specific feedback messages in place of the notes list, with no errors or crashes occurring.

**User Story**: As a user, I want clear feedback when my search returns no results so I'm not confused by a blank screen.

**Acceptance Criteria**:
- Whitespace-only input is treated as an empty query and shows the full note list.
- If search yields no matches, display: "No notes match your search."
- If there are no notes at all and user searches, display the empty state message from REQ-13, not "no results."
- Search state updates in real-time if a note is edited or deleted while search is active.

### BL-05 UI Alignment — Hero Toolbar Search Placement
**Requirement**: BL-05 search UX shall place the search field in the hero toolbar to the right of the "Create Note" button, not inside the notes list panel. Search requests shall update only the notes result area using HTMX partial swaps.

**User Story**: As a user, I want search controls near primary actions so I can quickly create or find notes from one top-level toolbar.

**Acceptance Criteria**:
- Hero toolbar includes "Create Note" followed by the search field and clear button.
- Search field performs live filtering via HTMX with a short debounce and case-insensitive matching against title/body.
- Clearing search resets the notes list to the full view without page navigation.
- Notes list panel content updates in place (`#notes-results`) while editor/create panel state remains unchanged.
- Search route returns REQ-16 messages for no-result and no-notes cases.
- API route `/api/notes/search` returns matching active notes and supports whitespace query fallback to full list.

## Lists in Notes

### REQ-17 — Bullet and Checkbox Lists
**Requirement**: The app shall allow the user to create and edit unordered bullet lists and checkbox lists inside the note body.

**User Story**: As a user, I want to structure my notes with bullet and checkbox lists so I can organize tasks and ideas clearly.

**Acceptance Criteria**:
- User can insert bullet list items and checkbox list items in the note body.
- User can edit existing list item text without breaking list structure.
- Ordered (numbered) lists are out of scope for MVP.

### REQ-18 — List Persistence and Rendering
**Requirement**: List content shall be persisted in note storage and rendered consistently after save, close, and reopen. Nested lists deeper than 2 levels are not required for MVP.

**User Story**: As a user, I want my list formatting to stay intact after reopening the app so I do not lose note structure.

**Acceptance Criteria**:
- Bullet and checkbox list syntax persists in JSON storage after save.
- After reopening the app, previously saved lists render the same as before close.
- Nesting up to 2 levels is preserved; deeper nesting behavior is not required for MVP.

### REQ-19 — Checkbox State Persistence
**Requirement**: The app shall allow the user to toggle checkbox list items between checked and unchecked states, and persist each state change immediately.

**User Story**: As a user, I want to check and uncheck tasks so I can track progress directly in my notes.

**Acceptance Criteria**:
- Clicking a checkbox item toggles state between checked and unchecked.
- Toggled state is saved immediately and remains after app restart.
- Toggling one checkbox does not alter other list items.

## Text Formatting

### REQ-20 — Apply Basic Formatting
**Requirement**: The app shall allow the user to apply bold, italic, and underline formatting to selected text in the note body.

**User Story**: As a user, I want to format text for emphasis so my notes are easier to scan.

**Acceptance Criteria**:
- User can apply bold, italic, and underline to selected body text.
- Formatting applies only to current selection.
- If no text is selected, formatting action does not modify note content.

### REQ-21 — Formatting Integrity
**Requirement**: Formatting actions shall not modify note title content and shall preserve existing surrounding text without data loss when multiple formats are combined.

**User Story**: As a user, I want formatting tools to be safe so they do not corrupt unrelated text.

**Acceptance Criteria**:
- Formatting actions are disabled or ignored for title input.
- Applying multiple formats to overlapping text does not delete nearby characters.
- Undo/redo of formatting changes restores exact previous/next body content states.

### REQ-22 — Formatting Storage Rules
**Requirement**: Bold and italic shall be stored using Markdown-compatible markers, and underline shall be stored using a consistent format supported by the renderer.

**User Story**: As a user, I want formatting to render consistently so saved notes look the same across sessions.

**Acceptance Criteria**:
- Bold is stored with Markdown-compatible syntax and renders as bold.
- Italic is stored with Markdown-compatible syntax and renders as italic.
- Underline uses one defined storage format and renders consistently after reopen.

## Note Capacity

### REQ-23 — Maximum Note Count
**Requirement**: The app shall allow up to 10,000 notes in a single user data store.

**User Story**: As a user, I want to keep a large number of notes without unexpected failures.

**Acceptance Criteria**:
- Creating notes is allowed while total note count is less than 10,000.
- Exactly 10,000 notes can exist in storage at once.
- App startup and list rendering remain functional at 10,000 notes.

### REQ-24 — Limit Reached Behavior
**Requirement**: When note count is 10,000, create and duplicate-title-save operations that would add a new note shall be blocked, the existing data shall remain unchanged, and the app shall display: "Note limit reached (10,000). Delete notes to create a new one."

**User Story**: As a user, I want a clear message when I hit the limit so I know what action to take.

**Acceptance Criteria**:
- At 10,000 notes, attempts to create a new note are rejected.
- At 10,000 notes, duplicate-title create flow does not create an additional suffixed note.
- App shows exact message: "Note limit reached (10,000). Delete notes to create a new one."
- No existing note is modified if create is blocked.

## Note Privacy

### REQ-25 — Private Toggle
**Requirement**: The app shall allow the user to mark or unmark any note as private using a per-note toggle.

**User Story**: As a user, I want to mark sensitive notes as private so they are handled with extra discretion.

**Acceptance Criteria**:
- Each note has a control to mark it private or non-private.
- Toggling private status updates the selected note only.
- Private toggle state is editable after initial note creation.

### REQ-26 — Privacy State Visibility and Persistence
**Requirement**: Private status shall be persisted in storage and visually indicated in the notes list.

**User Story**: As a user, I want to quickly identify which notes are private and trust that this setting is saved.

**Acceptance Criteria**:
- Private state is stored in JSON and survives app restart.
- Notes list shows a clear private indicator for private notes.
- Non-private notes do not show the private indicator.

### REQ-27 — Private Content Exposure Rules
**Requirement**: Private notes shall hide body preview text in list and search results to prevent accidental on-screen disclosure.

**User Story**: As a user, I want private note previews hidden so sensitive content is not exposed while browsing.

**Acceptance Criteria**:
- In the notes list, private notes do not display body preview text.
- In search results, private notes may appear by title match, but body preview remains hidden.
- Opening the private note still shows full content in the editor.

## Enhanced Non-Functional Requirements

Scope convention: All NFR acceptance criteria in this section are MVP test coverage unless explicitly marked otherwise.

### NFR-01 — Concurrency Capacity [MVP]
**Requirement**: The system shall support 100 concurrently active user sessions in a single deployment instance.

**User Story**: As a product owner, I want defined concurrency capacity so that system behavior is predictable under expected demand.

**Acceptance Criteria**:
- Load test with 100 active sessions completes without service crash.
- Session count is measured against one deployment instance.
- Core operations remain available while 100 active sessions are present.

### NFR-02 — Active Session Definition and Workload [MVP]
**Requirement**: A session shall be counted as active when it issues at least one request every 10 seconds during a continuous 5-minute test window. The concurrency test workload shall be 70% read operations (list, search, open), 20% update operations (edit), and 10% create operations.

**User Story**: As a QA engineer, I want a precise active-session and workload definition so that performance tests are repeatable and comparable.

**Acceptance Criteria**:
- Session activity threshold is enforced at 1 request per 10 seconds for 5 continuous minutes.
- Test mix is executed at 70% reads, 20% updates, 10% creates.
- Test report records total active sessions and workload distribution.

### NFR-03 — Concurrency Latency Targets [MVP]
**Requirement**: Under NFR-02 workload and with a dataset of up to 5,000 notes, measured latency targets shall be p95 <= 120 ms for read operations, p95 <= 180 ms for create/update operations, and p99 <= 300 ms for all operations.

**User Story**: As a user, I want responsive operations under load so that the app remains usable during peak activity.

**Acceptance Criteria**:
- With up to 5,000 notes and NFR-02 workload, read operations meet p95 <= 120 ms.
- With up to 5,000 notes and NFR-02 workload, create/update operations meet p95 <= 180 ms.
- Across all operations, p99 <= 300 ms under the same test conditions.

### NFR-04 — Concurrent Edit Conflict Policy [MVP]
**Requirement**: When concurrent edits target the same note, the system shall enforce optimistic concurrency using a note version field. A stale write shall be rejected with a conflict response and shall not overwrite newer data.

**User Story**: As a user, I want concurrent edits handled safely so that newer note changes are not silently overwritten.

**Acceptance Criteria**:
- Concurrent edits to the same note require version check on save.
- Stale version save attempts return a conflict response.
- Newer saved content remains unchanged after stale-write rejection.

### NFR-05 — Overload Behavior [MVP]
**Requirement**: For load above 100 active sessions, the system may throttle new requests, but shall not corrupt stored notes. During NFR-02 test conditions, non-user-cancelled request failures shall be <= 1%.

**User Story**: As a platform maintainer, I want safe degradation under overload so data integrity is preserved.

**Acceptance Criteria**:
- Above 100 active sessions, throttling behavior may occur without process crash.
- Stored notes remain consistent and uncorrupted during overload.
- Under NFR-02 test conditions, non-user-cancelled request failure rate is <= 1%.

### NFR-06 — Web Dataset Support [MVP]
**Requirement**: In web deployment mode, the system shall support a dataset of up to 5,000 notes per user account.

**User Story**: As an authenticated user, I want the app to handle thousands of my notes so I can rely on it long term.

**Acceptance Criteria**:
- System can load and operate with 5,000-note dataset per account.
- Create, edit, search, and delete remain functional at per-account dataset limit.
- No cross-user data leakage occurs at maximum dataset size.

### NFR-07 — Web/API Latency Targets [MVP]
**Requirement**: With up to 5,000 notes for the active account, operation latency targets shall be p95 <= 120 ms for read operations (open, list, search), p95 <= 180 ms for create/update operations, and p99 <= 300 ms for all API operations measured at the service boundary.

**User Story**: As a web user, I want low-latency interactions so the app feels responsive in-browser.

**Acceptance Criteria**:
- Read operations meet p95 <= 120 ms at 5,000 notes/account.
- Create/update operations meet p95 <= 180 ms in same conditions.
- All API operations meet p99 <= 300 ms in same conditions.

### NFR-08 — API Measurement Boundary [MVP]
**Requirement**: API latency measurements shall be recorded at the server service boundary from request entry to durable storage commit, excluding browser rendering time.

**User Story**: As a QA engineer, I want a strict server-side measurement boundary so latency results are comparable across builds.

**Acceptance Criteria**:
- Timing start is request entry at service boundary.
- Timing end is completion of durable storage commit.
- Browser render time is excluded from measured latency.

### NFR-09 — API Write Durability [MVP]
**Requirement**: For create and update API operations, successful completion shall guarantee durable persistence before success is returned.

**User Story**: As a user, I want successful saves to be durable so notes are not lost after app or system interruption.

**Acceptance Criteria**:
- Success response is returned only after durable storage commit.
- Power-loss simulation after success does not lose committed note updates.
- Failed durability check causes operation failure, not success.

### NFR-10 — Browser Keyboard-Only Workflows [MVP]
**Requirement**: On desktop web browsers, the UI shall support keyboard-only completion of core workflows: create note, open note, edit title/body, save, search, navigate note list, toggle checklist items, and delete with confirmation.

**User Story**: As a browser power user, I want to complete core actions by keyboard only for speed and accessibility.

**Acceptance Criteria**:
- Each listed core workflow is completable without mouse input.
- Keyboard navigation and action keys are sufficient to execute each workflow.
- Delete confirmation is actionable via keyboard only.

### NFR-11 — Mobile Touch-Only Workflows [Post-MVP]
**Requirement**: On mobile platforms, the same core workflows shall be completable using touch-only interaction without requiring a hardware keyboard.

**User Story**: As a mobile user, I want all core actions to work with touch so I am not blocked by missing keyboard input.

**Acceptance Criteria**:
- Each core workflow is completable with touch-only interaction.
- No hardware keyboard is required for any core workflow.
- Workflow completion on mobile matches desktop functional outcome.

### NFR-12 — Platform Input Reachability and Visibility [MVP]
**Requirement**: Every interactive control in core workflows shall be reachable by the primary input model of the platform (tab navigation on keyboard-capable platforms; touch interaction on mobile) and shall provide a clear visible active/focus indicator.

**User Story**: As a user, I want clear interaction state so I always know which control is active before executing actions.

**Acceptance Criteria**:
- Desktop controls are reachable with tab navigation.
- Mobile controls are reachable through touch interaction.
- Active/focus state is visually obvious for interactive controls.

### NFR-13 — Dependency Boundary Enforcement [MVP]
**Requirement**: The system shall enforce dependency boundaries that prevent direct coupling between UI and storage/security implementations, so that security and storage components can be replaced or tested independently without UI code changes.

**User Story**: As an architect, I want dependency boundaries enforced so we can evolve storage/security safely without rewriting UI.

**Acceptance Criteria**:
- UI module has no direct dependency on storage/security concrete implementations.
- Storage/security component swap does not require UI code changes.
- Boundary violations are detectable in automated checks or code review gates.

### NFR-14 — Interface-Based Testability [MVP]
**Requirement**: Storage and security capabilities shall be accessed through explicit interfaces that support test doubles, so UI and service logic can be tested without real file I/O or cryptographic backends.

**User Story**: As a developer, I want interface-based dependencies so tests run fast and deterministically.

**Acceptance Criteria**:
- Storage and security access occurs through explicit interfaces.
- UI and service tests can run with mocks/fakes instead of real file/crypto backends.
- Test suite includes at least one path proving mocked storage and security usage.

### NFR-15 — Independent Automated Validation [MVP]
**Requirement**: The system shall include automated tests that independently validate UI workflow logic, security policy enforcement, and storage persistence behavior.

**User Story**: As a maintainer, I want layered automated tests so regressions are caught in the component where they occur.

**Acceptance Criteria**:
- Automated tests exist for UI workflow behavior.
- Automated tests exist for security policy enforcement.
- Automated tests exist for storage persistence behavior independent of UI tests.

### NFR-16 — Storage Backend Replaceability [MVP]
**Requirement**: Replacing the storage backend implementation (for example, SQLite to PostgreSQL) shall not require changes to UI module code.

**User Story**: As a product team, I want storage backend migration flexibility so we can scale without UI rewrite.

**Acceptance Criteria**:
- A backend swap can be configured with no UI code modification.
- Existing UI workflows continue to pass after backend replacement.
- Storage integration tests pass for both old and new backend adapters.

### NFR-17 — Mobile Touch Target Size [Post-MVP]
**Requirement**: Interactive touch controls on mobile shall provide touch targets of at least 44x44 CSS pixels for primary actions in core workflows.

**User Story**: As a mobile user, I want sufficiently large touch targets so I can use the app accurately.

**Acceptance Criteria**:
- Primary action controls in core workflows meet minimum 44x44 CSS pixels.
- Touch target size is validated on representative mobile viewport sizes.
- Controls below threshold are treated as accessibility defects.

### NFR-18 — Desktop Shortcut Equivalence on Mobile [Post-MVP]
**Requirement**: Any keyboard shortcut action on desktop shall have an equivalent accessible touch action on mobile.

**User Story**: As a cross-platform user, I want feature parity so mobile access is not functionally reduced.

**Acceptance Criteria**:
- Every desktop shortcut-supported action has a documented touch equivalent.
- Touch equivalent is discoverable in UI or help surfaces.
- Functional outcome of touch action matches desktop shortcut outcome.

## Enhanced Security, Reliability, and Governance Requirements

Scope convention: SRG acceptance criteria inherit the scope tag in each SRG heading ([MVP] or [Post-MVP]).

### SRG-01 — All Notes At-Rest Encryption [MVP]
**Requirement**: All notes shall be encrypted at rest with authenticated encryption (AES-256-GCM or ChaCha20-Poly1305). At minimum, note title, note body, and note content versions shall be encrypted and shall never be written to persistent storage in plaintext; only minimal non-sensitive metadata required for indexing and lifecycle management may remain unencrypted.

**User Story**: As a user, I want all note content encrypted at rest so direct file access cannot expose my notes.

**Acceptance Criteria**:
- All notes (private and non-private) are encrypted at rest using AES-256-GCM or ChaCha20-Poly1305.
- Note title, body, and version content are never persisted in plaintext.
- Only minimal non-sensitive metadata required for indexing/lifecycle remains unencrypted.

### SRG-02 — Private Note Encryption Scope [MVP]
**Requirement**: For notes marked as private, encryption at rest shall include title, body, and private-note content versions; only minimal non-sensitive metadata required for indexing and lifecycle management may remain unencrypted.

**User Story**: As a user, I want private-note fields explicitly protected so sensitive data is always encrypted in storage.

**Acceptance Criteria**:
- Private note title, body, and private-note version content are encrypted at rest.
- No plaintext private title/body/version content is written to persistent storage.
- Only minimal non-sensitive metadata remains unencrypted.

### SRG-03 — Per-Note Key Isolation [Post-MVP]
**Requirement**: Each note shall be encrypted independently using a unique per-note data encryption key; compromise of one note key shall not expose plaintext of other notes.

**User Story**: As a security owner, I want per-note key isolation so compromise impact is limited to a single note.

**Acceptance Criteria**:
- Different notes use different data encryption keys.
- Decrypting one note key does not decrypt other notes.
- Security tests demonstrate key compromise blast radius is limited to one note.

### SRG-04 — Data In-Transit Protection [MVP]
**Requirement**: Any network transmission containing note content (including sync, backup, restore, and export/import APIs) shall use TLS 1.2 or higher; note content shall not be transmitted over unencrypted channels.

**User Story**: As a user, I want note content protected in transit so network interception cannot expose my data.

**Acceptance Criteria**:
- Network paths carrying note content enforce TLS 1.2+.
- Requests over insecure transport are rejected.
- Sync/backup/restore/export-import routes are covered by transport security tests.

### SRG-05 — Audit Log Coverage [MVP]
**Requirement**: Create, read, update, delete, restore, and export operations shall generate audit log entries containing actor identity, action type, note ID, UTC timestamp, operation outcome, and request correlation ID.

**User Story**: As an auditor, I want complete operation logs so I can trace who did what and when.

**Acceptance Criteria**:
- Each listed operation type creates an audit entry.
- Audit entry includes actor identity, action, note ID, UTC timestamp, outcome, and correlation ID.
- Failed and successful operations are both represented with correct outcome.

### SRG-06 — Tamper-Evident Audit Chain [Post-MVP]
**Requirement**: Audit logs shall be append-only and tamper-evident using SHA-256 hash chaining where each entry stores the hash of the previous entry.

**User Story**: As a compliance owner, I want tamper-evident logs so unauthorized log changes are detectable.

**Acceptance Criteria**:
- Audit records are append-only.
- Each entry stores SHA-256 hash of prior entry.
- Chain verification detects insertion, deletion, or modification of entries.

### SRG-07 — Audit Privacy Guardrails [MVP]
**Requirement**: Audit entries shall not store plaintext private note content; change details shall be limited to metadata and content fingerprints.

**User Story**: As a privacy-conscious user, I want auditing without exposing my private note content in logs.

**Acceptance Criteria**:
- Private note plaintext is absent from audit logs.
- Change details are represented as metadata/fingerprints only.
- Log scans for private plaintext content return no matches.

### SRG-08 — Immutable Version Records [MVP]
**Requirement**: Note version history shall be immutable; updates shall create new version records and shall not modify prior stored versions.

**User Story**: As a user, I want immutable history so prior note states remain trustworthy and recoverable.

**Acceptance Criteria**:
- Update operation creates a new version record.
- Existing version records remain unchanged after updates.
- Attempted mutation of historical versions is rejected.

### SRG-09 — Version Hash Validation [Post-MVP]
**Requirement**: Each stored note version shall include a SHA-256 content hash. Hash verification failures shall raise integrity errors, block further writes to affected records, and preserve existing data unchanged.

**User Story**: As a reliability engineer, I want version hash validation so corruption is detected before further damage occurs.

**Acceptance Criteria**:
- Every stored version includes a SHA-256 hash.
- Hash mismatch triggers explicit integrity error.
- Writes to affected records are blocked until integrity issue is resolved.

### SRG-10 — Soft Delete Retention [MVP]
**Requirement**: Deleting a note shall perform a soft delete by default, retaining recoverable metadata and content for 30 calendar days.

**User Story**: As a user, I want accidental deletions recoverable for a limited period.

**Acceptance Criteria**:
- Delete action marks note as soft-deleted by default.
- Metadata and content remain recoverable for 30 calendar days.
- Soft-delete timestamp is recorded for retention tracking.

### SRG-11 — Soft Delete Visibility and Restore Window [MVP]
**Requirement**: Soft-deleted notes shall be excluded from default list and search results, and shall be restorable only within the retention window.

**User Story**: As a user, I want deleted notes hidden from normal views but restorable before retention expiry.

**Acceptance Criteria**:
- Soft-deleted notes do not appear in default list results.
- Soft-deleted notes do not appear in default search results.
- Restore succeeds only while within retention window.

### SRG-12 — Retention Expiry Purge [Post-MVP]
**Requirement**: At retention expiry, soft-deleted notes shall be permanently purged within 24 hours unless an explicit policy override is configured.

**User Story**: As a governance owner, I want retention expiry enforced so stale deleted content does not persist indefinitely.

**Acceptance Criteria**:
- Expired soft-deleted notes are purged within 24 hours.
- Purged notes are no longer recoverable through normal restore flows.
- Explicit policy override prevents purge only when configured.

### SRG-13 — Restore Identity and Audit Continuity [MVP]
**Requirement**: Restore operations shall preserve original note ID, maintain version history continuity, and create an audit entry for restore action.

**User Story**: As a user, I want restored notes to keep their identity and history so links and auditability remain intact.

**Acceptance Criteria**:
- Restore retains original note ID.
- Version history remains continuous after restore.
- Restore action creates an audit entry with actor and timestamp.

### SRG-14 — Structured Error Handling [MVP]
**Requirement**: Invalid save, load, or delete operations (including malformed input, missing records, permission denial, and integrity check failures) shall return structured errors with machine-readable codes and user-safe messages, and shall not crash the application.

**User Story**: As a user, I want clear, safe errors instead of crashes so I can recover from failures.

**Acceptance Criteria**:
- Invalid operations return structured error payloads with machine-readable code.
- Error messages are user-safe and do not leak sensitive internals.
- Application process remains running after invalid operation errors.

### SRG-15 — Atomic Failure Safety [MVP]
**Requirement**: On failed save, load, delete, or restore operations, the system shall preserve pre-operation data state and prevent partial writes via atomic commit/rollback behavior.

**User Story**: As a user, I want failed operations to leave my data unchanged so I can trust persistence integrity.

**Acceptance Criteria**:
- Failed operations do not partially mutate persisted records.
- Pre-operation state is preserved after failure.
- Atomic commit/rollback behavior is verified for save, load, delete, and restore.

### SRG-16 — Repeated Invalid Request Consistency [MVP]
**Requirement**: Repeated identical invalid requests shall produce consistent error codes and shall not create duplicate side effects in storage or audit logs.

**User Story**: As a developer, I want deterministic failure behavior so retries and error handling are predictable.

**Acceptance Criteria**:
- Repeating identical invalid requests returns the same error code.
- Invalid retries do not create additional storage mutations.

## Security, Reliability, and Governance — Release Gate and Access Control

### SRG-17 — Transport Encryption Release Gate [MVP]
**Requirement**: No feature that transmits note content may be released unless SRG-04 transport encryption requirements are satisfied.

**User Story**: As a developer, I want a hard gate preventing any content-transmitting feature from shipping without transport encryption so that note data is never exposed over unencrypted channels.

**Acceptance Criteria**:
- Any feature that transmits note content is blocked from release until TLS 1.2+ is verified in place.
- Code review and DoD checklists include a SRG-04 confirmation step for all network-touching features.
- Features passing this gate have documented evidence of transport encryption compliance.

### SRG-18 — Private Note Passphrase Unlock [MVP]
**Requirement**: Viewing or decrypting a private note shall require successful private-note unlock authentication using a user-defined app passphrase.

**User Story**: As a user, I want my private notes locked behind a passphrase so that only I can access them.

**Acceptance Criteria**:
- Attempting to open a private note without authenticating redirects to the unlock prompt.
- Correct passphrase grants access to private note content.
- Incorrect passphrase denies access and shows an error message.
- No private note title, body, or version content is accessible without successful authentication.

### SRG-19 — Private Note Content Hidden Until Authenticated [MVP]
**Requirement**: Private note content shall remain hidden until unlock authentication succeeds; failed authentication shall not reveal any private title/body/version plaintext.

**User Story**: As a user, I want my private note content invisible during failed unlock attempts so that partial information cannot be inferred.

**Acceptance Criteria**:
- Private note title and body are not displayed before authentication succeeds.
- Failed unlock attempt does not flash or partially reveal any content.
- Content remains hidden for any number of consecutive failed attempts.

### SRG-20 — Session-Scoped Unlock [MVP]
**Requirement**: Unlock authentication shall be required at least once per app session before any private note can be opened.

**User Story**: As a user, I want to authenticate once per session so that I am not repeatedly prompted while working, but am protected when I reopen the app.

**Acceptance Criteria**:
- First private note access in a session prompts for passphrase.
- Subsequent private note accesses within the same session do not re-prompt while session is active.
- Closing and reopening the app starts a new session requiring re-authentication.

### SRG-21 — Inactivity Unlock Expiry [MVP]
**Requirement**: After 15 minutes of inactivity, private-note unlock state shall expire and re-authentication shall be required.

**User Story**: As a user, I want my private notes to re-lock after inactivity so that leaving my device unattended does not expose my private content.

**Acceptance Criteria**:
- Unlock state expires after exactly 15 minutes of inactivity.
- After expiry, the next private note access prompts for re-authentication.
- Inactivity timer resets on any user interaction with the app.

### SRG-22 — Unlock Rate Limiting [MVP]
**Requirement**: Failed unlock attempts shall return clear error messages, shall not crash the app, and shall apply rate limiting after 5 consecutive failures.

**User Story**: As a user, I want failed unlock attempts rate-limited so that brute-force guessing of my passphrase is impractical.

**Acceptance Criteria**:
- Failed unlock returns a clear, user-safe error message.
- App does not crash on any number of failed unlock attempts.
- After 5 consecutive failures, rate limiting is applied before further attempts are accepted.

### SRG-23 — Unlock Lockout with Exponential Backoff [MVP]
**Requirement**: After 5 consecutive failed unlock attempts within a single session, the private-note unlock mechanism shall enter a locked-out state for a minimum of 5 minutes. Each subsequent lockout period shall double (exponential backoff). The lockout state, attempt count, and expiry timestamp shall persist across app restarts.

**User Story**: As a security owner, I want consecutive unlock failures to trigger an escalating lockout so that persistent brute-force attempts are effectively blocked even across app restarts.

**Acceptance Criteria**:
- 5 consecutive failures trigger a 5-minute lockout.
- Each subsequent lockout period is double the previous (5 min → 10 min → 20 min, etc.).
- Lockout state, attempt count, and expiry timestamp are saved to persistent storage.
- Restarting the app during a lockout maintains the lockout until the expiry timestamp passes.
- Unlock prompt is disabled and displays remaining lockout time during lockout state.

### SRG-24 — Anti-Enumeration Unlock Responses [MVP]
**Requirement**: Unlock error responses shall be identical in content and timing regardless of whether the failure is caused by a wrong passphrase or an internal error, preventing enumeration of failure cause.

**User Story**: As a security owner, I want all unlock failure responses to be indistinguishable so that an attacker cannot determine the cause of failure.

**Acceptance Criteria**:
- Wrong passphrase and internal error responses display identical user-facing error messages.
- Response timing for both failure types is equivalent within an acceptable tolerance.
- No additional metadata or status codes differentiate the failure cause to the client.

## Security, Reliability, and Governance — Metadata Minimization

### SRG-25 — Plaintext Metadata Allowlist [MVP]
**Requirement**: The only fields permitted to remain unencrypted in local storage are: `note_id`, `created_at`, `updated_at`, `is_private` (boolean), `is_deleted` (boolean), and `deleted_at`. All other note fields—including `title`, `body`, and `version_content`—shall be encrypted at rest per SRG-01. Any future addition of a plaintext field requires explicit update to this allowlist in requirements before implementation.

**User Story**: As a developer, I want a defined allowlist of permitted plaintext fields so that no note content is accidentally stored unencrypted and any expansion requires a deliberate requirements change.

**Acceptance Criteria**:
- Local storage records contain no unencrypted fields outside the allowlist: `note_id`, `created_at`, `updated_at`, `is_private`, `is_deleted`, `deleted_at`.
- `title`, `body`, and `version_content` are verified to be encrypted in stored records.
- Adding any new plaintext field without updating this requirement is treated as a defect.

## Security, Reliability, and Governance — Key Management

### SRG-26 — Passphrase-Based Key Derivation [MVP]
**Requirement**: The encryption key used for private notes shall be derived from the user passphrase using PBKDF2-HMAC-SHA256 with a minimum iteration count of 260,000, a randomly generated 16-byte salt stored alongside the derived key material, and a 256-bit output key. The raw passphrase shall never be stored or logged. The derived key shall be held only in memory for the duration of the unlocked session.

**User Story**: As a user, I want my private note encryption key derived securely from my passphrase so that my notes cannot be decrypted without knowing my passphrase.

**Acceptance Criteria**:
- Key derivation uses PBKDF2-HMAC-SHA256 with ≥ 260,000 iterations.
- A randomly generated 16-byte salt is created on passphrase setup and stored with the encrypted data.
- Derived key length is 256 bits.
- The raw passphrase is not present in any persistent storage, log, or audit record.
- The derived key is cleared from memory when the session expires (per SRG-21) or the app is closed.
- Invalid retries do not create duplicate audit side effects.

## Serviceability and Manageability Requirements

### SMR-01 — Diagnostic Logging [MVP]
**Requirement**: The application shall write diagnostic (non-audit) log entries to a rotating log file with UTC timestamp, severity level, originating tier, correlation ID, and message. Log file rotates at 5 MB retaining two prior files.

**User Story**: As a developer or support engineer, I want structured diagnostic logs from all three tiers so that I can trace, reproduce, and resolve issues without access to a debugger.

**Acceptance Criteria**:
- Diagnostic log entries are written to a file in the data directory.
- Each entry includes UTC timestamp, severity (DEBUG/INFO/WARNING/ERROR), tier (UI/Service/Storage/Security), correlation ID, and message.
- Log file rotates at 5 MB; two previous rotated files are retained.
- Logging works independently for each tier.

### SMR-02 — Configurable Log Level [MVP]
**Requirement**: The active log level shall be configurable in `config.json` under `log_level`. Default is INFO. Changes take effect without app restart.

**User Story**: As a developer, I want to change the log verbosity at runtime so I can collect debug-level detail during troubleshooting without redeploying.

**Acceptance Criteria**:
- `log_level` key in `config.json` controls the active level.
- Valid values: DEBUG, INFO, WARNING, ERROR. Default: INFO.
- Changing the value in `config.json` while the app is running takes effect on next log emission without restart.
- Invalid values fall back to INFO and log a WARNING.

### SMR-03 — Log Privacy Guard [MVP]
**Requirement**: Log entries shall never contain plaintext note content. Diagnostic context is limited to `note_id` and operation type.

**User Story**: As a privacy-conscious user, I want diagnostic logs to be safe to share with support without exposing my note content.

**Acceptance Criteria**:
- No note title, body, or private-note field appears in any log entry.
- Diagnostic references to notes are limited to note_id and operation name.
- Log scan for private note content returns no matches.

### SMR-04 — Tier-Tagged Error Propagation [MVP]
**Requirement**: Errors from Storage or Security tier shall be wrapped in a `ResultError` with a `source_tier` field before reaching the Service tier. The UI tier shall not receive raw storage or crypto exceptions.

**User Story**: As a developer, I want errors labeled with their originating tier so I can pinpoint whether a failure is in storage, security, or business logic without reading stack traces.

**Acceptance Criteria**:
- Every error leaving the Storage or Security tier is wrapped in a ResultError with `source_tier` set.
- The UI tier receives only ResultError objects — no raw exceptions propagate to the UI.
- source_tier values are one of: `storage`, `security`, `service`, `ui`.

### SMR-05 — UI Error Rendering [MVP]
**Requirement**: The UI tier shall render a user-safe error state for every ResultError it receives, without exposing machine-readable codes or stack traces to the user.

**User Story**: As a user, I want error messages to be clear and safe so I am never shown internal codes or stack traces.

**Acceptance Criteria**:
- All ResultError responses are shown as user-friendly messages in the UI.
- No machine-readable error codes or stack traces are displayed to the user.
- The full error detail (code + source_tier) is logged at WARNING or ERROR level for diagnostics.

### SMR-06 — Startup Data Directory Verification [MVP]
**Requirement**: On startup, the app shall verify the data directory exists and is writable; create it if absent; refuse to launch if not writable, showing a clear startup error.

**User Story**: As a user, I want the app to set up its storage directory automatically on first run so I don't need to configure anything manually.

**Acceptance Criteria**:
- If data directory does not exist, it is created on startup with appropriate permissions.
- If data directory exists but is not writable, a clear startup error is displayed and the app does not launch.
- Successful directory verification is logged at INFO level.

### SMR-07 — Startup Storage Integrity Check [MVP]
**Requirement**: On startup, if the primary persistence store is unreadable or structurally invalid, the app shall log the error, preserve the corrupt store artifact with timestamp suffix, initialize a fresh store, and display a user-visible warning.

**User Story**: As a user, I want the app to recover gracefully from a corrupt data file so I am not permanently locked out, and my corrupt file is preserved for potential recovery.

**Acceptance Criteria**:
- If the persistence store is absent on first launch, app initializes fresh storage without error.
- If the persistence store is present and valid, app loads normally.
- If the persistence store is present but structurally invalid, the corrupt artifact is renamed with timestamp, a fresh store is initialized, and a warning is shown to the user.
- The rename and recovery are logged at ERROR level.

### SMR-08 — Storage Schema Version Guard [MVP]
**Requirement**: The persistence layer shall track schema version through migration metadata. The app shall refuse to write if stored version is higher than the app's supported version.

**User Story**: As a developer, I want schema version checking so that an older app version never silently corrupts data written by a newer version.

**Acceptance Criteria**:
- Migration metadata exposes the active schema revision.
- App logs and refuses to write if stored schema revision is higher than the app's supported revision.
- App proceeds normally if stored schema revision is less than or equal to app-supported revision.

### SMR-09 — Configuration Management [MVP]
**Requirement**: Configuration stored in `config.json` with defined keys and defaults. Unknown keys ignored. Missing keys use defaults. Invalid values fall back to defaults with a WARNING log.

**User Story**: As a developer, I want a well-defined configuration contract so that config changes are forward and backward compatible and never silently corrupt behavior.

**Acceptance Criteria**:
- All supported config keys have documented defaults.
- Unknown keys in config.json are silently ignored (forward compatibility).
- Missing keys use documented defaults (backward compatibility).
- Invalid key values produce a WARNING log and fall back to default.

### SMR-10 — Supported Configuration Keys [MVP]
**Requirement**: MVP supported config keys: `log_level` (default: "INFO"), `data_dir` (default: platform app data directory), `inactivity_timeout_minutes` (default: 15), `max_notes` (default: 10000).

**User Story**: As a developer or power user, I want documented configuration keys so I can customize app behavior without code changes.

**Acceptance Criteria**:
- All four keys are recognized and applied at runtime.
- `inactivity_timeout_minutes` controls the SRG-21 unlock expiry timer.
- `max_notes` controls the REQ-23 capacity limit.
- Each key's default value is applied when the key is absent from config.json.

### SMR-11 — Application Version Identity [MVP]
**Requirement**: The app shall embed a semantic version string accessible at runtime, displayed in an About/Help surface, and written to the startup diagnostic log at INFO level.

**User Story**: As a user or support engineer, I want to know exactly which version of the app is running so that bug reports and support requests can be matched to the correct release.

**Acceptance Criteria**:
- App version is displayed in an About or Help surface in the UI.
- App version is logged at INFO level on startup.
- Version follows semantic versioning format (e.g., "1.0.0").

### SMR-12 — Graceful Shutdown [MVP]
**Requirement**: On graceful shutdown, any in-progress storage write shall be allowed to complete before the process exits.

**User Story**: As a user, I want the app to finish saving before it closes so closing the window never causes data loss.

**Acceptance Criteria**:
- Closing the app window or receiving a clean OS exit signal does not interrupt an active atomic write.
- The process exits only after the current storage operation has committed or explicitly rolled back.
- Graceful shutdown is logged at INFO level.

## Web and Multi-User Requirements

### WEB-01 — Authenticated Account Required [MVP]
**Requirement**: The system shall require authenticated user accounts for all note operations.

**User Story**: As a user, I want to sign in before accessing notes so that my data is protected behind authentication.

**Acceptance Criteria**:
- Unauthenticated requests to note routes are redirected to sign-in (HTML) or rejected with 401 (API).
- Authenticated users can access note routes normally.
- Logout invalidates the active session and blocks further note access until sign-in.

### WEB-02 — Per-User Data Isolation [MVP]
**Requirement**: All note reads/writes shall be scoped to the authenticated user identity; users shall not access other users' notes.

**User Story**: As a user, I want to see only my notes so that other users cannot view or modify my data.

**Acceptance Criteria**:
- List/search endpoints return only notes owned by the authenticated user.
- Accessing another user's note ID returns not-found or forbidden without exposing ownership details.
- Create/update/delete operations always enforce owner_user_id scoping server-side.

### WEB-03 — HTTP JSON API Coverage [MVP]
**Requirement**: The system shall expose HTTP JSON APIs for create, edit, delete, list, search, and restore operations.

**User Story**: As a frontend/client developer, I want stable note APIs so that the web client can perform all core workflows through server contracts.

**Acceptance Criteria**:
- JSON endpoints exist for create, edit, delete, list, search, and restore.
- Each endpoint returns structured success and error payloads.
- Endpoint behavior matches REQ and SRG rules.

### WEB-04 — Web Client Uses Public APIs Only [MVP]
**Requirement**: The web client shall consume only public API endpoints and shall not access storage/security internals directly.

**User Story**: As an architect, I want strict UI-to-service boundaries so that storage/security changes do not require client rewrites.

**Acceptance Criteria**:
- UI code has no direct imports of repository or crypto modules.
- UI interactions use HTTP endpoint calls (directly or via HTMX).
- Boundary violations fail architecture checks.

### WEB-05 — Session Expiry by Inactivity [MVP]
**Requirement**: Session authentication shall expire after inactivity and require re-authentication.

**User Story**: As a security-conscious user, I want inactive sessions to expire automatically so that unattended browsers cannot continue using my account.

**Acceptance Criteria**:
- Session expires after configured inactivity window (default 15 minutes).
- After expiry, note operations require re-authentication.
- Activity refreshes last-active timestamp and extends valid session window.

### WEB-06 — Server-Side Authorization on Every Endpoint [MVP]
**Requirement**: API endpoints shall enforce authorization checks server-side for every request.

**User Story**: As a security owner, I want authorization enforced on the server so client-side bypasses cannot access protected actions.

**Acceptance Criteria**:
- Every protected endpoint validates authenticated identity.
- Every protected note action validates resource ownership.
- Missing/invalid auth context is rejected before service-layer mutation.

### WEB-07 — Transactional Multi-User Storage Integrity [MVP]
**Requirement**: Server-side storage shall support concurrent multi-user access with transactional integrity.

**User Story**: As a user, I want my saves and edits to remain correct even when other users are active at the same time.

**Acceptance Criteria**:
- Concurrent writes from different users do not corrupt data.
- Failed writes roll back cleanly with no partial commits.
- Optimistic concurrency conflict behavior remains enforced for same-note collisions.

### WEB-08 — Shared Persistent Demo Environment [MVP]
**Requirement**: Deployment shall support at least one shared persistent environment for instructor/demo review.

**User Story**: As an instructor or reviewer, I want a persistent deployed instance so that I can evaluate the application without local setup.

**Acceptance Criteria**:
- One shared environment is reachable for review.
- Data persists across app restarts in that environment.
- Basic health/status endpoint confirms service availability.