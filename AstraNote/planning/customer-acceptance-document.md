# Customer Acceptance Document — AstraNotes MVP

**Project**: AstraNotes  
**Version**: 1.1  
**Prepared**: 2026-06-05  
**Purpose**: This document records the agreed acceptance criteria for every user story in the AstraNotes MVP. The checklist boxes capture implementation evidence; the section sign-off lines confirm stakeholder acceptance of each major part, and the final release sign-off confirms overall release readiness.

---

## How to Use This Document

1. Each section covers one user story group (feature area).
2. Each story has a plain-English summary and simplified acceptance checklist; the stakeholder signs off at the end of each major part.
3. The developer checks off each criterion when implemented and tested; those boxes are evidence, not stakeholder approval.
4. The stakeholder reviews and signs off at the end of each part once the grouped stories are acceptable.
5. Release may only proceed after all in-scope MVP part sign-offs are completed (with Post-MVP sections explicitly deferred) and the Final Release Sign-Off (last section) is signed.

## Current Acceptance Status Snapshot (2026-06-05)

| Acceptance Area | Current Status | Notes |
|---|---|---|
| Part 1 — Core Note Features (REQ-01 to REQ-28) | 🟢 Ready for review | Implemented in MVP scope with supporting test and traceability evidence. |
| Part 2 — Quality/Performance/Architecture (in-scope NFR items) | 🟢 Ready for review | NFR-06/07/08/09 and architecture/testability criteria have evidence; Post-MVP items remain deferred. |
| Part 3 — Security and Governance (in-scope SRG items) | 🟢 Ready for review | Security controls and verification evidence are present for MVP scope; Post-MVP SRG items are deferred. |
| Part 4 — Serviceability/Manageability (in-scope SMR items) | 🟢 Ready for review | Startup guards, error mapping, and safe UI error handling are now explicitly reflected in UML + traceability. |
| Part 5 — Web Multi-User Foundations | 🔵 Deferred [Post-MVP] | Explicitly out of current single-user MVP release baseline. |

---

## Global Definition of Done

Every user story in this document is considered **Done** only when ALL of the following are true:

- ✅ In Scope — All acceptance criteria in this document for that story are met
- ✅ In Scope — Automated tests covering the story pass with no failures
- ✅ In Scope — No note content (title, body) ever appears in log files or error messages shown to the user
- ✅ In Scope — All data is saved reliably — a successful save means the data is on disk before the app reports success
- ✅ In Scope — The app does not crash on any user input, valid or invalid
- ✅ In Scope — For any story marked [Post-MVP], deferral is explicitly documented and accepted in release gates
- ✅ In Scope — The requirement ID is referenced in the associated code commit

---

## Part 1 — Core Note Features

---

### Feature: Create Note

#### US-REQ-01 · Create a New Note
> *As a user, I want to create a new note so that I can capture ideas quickly.*

**Acceptance Checklist:**
- [x] I can create a note by entering a title; body is optional
- [x] A note with no title is rejected with a clear validation message
- [x] The note appears in my notes list immediately after saving


---

#### US-REQ-02 · Title and Body Validation
> *As a user, I want the app to validate my note title so that invalid characters are caught before saving.*

**Acceptance Checklist:**
- [x] Titles accept letters (including accented/Unicode), numbers, spaces, and . , - ' " @ # & : ; ! ? ( ) [ ] / + _ ¿ ¡
- [x] Titles reject unsupported symbols and newlines with a clear message
- [x] Titles over 255 characters are rejected
- [x] Note bodies over 10,000 characters are rejected


---

#### US-REQ-03 · Duplicate Title Auto-Rename
> *As a user, I want the app to handle duplicate note titles automatically so that I don't lose a new note because a title already exists.*

**Acceptance Checklist:**
- [x] If "Plan" already exists and I save another note called "Plan", it saves as "Plan1"
- [x] If "Plan" and "Plan1" exist, the next is saved as "Plan2"
- [x] I am not shown an error — the renaming happens silently


---

#### US-REQ-04 · Note Saved Reliably
> *As a user, I want my notes to be saved reliably so that I can access them after closing the app.*

**Acceptance Checklist:**
- [x] Notes are still present after closing and reopening the app
- [x] Each note has a unique identity that never changes
- [x] If saving fails, the app shows an error and does not save corrupted data


