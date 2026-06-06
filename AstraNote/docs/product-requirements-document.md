# Product Requirements Document - AstraNotes

## 1. Purpose

This document gives the product-level framing for the delivered AstraNotes MVP. It sits above the detailed requirement baseline and explains the user value, scope boundaries, and acceptance criteria that the project now satisfies.

## 2. Product Overview

AstraNotes is a local, single-user note-taking web application designed for fast browser-based note capture, Markdown-style editing, private-note protection, and careful handling of deleted content. The MVP is intentionally narrow: it prioritizes correctness, clarity, and reviewability over multi-user breadth.

## 3. Business Goals

### Primary Goals

- Deliver a complete, review-ready graduate-course artifact chain
- Show that the team can build and document a real browser app end-to-end
- Provide a polished note workflow with privacy controls and recoverable deletion

### Supporting Goals

- Keep the scope small enough to finish cleanly within the academic timeline
- Make the implementation easy to review, test, and explain
- Leave a clear path for Post-MVP growth without overbuilding the baseline

## 4. Target Users

- Primary: course reviewers, instructors, and demonstrators
- Secondary: a single local user managing notes in a browser

## 5. Product Objectives

- Create, edit, delete, restore, list, and search notes without data loss
- Support structured body content with lists and text formatting
- Protect private note content with PIN-based unlock and encrypted storage
- Keep the note list readable, recoverable, and consistent after save or refresh
- Provide traceable evidence for requirements, testing, and release readiness

## 6. Scope Boundaries

### In Scope for the MVP

- Browser-based local web experience on 127.0.0.1
- FastAPI backend with Jinja2 + HTMX front-end rendering
- SQLite-backed persistence for the local baseline
- CRUD, search, formatting, privacy toggle, soft delete, restore, and Trash review
- Diagnostic and audit logging
- English/Spanish UI text toggle

### Out of Scope for the MVP

- Multi-user accounts and shared ownership scoping
- Device sync or cloud collaboration
- Native mobile packaging
- Real-time collaboration
- Per-note key isolation
- Image paste support and advanced content types

## 7. Product-Level Feature Set

### User Value

- Capture notes quickly
- Find notes reliably
- Edit and format content clearly
- Recover from accidental deletion within the retention window
- Keep sensitive content hidden until it is explicitly unlocked

### Delivery Value

- Show that the team can define, implement, test, and gate an MVP cleanly
- Preserve traceability from requirement to implementation to evidence
- Keep the design understandable for course review

## 8. Acceptance-Level Product Criteria

The MVP is acceptable when all of the following are true:

- A local browser user can complete the core note workflows
- Private-note content is encrypted at rest and hidden until unlock succeeds
- Deleted notes move to Trash and can be restored during retention
- The UI text toggle works without translating user-authored note content
- Release gates and tests show objective evidence that the baseline is complete
- The documented HTML review flow matches the source Markdown artifacts

## 9. Dependencies and Assumptions

- The approved MVP stack remains FastAPI, Jinja2 + HTMX, and SQLite
- The shared giraffe-branded review pages remain the primary review path for the course
- Post-MVP items stay deferred unless the rubric or instructor feedback changes scope

## 10. Relationship to Detailed Requirements

This PRD is a product-facing companion to [planning/requirements.md](../planning/requirements.md). The requirements document remains the canonical source for requirement IDs and detailed behavior. This PRD explains why the MVP exists and how the implemented baseline should be judged.