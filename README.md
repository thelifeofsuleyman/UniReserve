# UniReserve

**AzTU-inspired University Study-Space Reservation System**  
**Student:** Suleyman Shafizada · **Group:** m666i1  
**Software Engineering individual project · Deadline: 2 December 2026**

**Status:** Working local coursework prototype. All eight planned development milestones are merged. The current demonstration has four illustrative study areas, an interactive 2D seat map, a transactional booking engine, automated tests and six assessed PDF documents. See [Final Readiness Audit](docs/testing/FINAL_HANDOFF_AUDIT.md).

## What can be reserved?

- **Library reading area:** eight individually identified study desks.
- **Library computer area:** six individually identified desktop PCs.
- **Teaching computer lab:** eight individually identified PCs; approval required for demo bookings.
- **Group study room:** one bookable room; six chairs on the diagram are decorative, not six separate bookings.

Photos and floor plans are original **illustrations**, not authenticated photographs or surveyed layouts of AzTU rooms. Opening times, exact seat counts, lab access and the one-overlapping-study-place-per-user restriction are **coursework demonstration policies**, not official AzTU commitments.

A green badge means free according to confirmed reservations **at the current status-check time**. Yellow means an accepted booking begins within 15 minutes; red means a confirmed booking is active; gray marks disabled inventory. Closed-hours status is also indicated separately. This is **not** physical occupancy sensing. Booking/approval always rechecks current data transactionally.

## Quick start for an existing Windows clone

Open VS Code's PowerShell terminal:

\`\`\`powershell
cd C:\Users\Agach\UniReserve
git pull origin main
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/run_web.py
\`\`\`

Open **http://127.0.0.1:5000**. Keep the terminal open; use **Ctrl+C** to stop the server.

The local launcher performs a one-time, idempotent demonstration-area sync when there are no Space records. Existing accounts, bookings and audit history are preserved, and six named obsolete starter items are archived instead of deleted. The default database is \`instance/unireserve.sqlite3\`; **back it up before any manual migrations**. If you intentionally maintain your own custom catalogue, set \`UNIRESERVE_AUTO_SAMPLE_CATALOG=0\` before starting.

## First-time Windows setup

Install **Python 3.11+** with its virtual-environment and pip support. If \`py\` is missing or \`python\` resolves to MSYS2, use the explicit standard Windows Python executable instead of MSYS2.

\`\`\`powershell
git clone https://github.com/thelifeofsuleyman/UniReserve.git
cd UniReserve
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/seed_demo.py
.\.venv\Scripts\python.exe scripts/run_web.py
\`\`\`

Save the three randomized passwords printed by \`seed_demo.py\`. Accounts are \`student@unireserve.test\`, \`staff@unireserve.test\` and \`admin@unireserve.test\`. **Do not publish passwords, databases or .env secrets.** Running \`seed_demo.py\` against an already initialized demo does not reset existing passwords. See \`scripts/sync_aztu_demo.py\` for manual AzTU-style catalogue synchronization.

**macOS/Linux:** use \`python3 -m venv .venv\`, \`source .venv/bin/activate\`, then \`python -m pip install -r requirements-dev.txt\`, \`python scripts/seed_demo.py\` (first time only), \`python scripts/run_web.py\`.

## Manual workflow to review

1. Sign in as a student. Browse the **four zone cards** and open a chosen room's **2D seat map**.
2. Reserve one library desk/PC during its configured future opening hours. Verify the confirmation and **My Reservations** view.
3. Try an overlapping second seat for the same student and a booking during closed hours; both should be rejected without creating an extra confirmed reservation.
4. Submit a teaching-lab or group-room request requiring approval. Sign in as admin and approve/reject it.
5. As admin, review the catalogue, change area hours and add a teaching/maintenance closure. Existing confirmed reservations must not be silently invalidated.
6. Check cancellation before a booking begins and verify its audit history.

If the local database was created by an earlier version and the seat map is empty, restart the current local launcher or run \`.\.venv\Scripts\python.exe scripts/sync_aztu_demo.py\` once. Never discard your SQLite database merely to refresh the demo.

## Automated verification

\`\`\`powershell
.\.venv\Scripts\python.exe scripts/run_tests.py
.\.venv\Scripts\python.exe scripts/validate_models.py
.\.venv\Scripts\python.exe scripts/validate_traceability.py
.\.venv\Scripts\python.exe -m coverage run --source=src/unireserve scripts/run_tests.py
.\.venv\Scripts\python.exe -m coverage report -m --fail-under=80
\`\`\`

**Verified on GitHub Actions at commit \`d8dad20a\`:** 123 automated tests passed, 94% package-wide statement coverage, and a synthetic 200-request performance check passed (p95 ≈ 0.023 seconds). [View run 45110603568](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45110603568). These results describe the tested CI setup, **not** a local Windows usability session or production deployment.

## Documentation and handoff

- [Requirements, use cases, existing-system comparison](docs/requirements/)
- [Architecture, UML and conceptual/logical ERDs](docs/diagrams/)
- [Test plan, reports, defect log and final audit](docs/testing/)
- [Requirement-to-use-case/design/code/test traceability](docs/traceability/)
- [Change-management evidence (CR-001–CR-004)](docs/change-management/)
- [Process evidence, issues and self-review](docs/process/)
- [Six assessed PDF exports](docs/submission/)
- [Individual reflection — draft requiring personal review](docs/reflection/REFLECTION_DRAFT.md)
- [KOICA submission handoff](docs/submission/KOICA_HANDOFF.md)

This is a **locally run Flask/SQLAlchemy/SQLite prototype**, not a public multi-user university service. There is no university SSO, physical occupancy sensing, production rate limiting, TLS termination or verified campus room survey. Students must review their own reflection and disclose AI use. The repository is **private**; a lecturer needs GitHub access to view it.
