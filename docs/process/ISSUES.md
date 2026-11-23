# UniReserve — Issue Board and Milestone Progress

**Date:** 23 November 2026 | **Project:** SWE individual coursework | **Submission target:** 2 December 2026

This is a concise retrospective record of actual work and remaining gaps. GitHub PRs and CI runs are source evidence. Tasks were not invented as evidence of earlier activity.

## Completed and supported by Git history

- [x] M1 — Initialize private repository, source layout, test runner and initial booking boundary tests.
- [x] M2 — Requirements baseline: SRS, 18 functional / 8 NFR, six use cases and LibCal/Skedda research — PR #1.
- [x] M3 — Domain, use case, ERD, state, design class, architecture and six sequence diagrams, plus exported images — PR #2.
- [x] M4 — SQLite/SQLAlchemy domain service; transaction-safe booking, approvals, permissions and audit; race tests — PR #3.
- [x] M5 — Flask web UI, login/logout, booking/catalogue/admin routes, CSRF and HTTP tests — PR #4.
- [x] M5.5 — Owner-driven UI redesign, resource artwork, 2D interactive map, 15-minute status semantics, acceptance tests — PR #5 / CR-001.
- [x] M6 — Formal test plan, 36 executed case references, coverage, defect log and NFR-001 latency probe — PR #6.
- [x] M7 — Traceability of all 11 Must requirements, documented code/design deviations, supplementary CR-001 sequence — PR #7; model and traceability CI passed.

## Remaining / intentionally open

- [ ] M8 — Export and verify required PDF deliverables, complete self-review checklist and reflection draft, confirm KOICA repository URL.
- [ ] Owner review of **revised UI** and any subsequent feedback (has not occurred yet).
- [ ] Optional NFR-006 5-volunteer usability study (not measured).
- [ ] Optional NFR-007 keyboard-only walkthrough (not measured).
- [ ] Should-scope physical checkout/return and quota limits (deferred by SRS).

## Working process

The original setup used multiple small file commits. Later milestones are developed on separate branches, checked by GitHub Actions, and **squash merged** into `main` as single meaningful milestones. No commit history was artificially backdated. Requirements, diagrams, source modules and tests are reconciled through code and document checks.

## Real user-requested change

The owner expressed dissatisfaction with the original visual UI and asked for 2D/3D placement and green/yellow/red availability. That feedback is preserved in `docs/ui/UI_FEEDBACK_LOG.md`. CR-001 records the impact, alternatives, and acceptance checks. The 2D UI is demonstrative and intentionally does not pretend to know real physical campus coordinates.
