# Milestone 5.5 — Visual Availability Studio

## How to try it
Run `python scripts/seed_demo.py`, then `python scripts/run_web.py`, sign in and open **Availability studio** in the sidebar. Each pin is a room or equipment item. Click a pin to open a booking page. The resource catalogue now uses an original photographic illustration atlas. Status changes are refreshed by a read-only API approximately every 30 seconds.

## Semantics (VS-01 to VS-04)
- **AVAILABLE / green:** enabled; no current confirmed booking; next starts more than 15 min away or none exists.
- **SOON / yellow:** enabled; none currently active; next confirmed booking starts within 15 min (exactly 15 included).
- **OCCUPIED / red:** enabled; confirmed booking is active when `start <= now < end`.
- **DISABLED / grey:** resource disabled; overrides other indicators.

Confirmed intervals are half-open. Pending requests are excluded. The status indicator is not a sensor and is not a reservation guarantee: a booking may arrive immediately after the status check. The service retains the atomic booking conflict check.

## Design decisions
1. Keep layouts as illustrative zones rather than inventing real campus coordinates. Section A is for rooms, section B for equipment. Resource pin positions are stable by ID/order and do not reflect actual campus locations.
2. Prefer 2D clarity and accessible labels over a complicated 3D renderer.
3. Make original photos central to the catalogue and login without depending on external photo URLs. The resource illustration atlas is committed as an offline asset.
4. Match state words with colors; no status relies on color alone.
5. Refresh every 30 seconds (not WebSockets) and show the last checked time. This is near-live reservation status, **not** occupancy monitoring.

## Screenshots and human review
Screenshots used in final documentation must come from the actual running app or an explicitly labeled template preview. No real user satisfaction rating has been collected for this updated UI yet. Follow-up owner feedback should be appended to `UI_FEEDBACK_LOG.md`.

## Tests
- Pure boundary and precedence tests (`test_live_status.py`).
- SQLite integration tests (`test_status_integration.py`).
- Flask HTTP, authentication, no-cache, no-private-fields and page-link tests (`test_visual_web.py`).
- Existing transactional booking/role/CSRF tests must remain passing in CI.
