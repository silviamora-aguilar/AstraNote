# Customer Acceptance Document — AstraNotes MVP

**Project**: AstraNotes  
**Version**: 1.0  
**Prepared**: 2026-05-11  
**Purpose**: This document records the agreed acceptance criteria for every user story in the AstraNotes MVP. Stakeholder sign-off on each section confirms that the delivered feature meets the agreed definition of done.

---

## How to Use This Document

1. Each section covers one user story group (feature area).
2. Each story has a plain-English summary, simplified acceptance checklist, and a sign-off line.
3. The developer checks off each criterion when implemented and tested.
4. The stakeholder reviews and signs off on the section.
5. Release may only proceed after all sign-off lines are completed and the Final Release Sign-Off (last section) is signed.

---

## Global Definition of Done

Every user story in this document is considered **Done** only when ALL of the following are true:

- [ ] All acceptance criteria in this document for that story are met
- [ ] Automated tests covering the story pass with no failures
- [ ] No note content (title, body) ever appears in log files or error messages shown to the user
- [ ] All data is saved reliably — a successful save means the data is on disk before the app reports success
- [ ] The app does not crash on any user input, valid or invalid
- [ ] The feature is keyboard-operable on desktop without a mouse
- [ ] User data isolation and authorization checks are enforced server-side for all protected note actions
- [ ] The requirement ID is referenced in the associated code commit

---

## Part 1 — Core Note Features

---

### Feature: Create Note

#### US-REQ-01 · Create a New Note
> *As a user, I want to create a new note so that I can capture ideas quickly.*

**Acceptance Checklist:**
- [ ] I can create a note by entering a title; body is optional
- [ ] A note with no title is rejected with a clear validation message
- [ ] The note appears in my notes list immediately after saving

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-02 · Title and Body Validation
> *As a user, I want the app to validate my note title so that invalid characters are caught before saving.*

**Acceptance Checklist:**
- [ ] Titles accept letters (including accented/Unicode), numbers, spaces, and . , - ' "
- [ ] Titles reject @ # $ % & and newlines with a clear message
- [ ] Titles over 255 characters are rejected
- [ ] Note bodies over 10,000 characters are rejected

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-03 · Duplicate Title Auto-Rename
> *As a user, I want the app to handle duplicate note titles automatically so that I don't lose a new note because a title already exists.*

**Acceptance Checklist:**
- [ ] If "Plan" already exists and I save another note called "Plan", it saves as "Plan1"
- [ ] If "Plan" and "Plan1" exist, the next is saved as "Plan2"
- [ ] I am not shown an error — the renaming happens silently

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-04 · Note Saved Reliably
> *As a user, I want my notes to be saved reliably so that I can access them after closing the app.*

**Acceptance Checklist:**
- [ ] Notes are still present after closing and reopening the app
- [ ] Each note has a unique identity that never changes
- [ ] If saving fails, the app shows an error and does not save corrupted data

**Sign-off:** _________________________ Date: _________

---

### Feature: Edit Note

#### US-REQ-05 · Edit an Existing Note
> *As a user, I want to edit an existing note so that I can update its content.*

**Acceptance Checklist:**
- [ ] I can open an existing note and change its title and/or body
- [ ] Saving without making changes is allowed and does not alter the note
- [ ] The updated note appears correctly in the list after saving

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-06 · Edit Title Validation
> *As a user, I want the same title validation rules applied during editing so that my notes stay consistent.*

**Acceptance Checklist:**
- [ ] The same character and length rules from creation apply when editing a title
- [ ] Clearing the title and saving is rejected with a clear message

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-07 · Duplicate Title on Edit
> *As a user, I want the app to handle title conflicts during editing automatically so that my edits don't overwrite another note's identity.*

**Acceptance Checklist:**
- [ ] If I rename a note to a title that another note already has, a suffix is added automatically
- [ ] Saving a note with its current unchanged title is not treated as a duplicate

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-08 · Edit Saved Reliably
> *As a user, I want my edits saved reliably so that changes persist after closing the app.*

