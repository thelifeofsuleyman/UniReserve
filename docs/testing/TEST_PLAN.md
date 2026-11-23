# UniReserve — Test Plan

**ID:** TP-v1.0 | **Date:** 23 November 2026 | **Author:** Suleyman Shafizada (m666i1)  
**System under test:** UniReserve, a local Flask + SQLAlchemy + SQLite university resource booking application.

## 1. Objectives and scope

Verify all 11 Must-priority functional requirements FR-001 through FR-011, measurable NFRs, and the accepted UI change CR-001. Demonstrate that availability cannot cause overlapping confirmations even under concurrent requests. Verify both success and error flows rather than counting only happy paths. The room/equipment map is an **illustrative UI**, not sensor-based physical occupancy.

## 2. Test levels, tools, ownership and evidence

| Level | Intent | Tools / files | Evidence |
|---|---|---|---|
| Unit | Pure half-open interval, password and indicator thresholds | `unittest`, `test_availability.py`, `test_live_status.py`, `test_passwords.py` | CI log, coverage |
| Integration | Real SQLite transactions, approval/cancellation, audit atomicity, race conditions, persistence and status reads | SQLAlchemy + temporary on-disk SQLite; `test_booking_service.py`, `test_status_integration.py` | CI log including 50 synchronized two-client trials |
| HTTP/system | Login sessions, signed-cookie actor identity, CSRF, forms, permissions, resource screens, 2D studio and read-only status API | Flask test client; `test_web.py`, `test_visual_web.py` | CI log and response assertions |
| Nonfunctional performance | 200 sequential catalogue/status HTTP requests with 100 resources and 1,000 reservations | `scripts/measure_latency.py`, `time.perf_counter` | GitHub Actions performance log |
| Static model consistency | Requirement IDs, use cases, entity keys and transaction-state diagrams | `scripts/validate_models.py`, PlantUML exports | GitHub Actions logs |
| Manual UI | Readability, keyboard-only navigation, touch targets, responsive layout, owner satisfaction | Browser on student's machine | **Not executed by the automated test suite**; record only genuine review |

## 3. Entry criteria

Python 3.11+, dependencies from `requirements-dev.txt`, writable temporary SQLite directory, deterministic fixture accounts, test service startup and trusted local test configuration. All cases use synthetic `*.test` and `example.invalid` addresses; no real user credentials or personal records. For UI review, student must run the local app and log in with their own generated demo credentials.

## 4. Exit criteria

1. All automated unit, integration and HTTP tests pass and CI is green.
2. 50 synchronized competing reservation trials persist zero double confirmations.
3. No high-severity security or data-integrity defect is known unresolved.
4. At least 80% statement coverage across `src/unireserve` and a written caveat explaining what coverage does not prove.
5. The NFR-001 measured latency target is evaluated using the reproducible probe; any failed target must be reported honestly, not hidden.
6. All Must requirements have design, code and test traceability in Milestone 7.
7. Any unperformed manual usability/accessibility evaluation is marked unverified rather than passed.

## 5. Systematic test design techniques

**Equivalence partitioning:** valid/invalid credentials; authenticated/anonymous; admin/student; enabled/disabled resource; owner/other user; confirmed/pending reservation. Each group has representative tests rather than arbitrary examples.

**Boundary value analysis:** zero-length and reversed intervals; adjacent windows with half-open boundary; duration at and above the configured maximum; cancellation immediately at start; yellow status exactly 15 minutes before booking, green at 16 minutes, occupied at start, green at end.

**Decision-table testing:** actor role × reservation state × action × confirmed conflict × resource-enabled flag determines approval, rejection, cancellation or forbidden outcome. See `TC-017` through `TC-023` in `TEST_CASES.md`.

**State-transition testing:** PENDING_APPROVAL to CONFIRMED/REJECTED/CANCELLED, CONFIRMED to CANCELLED, and rejection of illegal transitions from terminal states. These correspond to the reservation state diagram.

**Use-case-based testing:** UC-01 login, UC-02 catalogue/availability, UC-03 request, UC-04 cancel, UC-05 approve/reject, UC-06 inventory management, plus CR-001 Studio.

## 6. Failure, concurrency and data handling

Every state-changing operation should produce a corresponding immutable event. Simulated event-write failures test rollback of reservation and audit event together. The 50 race trials synchronize two threads on a barrier and verify the persisted DB state, not merely HTTP response text. The 20-booking restart test checks durable state across a new engine. SQLite transactions use BEGIN IMMEDIATE to serialize competing write decisions. This does not mean SQLite would be an ideal production-scale booking backend.

## 7. Execution commands

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_models.py
coverage run --source=src/unireserve scripts/run_tests.py
coverage report -m --fail-under=80
python scripts/measure_latency.py
```

CI runs equivalent checks on Ubuntu with Python 3.11, reports coverage and fails on any test/latency gate. Keep the GitHub Actions run link and the code revision together when quoting results.

## 8. Threats to validity

- CI-based timing is hardware- and load-dependent and is **not** a production benchmark.
- Automation does not demonstrate real user satisfaction, keyboard accessibility, or room layout accuracy.
- The 2D positions are not surveyed; red/yellow/green reflects confirmed reservations only, not physical presence.
- Code coverage indicates executed lines, not the absence of logic errors; 100% coverage would not guarantee correct concurrency behavior.
- The security tests do not represent a full penetration test, nor do they validate TLS/session security under public deployment.