---

### Feature: Edit Note

#### US-REQ-05 · Edit an Existing Note
> *As a user, I want to edit an existing note so that I can update its content.*

**Acceptance Checklist:**
- [x] I can open an existing note and change its title and/or body
- [x] Saving without making changes is allowed and does not alter the note
- [x] The updated note appears correctly in the list after saving


---

#### US-REQ-06 · Edit Title Validation
> *As a user, I want the same title validation rules applied during editing so that my notes stay consistent.*

**Acceptance Checklist:**
- [x] The same character and length rules from creation apply when editing a title
- [x] Clearing the title and saving is rejected with a clear message


---

#### US-REQ-07 · Duplicate Title on Edit
> *As a user, I want the app to handle title conflicts during editing automatically so that my edits don't overwrite another note's identity.*

**Acceptance Checklist:**
- [x] If I rename a note to a title that another note already has, a suffix is added automatically
- [x] Saving a note with its current unchanged title is not treated as a duplicate


---

#### US-REQ-08 · Edit Saved Reliably
> *As a user, I want my edits saved reliably so that changes persist after closing the app.*

**Acceptance Checklist:**
- [x] Edited content is present after closing and reopening the app
- [x] The note's original creation date does not change after editing
- [x] If saving fails, the previous version of the note is preserved


---

### Feature: Delete Note

#### US-REQ-09 · Delete Confirmation
> *As a user, I want to be asked to confirm before a note is deleted so that I don't accidentally lose my work.*

**Acceptance Checklist:**
- [x] Deleting a note shows a confirmation dialog displaying the note's title
- [x] The dialog states the action cannot be undone
- [x] Cancelling the dialog leaves the note untouched


---

#### US-REQ-10 · Delete Executes and Handles Errors
> *As a user, I want a confirmed deletion to move the note out of active views while preserving recovery during retention.*

**Acceptance Checklist:**
- [x] After confirmation, the note is removed from active list/search views and moved to Trash
- [x] If deletion fails, the note remains intact and I see an error message
- [x] The app does not crash if I try to delete a note that no longer exists


---

#### US-REQ-11 · Notes List Updates After Delete
> *As a user, I want the notes list to update immediately after deletion so that I always see an accurate view.*

**Acceptance Checklist:**
- [x] The deleted note disappears from the list immediately
- [x] If I deleted the last note, I see an empty-state message
- [x] If other notes remain, the list shows them without requiring a manual refresh


---

### Feature: List Notes

#### US-REQ-12 · Notes List Display
> *As a user, I want to see all my notes in a clear, ordered list so I can quickly scan and find what I need.*

**Acceptance Checklist:**
- [x] Notes are displayed newest first
- [x] Titles longer than 40 characters are truncated with "…" (full title available via tooltip)
- [x] In the editor panel, directly under `Created:`, display `Modified: Month DD, YYYY HH:MM AM/PM PST/PDT`


---

#### US-REQ-13 · Empty State Message
> *As a user, I want to see a helpful message when I have no notes so that I am guided to create one.*

**Acceptance Checklist:**
- [x] When no notes exist, the list area shows: "No notes yet. Create your first note."
- [x] After creating the first note, the empty state is replaced by the note list


---

#### US-REQ-14 · List Always Up to Date
> *As a user, I want the notes list to always reflect the latest state so I never see stale data.*

**Acceptance Checklist:**
- [x] After creating, editing, or deleting a note, the list updates without requiring a manual refresh
- [x] The newest-first sort order is reapplied after each update


---

### Feature: Search Notes

#### US-REQ-15 · Search by Title or Content
> *As a user, I want to search my notes by title or content so I can locate specific information efficiently.*

**Acceptance Checklist:**
- [x] Typing in the search bar filters notes that match in title or body (case-insensitive)
- [x] The results update as I type
- [x] Typing symbols like @ or # in the search does not cause errors
- [x] Clearing the search bar restores the full list


---

#### US-REQ-16 · Search Edge Cases
> *As a user, I want clear feedback when my search returns no results so I'm not confused by a blank screen.*

**Acceptance Checklist:**
- [x] Searching with only spaces shows the full note list (treated as no search)
- [x] A search with no matches shows: "No notes match your search."
- [x] Searching when no notes exist shows the empty-state message, not a "no results" message


