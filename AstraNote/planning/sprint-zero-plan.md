# Sprint Zero Plan (AstraNotes)

## Sprint Zero Goal
Prepare the team and codebase to execute MVP-scoped backlog items with low delivery risk.
Sprint zero is for readiness, planning quality, and technical validation, not full feature completion.
Current pivot: prioritize web-based multi-user infrastructure decisions before implementation scaffolding.

**Status Update (2026-05-11)**: Three critical repo-driving architecture decisions have been locked:
- **User Model (WEB-09, Decision Locked)**: Minimal persistent User with `user_id`, `email`, `password_hash` (bcrypt/Argon2), `created_at`, `is_active`.
- **Session Behavior (WEB-10, Decision Locked)**: Database-backed server-side sessions with 30-minute idle timeout, 7-day absolute timeout, current-session logout, no remember-me in v1.
- **Password/Passphrase Separation (WEB-11, Decision Locked)**: Login password hashed with bcrypt/Argon2; private-note passphrase is 4-digit numeric PIN derived with PBKDF2-HMAC-SHA256 (≥100,000 iterations).

These decisions are now captured in requirements.md (WEB-09–11), user_stories.md, test-plan.md (TP-A01–14), and decisions.md. Planning artifacts are aligned. Mini repo structure can be scaffolded immediately.

## Duration
- 1 week (5 working days)

## Scope Boundaries
### In Scope
- Environment and workflow setup
  - Finalization of planning artifacts for REQ-01 to REQ-27, NFR-01 to NFR-18, and SRG MVP scope (SRG-01..02, SRG-04..05, SRG-07..08, SRG-10..11, SRG-13..26)
- Web application foundation decisions: backend framework, auth/session model, API contract, and multi-user data isolation strategy
- Early technical decisions needed for implementation
- Small risk-reduction spikes/prototypes

### Out of Scope
- Full implementation of MVP backlog items
- UI polish and production-ready feature completeness
- Post-MVP backlog items (BL-14 to BL-20)

## Sprint Zero Deliverables
- Finalized planning docs: requirements, user stories, backlog, sprint plan
- GitHub workflow ready: issue templates, labels, and board columns
- Definition of Ready (DoR) and Definition of Done (DoD) for this project
- Updated architecture decision record for web multi-user delivery and backend storage strategy
- Small technical spikes proving SQLite persistence integrity, session/auth flow, and core performance test approach
- Risk register with mitigations for MVP delivery

## Work Plan
### 1) Setup and Workflow Readiness
- Confirm local development setup and dependency install instructions.
- Confirm web stack selection (backend framework + frontend approach) and document rationale.
- Standardize branching and PR workflow (small, reviewable PRs).
- Configure issue tracking for BL-01 to BL-13 with IDs, priorities, and MVP labels.
- Create a lightweight status cadence (daily check-in notes, weekly review).

### 2) Planning Artifacts Hardening
- Ensure each enhanced requirement maps to backlog coverage:
	- REQ-01 to REQ-27 -> BL-01 to BL-09
	- NFR-01 to NFR-18 -> BL-10 to BL-12
	- SRG MVP requirements (SRG-01..02, SRG-04..05, SRG-07..08, SRG-10..11, SRG-13..26) -> BL-13
	- WEB-01 to WEB-08 -> BL-22
- Validate acceptance criteria are testable and implementation-neutral.
- Break BL-01 to BL-13, BL-21, and BL-22 into implementable Sprint 1 and Sprint 2 tasks.
- Add sequencing dependencies:
	- BL-01 before BL-02 and BL-03
	- BL-04 and BL-05 depend on persisted note model
	- BL-09 and BL-13 depend on privacy data contract decisions
	- BL-22 auth/session and ownership boundaries must be in place before full REQ workflow implementation
	- BL-10 depends on core CRUD implementation readiness

### 3) Early Technical Decisions
- Confirm note data model fields for MVP:
  - note_id, title, body, is_private, is_deleted, created_at, updated_at, deleted_at (soft delete)
  - Plaintext-at-rest allowlist per SRG-25: note_id, created_at, updated_at, is_private, is_deleted, deleted_at only; title, body, version_content must be encrypted
- Finalize SQLite persistence profile and PostgreSQL-ready migration strategy.
- Define authenticated user model (`user_id`) and mandatory ownership scoping for all note operations.
- Define API boundary for CRUD/search/restore and auth/session lifecycle.
- Define error handling expectations (invalid input, missing records, migration mismatch, not-found operations).
- Document decision to keep search simple (case-insensitive substring match).
- Define MVP security boundaries (private-note encryption scope, audit fields, restore behavior).

### 4) Risk Reduction Spikes (Time-Boxed)
- Spike A (2-3 hours): Verify SQLite persistence round-trip for create/update/delete and transaction rollback behavior.
- Spike B (2 hours): Validate soft delete/restore flow and retention timestamp handling.
- Spike C (3 hours): Validate private-note encryption-at-rest approach, PBKDF2-HMAC-SHA256 key derivation (SRG-26), metadata plaintext allowlist enforcement (SRG-25), passphrase unlock flow (SRG-18..20), and lockout/backoff behavior (SRG-22..23).
- Spike D (2 hours): Validate performance test harness setup for API latency measurements.
- Spike E (2 hours): Validate server-side session cookie flow (login, idle timeout, CSRF on write endpoints) against WEB-01, WEB-05, WEB-06.

## Story Readiness Targets (No Full Build)
- BL-01 to BL-05: Ready with CRUD, list, and search behaviors fully specified.
- BL-06 to BL-09: Ready with authoring, capacity, and privacy behaviors specified.
- BL-10 to BL-12: Ready with NFR test strategy and architecture/testing boundaries documented.
- BL-13: Ready with MVP SRG implementation boundaries documented, covering SRG-01..02, SRG-04..05, SRG-07..08, SRG-10..11, SRG-13..26 acceptance criteria.
- MVP security implementation boundaries (SRG MVP: SRG-01..02, SRG-04..05, SRG-07..08, SRG-10..11, SRG-13..26) documented and testable.

## Proposed Sprint Zero Schedule
- Day 1: Environment/workflow setup + board/labels/issues
- Day 2: Artifact hardening (requirements, stories, backlog mapping, MVP scope labels)
- Day 3: Technical decisions and ADR updates (data/security/error boundaries)
- Day 4: Risk-reduction spikes and results documentation
- Day 5: Sprint handoff package and readiness review

## Exit Criteria
- All BL-01 to BL-13, BL-21, and BL-22 have clear owners, estimates, and dependency order.
- All acceptance criteria are testable and unambiguous.
- SQLite storage and soft-delete/restore approach validated by spike results.
- MVP security implementation boundaries (SRG MVP: SRG-01..02, SRG-04..05, SRG-07..08, SRG-10..11, SRG-13..26) documented and testable.
- WEB-01 to WEB-08 implementation boundaries documented and testable.
- Top 5 delivery risks documented with mitigation steps.
- Sprint 1 can start immediately without planning blockers.