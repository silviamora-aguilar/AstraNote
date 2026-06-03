# Sprint Zero Backlog — AstraNotes

## Purpose

This backlog stages delivery from Sprint 0 through Sprint 3 so work is sequenced across the quarter rather than treated as a single undifferentiated implementation block.

## Delivery Timeline Overview

- Sprint 0: readiness and decision lock
- Sprint 1: single-user web core workflows and architecture foundation
- Sprint 2: privacy/security completion and localization
- Sprint 3: integration hardening, release evidence, and final acceptance readiness

## Sprint 0 — Readiness and Decision Lock

### Objectives
- finalize scope and architecture decisions,
- ensure planning artifacts are internally consistent,
- reduce technical risk before coding.

### Included Backlog Coverage
- BL-12 planning aspects (architecture/testability guardrails)
- BL-21 planning aspects (logging/config/startup integrity decisions)
- BL-13 planning aspects (security stack completion boundaries)
- BL-23 planning aspects (localization toggle acceptance coverage)

### Sprint 0 Work Packages
- SZ-01: Freeze approved implementation profile in requirements and ADRs
- SZ-02: Align user stories, backlog, traceability matrix, and test plan to active single-user MVP scope and explicit Post-MVP WEB deferrals
- SZ-03: Create readiness artifacts: PRD, executive one-pager, system design document, definition of done, readiness checkpoint
- SZ-04: Validate SQLite + PostgreSQL-ready migration approach
- SZ-05: Validate session-cookie + CSRF model conceptually against requirements
- SZ-06: Prepare Sprint 1 implementation sequencing and dependency order

### Exit Criteria
- all planning artifacts are in lockstep,
- no open scope ambiguity on framework/persistence/auth,
- Sprint 1 can begin without architectural blockers.

## Sprint 1 — Core Single-User Web Foundation

### Objectives
- deliver single-user note workflows,
- establish API/service/storage boundaries,
- enforce local persistence integrity and privacy controls.

### Included Backlog Items
- BL-01, BL-02, BL-03, BL-04, BL-05
- BL-12 implementation tasks
- BL-21 foundational implementation tasks
- BL-13 implementation tasks (security core)

### Primary Outcomes
- single-user CRUD/list/search hardening
- repository and service boundaries proven through tests
- encryption-at-rest and private-note unlock path active
- audit and diagnostic logging foundations active

## Sprint 2 — Privacy, Authoring, and Quality Hardening

### Objectives
- complete note authoring behaviors,
- deliver private-note security model,
- verify performance and durability targets.

### Included Backlog Items
- BL-06, BL-07, BL-08, BL-09, BL-10, BL-23

### Primary Outcomes
- lists and formatting
- localization toggle (English/Spanish interface text only)
- benchmark and durability evidence

## Sprint 3 — Final Integration and Release Readiness

### Objectives
- close remaining gaps,
- verify gates and acceptance evidence,
- prepare final instructor/demo review.

### Included Work
- regression hardening across BL-01 to BL-13, BL-21, BL-23
- deferred-scope handoff package for BL-22, BL-24, BL-25
- release-gate completion
- customer acceptance sign-off collection
- Lucid diagram refresh to approved baseline

### Primary Outcomes
- release gates satisfied,
- readiness checkpoint passes,
- deferred-scope handoff package complete for shared-environment and multi-user follow-on work,
- final package ready for evaluation.

## Staging Logic

The staging intentionally pushes decision and documentation work into Sprint 0, core web foundations into Sprint 1, higher-risk security features into Sprint 2, and release hardening into Sprint 3. This prevents early implementation from drifting away from the approved scope or consuming time needed for acceptance evidence at the end of the quarter.