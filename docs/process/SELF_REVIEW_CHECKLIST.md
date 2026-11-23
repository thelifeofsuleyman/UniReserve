# UniReserve — Final Technical Self-Review Checklist

**Technical review:** 23 November 2026  
**Method:** comparison of assignment, current repository, GitHub CI and documented CR-001–CR-004. This is **not** a substitute for the owner's personal code review or a simulated usability study.

| ID | Requirement / question | Evidence and actual result |
|---|---|---|
| R01 | All Must requirements have implementation | **PASS by automated checks:** 11 Must requirements map to code and tests; relevant cases passed. |
| R02 | Unique FR/NFR IDs, MoSCoW, Must acceptance criteria | **PASS:** SRS FR-001–FR-018, NFR-001–NFR-008; Must acceptance table. |
| R03 | Comparison of at least two existing systems | **PASS:** official LibCal/Skedda pages compared; no hands-on evaluation claimed. |
| R04 | At least four full use cases | **PASS:** six with main/alternative flows and pre/postconditions. |
| R05 | UML, state, 3NF conceptual/logical ERD, classes, architecture and sequences | **PASS:** 16 editable PlantUML sources and 32 exports; later Spaces and Closures documented. |
| R06 | Current database and model consistency | **PASS with documented deviations:** six implemented tables (users, resources, reservations, reservation_events, spaces, space_closures); the original four-table baseline is no longer complete. |
| R07 | Concurrency and overlap | **PASS in CI:** 50 repeated paired race trials, status/approval tests, and cross-seat owner-conflict tests. |
| R08 | Security at demo scope | **PASS for tested routes:** roles, ownership, sessions, password hashes and CSRF. Full penetration test not performed. |
| R09 | Must traceability | **PASS:** automated traceability checker and matrix including CR-002–004 addenda. |
| R10 | Systematic tests + defect log | **PASS:** 36 individually specified representative test cases, plus larger automated suite; real defects and fixes recorded. |
| R11 | CI, coverage and performance | **PASS:** 123/123 automated tests, 94% statement coverage, 200/200 synthetic HTTP latency requests under one second; [CI 45110603568](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110603568). |
| R12 | Change analysis and feedback | **PASS:** owner comments and screenshot-driven CR-001–004 with implemented UI/database impact. |
| R13 | README and runnable local system | **PASS for documented commands and CI workflows; student's Windows demonstration remains unverified by this audit.** |
| R14 | Real Git branches and commit history | **PASS:** milestone pull requests #1–#11, squash merges and Actions logs. |
| R15 | Secrets, privacy, invented AzTU data | **PASS for checked demo source:** generated credentials and ignored SQLite; schedules, seats and pictures labeled illustrative. |
| R16 | Owner visual preference | **Positive owner response to handoff**, but no independently witnessed full current-browser walkthrough; do not call this a five-person study. |
| R17 | Volunteer usability target NFR-006 | **OPEN:** five volunteer participants/time measurement not performed. |
| R18 | Keyboard-only walkthrough NFR-007 | **OPEN:** no personally observed keyboard-only end-to-end run on the user's Windows machine. |
| R19 | Six submission PDFs | **PASS in GitHub PDF build/validation:** files exist and checks cover source requirements, diagram count and reflection page limit. |
| R20 | Reflection personally authored/approved | **OPEN:** AI-assisted draft must be reviewed, edited and approved by the student. |
| R21 | Instructor repository access | **OPEN:** private repo; instructor's GitHub identity/permission unknown. |
| R22 | KOICA upload | **NOT DONE:** no authorized KOICA session or verified submission receipt in this conversation. |

## Last user-controlled actions
- Review the latest catalogue, four sample maps, login/admin workflow and a mobile/keyboard view on the actual Windows machine; report anything that differs from CI tests.
- Rewrite/approve the individual reflection so it honestly describes personal understanding and AI contribution.
- Grant the lecturer access to the **private** GitHub repository (or follow a verified course-specific access instruction).
- Submit the URL in KOICA by **2 December 2026**, retaining a receipt or screenshot. Do not claim submitted until that evidence exists.


## CR-005 presentation and deployment update

Product-facing screens now use service-language rather than repeated student-project warnings. Account/space provisioning, a local Waitress launcher, and a production-mode WSGI/secret/host/HTTPS baseline were added; none of this implies a public service has been hosted. Security configuration and related tests are documented in `docs/deployment/OPERATIONS.md`. Existing independent AzTU disclaimers remain in the service-information page, official engineering reports and reflection, not repeated on every booking screen. Real world SSO, TLS termination and backup/recovery operations still need the hosting institution.


### CR-005 follow-up
- [x] Customer-facing pages no longer repeatedly show internal development scripts and fixture wording.
- [x] Managed WSGI baseline and startup safety checks added; actual deployed domain/HTTPS not established by coursework CI.
- [x] Admin may create a Space and provision real users through a trusted CLI.
- [ ] Public launch gate: university authorization, TLS proxy, login throttling, backups/recovery, privacy/accessibility review and real room data remain unverified.
