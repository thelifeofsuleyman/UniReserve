# CR-006 — Future calendar and personal schedule test addendum

| Test ID | Technique/level | Expected result |
|---|---|---|
| TC-CR006-01 | Boundary and overlap | 10:00–11:00 confirmed booking turns 10:00 and 10:30 half-hour tiles red for another user; adjacent 09:30 and 11:00 remain green. |
| TC-CR006-02 | State transition | Cancellation restores red to green for another user without deleting history. |
| TC-CR006-03 | Decision table | Pending approval does not block future capacity; administrator approval then turns those tiles red. |
| TC-CR006-04 | Integration | Whole-area class closure turns overlapping workstation slots gray; adjoining slots remain free. |
| TC-CR006-05 | Fairness/user state | Requesting user sees amber on another resource when they already have a confirmed overlapping study-space reservation; unrelated user sees green. |
| TC-CR006-06 | Equivalence/weekday | Closed weekends show closed tiles, even without any booking. |
| TC-CR006-07 | Time boundary | Past intervals are unavailable; future valid intervals on current day remain selectable. |
| TC-CR006-08 | Invalid partitions | Dates outside the 14-day horizon, malformed dates and hidden resources are rejected. |
| TC-CR006-09 | Privacy/read-only | Schedule response contains no other account email, user ID or reservation ID and emits no audit event. |
| TC-CR006-10 | HTTP authentication/caching | Anonymous client is redirected to login; authenticated response uses `Cache-Control: no-store`. |
| TC-CR006-11 | UI contract | Booking page includes the day/date picker and grid; green slot selection updates existing form start/end fields. |
| TC-CR006-12 | Owner-only agenda | My reservations shows next seven days of only own confirmed/pending bookings, linked to their detail page. |

**Automated source:** `tests/test_cr006_booking_calendar.py` alongside preexisting Flask/security/integrity tests. Record actual pass/fail and coverage from GitHub Actions when available.

**Regression principle:** the visual calendar is read-only; it does not reserve or hold a slot. Backend confirmation/approval is still the source of truth, including conflicts that arise between viewing the calendar and clicking Book. Status indicates confirmed *reservation records*, not sensor-detected physical occupancy.