---

### Feature: Lists in Notes

#### US-REQ-17 · Bullet and Checkbox Lists
> *As a user, I want to structure my notes with bullet and checkbox lists so I can organize tasks and ideas clearly.*

**Acceptance Checklist:**
- [x] I can add bullet list items to a note body
- [x] I can add checkbox list items to a note body
- [x] I can edit the text of existing list items without breaking the list


---

#### US-REQ-18 · List Formatting Persists
> *As a user, I want my list formatting to stay intact after reopening the app so I do not lose note structure.*

**Acceptance Checklist:**
- [x] Bullet and checkbox lists look the same after saving, closing, and reopening the app
- [x] Existing checklist and bullet formatting remains intact after save/reopen cycles


---

#### US-REQ-19 · Checkbox Toggle Saves Immediately
> *As a user, I want to check and uncheck tasks so I can track progress directly in my notes.*

**Acceptance Checklist:**
- [x] Clicking a checkbox toggles it between checked and unchecked
- [x] The toggled state is saved immediately and is still present after app restart
- [x] Toggling one checkbox does not affect other list items


---

### Feature: Text Formatting

#### US-REQ-20 · Apply Bold, Italic, Underline
> *As a user, I want to format text for emphasis so my notes are easier to scan.*

**Acceptance Checklist:**
- [x] I can apply bold, italic, and underline to selected text in the note body
- [x] Formatting applies only to the selected text
- [x] If no text is selected, formatting does not change the note


---

#### US-REQ-21 · Formatting Does Not Corrupt Text
> *As a user, I want formatting tools to be safe so they do not corrupt unrelated text.*

**Acceptance Checklist:**
- [x] Applying formatting to body text does not alter the note title
- [x] Applying multiple overlapping formats does not delete surrounding text
- [x] Undo/redo of formatting restores the exact previous content


---

#### US-REQ-22 · Formatting Renders Consistently
> *As a user, I want formatting to render consistently so saved notes look the same across sessions.*

**Acceptance Checklist:**
- [x] Bold text renders as bold after save and reopen
- [x] Italic text renders as italic after save and reopen
- [x] Underline text renders consistently after save and reopen


---

### Feature: Note Capacity

#### US-REQ-23 · Large Note Collection Supported
> *As a user, I want to keep a large number of notes without unexpected failures.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — I can create up to 10,000 notes without errors
- [ ] ✅ In Scope — The app remains responsive when browsing and searching a full collection


---

#### US-REQ-24 · Note Limit Reached Message
> *As a user, I want a clear message when I hit the limit so I know what action to take.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — When at 10,000 notes, attempting to create a new note shows: "Note limit reached (10,000). Delete notes to create a new one."
- [ ] ✅ In Scope — No existing note is modified when the limit is enforced
- [ ] ✅ In Scope — Deleting a note and then creating one succeeds normally


---

### Feature: Note Privacy

#### US-REQ-25 · Mark Note as Private
> *As a user, I want to mark sensitive notes as private so they are handled with extra discretion.*

**Acceptance Checklist:**
- [x] Each note has a control to mark it private or non-private
- [x] I can change the private status of a note after it is created
- [x] Changing private status on one note does not affect other notes


---

#### US-REQ-26 · Private Status Visible and Persisted
> *As a user, I want to quickly identify which notes are private and trust that this setting is saved.*

**Acceptance Checklist:**
- [x] Private notes show a clear visual indicator in the notes list
- [x] The private status is retained after closing and reopening the app
- [x] Non-private notes do not show the private indicator


---

#### US-REQ-27 · Private Note Body Hidden in List and Search
> *As a user, I want private note previews hidden so sensitive content is not exposed while browsing.*

**Acceptance Checklist:**
- [x] Private notes do not show body preview text in the notes list
- [x] Private notes may appear in search results by title match, but the body preview is hidden
- [x] Opening a private note in the editor still shows full content after unlocking


---

**Part 1 sign-off:** _________________________ Date: _________

## Part 2 — Quality, Performance, and Architecture

*This section covers non-functional stories. Acceptance is confirmed through test results rather than manual walkthrough. The stakeholder signs off to confirm the results have been reviewed.*

---

### Feature Group: Performance

