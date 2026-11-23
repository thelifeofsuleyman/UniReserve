# UniReserve — Architecture and Design Models
**Milestone:** Design v1 · **Author:** Suleyman Shafizada (m666i1)  
**Requirements baseline:** `docs/requirements/SRS-v1.md` and `docs/requirements/USE_CASES-v1.md` on `main`  
**State:** Implementation design — not evidence that unimplemented functionality works.

## Diagram index
All diagram sources are in [source](source/) as **PlantUML .puml** files. [Rendered PNG/SVG images](rendered/) are generated from those exact sources by the diagram workflow and should be kept in sync. The exported diagrams are part of the deliverable, not a replacement for editable sources.

| Diagram | Source | What it shows / supported design decision |
|---|---|---|
| Use cases | [01](source/01-use-cases.puml) | Six actor-facing use cases and actor permissions. Distinguishes the normal requester from an administrator. |
| Domain model | [02](source/02-domain-model.puml) | User, Resource, Reservation, ReservationEvent and their conceptual cardinalities. Booking history belongs to its reservation. |
| State machine | [03](source/03-reservation-states.puml) | Allowed reservation state changes; PENDING_APPROVAL does not reserve capacity and only CONFIRMED blocks overlap. |
| Conceptual ERD | [04](source/04-erd-conceptual.puml) | Four domain entities and their conceptual one-to-many relationships, independent of SQL types. |
| Logical 3NF ERD | [05](source/05-erd-logical-3nf.puml) | Keys, FKs and column attributes for persistence. Audits reference users and reservations rather than duplicating their details. |
| Design classes | [06](source/06-design-classes.puml) | Attributes, visibility, methods, dependencies and Repository/Unit of Work/Service Layer patterns. BookingService owns transaction-level business decisions. |
| Architecture | [07](source/07-architecture.puml) | Flask presentation → services → domain/persistence → SQLite. One modular monolith avoids unnecessary distributed writes. |
| Sequence: UC-01 | [08](source/08-seq-UC-01-authenticate.puml) | Sign-in with correct/incorrect credentials, server-sourced role and logout. |
| Sequence: UC-02 | [09](source/09-seq-UC-02-availability.puml) | Read-only availability checks, with invalid/disabled alternatives; it never places a hold. |
| Sequence: UC-03 | [10](source/10-seq-UC-03-request.puml) | Write transaction, conflict rejection, pending/confirmed branch, and atomic audit event. |
| Sequence: UC-04 | [11](source/11-seq-UC-04-cancel.puml) | Ownership and start-time checks before cancellation; rollback on invalid transition. |
| Sequence: UC-05 | [12](source/12-seq-UC-05-approve.puml) | Admin decision, stale request/conflict alternatives and availability recheck before confirmation. |
| Sequence: UC-06 | [13](source/13-seq-UC-06-resources.puml) | Administrator resource operations with validation and forbidden-role alternative. |
| Supplementary CR-001 | [14](source/14-seq-CR-001-studio.puml) | Authenticated read-only near-live 2D status view; no booking lock or physical occupancy sensor. |

## Design consistency decisions
- **Half-open intervals:** `start < other.end && other.start < end`, so adjacent bookings do not conflict; see BR-01/BR-02 and the tested `TimeWindow` value object.
- **Pending is not confirmed:** Multiple pending requests may overlap. An approval must therefore recheck conflicts inside an atomic write transaction.
- **SQLite concurrency:** Use `BEGIN IMMEDIATE` before reading confirmed conflicts for a booking decision; hold the transaction through reservation and audit writes. A normal SELECT followed by a later INSERT is insufficient.
- **No post-start cancellation in v1:** UC-04 and the state diagram match BR-08.
- **Exactly one resource/user per reservation:** Stored as `user_id` and `resource_id` FKs, with multiple events through `reservation_id`.
- **Permission boundaries:** Ordinary users cannot approve or edit inventory. Domain/service authorization is authoritative; UI hiding is not an access-control mechanism.
- **Design-to-code honesty:** The current Flask/SQLAlchemy application implements booking services, state transitions, session checks and audit events. Repository interfaces and AuthService shown in design class diagrams are conceptual; the production prototype uses SQLAlchemy Sessions directly and Flask login routes. See `docs/traceability/MATRIX.md` for explicit deviations.

## 3NF argument
The logical design uses four tables: `users`, `resources`, `reservations`, and `reservation_events`. Each table has one surrogate primary key and stores facts about that entity only. Attributes such as a user's email and a resource's name are kept in their own tables, not copied into reservations or events. Every non-key field depends on its whole primary key, without a transitive dependency via another non-key attribute. `users.email` and `resources.public_code` are additional unique candidate identifiers. Audit events reference both the reservation and actor through separate foreign keys. These structures are designed to satisfy **third normal form (3NF)**; it must be verified against the implemented SQL schema.

### Constraints beyond an ordinary ERD
- Unique email and resource public code.
- Foreign keys from `reservations.user_id` / `reservations.resource_id`, and `reservation_events.reservation_id` / `reservation_events.actor_user_id`.
- `start_utc < end_utc` and enumerated role/status/category domain constraints.
- **No-overlap is cross-row**: ordinary SQL CHECK or UNIQUE is not enough in SQLite. It requires the `BEGIN IMMEDIATE` service transaction, conflict query and race-condition integration tests.
- `ReservationEvent` rows are audit records, not permission-free mutable public logs. Audit event IDs are independent of reservation IDs.

## Architectural trade-offs
A small local Flask + SQLAlchemy + SQLite monolith is appropriate for one developer and supports testable service-layer logic. SQLite's single-writer behavior can prevent race conditions with an immediate write transaction, but capacity, lock timeouts, and production operations need reassessment for real campus deployment.

## Required later validation
1. Run `python scripts/validate_models.py` (cross-artifact consistency checks).
2. Run the existing `python scripts/run_tests.py` and retain execution output.
3. Render every PlantUML source to PNG and SVG; check for syntax errors and missing files.
4. During implementation, add database concurrency, role, rollback and end-to-end tests; **model tests alone cannot prove behavior**.
5. Update design sources/exports whenever a change affects a state, attribute, role, or API.

## Limitations
The requirement policies are reasoned assumptions, not evidence from university stakeholders. This work is an engineering design baseline and does not imply every feature has been implemented.

## Change request CR-001 and implemented status view

The supplementary sequence [14](source/14-seq-CR-001-studio.puml) links the authenticated Studio to `BookingService.status_overview()`, confirmed-booking queries and `current_status` domain logic. The color-coded 15-minute status is calculated from stored confirmations rather than sensors; sample map coordinates are display-only and deliberately **not** in the 3NF ERD. See `docs/change-management/CR-001-visual-availability.md` and the traceability matrix.
