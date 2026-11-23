# UniReserve — Assessed Deliverables

**Student:** Suleyman Shafizada · **Group:** m666i1  
**Deadline:** 2 December 2026 · **Submission method:** GitHub repository URL through KOICA.

| PDF | What it contains |
|---|---|
| `01_Requirements_Specification.pdf` | A: SRS, priorities, acceptance criteria, six textual use cases, LibCal/Skedda comparison and documented requirement changes. |
| `02_Analysis_Design_Models.pdf` | B: 16 exported diagram models, captions and architecture/design rationale (editable PlantUML sources elsewhere in `docs/diagrams/source/`). |
| `03_Test_Plan_and_Report.pdf` | C: plan, 36 named representative cases, coverage/CI results, real defect and CR testing addenda. |
| `04_Traceability_Matrix.pdf` | D: all 11 Must requirements traced to use cases, designs, code and tests, plus CR-002/003/004 addenda. |
| `05_Process_Evidence.pdf` | F: Git milestones, CI/issue log, self-checklist and change impact records. |
| `06_Individual_Reflection_DRAFT.pdf` | G: 1–2-page reflection draft with AI-use disclosure; **requires the student's own reading and approval**. |

E (the implementation) is the working `src/` code and `tests/` suite, not a standalone PDF.

**CI evidence:** [Latest main suite: 123 tests, 94% coverage](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110603568); [CR-004 source-PDF validation](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110485448).

**The demo is not official AzTU booking infrastructure.** Room labels, seat counts, images, classroom access, opening hours and physical position layouts are illustrative. The software infers status from stored confirmed bookings, not live sensor measurements.

The repository is **private**. A lecturer cannot view it without authorized GitHub access. See [KOICA_HANDOFF.md](KOICA_HANDOFF.md) before submitting and keep a KOICA submission receipt. Neither GitHub CI nor this document constitutes a KOICA upload confirmation.


## CR-005 — Final presentation and hosting notes
The website's public-facing screens now prioritize booking actions rather than repeating coursework/setup notes. A dedicated Service information page retains honest source and occupancy limitations. Production-mode WSGI/security configuration and administrator-managed area/account setup are documented in `docs/deployment/OPERATIONS.md` and CR-005. No live hosted URL or institution-approved access has been asserted. All assessed PDFs are rebuilt and checked by the GitHub export workflow.


## CR-006: calendar clarification
The per-resource booking page now includes a date-dependent calendar; My reservations has a personal seven-day agenda. The new functionality, privacy rules, tests, and change impact are reflected in the Requirements, Testing, Traceability and Process PDF source material. The reflection remains a student-review draft, and university submission remains a separate action.
