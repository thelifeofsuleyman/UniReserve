# UniReserve — Final Technical Handoff Audit

**Audit date:** 23 November 2026 · **Source of truth:** merged `main` at `d8dad20a0ff65aa7f148382426001761d01e8d47` (CR-004), plus accompanying GitHub Actions results. No local Windows browser session or KOICA session was accessible to this audit.

## 1. Automated functional and technical checks
Latest [main CI run 45110603568](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110603568) completed successfully:

- **123 of 123 automated tests passed.**
- **94%** statement coverage across the tracked package (912 statements, 54 missed).
- Requirement/model validation and all 11 Must-requirement traces passed.
- NFR-001 synthetic test: **200/200** catalogue/availability requests under 1 second, measured **p95 = 0.02251 seconds**, on Python 3.11.18/Linux with 100 resources and 1,000 reservations.
- Tests cover booking conflicts, synchronized two-client races, approvals/rejections, cancellation, authentication/roles/CSRF, operating hours/closures, safe migration and CR-004 room-layout contracts.
- This is **not a claim** of multi-user load testing in a production AzTU deployment.

## 2. Final visual source/layout review
Source inspected in `src/unireserve/web/templates/resources.html`, `studio.html`, `partials/studio_seat.html` and `static/room-design.css`, with CR-004 integration tests:

| Example area | Expected logic | Verified source contract |
|---|---|---|
| Library reading area | 8 individually selectable seats in two banks | Corresponding template branch, 8 mapped units and unique study-area image |
| Library computer area | 6 individually selectable PCs | PC workstation symbols, access aisle, matching image |
| Teaching computer lab | 8 PCs with teaching screen and approval condition | Eight identifiers, classroom layout and admin approval logic |
| Group study room | ONE bookable whole room | Six decorative chairs, one room ID and one reservation link |

The four room-specific JPEG assets and Jinja image references exist in the committed repo. The old screenshot showing six miscellaneous items and no spaces was addressed by the idempotent local demo-area initialization. A screenshot of the **latest version on the owner's Windows PC** is not available to this audit, so pixel-perfect local rendering and user comfort cannot be independently certified.

## 3. PDF and structure review
`docs/submission/` contains exactly six assessed PDFs, source Markdown, 16 PlantUML sources and 32 rendered diagrams. [CR-004 PDF validation run 45110485448](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110485448) successfully generated/validated the six documents; the submission script checks non-empty pages, expected report terms, 16 design-model pages, and 1–2 reflection pages. **Human visual inspection of all pages is still recommended; CI PDF parsing is not equivalent to a typography/pagination review.**

## 4. Defect and change evidence
- **CR-001:** initial visual design/availability indicator.
- **CR-002:** library PCs, study seats, opening schedules, classroom closures.
- **CR-003:** fairness across simultaneous bookings, safe admin reclassification, badge color/label consistency.
- **CR-004:** mismatched repeated images and empty map fixed with four distinct room illustrations, logical seating and safe local initialization.
- Historical intermediate CI failures were corrected. The latest successful run is the accepted automated evidence, not a claim that all intermediate runs passed.

## 5. Outstanding human / external checks
- Run latest version on the owner's local Windows computer, including booking/cancel/admin and keyboard/mobile observations; this is not remotely verifiable here.
- NFR-006 five-volunteer usability experiment: **not measured**.
- NFR-007 full keyboard-only walkthrough: **not completed**.
- The reflection draft: **must be personally reviewed and approved**.
- Private GitHub access for the lecturer: **not verified**.
- Submission through KOICA: **not performed or confirmed**.

**Assessment:** Technical repository is complete for a coursework prototype. Its real-world AzTU assumptions and outstanding personal/external steps must remain explicit.


## Post-audit addendum — CR-005
This original audit recorded the tested CR-004 baseline. The owner's later request led to cleaner user-facing copy, a separate service-information screen, a managed Waitress/HTTPS deployment configuration and admin-configured Space creation. New QA evidence is in `docs/testing/CR-005_TEST_ADDENDUM.md` and the corresponding latest GitHub Actions result. No public website, real campus inventory or real-world usability study is asserted by these modifications.
