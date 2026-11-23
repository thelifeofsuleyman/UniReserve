# Initial scope (draft v0.1)

> These are provisional requirements for discussion and review, **not** the final SRS. Sources: SWE project brief and initial engineering assumptions.

## Stakeholders

- **Student:** can view and request available rooms/equipment and manage own reservations.
- **University staff:** can do the same; eligibility and priority rules need clarification.
- **Resource administrator:** manages resources, reviews approval-required requests, and records returns.
- **University IT:** responsible for account access, backups, and operating the system.

## Candidate Must requirements

| ID | Candidate requirement | Priority |
|---|---|---|
| FR-001 | Authorized users can view resources and their basic availability. | Must |
| FR-002 | An authorized user can request a resource for a valid future time interval. | Must |
| FR-003 | A resource cannot have two active reservations with overlapping time intervals. | Must |
| FR-004 | A user can cancel a reservation they own when the cancellation policy permits it. | Must |
| FR-005 | An administrator can approve or reject requests requiring approval. | Must |
| FR-006 | An administrator can add or deactivate a resource. | Must |
| FR-007 | The system must enforce user permissions for all protected actions. | Must |

## Candidate additional requirements

| ID | Candidate requirement | Priority |
|---|---|---|
| FR-008 | Administrators can record checkout, return, and overdue status. | Should |
| FR-009 | Users can filter resources by type. | Should |
| FR-010 | Users receive reminder emails. | Could |
| FR-011 | The system processes payments and deposits. | Won't (v1) |

## Initial acceptance criterion example

**FR-003 (time conflict)**: Given an approved reservation for camera C from 10:00 to 12:00, when another eligible user tries to reserve camera C from 11:00 to 13:00, the new request must be rejected without creating a conflicting active reservation. A reservation from 12:00 to 13:00 must be allowed if all other constraints are satisfied.

## Assumptions and open decisions

- Reservations use half-open intervals: **[start, end)**, so adjacent reservations do not conflict.
- Timestamps are stored in UTC and localized for display. Aware datetimes are mandatory in the domain rule.
- The meaning of “active” and which statuses block a slot must be specified in the formal state model.
- Whether staff receive booking priority is currently unresolved.
- Time limits, max bookings per user, privacy/data retention, and account enrollment require decisions.
- The reservation conflict rule must be enforced atomically in the database transaction, not just checked in application memory.
- The final SRS needs at least five measurable non-functional requirements and acceptance criteria for every Must requirement.

## Required elicitation work

Analyze at least two real booking applications, record observations, and cite them in the SRS appendix. Avoid treating these provisional assumptions as confirmed user requirements.
