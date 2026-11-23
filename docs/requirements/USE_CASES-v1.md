# UniReserve — Full Textual Use Cases
**Version:** 1.0 (23 November 2026) · **Student:** Suleyman Shafizada / m666i1

Use cases below specify the application boundary, actors, preconditions, triggers, main flow, alternative/error flows and postconditions. They will be paired with an overall use-case diagram and scenario sequence diagrams in the design milestone.

## UC-01 — Authenticate
**Primary actor:** Student / Staff / Administrator  
**Requirement trace:** FR-001, FR-010  
**Preconditions:** A pre-created enabled account exists.  
**Trigger:** Actor selects Sign in.

**Main success scenario**
1. System displays email/password form.
2. Actor submits credentials.
3. System checks matching account and password hash.
4. System establishes an authenticated session with server-side role.
5. System navigates to catalogue; logout destroys the session.

**Alternative/error flows**
- A1: Invalid credentials: show generic denial, create no session.
- A2: Blank/malformed fields: reject input; do not authenticate.
- A3: Expired session: require a new login before protected operations.

**Postconditions:** A valid session exists only after success; failure changes no authenticated state.

---

## UC-02 — Browse resources and check availability
**Primary actor:** Student / Staff / Administrator  
**Requirement trace:** FR-002, FR-003, FR-010  
**Preconditions:** Actor is authenticated.  
**Trigger:** Actor opens Resources.

**Main success scenario**
1. System lists resource IDs, names, types, enabled and approval flags.
2. Actor chooses a resource and an interval.
3. System validates timezone-aware interval with start < end.
4. System checks resource state and confirmed bookings for overlap.
5. System reports availability and whether an eventual request needs approval.

**Alternative/error flows**
- A1: Invalid interval: display validation error without saving a booking.
- A2: Disabled or missing resource: report unavailable.
- A3: Conflicting confirmation: report unavailable and invite another time.
- A4: Empty catalogue: display an empty state rather than a broken form.

**Postconditions:** No booking changed. Shown availability is informational and must be rechecked during confirmation.

---

## UC-03 — Request reservation
**Primary actor:** Student or Staff  
**Requirement trace:** FR-004, FR-005, FR-010, FR-011  
**Preconditions:** Signed-in user and enabled resource.  
**Trigger:** Actor chooses Book and submits times.

**Main success scenario**
1. System verifies account, resource, future interval, 14-day horizon and duration limit.
2. System enters a write transaction and checks confirmed conflicts.
3. For unrestricted resource, create CONFIRMED reservation; for approval-required resource, create PENDING_APPROVAL.
4. System appends actor/time/status event in the same transaction.
5. System commits and returns reservation ID and status.

**Alternative/error flows**
- A1: Past, zero-length, too-distant or too-long interval: no save.
- A2: Disabled/unknown resource: refuse request.
- A3: Confirmed conflict: rollback and explain conflict.
- A4: Competing simultaneous request: transaction recheck prevents second confirmation.
- A5: Write failure: rollback both reservation and audit event.

**Postconditions:** One new request and one matching audit event, or no database change.

---

## UC-04 — View and cancel own booking
**Primary actor:** Student or Staff  
**Requirement trace:** FR-006, FR-007, FR-010, FR-011  
**Preconditions:** Signed-in actor owns an existing booking.  
**Trigger:** Actor opens My Reservations and selects Cancel.

**Main success scenario**
1. System lists only actor-owned reservations.
2. Actor selects pending/confirmed reservation.
3. System transactionally verifies ownership, status and current time before start.
4. System records CANCELLED and its matching audit event.
5. System commits and shows updated booking.

**Alternative/error flows**
- A1: Different owner: deny without showing private data.
- A2: At/after start: reject cancellation.
- A3: Already terminal: reject duplicate transition.
- A4: Concurrent decision: re-read state inside transaction; only valid transition succeeds.

**Postconditions:** Successful cancellation no longer blocks capacity; other records remain untouched.

---

## UC-05 — Approve or reject restricted booking
**Primary actor:** Resource Administrator  
**Requirement trace:** FR-005, FR-008, FR-010, FR-011  
**Preconditions:** Authenticated administrator; pending request exists.  
**Trigger:** Administrator opens Pending Approvals.

**Main success scenario**
1. System lists pending requests and their time/resource.
2. Administrator selects one and chooses Approve or Reject.
3. System checks role and that request remains pending.
4. On Approve, transactionally recheck resource enabled and confirmed conflicts.
5. System sets CONFIRMED or REJECTED and appends audit event.
6. System commits and displays decision.

**Alternative/error flows**
- A1: Non-admin request: 403, no change.
- A2: Previously decided/cancelled: do not transition twice.
- A3: Conflict or disabled resource during approval: leave pending, show reason.
- A4: Storage error: rollback state and event together.

**Postconditions:** Exactly one valid decision plus event, or no mutation.

---

## UC-06 — Maintain resource catalogue
**Primary actor:** Resource Administrator  
**Requirement trace:** FR-002, FR-009, FR-010  
**Preconditions:** Admin session is active.  
**Trigger:** Administrator opens Manage Resources.

**Main success scenario**
1. System lists resources and edit/add controls.
2. Administrator supplies resource ID/name/category/approval flag/enabled status.
3. System checks admin role, required fields and unique resource ID.
4. System saves validated edits.
5. If disabling, system blocks future requests but retains historical reservations.

**Alternative/error flows**
- A1: Non-admin action: deny before mutation.
- A2: Duplicate ID or invalid fields: show error and save nothing.
- A3: Existing bookings on disabled resource: show warning; do not silently cancel confirmations.

**Postconditions:** Inventory reflects authorized change without destroying booking history.

## Testing and consistency notes

**Equivalence partitions:** eligible/unauthorized actors, active/disabled resources, valid/invalid intervals, pending/confirmed/terminal states.

**Boundary values:** exactly adjacent intervals; one-minute overlaps; duration at/above limit; cancellation immediately before versus at start; past versus future booking.

**Decision table dimensions:** role × reservation state × approval requirement × conflict × expected action. **State testing:** pending → approved/rejected/cancelled, confirmed → cancelled before start; forbid invalid terminal transitions.

**Integration tests:** two simultaneous conflicting booking transactions, approval with stale availability, rollback on event-write failure, and cross-account ownership attempts. Unit-testing a time-overlap function alone does not demonstrate double-booking prevention.

**Design mapping:** Each UC will have a corresponding scenario sequence diagram, so no UC is orphaned. Domain and logical-ERD entities must match the SRS; the final traceability matrix will identify exact source and test files.
