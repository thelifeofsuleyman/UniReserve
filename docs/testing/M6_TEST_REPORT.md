# UniReserve — Milestone 6 Testing Report

**Version:** 1.0 | **Project:** UniReserve | **Student:** Suleyman Shafizada (m666i1) | **Date:** 23 November 2026

## Summary of verified baseline

The latest verified code integration for the visual redesign (CR-001) passed **85 automated tests in 9.556 seconds** with **94% statement coverage** over `src/unireserve`. The results were obtained through [GitHub Actions 45103587996](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45103587996) using Python **3.11.18** on Ubuntu. This report is tied to that actual run; later performance runs are separately documented.

### Code coverage

| Module | Statements | Missed | Statement coverage |
|---|---:|---:|---:|
| Domain availability | 16 | 1 | 94% |
| Domain live status | 33 | 0 | 100% |
| Booking service | 228 | 6 | 97% |
| Account management | 41 | 5 | 88% |
| DB unit of work | 37 | 0 | 100% |
| SQLAlchemy models | 43 | 0 | 100% |
| Flask web app | 281 | 28 | 90% |
| **All package modules** | **679** | **40** | **94%** |

Source: the exact coverage output in the linked CI log. Coverage is rounded to the nearest whole percentage. It shows which statements were executed, **not** whether every logical condition, interaction or real deployment scenario is correct. Two-client race trials, approval state tests, ownership checks and rollback assertions provide evidence beyond statement coverage.

## Test design and requirements

[TEST_PLAN.md](TEST_PLAN.md) documents entry/exit criteria, tools, test levels and four systematic techniques. [TEST_CASES.md](TEST_CASES.md) presents 36 representative named cases with IDs, requirement IDs, test inputs, expected outcomes, actual verified outcomes and PASS status. The complete suite contains additional cases not separately enumerated there.

### Verified high-risk scenarios

- **Concurrent capacity:** 50 synchronized paired attempts to confirm the same resource/time; database inspection found at most one confirmed row per trial.
- **Approval workflow:** pending does not hold capacity; an admin approval conflict leaves the request pending without an extra event.
- **Audit atomicity:** failure while writing an audit event rolls back both the reservation and status transition.
- **Security:** signed session actor ID wins over submitted form identifiers; only admins decide/edit; CSRF failures cause HTTP 400 without mutation.
- **Data durability:** 20 representative bookings and events survive a database engine restart.
- **CR-001 UI:** state thresholds and precedence, private read-only status endpoint, 2D map links and labels.

## Non-functional verification status

| NFR | Verification | Status |
|---|---|---|
| NFR-001 | 200 sequential HTTP requests; 100 resources, 1,000 reservations | **Performance probe added; measured run results in M6_PERFORMANCE_REPORT.md.** |
| NFR-002 | 50 synchronized database race trials | PASS in CI 45103587996 |
| NFR-003 | HTTP and service-layer denial cases | PASS for tested cases; not a penetration audit |
| NFR-004 | Salted password-hash tests | PASS for seeded users |
| NFR-005 | 20 persisted bookings and events after restart | PASS in CI 45103587996 |
| NFR-006 | 5-volunteer, 3-minute user study | **NOT MEASURED** — no participants or results invented |
| NFR-007 | Keyboard-only walkthrough | **NOT MEASURED** — requires manual check |
| NFR-008 | Python 3.11 one-command tests, >=80% coverage | PASS at 94% |

## Defect and change evidence

Real-world setup issue ENV-001, original UI concern UX-001, and hosted preview limitation TOOL-001 are recorded in [DEFECT_LOG.md](DEFECT_LOG.md) with severity, discovery, resolution, and limitations. UX-001 is addressed by [CR-001](../change-management/CR-001-visual-availability.md). No unobserved code bugs have been invented.

## Exit assessment

Automated testing and coverage targets **pass** for the verified run. Latency evidence is collected in the following CI milestone. Manual usability/accessibility criteria remain **open**, and final quality assurance must not represent them as completed. The project is an offline local coursework prototype, not a production-secured multi-campus application.
