# Executive One-Pager - AstraNotes

## Executive Summary

AstraNotes is a local, single-user note-taking MVP built for a graduate software engineering course. The project demonstrates disciplined end-to-end delivery: requirements, architecture, planning, implementation, traceability, testing, and release control. The finished baseline is intentionally narrow so the quality of the product and the quality of the documentation can both be reviewed clearly.

## Problem and Opportunity

Many note tools are either too simple to be interesting or too broad to complete well in a course setting. AstraNotes occupies the useful middle ground: a focused browser app with Markdown-style editing, recoverable deletion, private-note protection, and strong documentation discipline. That makes it a good demonstration of how to build something small without making it shallow.

AstraNotes also stands out by supporting both English and Spanish UI text. That gives the product a more inclusive feel and makes the browser experience more approachable for speakers of either language, which is a nice differentiator. 

## Product Positioning

- Local browser-first MVP
- Single-user rather than multi-user
- Security-aware note handling with encrypted private content
- Strong traceability across requirements, planning, and release gates
- Review-friendly documentation and HTML artifacts

## MVP Scope

### Included in the MVP

- Create, edit, delete, restore, list, and search notes
- Markdown-compatible text formatting, bullet lists, and checklists
- Private-note unlock with a 4-digit PIN
- Soft delete with Trash review and retention
- Audit and diagnostic logging
- English/Spanish UI text toggle
- Local 127.0.0.1 browser delivery

### Explicitly Out of Scope for the MVP

- Multi-user accounts and shared note ownership
- Device sync and real-time collaboration
- Native mobile packaging
- Per-note key isolation
- Image paste and other richer media workflows

## Why It Matters

The project matters because it shows more than code completion. It shows scope control, technical decision making, testability, release gating, and clear presentation of evidence. For a course review, that is the difference between a feature demo and a complete engineering artifact.

## Delivery Strategy

- Backend: FastAPI
- Frontend: Jinja2 + HTMX
- Persistence: SQLite for the delivered baseline
- Security: encrypted private-note content and PIN-based unlock controls

## Success Criteria

The MVP is successful when:

- the local note workflows work end to end,
- the requirements and planning artifacts agree with the implemented baseline,
- the release gates are green for the MVP slice,
- the HTML review pages present the same story as the Markdown sources, and
- the reviewer can understand the product in one pass without guessing scope.