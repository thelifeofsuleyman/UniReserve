# ADR-0003 — Individual Seat/PC Reservations and Operational Calendar

**Status:** Implemented, verified tests pending; **date:** 2026-11-23.

**Decision:** Treat each student seat, library PC and lab workstation as a Resource with an optional `space_id` pointing to a Space. Booking the PC never books the whole room. Grouped Space stores site name, kind, local opening time, closing time, enabled flag, and a **seven-bit weekday mask**. SpaceClosure records periods reserved for lectures or maintenance. All booking-time checks use `Asia/Baku` and UTC storage; the final transactional booking/approval decision also rechecks every space policy. Old resources without a space retain backward-compatible rules until mapped.

**Transactional integrity:** `BEGIN IMMEDIATE` before reading closures and overlapping confirmed bookings; rejection writes no reservation or audit event. Admin closure creation rejects overlaps with confirmed bookings. Admin schedule change rejects any future confirmed booking made invalid by the change. Old camera/microphone/projector fixtures become unlisted and disabled through explicit idempotent demo sync; historical FKs remain.

**3NF:** Space depends on Space PK, Resource depends on Resource PK with one optional Space FK, SpaceClosure depends on SpaceClosure PK and Space FK. The weekday mask is a scalar integer 1..127, not a repeating text field. No resource name appears in reservations; no actor name appears in events. Demo display positions are not stored as official campus coordinates.

**Risk:** Referenced public working hours apply to specific administrative/library pages, not verified bookable computer lab schedules. Thus seeded hours, approval and weekdays are labeled assumptions and editable by administrators. No integration with official AzTU reservation systems or actual physical room inventory.