#### US-NFR-04 · Concurrent Edit Safety [Post-MVP]
> *As a user, I want concurrent edits handled safely so that newer note changes are not silently overwritten.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — If two edits target the same note, the newer one wins and the older one is rejected with a conflict message
- [ ] 🔵 Deferred [Post-MVP] — The winning note's content is preserved exactly


---

#### US-NFR-06/07 · Responsive Web/API Operation
> *As a web user, I want low-latency interactions so the app feels responsive in-browser.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — With up to 5,000 notes, opening, listing, and searching notes complete in under 120 ms (p95)
- [ ] ✅ In Scope — Creating and saving notes complete in under 180 ms (p95)
- [ ] ✅ In Scope — Performance benchmark results reviewed and attached: _______________


---

#### US-NFR-09 · Saves Are Durable
> *As a user, I want successful saves to be durable so notes are not lost after app or system interruption.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — A note reported as saved is present on disk — confirmed by benchmark test TP-P05
- [ ] ✅ In Scope — No successfully saved note is lost after a simulated restart


---

### Feature Group: Keyboard Accessibility [Post-MVP]

#### US-NFR-10 · Keyboard-Only Desktop Operation
> *As a desktop power user, I want to complete core actions by keyboard only for speed and accessibility.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — I can create, open, edit, save, search, navigate the list, toggle checkboxes, and delete notes using only the keyboard
- [ ] 🔵 Deferred [Post-MVP] — Delete confirmation is actionable via keyboard only


---

### Feature Group: Architecture and Testability

#### US-NFR-13/14 · Testable Three-Tier Architecture
> *As an architect, I want dependency boundaries enforced so we can evolve storage/security safely without rewriting UI.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — UI code has no direct imports of storage or security classes
- [ ] ✅ In Scope — Unit tests run with fake/in-memory storage — no real file I/O required
- [ ] ✅ In Scope — Swapping the storage backend does not require UI code changes


---

#### US-NFR-15 · Automated Test Coverage
> *As a maintainer, I want layered automated tests so regressions are caught in the component where they occur.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Automated tests exist and pass for: UI workflow logic, security policy, and storage persistence
- [ ] ✅ In Scope — Test run results reviewed and test suite passes: ☐ Yes
- [ ] ✅ In Scope — Test run date and result summary: _______________


---

**Part 2 sign-off:** _________________________ Date: _________

## Part 3 — Security and Governance

*Each item below represents a security commitment. Sign-off confirms the implementation has been reviewed and evidence has been sighted.*

---

#### US-SRG-01/02 · All Note Content Encrypted at Rest
> *As a user, I want all note content encrypted at rest so direct file access cannot expose my notes.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Inspecting persisted note records directly shows no readable note titles or bodies
- [ ] ✅ In Scope — All notes (private and non-private) are encrypted using strong authenticated encryption
- [ ] ✅ In Scope — Evidence reviewed (test TP-SV01 result): _______________


---

#### US-SRG-05 · All Operations Audited
> *As an auditor, I want complete operation logs so I can trace who did what and when.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Create, edit, delete, and restore operations each produce an audit log entry
- [ ] ✅ In Scope — Each entry includes timestamp, action type, note ID, and outcome
- [ ] ✅ In Scope — The audit log contains no private note content


---

#### US-SRG-08 · Version History Is Immutable [Post-MVP]
> *As a user, I want immutable history so prior note states remain trustworthy and recoverable.*

**Acceptance Checklist:**
- [Deferred Post-MVP] Editing a note creates a new version record
- [Deferred Post-MVP] Prior version records cannot be modified


---

#### US-SRG-10/11 · Soft Delete with 15-Day Recovery
> *As a user, I want accidental deletions recoverable for a limited period.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Deleted notes are hidden from the list and search immediately
- [ ] ✅ In Scope — A deleted note can be restored within 15 days
- [ ] ✅ In Scope — After 15 days, the note is no longer restorable


---

#### US-SRG-13 · Restore Preserves Identity and Auditability
> *As a user, I want restored notes to keep their identity and audit trail.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Restore keeps the original note ID
- [ ] ✅ In Scope — Restore creates an audit entry


---

