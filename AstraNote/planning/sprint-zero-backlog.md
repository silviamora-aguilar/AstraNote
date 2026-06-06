# Sprint 0-3 Delivery Plan — AstraNotes

## Purpose

This is the canonical sprint-planning document for AstraNotes. It consolidates readiness, implementation sequencing, and delivery status from Sprint 0 through Sprint 3.

## Current Delivery Status Snapshot

- Sprint 0 (Readiness and decision lock): ✅ Complete
- Sprint 1 (Core single-user web foundation): ✅ Complete
- Sprint 2 (Privacy, authoring, and quality hardening): ✅ Complete
- Sprint 3 (Integration and release-readiness packaging): ✅ Complete for MVP baseline; Post-MVP handoff items remain deferred by design

## Sprint 0 — Readiness and Decision Lock ✅

### Outcomes Completed

- ✅ Scope pivot finalized to single-user localhost MVP.
- ✅ Requirements, user stories, backlog, and traceability alignment completed.
- ✅ Technical decision set locked (FastAPI, Jinja2 + HTMX, SQLite, private-note security model).
- ✅ Startup/release-readiness and planning artifacts prepared for implementation kickoff.

### Backlog Coverage

- BL-12 planning aspects
- BL-13 planning aspects
- BL-21 planning aspects
- BL-23 planning aspects

## Sprint 1 — Core Single-User Web Foundation ✅

### Outcomes Completed

- ✅ Core CRUD/list/search workflows implemented and stabilized.
- ✅ Soft delete and restore flows implemented.
- ✅ Architecture boundary guardrails in code and tests.
- ✅ Serviceability/manageability baseline implemented for retained MVP SMR scope.

### Backlog Coverage

- BL-01, BL-02, BL-03, BL-03.1, BL-04, BL-05
- BL-12
- BL-13 foundational security slices
- BL-21 retained MVP scope

## Sprint 2 — Privacy, Authoring, and Quality Hardening ✅

### Outcomes Completed

- ✅ Bullet/checklist editing, formatting, and capacity-limit behavior delivered.
- ✅ Private-note security stack completed for MVP scope.
- ✅ Performance verification delivered for NFR-06 through NFR-09.
- ✅ English/Spanish interface toggle implemented.

### Backlog Coverage

- BL-06, BL-07, BL-08, BL-09, BL-10, BL-23

## Sprint 3 — Integration and Release Readiness ✅

### Outcomes Completed

- ✅ Regression hardening and release-gate evidence package completed for MVP scope.
- ✅ Phase-1 through Phase-6 planning/doc alignment completed for current baseline.
- ✅ Deferred-scope handoff explicitly documented for Post-MVP backlog items.

### Deferred by Design (Not Missed)

- BL-11 [Post-MVP]
- BL-22 [Post-MVP]
- BL-24 [Post-MVP]
- BL-25 [Post-MVP]
- BL-26 [Post-MVP]

## Delivery Sequencing Logic

The sequence intentionally front-loaded planning and architecture lock (Sprint 0), then delivered core workflows (Sprint 1), security/privacy and quality hardening (Sprint 2), and finally integration evidence plus release readiness (Sprint 3).

## Document Authority

If sprint planning content in older files conflicts with this document, this file is authoritative.