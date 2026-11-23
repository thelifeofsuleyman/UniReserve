# User Feedback Log — UniReserve

Feedback source: direct comments by the project owner in the ChatGPT development discussion. No fabricated interviews, survey scores, or usability sessions are included.

| ID | Date | Observation / request | Change request | Status | Verification |
|---|---|---|---|---|---|
| UX-001 | 2026-11-23 | The interface was logically sound but visually unsatisfying; it lacked imagery and felt too generic. | CR-001 | Implemented in M5.5; owner acceptance pending | Photo-based cards and login area, stronger visual identity; offline screenshot review |
| UX-002 | 2026-11-23 | Show equipment/rooms as positions on a 2D/3D layout and distinguish green available, red occupied and yellow if a booking begins within 15 minutes. | CR-001 | Implemented in M5.5; owner acceptance pending | Interactive 2D map, API snapshots, boundary-value tests including exactly 15 minutes |

## What we did not claim
- No owner feedback has yet been collected on the **revised** version.
- The map positions are illustrative demonstration coordinates; they are not a campus floor survey or live occupancy measurements.
- The images are original generated artwork, not photography of the user's university.
- Current availability is calculated from **confirmed reservations in SQLite**, refreshed in the Studio every 30 seconds, and never treated as a final booking lock.

## Follow-up for the actual owner
Try the Studio, resource catalogue and mobile layout. Record whether labels and colors are clear and whether the plan should use real room/floor labels. Any accepted changes should have an updated CR, tests and screenshots.
