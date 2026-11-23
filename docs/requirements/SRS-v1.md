# UniReserve — Software Requirements Specification
**Version:** 1.1 updated baseline (CR-003) — pending simulated-stakeholder confirmation  
**Prepared for:** Suleyman Shafizada (group m666i1)  
**Date:** 23 November 2026  
**Source:** SWE_P1.pdf, project idea 6: Equipment and Room Rental System.

> These are derived requirements, not university-approved policies. They are based on the course brief, explicit design assumptions, and a study of two existing platforms. No stakeholder interviews or product trial were conducted.

## 1. Introduction and purpose
A university department shares cameras, laptops, lab equipment and study rooms. A paper calendar or informal messages can cause overlapping bookings and obscure which requests require approval. UniReserve will keep one catalogue and one authoritative record of reservations. The engineering emphasis is on requirements quality, design consistency, transaction safety and repeatable testing rather than frontend polish.

## 2. Scope
**Included in v1:** pre-created student/staff/admin accounts; login/logout; searchable resource catalogue and date availability; booking requests and cancellation; approval/rejection for restricted resources; server-side authorization; administrator inventory management; audit events; local Flask UI and SQLite persistence.

**Excluded in v1:** card payments, fines, waitlists, automated notification delivery, university SSO, multi-campus operation, barcode scanning, and automatic equipment damage valuation. Physical checkout/return is listed as a Should extension, not a required initial implementation.

## 3. Stakeholders
| Stakeholder | Main interest |
|---|---|
| Student | See availability, reserve an eligible resource and cancel their requests. |
| Staff | Reserve rooms and equipment for teaching or university tasks. |
| Resource administrator | Manage inventory, decide requests, investigate conflicts. |
| IT/operator | Create demo accounts, deploy locally, protect stored information. |
| Department manager | Obtain reliable availability and consistent policy enforcement. |
| Instructor/evaluator | Verify traceable requirements, diagrams, code, tests and change evidence. |

These are analytical roles, not people interviewed for this document.

## 4. Definitions and business rules
**Resource:** exactly one individually reservable room or equipment item. **Reservation:** a request by one user for one resource and interval. **Pending approval:** a request which is not yet a guaranteed booking. **Confirmed:** accepted and capacity-blocking. **Cancelled/Rejected:** terminal and nonblocking. **Audit event:** immutable record of actor, action, time, and status transition.

| ID | Agreed-for-project design assumption / rule |
|---|---|
| BR-01 | Use timezone-aware UTC timestamps and half-open intervals [start, end); start must precede end. |
| BR-02 | Intervals A and B overlap if A.start < B.end and B.start < A.end; adjacent bookings are permitted. |
| BR-03 | A request starts in the future and no more than 14 days ahead. |
| BR-04 | Maximum duration is two hours for a room and 24 hours for equipment (provisional policy). |
| BR-05 | No two CONFIRMED reservations for one resource overlap. In the AzTU-inspired demo, a student cannot hold two overlapping CONFIRMED study places even if they are different resources. Both checks run in the same database transaction. The student limit is a project fair-use assumption, not a verified AzTU policy. |
| BR-06 | A resource marked requires_approval creates PENDING_APPROVAL; pending requests do not block capacity. |
| BR-07 | Approval atomically rechecks enabled status and confirmed conflicts. If blocked, no state change occurs and the request remains pending. |
| BR-08 | A user can cancel their own pending/confirmed reservation only before the start; terminal bookings cannot be cancelled again. |
| BR-09 | Disabled resources reject new requests but remain in historical bookings. Disabling never silently cancels existing confirmations. |
| BR-10 | Sessions use pre-created demo accounts; role and owner checks are performed by the server, not trusted to browser controls. |

**State baseline:** PENDING_APPROVAL → CONFIRMED / REJECTED / CANCELLED; CONFIRMED → CANCELLED before start. No "pending holds" or automatic historical erasure. Checkout/return will add states only if the Should extension is implemented.

