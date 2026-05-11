# Executive One-Pager — AstraNotes

## Executive Summary

AstraNotes is a web-based multi-user note-taking system being built for a graduate software engineering course to demonstrate disciplined end-to-end product engineering: requirements definition, architecture, planning, traceability, testing, and controlled delivery. The product combines practical note management workflows with security-sensitive private-note handling, making it a strong vehicle for showing both user-facing value and engineering rigor.

## Market Opportunity and Problem

Many note tools optimize either for convenience or for heavy enterprise collaboration. AstraNotes targets a smaller but meaningful middle ground for course scope: a lightweight note system with modern web interaction, structured authoring, and privacy-aware handling of sensitive notes. The project matters because it models a realistic product problem where usability, performance, data protection, and maintainability must all be balanced within a constrained delivery window.

## Product Positioning

- Web-based, multi-user, browser-accessible product
- Focused MVP rather than feature sprawl
- Engineering-first implementation with strong traceability and release controls
- Security-aware note handling through encrypted private-note content, session controls, and auditability

## MVP Scope

### Included in MVP
- Authenticated multi-user access
- Create, edit, delete, list, and search notes
- Markdown-oriented text authoring, lists, and formatting
- Private-note workflow with encrypted-at-rest content
- Soft delete and restore
- Audit logging, diagnostic logging, and structured errors
- Web multi-user API boundary and shared deployment readiness

### Explicitly Out of Scope for MVP
- Native mobile apps
- Rich real-time collaboration
- Device sync across platforms
- Per-note key isolation
- Post-MVP mobile accessibility hardening items already tagged in requirements

## Why AstraNotes Matters

The project matters academically because it demonstrates more than coding. It shows that the team can define requirements, make architecture decisions deliberately, lock implementation assumptions before scaffolding, map backlog to delivery phases, enforce quality gates, and prepare stakeholder acceptance artifacts. It is a compact but credible representation of graduate-level software engineering practice.

## Delivery Strategy

- Backend: FastAPI
- Frontend: Jinja2 + HTMX
- Persistence: SQLite now, PostgreSQL-ready migration discipline
- Auth/session: server-side sessions with secure HttpOnly cookies and CSRF protection on write endpoints

## Success Criteria

The AstraNotes MVP is successful when:

- the approved 91-item requirement baseline is internally consistent across planning artifacts,
- BL-01 through BL-13, BL-21, and BL-22 are implemented or demonstrably ready per plan,
- all release gates are satisfied,
- customer acceptance sign-off is complete, and
- a shared reviewable deployment exists for instructor evaluation.