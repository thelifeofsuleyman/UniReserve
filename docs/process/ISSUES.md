# UniReserve — Project Board (Final Handoff)

**Project:** Software Engineering individual assignment · **Deadline:** 2 December 2026  
Completed items reflect actual merged PRs, not invented task-board activity.

## Engineering milestones completed
- [x] M1 — Initialize repository and starter tests.
- [x] M2 — Requirements baseline, six use cases and product comparison — PR #1.
- [x] M3 — UML, conceptual/logical ERD and architecture diagrams — PR #2.
- [x] M4 — Transactional SQLite/SQLAlchemy booking engine — PR #3.
- [x] M5 — Flask authentication, catalogue, bookings, approvals and admin UI — PR #4.
- [x] M5.5 — First visual Studio/map iteration — PR #5, CR-001.
- [x] M6 — Formal testing techniques, 36 identified cases, coverage/latency and defect evidence — PR #6.
- [x] M7 — Traceability of all 11 Must requirements and documented design deviations — PR #7.
- [x] M8 — Submission PDFs, process record, reflection draft and validation — PR #8.
- [x] CR-002 — AzTU-inspired library seats, lab PCs, schedules and area closures — PR #9.
- [x] CR-003 — Cohesive UI, simultaneous-seat fairness and safer admin edits — PR #10.
- [x] CR-004 — Correct room-specific images, four logical maps, automatic local sample setup — PR #11.
- [x] Final technical audit — latest CI confirms 123 tests/94% coverage; reference `docs/testing/FINAL_HANDOFF_AUDIT.md`.

## Honest outstanding tasks
- [ ] Owner runs and personally evaluates current build on Windows (including keyboard/mobile behavior).
- [ ] Owner reviews, edits and approves `docs/reflection/REFLECTION_DRAFT.md`.
- [ ] Instructor access granted to the private GitHub repository.
- [ ] Owner submits GitHub link through KOICA and retains submission confirmation.

## Deferred / not represented as completed
- [ ] NFR-006 five-volunteer usability study (not measured).
- [ ] NFR-007 manual keyboard-only walkthrough (not completed).
- [ ] Real AzTU room IDs, physical layouts, holiday schedule and official booking rights (not verified).
- [ ] Payment, equipment returns, priority scheduling, campus SSO and production hardening (outside assessed v1 scope).

Repository: https://github.com/thelifeofsuleyman/UniReserve


## CR-005 — Production-oriented presentation
- [x] Replace repetitive student-project UI language with actionable customer copy.
- [x] Provide `/about` for truthful source/occupancy limitations.
- [x] Add Waitress, secure production-mode settings, account creation and admin area creation.
- [ ] Real domain + HTTPS reverse proxy, institutional room/identity approval, rate limiting and backup restore drill remain separate deployment tasks.


## CR-006 — Date-specific reservations
- [x] Confirm future occupied intervals are shown red to all signed-in visitors without exposing reservation owner data.
- [x] Provide a date picker and clickable green intervals under the reservation form, with an atomic booking recheck.
- [x] Show the signed-in user's confirmed/pending future bookings in the My reservations seven-day agenda.
- [x] Add regression tests and formal traceability addenda.
- [ ] Owner-led browser usability/keyboard review remains to be performed on their Windows machine.
