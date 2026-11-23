# Change Request CR-001 — Visual Availability Studio

**Requested by:** project owner, 23 November 2026 (direct conversation)  
**Status:** accepted for implementation; final UI acceptance by owner pending  
**Baseline affected:** M5 Flask UI, SRS FR-002/FR-003, NFR-006 usability goal.

## Problem and evidence
The original interface was logically correct but lacked images and a distinctive, useful spatial presentation. The owner explicitly proposed a 2D/3D layout where the location of equipment/rooms could be inspected and statuses communicated as green (available), red (occupied), and yellow (reservation in the next 15 minutes).

## Options evaluated
1. **Do nothing:** cheapest but does not address feedback.
2. **Full 3D digital twin:** attractive but needs verified floor geometry and a renderer, and adds unnecessary risk to the individual assignment.
3. **Illustrative 2D map + photo catalogue:** chosen; supplies spatial interaction and meaningful status rules without pretending to have sensor-based occupancy or surveyed coordinates.

## Decision and implementation
- Add clickable `/studio` grouped into demo Study Wing and Equipment Bay, with stable illustrative positions (not physical coordinates).
- Add original resource imagery, improved catalogue, login and resource-detail visual styles.
- Use **confirmed** bookings only, with priority Disabled > Occupied > Soon > Available.
- SOON applies if the next confirmed booking begins in **(0,15] minutes**; OCCUPIED applies on `[start,end)`.
- Refresh a read-only authenticated API (`/api/availability-status`) every 30 seconds; do not disclose booking owners.
- Maintain accessible textual statuses next to color, including keyboard-focusable resource links.
- Keep all existing booking routes, CSRF and transactional conflict enforcement unchanged.

## Impact analysis
| Area | Changes | Verification |
|---|---|---|
| Requirements | FR-002/003 have clearer presentation; booking rule BR-05/06 unchanged. New supplementary indicator rules (VS-01..VS-04). | Verify all statuses and boundary at exactly 15 min. |
| Domain code | `domain/live_status.py` pure snapshot rules | Unit boundary tests |
| Service | `BookingService.status_overview()` filters CONFIRMED and excludes private user data | SQLite integration tests |
| HTTP | Authenticated read-only `/studio` and `/api/availability-status`, updated catalogue/detail | Flask integration tests |
| UI | Photo atlas, map with positions, 30-second polling, mobile layout | Static render + human UI review still pending |
| Data model / ERD | **No schema changes**. Positions are illustrative and derived at view time. | ERD remains consistent; explicitly document limitation |
| Sequence/architecture | Added read-only visual availability flow; no change to reservation commit flow | Architecture addendum + coverage checks |
| Risk | Status can be up to 30 seconds stale; demo map may be mistaken for real location | Visible non-scale/sensor disclaimers; recheck at booking commit |

## Acceptance criteria
- Authenticated users can open the 2D map; anonymous users are redirected to login.
- Each displayed resource links to its booking/detail page.
- An active CONFIRMED interval is red; the next CONFIRMED booking beginning within 15 minutes is yellow, otherwise green; disabled overrides all.
- Pending approval requests do **not** reserve capacity and do not affect indicator state.
- API reveals no owner emails and is marked no-store.
- All previous booking/authentication tests still pass.

## Evidence
The real owner comments are logged in `docs/ui/UI_FEEDBACK_LOG.md`. Automated test cases are in `tests/test_live_status.py`, `tests/test_status_integration.py` and `tests/test_visual_web.py`. CI results are linked from the eventual pull request. **No follow-up acceptance from the owner is recorded until actually supplied.**