#### US-SRG-14/15 · Errors Never Crash or Corrupt Data
> *As a user, I want clear, safe errors instead of crashes so I can recover from failures.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Invalid operations (bad input, missing note, disk error) show a clear message and do not crash the app
- [ ] ✅ In Scope — A failed save or delete leaves my data exactly as it was before the operation


---

#### US-SRG-18–20 · Private Note Passphrase Unlock
> *As a user, I want my private notes locked behind a passphrase so that only I can access them.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Opening a private note without authenticating redirects to the passphrase prompt
- [ ] ✅ In Scope — The correct passphrase grants access; an incorrect one is denied with a generic error message
- [ ] ✅ In Scope — Once authenticated, I can open all private notes in the same session without re-entering the passphrase


---

#### US-SRG-21 · Private Notes Re-Lock After Inactivity
> *As a user, I want my private notes to re-lock after inactivity so that leaving my device unattended does not expose my private content.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — After 15 minutes of inactivity, the next attempt to open a private note prompts for the passphrase again
- [ ] ✅ In Scope — Active use resets the inactivity timer


---

#### US-SRG-22/23 · Brute-Force Lockout
> *As a security owner, I want consecutive unlock failures to trigger an escalating lockout so that persistent brute-force attempts are blocked.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — After 5 wrong passphrase attempts, unlock is locked out for at least 5 minutes
- [ ] ✅ In Scope — Each subsequent lockout is double the previous duration
- [ ] ✅ In Scope — Lockout state resets on app restart as defined by the MVP in-memory session policy
- [ ] ✅ In Scope — The unlock screen shows the remaining lockout time


---

#### US-SRG-24 · Unlock Errors Give No Information to Attackers
> *As a security owner, I want all unlock failure responses to be indistinguishable so that an attacker cannot determine the cause of failure.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — A wrong passphrase and an internal error produce identical error messages
- [ ] ✅ In Scope — No additional detail differentiates the two failure types in anything the user can see


---

#### US-SRG-25/26 · Encryption Key Derived Securely; Passphrase Never Stored
> *As a user, I want my private note encryption key derived securely from my passphrase so that my notes cannot be decrypted without knowing my passphrase.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — The passphrase is never written to disk or log files — confirmed by test TP-SV05
- [ ] ✅ In Scope — The encryption key is derived using a strong key-derivation function with high iteration count
- [ ] ✅ In Scope — Evidence reviewed: _______________


---

**Part 3 sign-off:** _________________________ Date: _________

## Part 4 — Serviceability and Manageability

*This section covers operational requirements for a production-quality 3-tier application.*

---

#### US-SMR-01/02/03 · Diagnostic Logging
> *As a developer or support engineer, I want structured diagnostic logs so I can trace and resolve issues.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — A diagnostic log file is created in the app data directory during normal operation
- [ ] ✅ In Scope — Log entries include a timestamp, severity level, and the tier that produced them (UI / Service / Storage / Security)
- [ ] 🔵 Deferred [Post-MVP] — Log verbosity can be changed in the config file without restarting the app
- [ ] ✅ In Scope — Opening the log file shows no note titles or body text


---

#### US-SMR-04/05 · Errors Are Tier-Attributed and User-Safe
> *As a user and developer, I want errors labeled by tier and shown safely so that the user sees a friendly message and the developer sees the full detail.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — When a storage or security error occurs, the user sees a clear, friendly message — no codes or stack traces
- [ ] ✅ In Scope — The full technical error detail appears in the diagnostic log
- [ ] ✅ In Scope — The log entry identifies which tier (storage / security / service / UI) produced the error


---

#### US-SMR-06/07/08 · Reliable Startup and Data Protection
> *As a user, I want the app to start reliably and protect my data if something goes wrong with the data file.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — The app creates its data directory automatically on first launch without any setup steps from me
- [ ] ✅ In Scope — If the app cannot write to its data directory, I see a clear startup error and the app does not launch in a broken state
- [ ] 🔵 Deferred [Post-MVP] — If the data file is corrupted, the app preserves the corrupted file for recovery, starts fresh, and warns me — it does not silently discard data
- [ ] 🔵 Deferred [Post-MVP] — The app refuses to open a data file that was written by a newer version of the app


---

