# ADR-0002 — Transactional booking and approval
**Status:** Implemented and verified by booking/approval integration tests  
**Date:** 2026-11-23  
**Related requirements:** FR-003/004/005/007/008/010/011; BR-01/02/05/06/07/08.

## Decision
Use half-open UTC intervals; persist all reservation state and audit-event changes within one SQLite write transaction. For capacity-changing actions, **BEGIN IMMEDIATE** before reading conflicts. Unrestricted requests confirm in that transaction; restricted requests enter PENDING_APPROVAL without occupying capacity. Admin approval rechecks current enabled status and confirmed overlaps within a new immediate transaction before confirmation. Pending requests may overlap.

## Alternatives considered
1. **UI availability check alone:** rejected, as two users can see the same slot before saving.
2. **READ then INSERT in separate transactions:** rejected; race conditions can confirm overlapping reservations.
3. **Hold pending approvals as exclusive capacity:** rejected for v1 because abandoned requests can block resources; could be reconsidered with request expiry and fairness policy.
4. **Database exclusion constraint:** PostgreSQL can express powerful interval constraints, but SQLite's simple local deployment was selected. Our explicit transaction/recheck rule will need integration testing.

## Error and state behavior
- Invalid actor/owner, disabled resource, invalid interval, or confirmed conflict: reject with no state or audit write.
- Approval conflict: leave the request pending; do not alter confirmed reservations.
- Owner cancellation before start: change to CANCELLED, append audit event, commit.
- Terminal status: no new decision or cancellation.
- System crashes or event-write fails: rollback both reservation and audit event.
- Adjacent intervals are allowed.

## Verification plan
Run boundary-value tests, decision-table role/status tests, two-client race tests repeated at least 50 times, and rollback-on-failure tests. Report successes/failures honestly. The evaluated implementation now uses `write_transaction()` with `BEGIN IMMEDIATE` and includes 50 repeated two-client race tests. See QA report and the design/code deviation notes in `docs/traceability/MATRIX.md`.