**Acceptance Checklist:**
- [ ] Edited content is present after closing and reopening the app
- [ ] The note's original creation date does not change after editing
- [ ] If saving fails, the previous version of the note is preserved

**Sign-off:** _________________________ Date: _________

---

### Feature: Delete Note

#### US-REQ-09 · Delete Confirmation
> *As a user, I want to be asked to confirm before a note is deleted so that I don't accidentally lose my work.*

**Acceptance Checklist:**
- [ ] Deleting a note shows a confirmation dialog displaying the note's title
- [ ] The dialog states the action cannot be undone
- [ ] Cancelling the dialog leaves the note untouched

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-10 · Delete Executes and Handles Errors
> *As a user, I want a confirmed deletion to remove the note immediately and permanently so that my storage stays clean.*

**Acceptance Checklist:**
- [ ] After confirmation, the note is removed from storage completely
- [ ] If deletion fails, the note remains intact and I see an error message
- [ ] The app does not crash if I try to delete a note that no longer exists

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-11 · Notes List Updates After Delete
> *As a user, I want the notes list to update immediately after deletion so that I always see an accurate view.*

**Acceptance Checklist:**
- [ ] The deleted note disappears from the list immediately
- [ ] If I deleted the last note, I see an empty-state message
- [ ] If other notes remain, the list shows them without requiring a manual refresh

**Sign-off:** _________________________ Date: _________

---

### Feature: List Notes

#### US-REQ-12 · Notes List Display
> *As a user, I want to see all my notes in a clear, ordered list so I can quickly scan and find what I need.*

**Acceptance Checklist:**
- [ ] Notes are displayed newest first
- [ ] Titles longer than 60 characters are truncated with "…"
- [ ] In the editor panel, directly under `Created:`, display `Modified: Month DD, YYYY HH:MM PST/PDT`

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-13 · Empty State Message
> *As a user, I want to see a helpful message when I have no notes so that I am guided to create one.*

**Acceptance Checklist:**
- [ ] When no notes exist, the list area shows: "No notes yet. Create your first note."
- [ ] After creating the first note, the empty state is replaced by the note list

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-14 · List Always Up to Date
> *As a user, I want the notes list to always reflect the latest state so I never see stale data.*

**Acceptance Checklist:**
- [ ] After creating, editing, or deleting a note, the list updates without requiring a manual refresh
- [ ] The newest-first sort order is reapplied after each update

**Sign-off:** _________________________ Date: _________

---

### Feature: Search Notes

#### US-REQ-15 · Search by Title or Content
> *As a user, I want to search my notes by title or content so I can locate specific information efficiently.*

**Acceptance Checklist:**
- [ ] Typing in the search bar filters notes that match in title or body (case-insensitive)
- [ ] The results update as I type
- [ ] Typing symbols like @ or # in the search does not cause errors
- [ ] Clearing the search bar restores the full list

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-16 · Search Edge Cases
> *As a user, I want clear feedback when my search returns no results so I'm not confused by a blank screen.*

**Acceptance Checklist:**
- [ ] Searching with only spaces shows the full note list (treated as no search)
- [ ] A search with no matches shows: "No notes match your search."
- [ ] Searching when no notes exist shows the empty-state message, not a "no results" message

**Sign-off:** _________________________ Date: _________

---

### Feature: Lists in Notes

#### US-REQ-17 · Bullet and Checkbox Lists
> *As a user, I want to structure my notes with bullet and checkbox lists so I can organize tasks and ideas clearly.*

**Acceptance Checklist:**
- [ ] I can add bullet list items to a note body
- [ ] I can add checkbox list items to a note body
- [ ] I can edit the text of existing list items without breaking the list

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-18 · List Formatting Persists
> *As a user, I want my list formatting to stay intact after reopening the app so I do not lose note structure.*

**Acceptance Checklist:**
- [ ] Bullet and checkbox lists look the same after saving, closing, and reopening the app
- [ ] Nesting up to 2 levels is preserved

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-19 · Checkbox Toggle Saves Immediately
> *As a user, I want to check and uncheck tasks so I can track progress directly in my notes.*

