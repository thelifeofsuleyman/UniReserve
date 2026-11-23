# CR-006 — Date-specific calendar traceability

| Requirement / use case | Design and implementation | Evidence |
|---|---|---|
| FR-003, UC-02: time-specific availability | `BookingService.calendar_day`: SQLAlchemy confirmed rows + SpaceClosure + open weekdays + Baku date boundaries; `resource_calendar`: authenticated read-only JSON | TC-CR006-01, 04, 06–10 |
| FR-004/005, UC-03: request still checks conflicts | `booking-calendar.js` fills existing start/end, does not confirm a booking; `BookingService.request` retains write-transaction revalidation | TC-CR006-01–03, 11 + existing concurrency tests |
| FR-006/007, UC-04: own bookings and cancellation | `my_reservations` builds a seven-day personal agenda; cancelled entries omitted from agenda, included in full history | TC-CR006-02, 12 + existing owner/cancel tests |
| FR-008: pending approval semantics | Pending is omitted from blocked resource slots until the admin confirms it | TC-CR006-03 |
| NFR-003/007: privacy and accessible status | Response contains no user details; colored tiles also have text labels and disabled/focus states | TC-CR006-09–11; manual keyboard walkthrough still pending |

Design model: no new table or entity required, so existing normalized ERD is unchanged. The new read-only flow extends the availability sequence: UI → authenticated Flask API → BookingService → reservation/closure queries → anonymized half-hour status tiles. Booking write paths continue to revalidate atomically. The date-dependent calendar is distinct from the map's current-moment green/red/yellow indicators.
