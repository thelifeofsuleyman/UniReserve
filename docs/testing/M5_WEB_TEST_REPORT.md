# Milestone 5 — HTTP/Flask integration test plan and report

**Baseline:** Database and booking service from milestone 4, plus a Flask presentation layer from milestone 5.

## Test strategy

- **Unit:** half-open interval and password-hash checks (`test_availability.py`, `test_passwords.py`).
- **Integration:** SQLite transaction, event rollback, state transitions, 50 concurrent-booking trials (`test_booking_service.py`).
- **System/HTTP:** browser route access, signed sessions, form CSRF, timezone input, booking and admin screens, ownership and role authorization (`test_web.py`).
- **Static design consistency:** `scripts/validate_models.py` tracks requirements/diagrams. Existing models describe service dependencies and remain relevant.

## Entry and exit criteria

Entry: Python dependencies install; temporary test databases can be created; test account provisioning succeeds. Exit: all unit/integration/HTTP tests pass, 50 race trials yield no confirmed overlaps, no high-severity known HTTP bug remains; code coverage is >=80% for the covered package; architecture validation passes. Test runner must exit nonzero on failure.

## Testing technique examples

| Technique | Representative tests | Requirement |
|---|---|---|
| Equivalence partitioning | valid vs invalid passwords; student vs admin; enabled vs disabled resource; own vs other user's reservation | FR-001/004/007/010 |
| Boundary values | adjacent vs overlapping intervals; empty/reversed range; time at cancellation cutoff | FR-003/005/007 |
| Decision table | actor role × pending/confirmed state × action approval/cancellation × resource conflicts | FR-005/007/008/010 |
| State transition | PENDING_APPROVAL→CONFIRMED/REJECTED/CANCELLED, CONFIRMED→CANCELLED; deny terminal transitions | FR-007/008/011 |
| Use-case/system | UC-01 sign in/out, UC-02 browse/check, UC-03 book, UC-04 cancel, UC-05 approve, UC-06 catalogue edit | All six UCs |

## Test execution

**Local static verification:** Python compileall completed. The 35 existing milestone-4 domain/database tests passed locally before publishing milestone 5. Full web tests require Flask, which must be installed by `pip install -r requirements-dev.txt` in the student environment or GitHub Actions.

**GitHub Actions:** Workflow `Python unit and integration tests` installs the new Flask + tzdata dependencies and runs all tests with package coverage. Inspect the most recent green run in the repository Actions tab. The definitive run ID, total tests, coverage percentage and conclusion should be recorded after a verified run rather than invented here.

## Defect tracking and feedback

Real failures go into the final defect log with test ID, steps, observed result, expected result, severity, fix and verification commit. UI opinions are collected in `docs/ui/UI_FEEDBACK_LOG.md` and can drive change requests. This milestone does not falsely claim a real external usability study.
