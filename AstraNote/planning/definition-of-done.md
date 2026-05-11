# Definition of Done — AstraNotes

## Purpose

This document defines the evidence and gates that each story and backlog item must satisfy before it can be considered done.

## 1. Story-Level Definition of Done

A user story is done only when all of the following are true:

- all acceptance criteria in [planning/user_stories.md](./user_stories.md) pass,
- relevant requirement IDs are referenced in the implementation artifact (commit/PR/task evidence),
- the feature works in the approved architecture path,
- automated tests for the touched behavior exist and pass,
- no regression is introduced in previously passing suites,
- errors are user-safe and do not expose sensitive implementation detail,
- traceability is updated if the story changes requirement coverage status.

## 2. Backlog-Item Definition of Done

A backlog item is done only when:

- every included story is done,
- the planned exit criteria for that backlog item are satisfied,
- affected sprint tasks are complete,
- integration evidence exists where the backlog item crosses multiple tiers,
- the item does not violate release-gate rules.

## 3. Evidence Required Per Done Item

### Required Evidence
- acceptance criteria check
- linked tests
- implementation note or commit reference
- updated traceability status where relevant
- no open P0/P1 defect caused by the item

### Recommended Evidence
- screenshot or short workflow proof for UI-visible features
- benchmark or security evidence where applicable
- reviewer/self-review note

## 4. Quality Gates Embedded in Done Status

The following must be true before marking any item done:

- no unhandled exception on expected or invalid user paths,
- no plaintext note content in logs or audit output,
- owner scoping enforced for protected note actions,
- transaction safety or rollback behavior preserved for writes,
- architecture boundaries remain intact.

## 5. Special Rules by Requirement Class

### REQ Stories
- must be demonstrable in the UI and/or API workflow

### NFR Stories
- must have measurable evidence, not just implementation claims

### SRG Stories
- must include explicit security validation evidence

### SMR Stories
- must include operational/diagnostic evidence

### WEB Stories
- must include authorization, isolation, or deployment proof as appropriate

## 6. Minimum Done Checklist

- [ ] Acceptance criteria complete
- [ ] Unit/integration/security tests updated and passing as applicable
- [ ] No regression introduced
- [ ] Requirement IDs referenced
- [ ] Traceability updated if status changed
- [ ] No P0/P1 defects introduced

## 7. Relationship to Release Gates

This document governs local completion of stories and backlog items. [planning/release-gates.md](./release-gates.md) governs whether the overall MVP is allowed to ship. An item may be done while the product is not yet release-ready.