## 5. Functional requirements (MoSCoW)
Each requirement has a stable identifier. Every Must has acceptance criteria in §5.1.

| ID | Priority | Testable requirement |
|---|---|---|
| FR-001 | Must | Authenticate pre-provisioned student, staff and administrator accounts; reject invalid credentials and support logout. |
| FR-002 | Must | Display the resource catalogue with stable ID, name, category, enabled status and approval flag. |
| FR-003 | Must | Report whether an enabled resource is available for a specified valid time range, considering confirmed reservations. |
| FR-004 | Must | Let authenticated students and staff request an enabled resource in a valid future time range. |
| FR-005 | Must | Prevent overlapping CONFIRMED reservations for the same resource, including concurrent requests and approval actions; in demo study areas also prevent the same user from holding overlapping confirmed study places. |
| FR-006 | Must | Show users only their own reservation details and statuses. |
| FR-007 | Must | Permit the owner to cancel a PENDING_APPROVAL or CONFIRMED reservation before its start time. |
| FR-008 | Must | Allow administrators to approve or reject pending requests with an availability recheck on approval. |
| FR-009 | Must | Allow administrators to create, edit, enable and disable resources while preserving booking history. |
| FR-010 | Must | Enforce authentication, role and reservation ownership in server-side code for every protected operation. |
| FR-011 | Must | Append an audit event atomically for each successful reservation create, approve, reject and cancel. |
| FR-012 | Should | Allow administrators to record equipment checkout, return and overdue status. |
| FR-013 | Should | Filter the resource catalogue by resource category and enabled status. |
| FR-014 | Should | Allow configurable per-user limits on future reservations. |
| FR-015 | Could | Notify users by email on approval or cancellation. |
| FR-016 | Could | Maintain a waiting list for highly demanded resources. |
| FR-017 | Won't (v1) | Collect rental payments, deposits or fines. |
| FR-018 | Won't (v1) | Use institution SSO or external identity providers. |

### 5.1 Must requirement acceptance criteria
| Requirement | Acceptance criterion |
|---|---|
| FR-001 | Valid account signs in; incorrect password yields a generic denial and no session; logout invalidates session. |
| FR-002 | A signed-in user sees all seeded resources with these fields, and authorized changes appear in the catalogue. |
| FR-003 | A confirmed 10:00–12:00 booking conflicts with 11:00–13:00 but not 12:00–13:00; disabled resources are not bookable. |
| FR-004 | Valid normal-resource request becomes CONFIRMED; approval-required request becomes PENDING_APPROVAL; invalid ranges create no row. |
| FR-005 | For 50 pairs of simultaneous conflicting confirmations, at most one per pair commits and zero conflicting confirmed rows persist. One student cannot hold two concurrent study places; different students can book distinct resources. |
| FR-006 | User A's list contains A's bookings only; accessing B's reservation by ID does not disclose it. |
| FR-007 | Eligible owner cancellation changes status to CANCELLED; cancellation by others, after start, or on terminal states fails. |
| FR-008 | Admin approve confirms an available request, reject sets REJECTED; conflicts/disabled resources block approval; other roles cannot decide. |
| FR-009 | Admin edits persist and disabling prevents new bookings; non-admin changes are denied; existing booking history is preserved. |
| FR-010 | Each unauthorized scenario results in 401/403 or login redirect without any database mutation, regardless of client-supplied IDs. |
| FR-011 | Each success writes one actor/time/action/status-change event; rolled-back transactions write neither changes nor events. |

These are **planned acceptance checks**, not claims of current application coverage.

## 6. Non-functional requirements
The numbers below are verification **targets**, not measured results; when implemented, record the machine, test data, scripts and observed values.