**Acceptance Checklist:**
- [ ] Clicking a checkbox toggles it between checked and unchecked
- [ ] The toggled state is saved immediately and is still present after app restart
- [ ] Toggling one checkbox does not affect other list items

**Sign-off:** _________________________ Date: _________

---

### Feature: Text Formatting

#### US-REQ-20 · Apply Bold, Italic, Underline
> *As a user, I want to format text for emphasis so my notes are easier to scan.*

**Acceptance Checklist:**
- [ ] I can apply bold, italic, and underline to selected text in the note body
- [ ] Formatting applies only to the selected text
- [ ] If no text is selected, formatting does not change the note

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-21 · Formatting Does Not Corrupt Text
> *As a user, I want formatting tools to be safe so they do not corrupt unrelated text.*

**Acceptance Checklist:**
- [ ] Applying formatting to body text does not alter the note title
- [ ] Applying multiple overlapping formats does not delete surrounding text
- [ ] Undo/redo of formatting restores the exact previous content

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-22 · Formatting Renders Consistently
> *As a user, I want formatting to render consistently so saved notes look the same across sessions.*

**Acceptance Checklist:**
- [ ] Bold text renders as bold after save and reopen
- [ ] Italic text renders as italic after save and reopen
- [ ] Underline text renders consistently after save and reopen

**Sign-off:** _________________________ Date: _________

---

### Feature: Note Capacity

#### US-REQ-23 · Large Note Collection Supported
> *As a user, I want to keep a large number of notes without unexpected failures.*

**Acceptance Checklist:**
- [ ] I can create up to 10,000 notes without errors
- [ ] The app remains responsive when browsing and searching a full collection

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-24 · Note Limit Reached Message
> *As a user, I want a clear message when I hit the limit so I know what action to take.*

**Acceptance Checklist:**
- [ ] When at 10,000 notes, attempting to create a new note shows: "Note limit reached (10,000). Delete notes to create a new one."
- [ ] No existing note is modified when the limit is enforced
- [ ] Deleting a note and then creating one succeeds normally

**Sign-off:** _________________________ Date: _________

---

### Feature: Note Privacy

#### US-REQ-25 · Mark Note as Private
> *As a user, I want to mark sensitive notes as private so they are handled with extra discretion.*

**Acceptance Checklist:**
- [ ] Each note has a control to mark it private or non-private
- [ ] I can change the private status of a note after it is created
- [ ] Changing private status on one note does not affect other notes

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-26 · Private Status Visible and Persisted
> *As a user, I want to quickly identify which notes are private and trust that this setting is saved.*

**Acceptance Checklist:**
- [ ] Private notes show a clear visual indicator in the notes list
- [ ] The private status is retained after closing and reopening the app
- [ ] Non-private notes do not show the private indicator

**Sign-off:** _________________________ Date: _________

---

#### US-REQ-27 · Private Note Body Hidden in List and Search
> *As a user, I want private note previews hidden so sensitive content is not exposed while browsing.*

**Acceptance Checklist:**
- [ ] Private notes do not show body preview text in the notes list
- [ ] Private notes may appear in search results by title match, but the body preview is hidden
- [ ] Opening a private note in the editor still shows full content after unlocking

**Sign-off:** _________________________ Date: _________

---

## Part 2 — Quality, Performance, and Architecture

*This section covers non-functional stories. Acceptance is confirmed through test results rather than manual walkthrough. The stakeholder signs off to confirm the results have been reviewed.*

---

### Feature Group: Performance

#### US-NFR-04 · Concurrent Edit Safety
> *As a user, I want concurrent edits handled safely so that newer note changes are not silently overwritten.*

**Acceptance Checklist:**
- [ ] If two edits target the same note, the newer one wins and the older one is rejected with a conflict message
- [ ] The winning note's content is preserved exactly

**Sign-off:** _________________________ Date: _________

---

#### US-NFR-06/07 · Responsive Web/API Operation
> *As a web user, I want low-latency interactions so the app feels responsive in-browser.*

