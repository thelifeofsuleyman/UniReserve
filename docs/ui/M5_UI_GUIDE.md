# Milestone 5 — Web UI implementation and review guide

**Milestone:** 5 of 8 · **Date:** 23 November 2026 · **Role:** presentation layer for the existing booking engine.

## Implemented views and source trace

| URL | Actor | UI responsibility | SRS / use cases | Code template |
|---|---|---|---|---|
| `/login` | All, signed out | Sign in using pre-created account | FR-001, UC-01 | `login.html` |
| `/resources` | Authenticated | Search/filter catalogue and see flags | FR-002, UC-02 | `resources.html` |
| `/resources/<id>` | Authenticated | Inspect resource, choose interval, check availability | FR-003, FR-004, UC-02/03 | `resource_detail.html` |
| `/my-reservations` | Authenticated | View own reservations, cancel before start | FR-006/007, UC-04 | `my_reservations.html` |
| `/reservations/<id>` | Owner | See booking detail and audit history | FR-006/010/011, UC-04 | `reservation_detail.html` |
| `/admin` | Admin only | Pending approvals, resource inventory/edits | FR-008/009/010, UC-05/06 | `admin.html` |

The HTML is rendered server-side using Flask/Jinja; CSS is responsive and does not require a frontend build step or JavaScript framework. The site distinguishes a *request awaiting approval* from a *confirmed reservation*, matching the state diagram. Availability checks are read-only and do not hold capacity. Final booking/approval rechecks the database.

## UI and security design decisions

1. **Signed sessions:** user ID comes from a server-signed session cookie; current role/active status is reloaded from the database on each request. No posted user ID is trusted.
2. **Form CSRF:** every POST requires a session-specific cryptographic token, including login, logout, booking and admin changes. Forms without valid tokens are rejected with HTTP 400.
3. **Least privilege:** administrators manage inventory/approval but cannot create a student booking; ordinary users cannot access admin views. Users cannot read or cancel other users' booking details.
4. **Time semantics:** HTML `datetime-local` is interpreted in the explicitly displayed `Asia/Baku` timezone. UTC-aware intervals are passed to the service, which checks future start, 14-day horizon, and room/equipment duration.
5. **Failure UX:** booking conflicts and policy failures use understandable flash messages; inactive/invalid users must sign in again; access-denied errors show 403 without mutating data.
6. **Audits:** reservation detail shows status transitions that the service saved atomically; the UI never writes events itself.
7. **Local-only:** development server binds `127.0.0.1`, with HTTPS/cookie-secure mode reserved for a production reverse proxy.

## Manual exploratory walkthrough (to be completed by the student)

1. Follow the Windows or macOS/Linux startup instructions in the root README. Save generated passwords privately.
2. On a desktop browser (recommended minimum 1280px), sign in as student. Check page readability, card layout, resource category filters, room/equipment descriptions and time inputs.
3. Book an unrestricted study room for a future 60-minute interval. Verify green confirmation, own-reservations row, booking details and audit history.
4. Attempt the same interval for the same room as staff. Verify that the second request is refused. Check an immediately adjacent slot: it should be allowed.
5. As student, reserve a camera requiring approval. Verify a **pending** status and correct explanatory text. Sign in as admin and approve it; if another confirmation was placed meanwhile, approval should fail with the request still pending.
6. As admin, create a new resource and disable a resource. Verify that the catalogue keeps history while disabling stops new bookings.
7. Test mobile and tablet layouts, keyboard-only navigation, errors for invalid intervals and blank login form, and log real observations.
8. Run automated tests; if anything fails, log issue ID, reproduction steps, expected/actual result, severity, and fix commit.

## Known limitations / items for the next milestone

- This is a local demo; account creation, password reset and actual university SSO are excluded by current SRS.
- The design uses programmatically rendered room/equipment symbols rather than real uploaded item photos; this is a deliberate small-project simplification.
- Date/time validation is server-side; the form does not implement live client-side conflict polling.
- Formal accessibility/usability evaluation with volunteers, performance benchmarks, a complete defect log, and cross-artifact traceability remain part of later milestones.
- CSS attempts an optional Google Fonts request, with local Arial fallback. No image assets or remote scripts are needed.

## Documentation and review protocol

The user should provide feedback in conversation or screenshots. Record only **actual** feedback in `UI_FEEDBACK_LOG.md` with date, screen, observation, action and affected requirement/design/test IDs. If feedback changes agreed behavior, create a change request and update both requirements and UML sources before claiming consistency. Do not invent stakeholder sign-off or test outcomes.
