# UniReserve — Requirements Traceability Matrix

**Version:** 1.0, 23 November 2026. **Student:** Suleyman Shafizada (m666i1).

## A. Every Must functional requirement is traced

Each UML filename is under `docs/diagrams/source`. Each code path and test ID points to a real artifact; the 36 named cases in `docs/testing/TEST_CASES.md` were verified by GitHub Actions. This is a consistency index, not a promise of exhaustive scenario coverage.

| FR | Use case | UML design elements | Existing code modules | Executed test IDs | Result |
|---|---|---|---|---|---|
| FR-001 | UC-01 | 02-domain-model.puml; 08-seq-UC-01-authenticate.puml | `src/unireserve/web/app.py`; `src/unireserve/storage/accounts.py` | TC-001, TC-002, TC-003 | PASS |
| FR-002 | UC-02, UC-06 | 01-use-cases.puml; 09-seq-UC-02-availability.puml; 14-seq-CR-001-studio.puml | `src/unireserve/web/app.py`; `src/unireserve/web/templates/resources.html` | TC-004, TC-036 | PASS |
| FR-003 | UC-02 | 03-reservation-states.puml; 09-seq-UC-02-availability.puml; 14-seq-CR-001-studio.puml | `src/unireserve/domain/availability.py`; `src/unireserve/domain/live_status.py`; `src/unireserve/services/booking.py` | TC-005, TC-006, TC-029, TC-030, TC-031, TC-032, TC-033 | PASS |
| FR-004 | UC-03 | 03-reservation-states.puml; 10-seq-UC-03-request.puml | `src/unireserve/services/booking.py`; `src/unireserve/web/app.py` | TC-007, TC-008, TC-009, TC-010 | PASS |
| FR-005 | UC-03, UC-05 | 05-erd-logical-3nf.puml; 10-seq-UC-03-request.puml; 12-seq-UC-05-approve.puml | `src/unireserve/services/booking.py`; `src/unireserve/storage/db.py` | TC-005, TC-011, TC-012, TC-019 | PASS |
| FR-006 | UC-04 | 02-domain-model.puml; 11-seq-UC-04-cancel.puml | `src/unireserve/services/booking.py`; `src/unireserve/web/app.py` | TC-013 | PASS |
| FR-007 | UC-04 | 03-reservation-states.puml; 11-seq-UC-04-cancel.puml | `src/unireserve/services/booking.py`; `src/unireserve/web/app.py` | TC-014, TC-015, TC-016 | PASS |
| FR-008 | UC-05 | 03-reservation-states.puml; 12-seq-UC-05-approve.puml | `src/unireserve/services/booking.py`; `src/unireserve/web/app.py` | TC-017, TC-018, TC-019 | PASS |
| FR-009 | UC-06 | 05-erd-logical-3nf.puml; 13-seq-UC-06-resources.puml | `src/unireserve/services/booking.py`; `src/unireserve/web/templates/admin.html` | TC-020, TC-021 | PASS |
| FR-010 | UC-01, UC-03, UC-04, UC-05, UC-06 | 06-design-classes.puml; 08-seq-UC-01-authenticate.puml; 12-seq-UC-05-approve.puml | `src/unireserve/web/app.py`; `src/unireserve/services/booking.py` | TC-013, TC-016, TC-021, TC-022, TC-023, TC-024, TC-034 | PASS |
| FR-011 | UC-03, UC-04, UC-05 | 02-domain-model.puml; 05-erd-logical-3nf.puml; 10-seq-UC-03-request.puml; 11-seq-UC-04-cancel.puml | `src/unireserve/services/booking.py`; `src/unireserve/storage/db.py`; `src/unireserve/storage/models.py` | TC-025, TC-026, TC-027 | PASS |

**Untraced Must functional requirements: none.** A full requirement cross-reference check is automated by `scripts/validate_traceability.py`. Testing results apply to the cited fixtures and CI environment, not every possible deployment.

## B. Remaining functional requirements and meaningful gaps

| Requirement | Priority | State | Notes |
|---|---|---|---|
| FR-012 | Should | NOT IMPLEMENTED | Physical checkout, return and late/damage handling are documented extensions, not silently treated as complete. |
| FR-013 | Should | IMPLEMENTED | Resource text/category filter in `web/app.py`, `templates/resources.html`, `test_web.py::test_catalogue_lists_resources_and_filters`. |
| FR-014 | Should | NOT IMPLEMENTED | Configurable per-user reservation quota is deferred. |
| FR-015 | Could | NOT IMPLEMENTED | Email delivery was deliberately left out of v1. |
| FR-016 | Could | NOT IMPLEMENTED | Waitlist not provided. |
| FR-017 | Won't | EXCLUDED | No payment processing. |
| FR-018 | Won't | EXCLUDED | No university SSO. |

## C. Nonfunctional requirements and verification gaps

| NFR | Status | Evidence |
|---|---|---|
| NFR-001 | PASS (CI environment) | `scripts/measure_latency.py`: 200/200 under 1s, p95 0.03152s, CI 45103990514. |
| NFR-002 | PASS | TC-011 fifty two-client race trials and TC-012 competing approval/request. |
| NFR-003 | PASS for covered cases | TC-013, TC-016, TC-021..024 and TC-034/035. No external security audit. |
| NFR-004 | PASS | TC-003 and account hash verification. |
| NFR-005 | PASS | TC-028: 20 reservations plus events after restart. |
| NFR-006 | NOT MEASURED | Five-person timed usability study requires real volunteers. |
| NFR-007 | NOT MEASURED | Manual keyboard-only accessibility walkthrough. |
| NFR-008 | PASS | One-command tests, Python 3.11, 94% statement coverage in CI. |

## D. Design versus actual code: documented deviations

1. **Repository classes:** The design class diagram uses interfaces as architectural abstractions, while the implementation performs SQLAlchemy Session queries directly inside BookingService. For an individual coursework prototype, a separate repository adapter layer would add scaffolding; booking/service responsibilities remain distinct from Flask UI.
2. **Unit-of-work representation:** The design diagram names `SQLiteUnitOfWork`, but implemented behavior is `write_transaction(engine)` in `storage/db.py`, using BEGIN IMMEDIATE. Its transaction semantics match the intended architecture.
3. **AuthService representation:** Authentication operations are split between Flask routes and `storage/accounts.py`, not a standalone AuthService class.
4. **Physical location:** CR-001 studio positions are illustrative and generated at display time; no location fields were added to the logical 3NF ERD. A genuine physical layout requires verified coordinates and would be a new change request.
5. **User experience:** Added the supplementary sequence diagram `14-seq-CR-001-studio.puml` for the authenticated read-only status API, without changing the existing UC-01..06 sequence diagrams.

## E. Test and requirement orphan assessment

Every Must requirement has an actual UC, diagram, source code file and named automated test. Some unit helper tests are not individually assigned TC numbers but still contribute to the 85-test suite; this is not an assertion that all helper assertions represent distinct requirements. The deliberate gaps NFR-006/007 and FR-012/014/015/016 are visible rather than falsely completed.

## F. Change control and updates

CR-001 was requested by the owner after a real UI review. Its effect on FR-002/003, domain status rules, Flask read-only routes, UI assets, tests and architecture is recorded in `docs/change-management/CR-001-visual-availability.md` and the supplementary sequence. Any future change must update the SRS, diagrams, code, tests and this matrix together.
