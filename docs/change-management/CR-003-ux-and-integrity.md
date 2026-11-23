# CR-003 — UX Refresh and Booking-Integrity Review
**Date:** 23 November 2026 · **Reason:** owner feedback after running UniReserve locally.

## User feedback (actual)
The user reported that the interface lacked personality and visual polish, and asked for a more realistic, logically coherent AzTU-inspired seat/PC booking experience. This change is a design iteration, not a claim of a real university usability study.

## Changes
1. Consistent forest-green/cream editorial design across navigation, resource catalogue, room map, booking page, administrator forms and login. Use locally bundled original illustrative imagery; do not depend on hot-linked, potentially broken third-party photographs.
2. Interactive map zone filters; select a seat to open the actual reservation form. The plan remains illustrative and not a verified surveyed floor plan.
3. Fix status refresh so **both badge color and text** follow the latest database-derived availability state, including CLOSED/DISABLED. A network error displays a warning rather than showing stale values as freshly checked.
4. Add a project-level **one simultaneous confirmed study-place per student** policy (only resources assigned to Spaces). Pending requests do not hold capacity; approval checks again. This is a proposed fair-use rule, **not** a verified AzTU policy.
5. Prevent administrator reclassification or relocation of a resource when it would invalidate an existing future confirmed booking's hour window, closure or session duration.
6. Clarify the difference between a green current-status badge and availability for a future time or for a student who already has another booking.

## Acceptance criteria
- AC-003-A: color and text both change when a resource's status changes; area tabs filter the diagram client-side.
- AC-003-B: same student cannot confirm two different PCs/seats for overlapping intervals. Different students may book different units in parallel. Adjacent intervals remain allowed.
- AC-003-C: a pending approval may overlap the student's confirmed booking, but admin approval is rejected and remains pending if the student is already booked.
- AC-003-D: moving a resource to a new area or shortening its permitted duration must not silently invalidate existing future confirmed reservations.
- AC-003-E: external image hosts are not required for the site to render.
- AC-003-F: all existing automated tests continue to pass; add regression cases for the new policies.

## Impact and traceability
- **Requirements:** extended FR-003/004/005/008/009 and NFR-003 through a **demo-only fair-use assumption**. Do not misrepresent policy as official AzTU practice.
- **Design:** BookingService checks owner overlap in addition to resource overlap, under the same BEGIN IMMEDIATE transaction. Current UML sequence diagram depicts the generic conflict check; this addendum specifies the new second check.
- **Modules:** `src/unireserve/services/booking.py`, `src/unireserve/web/static/studio.js`, all main UI templates and `refined.css`.
- **Tests:** `tests/test_cr003_fair_seats.py` and previous AzTU policy/web checks. The final test report should cite the actual CI run.
- **Database:** no destructive schema migration; original records and all audit event rows are preserved.

## Residual limitations / unverified decisions
- Color indicates **reservation records**, not physical occupancy; no sensors or campus integrations exist.
- Real university operating hours, seating eligibility, exact seat locations, break periods, holidays and class timetables remain unverified and are represented only as configurable assumptions.
- For real deployment, add production authentication/SSO, login rate limiting, backup/recovery testing, session/role review, and capacity/performance testing on target hardware.
- The individual reflection draft must be reviewed and written in the student's own words.
