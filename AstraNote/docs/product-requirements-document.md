# Product Requirements Document — AstraNotes

## 1. Purpose

This Product Requirements Document frames the business goals, scope boundaries, and acceptance-level view of AstraNotes. It sits above the detailed requirement baseline and provides the product-level interpretation of what the MVP must achieve.

## 2. Product Overview

AstraNotes is a web-based multi-user note-taking application designed to support everyday note capture, organization, privacy-sensitive note handling, and structured engineering delivery. The MVP emphasizes correctness, maintainability, and security-aware behavior rather than broad platform reach.

## 3. Business Goals

### Primary Goals
- Deliver a complete graduate-course product artifact chain from scope through release readiness
- Demonstrate a realistic multi-user web architecture with clear boundaries between UI, service, storage, and security
- Provide a usable note workflow for authenticated users with reliable persistence and privacy controls

### Secondary Goals
- Preserve a low-risk delivery path for a single academic quarter
- Keep the implementation stack approachable enough to complete with quality
- Maintain a migration path toward stronger production infrastructure later

## 4. Target Users

- Primary: course reviewers, instructors, and demonstrators validating software engineering execution
- Secondary: end users who need a structured note system with optional private-note handling

## 5. Product Objectives

- Users can authenticate and manage their own notes only
- Users can create, update, delete, restore, list, and search notes without data corruption
- Users can author structured note content with lists and formatting
- Users can mark notes private and rely on stronger protections for protected content
- The product exposes traceable engineering evidence for planning, quality, security, and release decisions

## 6. Scope Boundaries

### In Scope
- Browser-based desktop web experience
- Multi-user access with per-user data isolation
- FastAPI backend with Jinja2 + HTMX frontend rendering
- SQLite persistence with PostgreSQL-ready schema discipline
- Server-side session cookies with inactivity timeout and CSRF protection
- CRUD, search, authoring, privacy state, soft delete/restore, audit logging

### Out of Scope
- Native mobile applications
- Real-time collaboration or shared editing
- Cross-device sync
- Full cloud-native microservices deployment
- Advanced plugin ecosystem

## 7. Product-Level Feature Set

### Core User Value
- Capture notes quickly
- Find notes reliably
- Edit and organize content clearly
- Recover from accidental deletion within retention boundaries
- Protect sensitive notes through private-note controls

### Engineering Value
- Traceability from requirement to test and release gate
- Controlled delivery through sprint staging and readiness checkpoints
- Architecture that supports backend replacement and future hardening

## 8. Acceptance-Level Product Criteria

The product is acceptable at MVP level when all of the following are true:

- authenticated users can complete core note workflows in browser,
- no user can access another user's notes,
- persistence is durable and transaction-safe,
- private-note content is encrypted at rest,
- session inactivity and authorization controls are enforced server-side,
- automated tests and release gates show objective evidence of readiness,
- the shared review environment is reachable for instructor evaluation.

## 9. Dependencies and Assumptions

- The approved technology decisions remain unchanged unless formally revised in ADRs
- Lucid UML artifacts will be refreshed to the web multi-user baseline in a follow-up pass
- Mobile-web parity remains Post-MVP unless the course rubric explicitly elevates it

## 10. Relationship to Detailed Requirements

This PRD is intentionally shorter and more product-facing than [planning/requirements.md](../planning/requirements.md). The detailed requirement baseline remains the canonical source for REQ, NFR, SRG, SMR, and WEB identifiers. This document provides the business framing and acceptance view that explains why those detailed requirements exist.