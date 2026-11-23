# CR-002 Supplementary Traceability

This is an **addendum** to the original 11 Must functional requirement mappings, not a claim that all campus rules were in the initial SRS. All paths below are relative to repository root.

| New rule | Existing FR | Design | Implementation | Tests |
|---|---|---|---|---|
| AZ-01 Individual bookable seat/PC | FR-002, FR-004, FR-005 | `15-aztu-space-extension.puml` | `storage/models.py`, `storage/aztu_demo.py`, `services/booking.py` | `test_aztu_policy.py::test_each_pc_has_separate_capacity`, `test_aztu_web.py::test_studio_lists_zone_seats_and_not_camera_gear` |
| AZ-02 Opening hours and weekdays | FR-003, FR-004 | `16-aztu-booking-hours-sequence.puml` | `domain/operating_hours.py`, `services/booking.py` | `test_aztu_policy.py::test_opening_boundaries_inclusive_start_and_closing_end`, `test_weekend_rejected_and_no_audit` |
| AZ-03 Block teaching/maintenance | FR-005, FR-008, FR-009 | `15-aztu-space-extension.puml`, `16-aztu-booking-hours-sequence.puml` | `services/booking.py`, `web/app.py` | `test_aztu_policy.py::test_closure_blocks_seats_in_whole_area_and_approval`, `test_aztu_web.py::test_admin_can_create_a_closure_with_csrf` |
| AZ-04 Safe schedule updates | FR-005, FR-009 | `16-aztu-booking-hours-sequence.puml` | `services/booking.py::update_space_hours` | `HoursUpdateTests::test_cannot_silently_invalidate_confirmed_booking` |
| AZ-05 Preserve history, remove starter gear | FR-002, FR-006, FR-009 | `15-aztu-space-extension.puml` | `storage/db.py`, `storage/aztu_demo.py`, `scripts/sync_aztu_demo.py` | `test_aztu_policy.py::test_legacy_booking_preserved_while_gear_archived`, `test_old_sqlite_schema_migrates_without_losing_reservations` |
| AZ-06 Show CLOSED alongside live colors | FR-003 | `15-aztu-space-extension.puml` | `domain/operating_hours.py`, `web/app.py`, `web/templates/studio.html`, `web/static/studio.js` | `test_aztu_policy.py::test_closed_now_status_is_distinct_from_booking`, `test_aztu_web.py::test_studio_api_can_report_closed` |

The exact numbered test cases and execution result should be recorded in the amended test report, not inferred from a passing unrelated workflow. Approval of the new look by the project owner remains pending.
