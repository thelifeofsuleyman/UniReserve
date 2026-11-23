# CR-005 — Production-oriented presentation and deployment baseline

**Date:** 23 November 2026  
**Initiating feedback:** Owner asked to remove unnecessary AI-style reminders and internal demo language throughout the website, revise related files/PDFs, and make the site feel like a production service.

## Problem

Login, catalogue, Studio and admin screens repeatedly displayed "demo", "example campus", setup commands and caveats. This distracted from choosing a room or making a reservation. Furthermore, the local Flask entry point, transient secret and lack of a new-area creation route left a gap between screenshots and an administrable web service.

## Implementation

- Simplified customer-facing labels while retaining reservation rules (live-status meaning, booking windows, approvals and closed hours).
- Moved source limitations and independent-service status to one dedicated **Service information** page, linked from the footer. Academic reports/AI disclosure remain truthful.
- Added production mode: mandatory stable secret, trusted hosts, secure session cookies, CSP/HSTS and other response headers, plus a database health endpoint.
- Added Waitress local and managed-production entry points and optional exact-count trusted reverse-proxy handling.
- Added account provisioning without synthetic users, administrator Space creation, and room/resource creation using real configured hours.
- All existing booking state transitions, no-overlap tests and audit semantics remain unchanged.

## Traceability

Affected: FR-001/003/009/010 and NFR-003/004/005; UC-01/02/06; `app.py`, `booking.py`, Jinja templates, account management, Waitress scripts, test fixtures, deployment docs and all PDF-building source sections. No schema migration or new entity was required.

## Boundaries

A polished website is **not evidence of an actual public host**. An accredited real deployment needs validated room/seat data, TLS domain ownership, university authorization, credential recovery/SSO, rate limiting, security review and backup/monitoring operations. These are not silently claimed to exist.

**Verification:** See `docs/testing/CR-005_TEST_ADDENDUM.md`, actual GitHub Actions results, and `docs/deployment/OPERATIONS.md`.
