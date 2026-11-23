# UniReserve — Software Engineering Process Evidence

**Student:** Suleyman Shafizada (m666i1) · **Date:** 23 November 2026  
**Repo:** https://github.com/thelifeofsuleyman/UniReserve (private)

## Genuine version-control history
Work began with starter-file commits, then continued through feature/document branches and squash-merged pull requests to keep final history compact. Commit history and workflow logs are real, not reconstructed.

| PR | Work |
|---|---|
| #1 | SRS, MoSCoW, six use cases and LibCal/Skedda study. |
| #2 | UML, design/ERD, state machine, six sequences and architecture. |
| #3 | Transaction-safe SQLite domain/service, audit records and race tests. |
| #4 | Flask login/session, booking views, administration and HTTP tests. |
| #5 | CR-001: visual map, availability states and original imagery. |
| #6 | Systematic test plan/report, coverage, performance and defect log. |
| #7 | Complete Must traceability and design/implementation discrepancy review. |
| #8 | Six PDF exports, reflection draft and final-review documents. |
| #9 | CR-002: AzTU-inspired seats/PCs, hours and classroom closures. |
| #10 | CR-003: visual refinement, per-user booking rule, safe admin edits. |
| #11 | CR-004: matching room imagery, meaningful seat layouts, automatic sample sync. |

## Test and quality evidence
- `python scripts/run_tests.py` — one-command unit, integration and Flask route suite.
- `scripts/validate_models.py` and `scripts/validate_traceability.py` — diagram/requirement consistency.
- `scripts/measure_latency.py` — NFR-001 CI performance fixture.
- `.github/workflows/tests.yml`, `render-diagrams.yml` and `build-submission.yml` — CI and diagram/PDF exports.
- [Latest main CI, 45110603568](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110603568): **123 tests passed**, 94% statement coverage, 200/200 performance requests under 1 second, p95 0.02251s on a documented Linux runner.
- [CR-004 PDF verification, 45110485448](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110485448): six documents generated and validated from sources.
- Genuine failing intermediate test runs were investigated and corrected before merge; final CI results are the latest verification, not an edited historical narrative.

## Changes and differences from initial design
Original requirement scope featured equipment borrowing; the user later prioritized study seats/PCs and an illustrative room map. New `Space` and `SpaceClosure` tables and schedules extend the original four-table domain to **six tables**. The conceptual repository/service design is more elaborate than the actual SQLAlchemy Session implementation. The implementation preserved transaction rules, normalized relational data and a consistent booking lifecycle; deviations are explained in SRS/traceability/change records.

## Explicit exclusions and pending human checks
The current project uses synthetic accounts, generated illustration assets and demo seat counts/hours. It does not prove any actual AzTU student has official reservation rights for a given space. Owner-on-Windows visual, keyboard and multi-person usability checks are not reported as automated outcomes. The reflection remains an AI-assisted draft until student approval, and KOICA upload/instructor access is a separate action.

See `docs/process/SELF_REVIEW_CHECKLIST.md` and `docs/testing/FINAL_HANDOFF_AUDIT.md`.