**Acceptance Checklist:**
- [ ] With up to 5,000 notes, opening, listing, and searching notes complete in under 120 ms (p95)
- [ ] Creating and saving notes complete in under 180 ms (p95)
- [ ] Performance benchmark results reviewed and attached: _______________

**Sign-off:** _________________________ Date: _________

---

#### US-NFR-09 · Saves Are Durable
> *As a user, I want successful saves to be durable so notes are not lost after app or system interruption.*

**Acceptance Checklist:**
- [ ] A note reported as saved is present on disk — confirmed by benchmark test TP-P05
- [ ] No successfully saved note is lost after a simulated restart

**Sign-off:** _________________________ Date: _________

---

### Feature Group: Keyboard Accessibility

#### US-NFR-10 · Keyboard-Only Desktop Operation
> *As a desktop power user, I want to complete core actions by keyboard only for speed and accessibility.*

**Acceptance Checklist:**
- [ ] I can create, open, edit, save, search, navigate the list, toggle checkboxes, and delete notes using only the keyboard
- [ ] Delete confirmation is actionable via keyboard only

**Sign-off:** _________________________ Date: _________

---

### Feature Group: Architecture and Testability

#### US-NFR-13/14 · Testable Three-Tier Architecture
> *As an architect, I want dependency boundaries enforced so we can evolve storage/security safely without rewriting UI.*

**Acceptance Checklist:**
- [ ] UI code has no direct imports of storage or security classes
- [ ] Unit tests run with fake/in-memory storage — no real file I/O required
- [ ] Swapping the storage backend does not require UI code changes

**Sign-off:** _________________________ Date: _________

---

#### US-NFR-15 · Automated Test Coverage
> *As a maintainer, I want layered automated tests so regressions are caught in the component where they occur.*

**Acceptance Checklist:**
- [ ] Automated tests exist and pass for: UI workflow logic, security policy, and storage persistence
- [ ] Test run results reviewed and test suite passes: ☐ Yes
- [ ] Test run date and result summary: _______________

**Sign-off:** _________________________ Date: _________

---

## Part 3 — Security and Governance

*Each item below represents a security commitment. Sign-off confirms the implementation has been reviewed and evidence has been sighted.*

---

#### US-SRG-01/02 · All Note Content Encrypted at Rest
> *As a user, I want all note content encrypted at rest so direct file access cannot expose my notes.*

**Acceptance Checklist:**
- [ ] Inspecting persisted note records directly shows no readable note titles or bodies
- [ ] All notes (private and non-private) are encrypted using strong authenticated encryption
- [ ] Evidence reviewed (test TP-SV01 result): _______________

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-05 · All Operations Audited
> *As an auditor, I want complete operation logs so I can trace who did what and when.*

**Acceptance Checklist:**
- [ ] Create, edit, delete, and restore operations each produce an audit log entry
- [ ] Each entry includes timestamp, action type, note ID, and outcome
- [ ] The audit log contains no private note content

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-08 · Version History Is Immutable
> *As a user, I want immutable history so prior note states remain trustworthy and recoverable.*

**Acceptance Checklist:**
- [ ] Editing a note creates a new version record
- [ ] Prior version records cannot be modified

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-10/11 · Soft Delete with 30-Day Recovery
> *As a user, I want accidental deletions recoverable for a limited period.*

**Acceptance Checklist:**
- [ ] Deleted notes are hidden from the list and search immediately
- [ ] A deleted note can be restored within 30 days
- [ ] After 30 days, the note is no longer restorable

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-14/15 · Errors Never Crash or Corrupt Data
> *As a user, I want clear, safe errors instead of crashes so I can recover from failures.*

**Acceptance Checklist:**
- [ ] Invalid operations (bad input, missing note, disk error) show a clear message and do not crash the app
- [ ] A failed save or delete leaves my data exactly as it was before the operation

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-18–20 · Private Note Passphrase Unlock
> *As a user, I want my private notes locked behind a passphrase so that only I can access them.*

