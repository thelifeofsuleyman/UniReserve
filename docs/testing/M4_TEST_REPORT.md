# Milestone 4 — Unit, Integration and Concurrency Evidence

**Author:** Suleyman Shafizada (m666i1)
**Initial execution:** Linux / Python 3.13 / SQLAlchemy 2.0.50 / SQLite / coverage.py. GitHub Actions independently runs Python 3.11 on pull requests and main.

## Test strategy

| Evidence | Technique | Requirements |
|---|---|---|
| TimeWindow edge cases | Boundary values: adjacent/partial/identical/zero-length | FR-003/005, BR-01/02 |
| Booking policy/state | Equivalence partitions: past/future, enabled/disabled, room/equipment; state changes | FR-003/004/007/008 |
| Permissions | Decision cases: student/staff/admin/disabled × request/approve/edit/other-owner | FR-006/008/009/010, NFR-003 |
| SQLite competition | 50 synchronized two-client races; pending approval vs new booking | FR-005, NFR-002 |
| Atomic writes | Failure injection in audit-event generation; assert booking and audit rollback | FR-011 |
| Durability and privacy | Restart with 20 bookings, password hash tests, FK integrity, immutable event triggers | NFR-004/005 |

## Observed local results

- 35 tests passed with python scripts/run_tests.py.
- All 50 synchronized two-client conflict trials preserved one confirmed booking each and zero double-confirmations.
- An approval-versus-new-booking competition also preserved only one confirmed booking.
- Failed audit writes rolled back both new booking and pending approval changes.
- Restart test recovered 20 reservations and 20 creation audit events.
- Coverage measured 96% statement coverage (335 measured statements, 13 not executed). Coverage tells us which statements ran, NOT correctness of every branch or user workflow.

These are actual local observations, not claims about web integration or production reliability. GitHub Actions stores separate remote logs and a downloadable coverage XML artifact.

## Reproduce

    python -m pip install -r requirements-dev.txt
    python scripts/run_tests.py
    python scripts/validate_models.py
    coverage run --source=src/unireserve scripts/run_tests.py
    coverage report -m --fail-under=80

## Remaining verification

- End-to-end Flask/browser authorization, CSRF protection, real API 401/403 behavior, usability and accessibility tests remain pending.
- NFR-001 performance with large seed data and backup/restore tests are not yet measured.
- Defects will be logged when observed, not fabricated.
