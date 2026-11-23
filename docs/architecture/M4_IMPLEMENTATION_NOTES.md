# Milestone 4 — Database and Reservation Engine

**Author:** Suleyman Shafizada, group m666i1  
**Status:** Verified local service-layer implementation; Flask UI and browser sessions are not implemented yet.  
**Requirements:** FR-002–FR-011 (partial API coverage), NFR-002/003/004/005/008 (selected measurable checks).  
**Baseline:** SRS v1, UML diagram set, and ADR-0002.

## What is implemented

The SQLAlchemy declarative tables follow the four entities in the logical 3NF ERD: users, resources, reservations, and reservation_events. Foreign keys, unique identifiers, valid status/role/category constraints, start-before-end, and append-only audit triggers are part of the SQLite schema.

SQLite timestamp columns hold UTC-normalized naive database values because SQLite does not preserve timezone objects. All service inputs and outputs require/return timezone-aware UTC datetimes. This is a persistence representation detail, not permission to accept naive user input.

BookingService implements catalogue listing, availability checks, booking requests, own-booking listing, owner cancellation, pending approval/rejection, administrator resource creation and editing, and audit inspection with ownership checks. A trusted one-off provisioning function stores PBKDF2-HMAC-SHA256 salted password hashes. Web authentication and Flask session handling are deferred to the next milestone. Services currently use verified database user IDs supplied by a trusted caller. Future routes must derive identity from an authenticated session, never arbitrary client input.

## Transaction invariant

Every booking decision, approval, cancellation or resource edit is made inside BEGIN IMMEDIATE on a file-backed SQLite database. The service re-reads confirmed overlaps inside that transaction. A booking and its reservation event are committed together, or both rolled back. Only CONFIRMED blocks a resource; PENDING_APPROVAL is nonblocking. The time comparison uses half-open [start, end) intervals.

Creating a booking on an already-confirmed slot is rejected even for approval-required resources, but two pending requests may overlap. A pending request that conflicts at the time of approval remains pending and gains no approval audit event. Disabling a resource blocks further requests and approvals without altering historical confirmations.

## Match with models and documented deviation

The entity names, FKs, state names and transactional rules match the UML diagrams. In this milestone BookingService also contains resource listing/edit methods and availability checks instead of introducing a separate ResourceService class. This is a temporary design deviation from diagram 06-design-classes and 07-architecture to keep a small testable service surface. The next milestone must either extract ResourceService and update tests or revise those diagrams and the traceability matrix. Method names use concise request() and available() rather than the diagram's proposed request_booking() and check_availability().

An extra guard disallows approval after the requested start; it is a sensible restriction but not explicit in SRS v1. Update the SRS and approval use case during formal change control before declaring full traceability.

## Limitations and later work

- The service layer itself is not a protected HTTP API. Authentication, CSRF defenses, request parsing, UI messages and HTTP 401/403 tests remain to be implemented.
- SQLite's single-writer transactions are appropriate for a local demonstration, not proof of production concurrency or backup readiness.
- Audit triggers forbid UPDATE/DELETE of events, but the local disk is not tamper-proof.
- Actual routes, traceability matrix, code review evidence, change-impact analysis and reflection are outstanding.

## Run

    python -m pip install -r requirements-dev.txt
    python scripts/run_tests.py
    python scripts/validate_models.py
    coverage run --source=src/unireserve scripts/run_tests.py
    coverage report -m --fail-under=80
    python scripts/demo_engine.py
