# ADR-0001: Modular monolith for UniReserve

**Status:** Proposed  
**Date:** 2026-11-23

## Context

The assignment values requirements, models, traceability, and tests more heavily than implementation size. A small student-owned resource reservation system must handle authorization, resource availability, approval, and conflicting bookings.

## Decision

Use a **Python modular monolith** with the following separation:

1. **Presentation**: Flask request handlers and templates (future work).
2. **Application services**: booking, approval, resource administration (future work).
3. **Domain**: business rules and reservation state transitions.
4. **Persistence**: SQLAlchemy and SQLite with explicit transactions (future work).

For the first milestone only, implement a standalone interval rule that can be tested without the framework.

## Why not alternatives?

- **Microservices:** unnecessary operational complexity and costly consistency between services for this assignment.
- **Single-file Flask application:** fast initially but makes it harder to relate design classes, business rules, and tests.

## Risks and mitigations

- **Double booking:** application-level overlap checking is insufficient with concurrent requests; use a database transaction strategy and an integration test that attempts competing bookings.
- **Growing documentation:** keep requirement IDs aligned with diagrams, code, and test IDs.
- **SQLite limitations:** suitable for a small local demo, but production-grade concurrency and multi-user deployment require reassessment.

## Follow-up artifacts

Use-case diagram; textual use cases; domain class diagram; reservation state machine; conceptual and 3NF logical ERD; design class diagram; two sequence diagrams (one with an alternate flow); architecture overview; test plan and traceability matrix.
