# UniReserve — Actual UI Feedback Log

Only direct owner comments and observed screenshots are recorded. This is not a student interview survey.

| ID | Date | Actual owner feedback/evidence | Change request | Engineering outcome |
|---|---|---|---|---|
| UX-001 | 2026-11-23 | First web interface felt generic and had no photos. | CR-001 | Reworked photo-led cards, colors and hierarchy. |
| UX-002 | 2026-11-23 | Asked for 2D/3D placement and green/red/yellow 15-minute availability. | CR-001 | 2D map, stored-booking status API, 15-minute threshold and tests. |
| UX-003 | 2026-11-23 | Requested AzTU-like computer labs, library PCs, separately bookable study seats and realistic opening rules. | CR-002 | Four demo areas, 23 units, weekly schedules and closures, safe migration. |
| UX-004 | 2026-11-23 | Two screenshots showed six obsolete starter resources with identical, mismatched photos and an empty seat map. Asked for distinct room images and logical seating. | CR-004 | Four original room-specific images, distinct layouts and automatic local catalogue sync. |
| UX-005 | 2026-11-23 | Responded "it is perfect do these steps" to the final pre-submission checklist. | Final handoff | Positive response to the plan; **not** evidence of an independently observed full Windows walkthrough or a measured usability study. |

## Current 2D room-plan design
- **Reading area:** eight individually bookable seats in two banks of four, access aisle.
- **Library PC area:** six independently bookable PCs in two banks of three.
- **Teaching lab:** eight workstations, teaching screen and aisle; administrator approval as a demo rule.
- **Group study:** one whole-room booking, decorative central six-chair table; chairs are not independently reservable.

Status colors reflect confirmed reservation records, not physical occupancy. Images, positions, operating hours and permissions are illustrative; the system does not claim to reproduce a surveyed AzTU site.

## Remaining user acceptance checks
Actual Windows screenshot of the **latest** CR-004 version, full student/admin booking walkthrough, mobile and keyboard-only exploration. NFR-006 five-volunteer results have not been collected. Document any subsequent feedback with date and concrete evidence.


| UX-006 | 2026-11-23 | Owner requested removal of repetitive AI-style reminders, demo instructions and disclaimers from the booking interface, and asked for a more production-facing service. | CR-005 | Main screens simplified; source caveats consolidated in Service information and engineering reports. Production-mode configuration and admin room setup added. Public hosting not claimed. |


| UX-007 | 2026-11-23 | Owner booked a room and noticed it did not display red for another person, and requested a date-selectable calendar under reservations to see availability. | CR-006 | Added half-hour future calendar to each booking page and seven-day personal agenda. Clarified present-moment status vs future reservations. |
