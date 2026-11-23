# Completed Self-Review Checklist — UniReserve

**Review date:** 23 November 2026. **Method:** examination of actual repo source/diagrams and GitHub Actions evidence, not a fabricated peer review.

| Item | Check | Result / evidence |
|---|---|---|
| R1 | Scope manageable, all Musts implemented | PASS: FR-001..011 code and matrix, 85 passing tests; optional features labeled deferred. |
| R2 | Functional IDs unique, MoSCoW and Must acceptance criteria | PASS: SRS lists FR-001..018, NFR-001..008 and 11 high-priority criteria. |
| R3 | Existing-system comparison | PASS: LibCal and Skedda official documentation compared, sources recorded; no hands-on testing claimed. |
| R4 | Use cases include alternatives/pre/postconditions | PASS: UC-01..06 described and represented by six sequence diagrams. |
| R5 | Domain/ERD/class/state/architecture models | PASS: 14 PlantUML sources and PNG+SVG exports; model-validation CI checks syntax and structural consistency. |
| R6 | 3NF explanation and implementation relation | PASS: four entities, primary/foreign keys and normalized history; deviation notes in matrix. |
| R7 | Booking overlap and concurrency protection | PASS: `BEGIN IMMEDIATE`, 50 competing pairs and two-client approval conflict test. |
| R8 | Role, owner, login, CSRF, HTML escaping | PASS for tested routes; full security penetration testing NOT performed. |
| R9 | Traceability every Must to UC, design, code and case | PASS: automated traceability checker and matrix. |
| R10 | Tests derived systematically | PASS: equivalence classes, boundaries, decision table and state/use case testing; 36 representative cases. |
| R11 | Code coverage and performance measured | PASS: 85 tests / 94% statement coverage; 200/200 latency requests within 1s, p95 0.03152s on documented runner. |
| R12 | Real user change / impact analysis | PASS: CR-001 with observed feedback, 2D status rules, code, tests and diagram impact. |
| R13 | README Windows/macOS setup and test commands | PASS: venv, pip, seed, run_web, run_tests, validate_models, perf probe. |
| R14 | Repository branches, commits and CI | PASS: PR #1..#7 and GitHub Actions; milestones squash-merged to reduce commits. |
| R15 | Avoid secrets and invented real data | PASS: generated passwords are shown once, ignored database, synthetic `.test` accounts, illustrative locations clearly labeled. |
| R16 | Owner acceptance and volunteer study | OPEN: revised UI not yet approved by owner; NFR-006 and NFR-007 manual checks not completed. |
| R17 | Local production readiness | NOT CLAIMED: no public TLS, rate limiting, recovery, deployed load testing or sensors. |

## Action for final submission

Follow the owner-run UI walkthrough; confirm display on their Windows computer; provide any real feedback; read and personally approve the 1–2-page reflection. Changes must be documented as new, not backdated.
