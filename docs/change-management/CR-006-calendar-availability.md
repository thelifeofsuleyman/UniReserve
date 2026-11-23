# CR-006 — Date-specific reservation calendar

**Date:** 23 November 2026  
**Source:** Direct owner testing feedback: after reserving a room, the map stayed green for other people, so they could not understand whether a future time was already booked. The owner requested a calendar under reservations.

## Root cause and clarified behavior

Previously the green/red/yellow/gray floor-map indicators described only **the instant at which the page was checked**. They did not represent availability for a user-selected future date. A room booked tomorrow must still be green today if it is free at the present moment; turning it red all day would falsely suggest current occupancy. That distinction was not clear in the original booking workflow.

## Change accepted

- Show an interactive **day-by-day calendar in every resource's reservation panel**. Render half-hour intervals within each Space's configured operating hours (00:00–24:00 for legacy resources without a Space).
- Green = free for the displayed half-hour. Red = overlaps a **confirmed** reservation, regardless of which student reserved it. Gray = the space is closed, disabled, outside the booking horizon or the interval has passed. Amber = requesting student has a different overlapping **confirmed** study-space booking. Status uses text as well as color.
- Clicking a green interval fills the start/end form values (one hour if the following half-hour is also free, otherwise thirty minutes). The user may edit the times. The existing availability-check and booking/approval path remain authoritative and recheck in the SQLite immediate write transaction.
- Pending approvals are **not** shown as reserved because pending requests do not hold capacity; they only become red after actual confirmation.
- Add **Your next 7 days** to My reservations. It shows only the signed-in person's confirmed and pending future bookings; cancelled/rejected requests remain in history, not the weekly agenda.
- Fetch the date-specific snapshot via an authenticated same-origin GET endpoint with no-store caching. Return no other users' names, reservation IDs or emails; never expose the entire personal calendar of other accounts.

## Impact

FR-003 read-only availability reporting and FR-006 owner visibility; UC-02, UC-03 and UC-04. Architecture unchanged: BookingService query + Flask JSON route + Jinja and vanilla JS. Six database entities, their 3NF relationships, reservation states, transaction isolation, admin closures and 14-day booking horizon are unchanged.

**Source:** `src/unireserve/services/booking.py` (`calendar_day`); `src/unireserve/web/app.py` (`resource_calendar`, `my_reservations`); `src/unireserve/web/static/booking-calendar.js`, `booking-calendar.css`; Jinja templates for resource detail and reservations.

**Testing:** `tests/test_cr006_booking_calendar.py`; cases include reserved/adjacent slots, cross-user visibility, pending-to-confirmed approvals, cancellations, class closures, weekends, past/horizon limits, user-specific conflicts, no identity leaks, and UI integration. Check real GitHub CI for measurements, rather than inventing test execution.

**Usability limit:** no visual or keyboard study has been independently observed on the owner's Windows machine. Booking availability remains derived from reservation records, **not sensors or actual physical occupancy**. User-facing copy is action-oriented; technical limitations remain accessible in Service information and the course documentation.
