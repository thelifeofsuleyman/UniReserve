# CR-003 — Requirement-to-design-to-test traceability
| Reference | Design decision | Source | Automated evidence |
|---|---|---|---|
| BR-05 / FR-005 | Add atomic owner-level conflict recheck to the original resource-level overlap check | `src/unireserve/services/booking.py`: `_no_other_space_booking`, `request`, `available` | `tests/test_cr003_seat_integrity.py`, `tests/test_aztu_policy.py` |
| FR-008 | Approval rechecks a student's existing confirmed study-space bookings; leaves blocked request pending | `BookingService.decide` | TC-CR003-04 |
| FR-009 | Reassignment or category change cannot invalidate future confirmed reservations | `BookingService.update_resource` | TC-CR003-05/06 |
| FR-003 / CR-001 | Live-status text AND badge class updated together | `static/studio.js`, `static/refined.css`, `templates/studio.html` | Existing Flask status tests and manual UI review |
| Owner satisfaction | Consistent component design, filterable 2D map and locally bundled illustrative images | Main Jinja templates and CSS | TC-CR003-07/08 (manual review remains open) |

The 2D map is an illustrative clickable layout; it is not a verified map of an actual AzTU floor or evidence of sensor-based occupancy.