**Acceptance Checklist:**
- [ ] Opening a private note without authenticating redirects to the passphrase prompt
- [ ] The correct passphrase grants access; an incorrect one is denied with a generic error message
- [ ] Once authenticated, I can open all private notes in the same session without re-entering the passphrase

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-21 · Private Notes Re-Lock After Inactivity
> *As a user, I want my private notes to re-lock after inactivity so that leaving my device unattended does not expose my private content.*

**Acceptance Checklist:**
- [ ] After 15 minutes of inactivity, the next attempt to open a private note prompts for the passphrase again
- [ ] Active use resets the inactivity timer

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-22/23 · Brute-Force Lockout
> *As a security owner, I want consecutive unlock failures to trigger an escalating lockout so that persistent brute-force attempts are blocked.*

**Acceptance Checklist:**
- [ ] After 5 wrong passphrase attempts, unlock is locked out for at least 5 minutes
- [ ] Each subsequent lockout is double the previous duration
- [ ] The lockout is still active after closing and reopening the app during the lockout window
- [ ] The unlock screen shows the remaining lockout time

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-24 · Unlock Errors Give No Information to Attackers
> *As a security owner, I want all unlock failure responses to be indistinguishable so that an attacker cannot determine the cause of failure.*

**Acceptance Checklist:**
- [ ] A wrong passphrase and an internal error produce identical error messages
- [ ] No additional detail differentiates the two failure types in anything the user can see

**Sign-off:** _________________________ Date: _________

---

#### US-SRG-25/26 · Encryption Key Derived Securely; Passphrase Never Stored
> *As a user, I want my private note encryption key derived securely from my passphrase so that my notes cannot be decrypted without knowing my passphrase.*

**Acceptance Checklist:**
- [ ] The passphrase is never written to disk or log files — confirmed by test TP-SV05
- [ ] The encryption key is derived using a strong key-derivation function with high iteration count
- [ ] Evidence reviewed: _______________

**Sign-off:** _________________________ Date: _________

---

## Part 4 — Serviceability and Manageability

*This section covers operational requirements for a production-quality 3-tier application.*

---

#### US-SMR-01/02/03 · Diagnostic Logging
> *As a developer or support engineer, I want structured diagnostic logs so I can trace and resolve issues.*

**Acceptance Checklist:**
- [ ] A diagnostic log file is created in the app data directory during normal operation
- [ ] Log entries include a timestamp, severity level, and the tier that produced them (UI / Service / Storage / Security)
- [ ] Log verbosity can be changed in the config file without restarting the app
- [ ] Opening the log file shows no note titles or body text

**Sign-off:** _________________________ Date: _________

---

#### US-SMR-04/05 · Errors Are Tier-Attributed and User-Safe
> *As a user and developer, I want errors labeled by tier and shown safely so that the user sees a friendly message and the developer sees the full detail.*

**Acceptance Checklist:**
- [ ] When a storage or security error occurs, the user sees a clear, friendly message — no codes or stack traces
- [ ] The full technical error detail appears in the diagnostic log
- [ ] The log entry identifies which tier (storage / security / service / UI) produced the error

**Sign-off:** _________________________ Date: _________

---

#### US-SMR-06/07/08 · Reliable Startup and Data Protection
> *As a user, I want the app to start reliably and protect my data if something goes wrong with the data file.*

**Acceptance Checklist:**
- [ ] The app creates its data directory automatically on first launch without any setup steps from me
- [ ] If the app cannot write to its data directory, I see a clear startup error and the app does not launch in a broken state
- [ ] If the data file is corrupted, the app preserves the corrupted file for recovery, starts fresh, and warns me — it does not silently discard data
- [ ] The app refuses to open a data file that was written by a newer version of the app

**Sign-off:** _________________________ Date: _________

---

#### US-SMR-09/10 · Configuration Is Predictable
> *As a developer, I want a well-defined configuration contract so that config changes are safe and predictable.*

**Acceptance Checklist:**
- [ ] Unknown keys in the config file are silently ignored — the app still runs
- [ ] Missing keys use documented defaults — the app still runs
- [ ] The configurable inactivity timeout and note limit behave as specified in the config file