#### US-SMR-09/10 · Configuration Is Predictable
> *As a developer, I want a well-defined configuration contract so that config changes are safe and predictable.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — Unknown keys in the config file are silently ignored — the app still runs
- [ ] ✅ In Scope — Missing keys use documented defaults — the app still runs
- [ ] ✅ In Scope — The configurable inactivity timeout and note limit behave as specified in the config file


---

#### US-SMR-11 · App Version Is Visible
> *As a user or support engineer, I want to know which version of the app is running.*

**Acceptance Checklist:**
- [ ] ✅ In Scope — The app version is visible in an About or Help surface
- [ ] ✅ In Scope — The app version appears in the log file at startup


---

#### US-SMR-12 · Closing the App Never Loses In-Progress Saves [Post-MVP]
> *As a user, I want the app to finish saving before it closes so closing the window never causes data loss.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — Closing the app window while a save is in progress does not interrupt it
- [ ] 🔵 Deferred [Post-MVP] — The persistence transaction is not partially committed after any shutdown


---

**Part 4 sign-off:** _________________________ Date: _________

## Part 5 — Web Multi-User Foundations [Post-MVP]

*This section covers required web-specific acceptance criteria for authentication, authorization, API boundaries, and shared deployment readiness.*

---

#### US-WEB-01 · Authenticated Access Required
> *As a user, I want sign-in required for note operations so my data is protected from anonymous access.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — Unauthenticated access to note routes is blocked
- [ ] 🔵 Deferred [Post-MVP] — Sign-in creates a valid session; sign-out invalidates it immediately


---

#### US-WEB-02 / WEB-06 · Per-User Isolation and Server-Side Authorization
> *As a user, I want only my notes accessible and modifiable so no other user can access my data.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — I can only see my own notes in list/search views
- [ ] 🔵 Deferred [Post-MVP] — Direct access attempts to another user's note are denied without leaking ownership details
- [ ] 🔵 Deferred [Post-MVP] — Server enforces authorization checks for every protected endpoint


---

#### US-WEB-03 / WEB-04 · API Contract and UI Boundary
> *As an architect, I want the web UI to use public API routes only so internal storage/security modules remain isolated.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — JSON API endpoints exist for create/edit/delete/list/search/restore
- [ ] 🔵 Deferred [Post-MVP] — UI interactions occur through API calls (including HTMX interactions)
- [ ] 🔵 Deferred [Post-MVP] — UI code has no direct repository or crypto module access


---

#### US-WEB-05 · Session Inactivity Expiry
> *As a security-conscious user, I want inactive sessions to expire automatically so unattended browsers cannot continue using my account.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — Session expires after configured inactivity window (default 15 minutes)
- [ ] 🔵 Deferred [Post-MVP] — After expiry, protected actions require re-authentication


---

#### US-WEB-07 · Transactional Multi-User Integrity
> *As a user, I want concurrent activity from multiple users to never corrupt persisted note data.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — Concurrent writes by multiple users do not corrupt stored notes
- [ ] 🔵 Deferred [Post-MVP] — Failed writes roll back cleanly with no partial commits


---

#### US-WEB-08 · Shared Persistent Review Environment
> *As an instructor/reviewer, I want one shared deployed environment so I can evaluate the system without local setup.*

**Acceptance Checklist:**
- [ ] 🔵 Deferred [Post-MVP] — A shared environment is reachable for review
- [ ] 🔵 Deferred [Post-MVP] — Data persists across app restarts in that environment
- [ ] 🔵 Deferred [Post-MVP] — Health/status endpoint confirms application availability


---

## Final Release Sign-Off

This section must be completed before the AstraNotes MVP is released.

**Confirming that:**
- Part 1 (Functional) sign-off above is completed
- Part 2 (Quality/Performance) sign-off above is completed
- Part 3 (Security) sign-off above is completed and evidence attached
- Part 4 (Serviceability) sign-off above is completed; Post-MVP lines are explicitly deferred
- All in-scope MVP part sign-offs above are completed; Part 5 (Web Multi-User Foundations) remains explicitly deferred [Post-MVP]
- All automated tests pass (test run result attached: _______________)
- All release gates in `planning/release-gates.md` are satisfied
- No open P0 or P1 defects exist

| Role | Name | Signature | Date |
|---|---|---|---|
| Developer | | | |
| Product Owner / Stakeholder | | | |

**Release approved:** ☐ Yes — MVP is ready to ship
