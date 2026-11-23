# CR-004 — Contextual room catalogue, real floor-plan interactions and safe demo setup

**Date:** 23 November 2026 · **Origin:** Direct screenshot review and explicit product-owner feedback.

## Actual problem observed
The owner showed two screenshots: six outdated starter resources including a camera and projector all displayed the same inappropriate conference-room image, while the 2D map showed "No sample spaces yet". This was not a mere color preference. The running local database had not undergone the idempotent AzTU demo synchronization, and the visual structure still treated each seat as a separate large photo card.

## Corrective implementation
1. Create four **distinct original illustrations** (not claimed to be photographs of AzTU): library reading desks, library PCs, teaching computer lab, group study room. Photos are generated assets optimized as local JPEGs; no external image hotlink is required.
2. Replace repeated photo-per-unit cards with **four zone cards** showing the corresponding image, count of bookable units, sample hours and a link to its room map. Keep a compact searchable unit directory below so a user can still select any resource by ID.
3. Design a different clickable 2D room diagram for each area. Reading desks: eight seats in two banks of four with a central aisle; library PC area: six PCs in two banks of three; teaching lab: eight workstations facing a teaching screen with an aisle; group room: one reservable whole room represented by a single selectable booking control and a shared table with six decorative chairs. The six group chairs are **not** six independently bookable resources.
4. In the **local demo launcher only**, automatically synchronize sample areas if the database has none. The synchronization uses the existing idempotent and transaction-safe routine: known starter camera, projector, etc. become hidden/disabled, while existing reservation and audit records remain untouched. The auto-sync can be disabled with `UNIRESERVE_AUTO_SAMPLE_CATALOG=0` or by using the app factory without explicit opt-in.
5. A room-card link opens the 2D map focused on that area using the `area` query parameter; all other rooms remain visible if the user chooses "All rooms". The current-status API and server-side reservation checks remain authoritative and unchanged.

## Acceptance criteria and test technique
- **CR004-01 / web integration:** first demo launch with no Spaces creates four Spaces and 23 individually identified resources; does not create new user accounts.
- **CR004-02 / presentation contract:** four visually distinct local room image files appear on the catalogue; the individual units are displayed as compact links rather than 23 copies of one image.
- **CR004-03 / cardinality:** map lists eight reading seats, six library PCs, eight lab PCs and one group-room booking. All are selectable by ID. The group table has six chairs for context only.
- **CR004-04 / regression:** filtered catalogue still lists specific unit names and normal legacy resource tests continue to work.
- **CR004-05 / migration:** a second startup doesn't overwrite administrator edits; historic confirmed reservations remain attached to archived demo resources.
- **CR004-06 / test isolation:** test application factories remain empty by default and only seed with explicit opt-in.

## Architecture and change impact
Affected: `src/unireserve/web/app.py`, `scripts/run_web.py`, Jinja catalogue/map/detail templates, `studio.js`, `room-design.css` and four local JPEG assets. No database schema change. The resource-to-Space model and all core transaction rules are unchanged, so existing UML entity cardinalities remain valid. This is an interface and demo-initialization improvement recorded for the final reflection and process evidence.

**Ethical/source boundary:** The floor plans, seat numbers, images, booking eligibility, and opening rules are coursework simulations inspired by university spaces; they must not be presented as actual AzTU room survey results or as proof of an official student reservation service.