**Sign-off:** _________________________ Date: _________

---

#### US-SMR-11 · App Version Is Visible
> *As a user or support engineer, I want to know which version of the app is running.*

**Acceptance Checklist:**
- [ ] The app version is visible in an About or Help surface
- [ ] The app version appears in the log file at startup

**Sign-off:** _________________________ Date: _________

---

#### US-SMR-12 · Closing the App Never Loses In-Progress Saves
> *As a user, I want the app to finish saving before it closes so closing the window never causes data loss.*

**Acceptance Checklist:**
- [ ] Closing the app window while a save is in progress does not interrupt it
- [ ] The persistence transaction is not partially committed after any shutdown

**Sign-off:** _________________________ Date: _________

---

## Part 5 — Web Multi-User Foundations

*This section covers required web-specific acceptance criteria for authentication, authorization, API boundaries, and shared deployment readiness.*

---

#### US-WEB-01 · Authenticated Access Required
> *As a user, I want sign-in required for note operations so my data is protected from anonymous access.*

**Acceptance Checklist:**
- [ ] Unauthenticated access to note routes is blocked
- [ ] Sign-in creates a valid session; sign-out invalidates it immediately

**Sign-off:** _________________________ Date: _________

---

#### US-WEB-02 / WEB-06 · Per-User Isolation and Server-Side Authorization
> *As a user, I want only my notes accessible and modifiable so no other user can access my data.*

**Acceptance Checklist:**
- [ ] I can only see my own notes in list/search views
- [ ] Direct access attempts to another user's note are denied without leaking ownership details
- [ ] Server enforces authorization checks for every protected endpoint

**Sign-off:** _________________________ Date: _________

---

#### US-WEB-03 / WEB-04 · API Contract and UI Boundary
> *As an architect, I want the web UI to use public API routes only so internal storage/security modules remain isolated.*

**Acceptance Checklist:**
- [ ] JSON API endpoints exist for create/edit/delete/list/search/restore
- [ ] UI interactions occur through API calls (including HTMX interactions)
- [ ] UI code has no direct repository or crypto module access

**Sign-off:** _________________________ Date: _________

---

#### US-WEB-05 · Session Inactivity Expiry
> *As a security-conscious user, I want inactive sessions to expire automatically so unattended browsers cannot continue using my account.*

**Acceptance Checklist:**
- [ ] Session expires after configured inactivity window (default 15 minutes)
- [ ] After expiry, protected actions require re-authentication

**Sign-off:** _________________________ Date: _________

---

#### US-WEB-07 · Transactional Multi-User Integrity
> *As a user, I want concurrent activity from multiple users to never corrupt persisted note data.*

**Acceptance Checklist:**
- [ ] Concurrent writes by multiple users do not corrupt stored notes
- [ ] Failed writes roll back cleanly with no partial commits

**Sign-off:** _________________________ Date: _________

---

#### US-WEB-08 · Shared Persistent Review Environment
> *As an instructor/reviewer, I want one shared deployed environment so I can evaluate the system without local setup.*

**Acceptance Checklist:**
- [ ] A shared environment is reachable for review
- [ ] Data persists across app restarts in that environment
- [ ] Health/status endpoint confirms application availability

**Sign-off:** _________________________ Date: _________

---

## Final Release Sign-Off

This section must be completed before the AstraNotes MVP is released.

**Confirming that:**
- All Part 1 (Functional) sign-off lines above are completed
- All Part 2 (Quality/Performance) sign-off lines above are completed
- All Part 3 (Security) sign-off lines above are completed and evidence attached
- All Part 4 (Serviceability) sign-off lines above are completed
- All Part 5 (Web Multi-User Foundations) sign-off lines above are completed
- All automated tests pass (test run result attached: _______________)
- All release gates in `planning/release-gates.md` are satisfied
- No open P0 or P1 defects exist

| Role | Name | Signature | Date |
|---|---|---|---|
| Developer | | | |
| Product Owner / Stakeholder | | | |

**Release approved:** ☐ Yes — MVP is ready to ship