| ID | Priority | Attribute | Measurable target |
|---|---|---|---|
| NFR-001 | Must | Performance | With 100 seeded resources and 1,000 reservations on a documented local environment, at least 95% of 200 sequential catalogue/availability requests finish server-side within 1.0 second. |
| NFR-002 | Must | Integrity | Fifty repeated two-client conflicting booking trials produce zero overlapping confirmed reservations; measure using integration tests and DB inspection. |
| NFR-003 | Must | Authorization | All tested unauthenticated, non-admin, and cross-user access attempts are denied and cause zero persistent modifications. |
| NFR-004 | Must | Credential security | All seeded password fields contain salted password hashes rather than plaintext; authentication tests confirm incorrect passwords never establish a session. |
| NFR-005 | Must | Durability | After an application restart, all 20 seeded sample bookings and their events are unchanged in a repeatable restart test. |
| NFR-006 | Should | Usability | At least four of five volunteer evaluators independently find and request a camera within three minutes using the test script; record results rather than assuming success. |
| NFR-007 | Should | Accessibility | All core forms and controls are keyboard-operable in a documented walkthrough, and every validation failure is conveyed by text, not color alone. |
| NFR-008 | Should | Maintainability | One test command passes on Python 3.11; target at least 80% statement coverage for implemented domain and service modules, measured with a coverage tool. |

## 7. Interfaces, constraints and data
**Technology choice:** Flask (browser UI/routes), framework-independent domain services, SQLAlchemy persistence, SQLite transaction-controlled writes. Python 3.11+. Desktop/local demonstration is sufficient; microservices and external cloud dependencies are unnecessary.

**Conceptual entities:** User (identity, role); Resource (ID, category, enabled, approval-required); Reservation (user, resource, start/end, status); ReservationEvent (actor, action, timestamp, before/after). Formal conceptual and 3NF logical ERDs are scheduled for the design milestone. Do not store genuine student data in seed accounts.

**Conflict implementation constraint:** a UI-only availability check is never sufficient. Recheck under a write transaction; concurrent attempts must not yield two confirmed reservations. Use integration tests in addition to the existing overlap unit tests.

## 8. Elicitation evidence and prioritization
Source 1: `SWE_P1.pdf`, sections 3–7, explicitly mentions conflicts, approvals, damaged items, late returns and priority users. Sources 2–3: official documentation of Springshare LibCal and Skedda, analyzed in `EXISTING_SYSTEMS_REVIEW.md`.

These sources justify including availability, configurable approval and permission rules. We deliberately defer physical checkout, quotas, notifications and payment to keep the required deliverables manageable. The competitor products were **not** used or tested hands-on.

## 9. Assumptions, constraints, risks, open issues
**Assumptions:** resources are individually identified; account creation is handled outside the application; an approval queue can contain competing requests; a single physical resource supports at most one confirmed booking at a time; admins can disable resources without deleting history.

**Constraints:** individual project; submission deadline 2 December 2026; MoSCoW priorities; use cases, UML, two ERDs (3NF), automated and systematic tests, defect log, traceability, change analysis, Git history, and reflection with AI-use disclosure.

**Risks:** naive check-then-insert causing concurrent double booking (high); unauthorized role elevation (high); treating pending as reserved in one layer but not another (medium); drifting document/implementation state transitions (medium).

**Unresolved questions:**
1. Should staff receive priority for restricted equipment?
2. Are cleaning/return buffers required?
3. Should per-user booking quotas be mandatory?
4. Who decides a pending request that is never reviewed?
5. Does the instructor expect physical checkout/return inside Must scope?

These questions require a policy decision or recorded change request; neither the course idea nor public websites supply actual local university policy.

## 10. Use-case and verification mapping
| Use case | Requirement coverage |
|---|---|
| UC-01 Authenticate | FR-001, FR-010 |
| UC-02 Browse and check availability | FR-002, FR-003, FR-010 |
| UC-03 Request booking | FR-004, FR-005, FR-010, FR-011 |
| UC-04 Cancel own booking | FR-006, FR-007, FR-010, FR-011 |
| UC-05 Approve/reject request | FR-005, FR-008, FR-010, FR-011 |
| UC-06 Manage resources | FR-009, FR-010 |

