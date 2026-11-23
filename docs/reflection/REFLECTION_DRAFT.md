# Individual Reflection — UniReserve

**Student:** Suleyman Shafizada, group m666i1  
**Software Engineering individual project**  
**Draft for student review and personal sign-off, 23 November 2026**

## What changed while developing the requirements?

I chose a small university room and equipment reservation system because it has clear user roles and important correctness rules. The original topic description mentioned availability, approvals, late returns, damaged equipment and priority users without defining the policy for any of them. At first, I treated the application mostly as a standard calendar. While writing the scenarios and tests, I realized that the meaning of a pending request had to be decided: if pending approvals reserve a resource, abandoned requests can block capacity; if they do not, the administrator has to recheck availability when approving. I chose the second behavior and documented it in the SRS, state machine, sequence diagrams and service tests. This decision cost some additional modeling and concurrency tests, but it removed an ambiguity that could otherwise create double bookings.

A second requirement problem surfaced when reviewing the interface. The initial application could book resources correctly, but the visual presentation did not communicate the current state clearly. I asked for more visual individuality and for a 2D or 3D layout that would show where equipment is represented and whether it is reserved. This became change request CR-001. I chose an illustrative 2D map rather than full 3D, because actual room geometry and sensor data were not available. The map therefore shows demonstration positions, not verified physical coordinates. Green means available now, yellow means the next confirmed booking begins within 15 minutes, red means a confirmed booking is active, and gray means disabled. The change required new domain status rules, a read-only status endpoint, new UI tests and a supplementary sequence diagram. These design decisions are assumptions for the coursework, not policies confirmed by a university department.

## Design and implementation differences

The original design class diagram included explicit repository interfaces, an AuthService and a SQLiteUnitOfWork class. The working Python implementation is simpler: BookingService uses SQLAlchemy Session queries, Flask handles signed login sessions, and the database transaction helper is a context manager. The essential layering and transaction boundaries remain, but the code is smaller and easier to inspect for an individual project. This deviation is documented in the traceability matrix rather than pretending the conceptual classes all exist as concrete modules. The logical ERD still has four normalized entities; I intentionally did not add physical location coordinates because there is no trustworthy data source for them.

## Verification, limitations and what I would change

The automated tests focus on costly failures: overlapping confirmed bookings, role bypass, stale approvals, rollback of audit events and persistence after restart. Fifty synchronized two-client trials in CI produced no overlapping confirmations, and GitHub Actions recorded the test counts, coverage and measured latency. However, successful automated tests do not prove that the UI feels good to actual students or that the security is production ready. I have not completed the specified five-volunteer usability test or full keyboard-only walkthrough, and I will not claim those results. If I repeated the work, I would validate real university borrowing policies earlier, review visual prototypes before coding all screens, and obtain real room-layout data before presenting coordinates as physical placements. I would also consider PostgreSQL if this were deployed for many concurrent real users.

## AI assistance disclosure

I used ChatGPT extensively to help interpret the assignment, draft requirements and comparisons of existing systems, plan UML diagrams, write and revise Flask/SQLAlchemy source code, create test cases, review CI outcomes and organize the documentation. Original imagery for the revised interface was AI-generated. The actual GitHub Actions runs, test logs and change records are cited so the technical claims can be checked. The architecture, scope, requirements and implementation should be reviewed and understood by me before submission. AI assistance should not be mistaken for interviews, independent usability sessions or work personally carried out without assistance.
