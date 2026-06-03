# BL-13 Security Closure Summary (2026-06-03)

This document captures the BL-13 security hardening work that was completed for the current AstraNotes MVP baseline.

## Scope Completed

- SRG-01 / SRG-02: At-rest encryption behavior verified for note title/body payloads.
- SRG-05 / SRG-07: Audit logging implemented with privacy-safe fields and no plaintext note content.
- SRG-10 / SRG-11 / SRG-12 / SRG-13: Trash retention/recovery flows verified, including purge on retention expiry.
- SRG-14 / SRG-15: Structured error mapping and atomic persistence failure handling retained.
- SRG-16: Deterministic machine-readable error codes implemented and validated.
- SRG-17: TLS release-gate requirement documented and satisfied for current MVP scope by confirming no non-local content-transmitting path exists.
- SRG-18 through SRG-24: PIN unlock gating, session timeout/lockout behavior, and anti-enumeration handling verified.
- SRG-25 / SRG-26: Plaintext metadata allowlist maintained; private PIN persistence moved to encrypted token storage with legacy migration.

## Key Code Changes

- Added file-backed audit logger and integrated it into note service operations.
- Added deterministic error-code mapping and surfaced error codes in API error headers.
- Hardened PIN settings persistence to prevent raw PIN storage in persisted config.
- Added eager migration path for legacy plaintext PIN config values.

## Test Evidence Added or Updated

- Unit tests:
  - tests/unit/test_audit_logging.py
  - tests/unit/test_error_mapping.py
  - tests/unit/test_pin_settings_manager.py
  - tests/unit/test_unlock_session_manager.py
- Integration tests:
  - tests/integration/test_create_note_api.py (repeated invalid request consistency)
  - tests/integration/test_private_unlock_ui.py
  - tests/integration/test_private_pin_settings_ui.py
  - tests/integration/test_trash_ui.py

## Planning and Governance Alignment

The following planning artifacts were updated to align status with implemented BL-13 behavior and evidence:

- planning/requirements.md
- planning/user_stories.md
- planning/backlog.md
- planning/traceability-matrix.md
- planning/test-plan.md
- planning/release-gates.md
- docs/sdlc-document-map.html

## Notes for Reviewers

- This document is a summary artifact only; implementation and test evidence are already on main in commit 8f2484c.
- Any follow-on work should target remaining open MVP gates (BL-12, BL-21, BL-23) or approved Post-MVP items.