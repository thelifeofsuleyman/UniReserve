# UniReserve — Test Case Catalogue and Execution Record

**Baseline CI result:** 85 tests passed in [GitHub Actions run 45103587996](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45103587996); Python 3.11.18, Ubuntu runner; 94% package statement coverage. **Date:** 23 November 2026.

The table intentionally includes representative traceable tests, not one row per automated assertion. All mapped tests were part of the verified successful 85-test run. Input summaries refer to synthetic fixtures in source files. "Actual" reports the observed CI outcome, not made-up browser evaluations.

| Test ID | Requirement | Technique | Input / scenario | Expected result | Actual | Result | Executable case |
|---|---|---|---|---|---|---|---|
| TC-001 | FR-001 | EP / UC-01 | Valid pre-created student email + correct password | Signed-in session, catalogue accessible | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_valid_login_and_logout` |
| TC-002 | FR-001 | EP / UC-01 | Incorrect password | Generic denial; no session | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_invalid_password_does_not_create_session` |
| TC-003 | FR-001; NFR-004 | EP | Two seeded users / password verification | Salted hashes, no plaintext in DB | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_passwords.py::test_provisioning_does_not_store_plaintext` |
| TC-004 | FR-002 | UC-02 | Catalogue with one room and one camera | Both listed with names and codes; category filter works | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_catalogue_lists_resources_and_filters` |
| TC-005 | FR-003; FR-005 | BVA / UC-02 | Confirmed 10:00–12:00, request 12:00–13:00 | Adjacent permitted, shared minutes rejected | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_adjacent_allowed_and_partial_overlap_rejected` |
| TC-006 | FR-003 | UC-02 | Check availability form for free slot | Positive availability with no inserted reservation | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_check_availability_does_not_create_reservation` |
| TC-007 | FR-004 | UC-03 | Future enabled room, valid hour | Creates CONFIRMED with same-time audit event | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_confirm_standard_booking_and_atomic_event` |
| TC-008 | FR-004 | BVA | Past start; 15-day horizon; room >2h | Reject each invalid interval without database mutation | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_invalid_booking_window_and_policy_limits` |
| TC-009 | FR-004 | BVA | Exactly 2-hour room, exactly 24-hour equipment | Accept both boundary durations | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_duration_limits_accept_exact_boundary` |
| TC-010 | FR-004; FR-008 | State | Two overlapping camera requests requiring approval | Both remain PENDING_APPROVAL, slot not held | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_pending_request_does_not_hold_capacity` |
| TC-011 | FR-005; NFR-002 | Race/decision table | Two threads, same resource/time, repeated 50 times | Exactly one confirmed per trial; no overlapping confirmed rows | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_50_two_client_races_never_double_confirm` |
| TC-012 | FR-005; FR-008 | Race/state | Approval and request compete for same slot | Exactly one confirmed, other conflicts | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_concurrent_approval_and_booking_never_both_confirm` |
| TC-013 | FR-006 | EP / UC-04 | Two user accounts and booking owned by account A | B cannot list or inspect A booking by ID | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_other_user_cannot_see_or_cancel_owners_booking` |
| TC-014 | FR-007 | UC-04 | Owner cancels confirmed future booking | CANCELLED plus event; slot can be rebooked | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_cancel_releases_capacity_and_tracks_event` |
| TC-015 | FR-007 | BVA | Cancellation at booking start | Denied; reservation unchanged | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_cancellation_at_start_fails` |
| TC-016 | FR-007; FR-010 | EP | Other user submits victim reservation ID | Denied without ownership leak or state change | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_cannot_cancel_another_users_booking` |
| TC-017 | FR-008 | Decision table / UC-05 | Admin approves available pending camera | Confirmed and activity visible to owner | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_admin_can_approve_and_audit_is_visible_to_owner` |
| TC-018 | FR-008 | State / UC-05 | Admin rejects pending camera | REJECTED terminal; cannot approve afterwards | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_admin_rejection_is_terminal` |
| TC-019 | FR-008; FR-005 | Decision table | Two pending same camera, approve first then second | Second approval refused; no audit event added | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_approval_conflict_leaves_request_pending_and_no_event` |
| TC-020 | FR-009 | UC-06 | Admin creates/edit-disables a resource | Resources persist; disabled item not bookable, history preserved | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_admin_can_create_resource_and_disable_it` |
| TC-021 | FR-009; FR-010 | EP | Student POSTs admin inventory change | 403; inventory remains unchanged | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_nonadmin_cannot_mutate_resource_through_http` |
| TC-022 | FR-010 | EP / HTTP | Anonymous user tries booking | Redirect login; no new booking | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_anonymous_access_redirects_and_cannot_create_booking` |
| TC-023 | FR-010 | Security decision | Forgery of actor_id in POST form | Session identity wins, student remains owner | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_forged_session_user_id_does_not_escalate_privileges` |
| TC-024 | FR-010 | Security EP | Missing or corrupted CSRF token | HTTP 400 and no persistent mutation | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_web.py::test_csrf_missing_or_invalid_is_rejected_before_mutation` |
| TC-025 | FR-011 | Rollback | Exception while writing create audit event | Reservation AND event both rolled back | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_write_failure_rolls_back_booking_and_audit` |
| TC-026 | FR-011 | Rollback | Exception while approving audit event | Status and audit remain unchanged | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_write_failure_rolls_back_state_change` |
| TC-027 | FR-011 | DB integrity | Direct SQL UPDATE/DELETE on audit event | SQLite trigger blocks both operations | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_audit_events_cannot_be_edited_or_deleted_directly` |
| TC-028 | NFR-005 | Persistence | 20 committed bookings and events; dispose/reopen engine | All 20 persist with correct events | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_booking_service.py::test_20_bookings_survive_restart_with_audit` |
| TC-029 | CR-001; FR-003 | BVA | Booking starts in exactly 15 minutes | Status SOON (yellow) | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_live_status.py::test_yellow_when_exactly_fifteen_minutes_out` |
| TC-030 | CR-001; FR-003 | BVA | Booking starts in 16 minutes | Status AVAILABLE (green) | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_live_status.py::test_green_when_more_than_fifteen_minutes_out` |
| TC-031 | CR-001; FR-003 | BVA | Booking interval starts now | Status OCCUPIED (red) | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_live_status.py::test_red_when_booking_starts_now` |
| TC-032 | CR-001; FR-003 | BVA | Booking interval ends now | Status AVAILABLE unless another future starts within 15 minutes | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_live_status.py::test_green_when_booking_ends_now` |
| TC-033 | CR-001; FR-003 | Decision table | Disabled resource has active confirmed booking | Status DISABLED (gray priority) | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_live_status.py::test_gray_overrides_current_occupancy` |
| TC-034 | CR-001; FR-010 | HTTP / Security | Anonymous GET /api/availability-status | Redirect sign-in; no data exposed | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_visual_web.py::test_studio_requires_authentication` |
| TC-035 | CR-001; FR-003 | HTTP / Privacy | Authenticated GET status API | 200 no-store JSON; no owner emails | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_visual_web.py::test_status_endpoint_is_private_and_not_cached` |
| TC-036 | CR-001; FR-002 | UC-02 | Student GET /studio with room and camera | Both are clickable, demo map explicitly not to scale | Asserted outcome matched in CI run 45103587996 | PASS | `tests/test_visual_web.py::test_studio_renders_equipment_rooms_and_survey_warning` |

## Additional quality gates
- **NFR-001 latency:** `scripts/measure_latency.py` measures 200 sequential requests with 100 resources and 1,000 synthetic reservations. Results are documented in `M6_PERFORMANCE_REPORT.md` after the GitHub Actions probe runs.
- **NFR-002:** TC-011 includes 50 synchronized two-client race trials; no overlap was detected in verified CI runs.
- **NFR-003:** TC-013, 016, 021-024, 034-035 cover isolation and authorization. Automated coverage is not a substitute for a security audit.
- **NFR-004:** TC-003 checks password hashes; a public TLS deployment is out of scope.
- **NFR-005:** TC-028 checks restart durability of 20 bookings and their corresponding events.
- **NFR-006:** volunteer usability target NOT MEASURED; owner feedback drove CR-001, but does not constitute a 5-person study.
- **NFR-007:** full keyboard walkthrough NOT MEASURED. The templates include text labels and focus styles; this alone does not prove conformance.
- **NFR-008:** test command runs on Python 3.11, 94% package statement coverage in the cited CI run.

## Interpretation
A PASS is evidence for that named test input and environment, not a universal guarantee that the software has no bugs. Every fully traced Must requirement has at least one representative automated test; the matrix will link source code and diagrams in Milestone 7.
