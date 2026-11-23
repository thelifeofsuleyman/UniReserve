# UniReserve — Software Engineering Process Evidence

**Student:** Suleyman Shafizada (m666i1) · **Dated:** 23 November 2026

## Scope and development rhythm

Private repository: https://github.com/thelifeofsuleyman/UniReserve. The first setup was committed as separate source files; subsequent work took place in feature/documentation branches, checked using GitHub Actions and squash-merged into `main` to keep the final history concise. These are genuine Git operations, not a retrospective reconstruction of project activity.

| PR | Milestone | Actual work and evidence |
|---|---|---|
| #1 | Requirements | SRS, priority decisions, acceptance criteria, six textual use cases, comparison of LibCal and Skedda. |
| #2 | Models | UML use case/domain/state/design/architecture, conceptual and 3NF logical ERDs, six scenario sequences, validated exports. |
| #3 | Engine | SQLAlchemy models, SQLite transaction integrity, authorization, audit log and race tests. |
| #4 | Web UI | Flask login/logout, browse/book, cancellation, approval, admin resource management and HTTP tests. |
| #5 | Change CR-001 | Owner feedback, photo-driven UI, illustrative 2D Studio, 15-minute status rules and new tests. |
| #6 | QA | Test plan, 36 named cases, coverage, NFR performance measure, defect log. |
| #7 | Traceability | All 11 Must requirements linked to UCs, diagrams, code and tests; supplementary CR-001 sequence and design deviation review. |
| #8 | Final submission | Six PDF exports, reflection draft, self-review checklist, final verification (generated in final milestone). |

## Test infrastructure

- `python scripts/run_tests.py`: single-command unit/integration/HTTP suite.
- `python scripts/validate_models.py`: checks 14 PlantUML sources, requirement IDs, entities and state consistency.
- `python scripts/validate_traceability.py`: checks all 11 Must requirement links to real files/tests.
- `python scripts/measure_latency.py`: repeats NFR-001 synthetic 200-request performance probe.
- `.github/workflows/tests.yml`: installs dependencies on Python 3.11, runs validation, coverage and latency.
- `.github/workflows/render-diagrams.yml`: renders/validates source PlantUML into 14 PNGs and 14 SVGs.

## Actual CI evidence

- [M5.5 UI feature CI 45103587996](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45103587996): 85 tests passed, 94% statement coverage.
- [M6 QA performance CI 45103990514](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45103990514): 85 tests passed, 94% coverage; 200/200 requests under 1.0 second, measured p95 0.03152 seconds.
- [M7 consistency failure 45104488696](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45104488696): genuine traceability mismatch FR-010/TC-013 detected and corrected, entered in defect log. Corrected in the traceability branch; re-verified in [CI 45104594409](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45104594409), with [diagram check 45104594391](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45104594391) also passing.

## Code and design decisions

The project deliberately prioritizes a small tested core over payments, waitlists, actual equipment checkout or physical sensor monitoring. SQLite BEGIN IMMEDIATE and status transitions protect booking integrity. Original generated imagery and the illustrative 2D layout address real user feedback without asserting knowledge of physical university locations. The conceptual class diagram over-describes repositories relative to the smaller SQLAlchemy Session implementation; the deviation is explained in the traceability matrix.

## Review and limitations

`docs/process/SELF_REVIEW_CHECKLIST.md` records completed evidence checks and outstanding manual items. The owner still needs to review the redesigned UI. Five-person usability measurement and keyboard walkthrough are **not** claimed. This is a locally runnable coursework prototype, not a production service.