All six use cases are specified in `USE_CASES-v1.md`. Every use case must appear in an appropriate sequence diagram in the design milestone. The formal traceability matrix later maps each Must requirement to use case, domain/design classes, code module and test case ID. Changes must update affected docs, diagrams and tests together.

## 11. Change management
Log each genuine change request with ID, reason, impact on requirement IDs, diagrams, schema, code, tests and estimates; record the accept/reject decision. Do not invent historical stakeholder decisions or defects to fill process evidence.

## 12. References
- Course handout: `SWE_P1.pdf`, Software Engineering Project, sections 3–7.
- Springshare LibCal: https://www.springshare.com/libcal
- Springshare library space reservations: https://blog.springshare.com/2025/05/managing-room-reservations-for-libraries-of-all-sizes
- Skedda booking rules: https://www.skedda.com/platform/fully-customizable-booking-system
- Skedda approvals: https://support.skedda.com/en/articles/11774950-booking-requests-approvals

Official product pages consulted 23 November 2026.

## CR-002 — University PC and seat-booking extension (23 Nov 2026)

The original baseline scope included equipment lending. A user-requested change refocuses the demonstrator on **library study seats, library PCs and teaching-lab workstations**. For new demonstration areas, each seat/PC is an individually reservable Resource belonging to a Space; no student can book an entire PC laboratory merely by requesting one workstation. Reservations must fit the area's configurable local operating hours and weekdays, cannot overlap an administrator closure, and still obey FR-005 concurrency protection. Hidden legacy demo equipment is not bookable, but historical records remain. Detailed new rules AZ-01 through AZ-06, sourced facts vs illustrative campus assumptions, tests and impact are maintained in `docs/change-management/CR-002-aztu-seat-reservations.md`. Library hours 09:00–17:30 are publicly referenced by AzTU; assigned demo weekdays, room identities and PC quantities are *not* verified AzTU facts. The original FR IDs and Must acceptance criteria remain traceable, while this extension refines their policy and catalogue acceptance conditions.


## CR-003: user-level fairness and visual review

Actual owner feedback reported that the previous UI felt visually generic. The new UI uses original offline illustrative images, stronger hierarchy, a filterable 2D map, and synchronizes color+text status indicators. The proposed fair-use rule extends BR-05 and FR-005 without renumbering the requirements. The system also prevents an administrator edit from silently invalidating future confirmed reservations. See `docs/change-management/CR-003-ux-and-integrity.md`. Real AzTU seat assignment and the one-simultaneous-booking policy remain **unverified demonstration assumptions**.


## CR-005 — Product presentation and production-mode controls

The owner's feedback prompted a less intrusive user interface: booking screens no longer display internal project/setup reminders, while the distinct `/about` page preserves factual information about configured room data and non-sensor availability. FR-001/010 and NFR-003/004 now have a production configuration baseline: stable secret, explicit trusted hosts, Secure session cookies and security headers. FR-009 extends to authorized creation of Spaces, not only inventory inside pre-created areas. No original requirement IDs were renumbered and the existing booking transaction/status rules were not weakened. See CR-005, its QA and traceability addenda, and `docs/deployment/OPERATIONS.md`. A documented hosting path is not proof of an officially approved public university deployment.


## CR-006 — Date-specific reservation calendar

Owner feedback identified that the live-status map's green badge could be mistaken for future booking availability. FR-003 now includes a date-specific schedule of 30-minute units on each room/PC booking page. Only confirmed bookings block those units; pending approval, cancelled and rejected reservations do not. Existing operating hours, closures, 14-day advance horizon and one-confirmed-study-place-per-user checks still apply. FR-006 now includes a read-only seven-day *owner-only* booking agenda, while cancelled/rejected rows remain in personal history. User selection on the calendar populates but does not bypass the booking form or its atomic write-time checks. Details: `docs/change-management/CR-006-calendar-availability.md`, related test and traceability addenda. No schema migration or changed requirement IDs.
