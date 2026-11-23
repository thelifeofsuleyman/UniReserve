# UniReserve

A small, locally runnable **University Equipment and Room Reservation System** developed for a Software Engineering individual project.

**Student:** Suleyman Shafizada · **Group:** m666i1  
**Submission deadline:** 2 December 2026  
**Status:** Milestone 8 submission package prepared — working local Flask application, visual 2D availability Studio, requirements/diagrams, 85 verified tests, traceability, and six PDF exports. Personal reflection review and real usability evaluation remain open.

## Start the web UI (Windows 10/11)

Install **Python 3.11 or later** and Git. Open **PowerShell** (or VS Code Terminal) and run:

```powershell
git clone https://github.com/thelifeofsuleyman/UniReserve.git
cd UniReserve
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/seed_demo.py
python scripts/run_web.py
```

Open **http://127.0.0.1:5000** in a browser. Leave the terminal open while using the site; press **Ctrl+C** to stop it.

**Save the demo login credentials shown by `seed_demo.py`.** Three randomized accounts are created (`student@unireserve.test`, `staff@unireserve.test` and `admin@unireserve.test`). Their passwords are printed **once**, never checked into Git. The student/staff accounts can book; the admin account can review pending requests and manage resources. The script also creates six sample rooms/equipment items. Running it twice on the same database does not reset existing accounts.

> PowerShell execution-policy error when activating? You can skip activation and use `.venv\Scripts\python.exe` instead of `python` for every command, including install/seed/start. Alternatively, in the current terminal run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again.

### Start on macOS / Linux

```bash
git clone https://github.com/thelifeofsuleyman/UniReserve.git
cd UniReserve
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/seed_demo.py
python scripts/run_web.py
```

Open http://127.0.0.1:5000. Works offline after packages have been installed; fonts gracefully fall back if Google Fonts is unreachable.

### Already cloned this repository?

In your existing UniReserve folder, run `git pull origin main`, activate your environment, install dependencies, and run the seed + web startup commands. Avoid re-cloning over local work.

### Clean demo / re-seeding

The database defaults to `instance/unireserve.sqlite3`, which is ignored by Git. To start from scratch **without touching your existing data**, choose a different file:

```powershell
$env:UNIRESERVE_DB_PATH = "instance/second-demo.sqlite3"
python scripts/seed_demo.py --db instance/second-demo.sqlite3
python scripts/run_web.py
```

Run both seed and web commands against the same DB path. On macOS/Linux use `export UNIRESERVE_DB_PATH=instance/second-demo.sqlite3`.

## What can I try?

1. **Student**: sign in, browse/filter the catalogue, open a study room, check a future interval, confirm a booking, then open My Reservations and view/cancel it.
2. **Student**: choose a camera that requires approval, submit a pending request, and inspect the pending status.
3. **Admin**: sign out, sign in as admin, review/approve/reject the pending camera request, add a new resource, or disable one.
4. **Student**: sign back in to verify the approval state and audit history.
5. **2D Availability Studio**: open **Availability studio** in the sidebar to inspect the illustrative resource map. Green = available, yellow = confirmed booking within 15 minutes, red = current confirmation, gray = disabled. The status API refreshes every 30 seconds; positions are not surveyed and colors do not come from physical sensors.
6. **Double booking**: attempt a second booking for the same room and time using another user; the engine must reject the conflict.

All booking times in the web UI are explicitly interpreted in **Asia/Baku** by default. Times are stored as UTC in SQLite and shown back in the configured display timezone. The app only runs on the local machine by default (`127.0.0.1`).

## Test the system

```powershell
python scripts/run_tests.py
python scripts/validate_models.py
python scripts/validate_traceability.py
python scripts/measure_latency.py
coverage run --source=src/unireserve scripts/run_tests.py
coverage report -m --fail-under=80
```

The test suite includes Python domain/unit tests, SQLite transaction/integration tests, 50 repeated concurrent-booking race trials, and Flask HTTP integration tests for sessions, CSRF, admin/ownership controls, and major UI flows. GitHub Actions runs the same test command and reports coverage. Run results are available in the repository's **Actions** tab. The [formal test plan and case catalogue](docs/testing/TEST_PLAN.md), [measured QA report](docs/testing/M6_TEST_REPORT.md) and [defect log](docs/testing/DEFECT_LOG.md) document the executed and unmeasured checks.

## Architecture and documentation

- **SRS and use cases:** [`docs/requirements/`](docs/requirements/)
- **UML, ERDs and sequence diagrams:** [`docs/diagrams/`](docs/diagrams/)
- **Database and service decision records:** [`docs/architecture/`](docs/architecture/)
- **UI/user-feedback and manual trial instructions:** [`docs/ui/M5_UI_GUIDE.md`](docs/ui/M5_UI_GUIDE.md)
- **Traceability:** [all Must requirements mapped to code and tests](docs/traceability/MATRIX.md)
- **Change request and feedback:** [CR-001](docs/change-management/CR-001-visual-availability.md), [user feedback log](docs/ui/UI_FEEDBACK_LOG.md)
- **Reflection and process review:** [reflection draft](docs/reflection/REFLECTION_DRAFT.md), [self-review](docs/process/SELF_REVIEW_CHECKLIST.md)
- **PDF submission package:** [six PDFs](docs/submission/README.md)

The project is a **Flask modular monolith**. The browser calls Flask routes, which derive the actor identity from the signed session and call the tested booking service. That service handles UTC interval rules, resource access, approvals, and transaction-safe changes using SQLite's `BEGIN IMMEDIATE`. Audit events use database triggers to prevent modification/deletion. The template layer never directly takes a user ID from submitted forms.

## UI review and feedback

Please use the interface and share opinions about (1) navigation and appearance, (2) booking/approval clarity, (3) features that are confusing or missing, and (4) any errors. Screenshots are particularly helpful. Feedback will be logged in [`docs/ui/UI_FEEDBACK_LOG.md`](docs/ui/UI_FEEDBACK_LOG.md) with requirement/diagram/code/test impact for the final change-control report. **No feedback is fabricated.**

## Security and deployment limits

This is a **local coursework demo**, not an internet-facing production system: no TLS termination or production-grade rate limiting, no university SSO, no automated backups, and no account recovery. Flask development server runs on localhost only. For an actual deployment, use HTTPS with `SESSION_COOKIE_SECURE=True`, rate limiting, deployment secrets, password reset and institution-specific data/retention policies.

## AI use disclosure

ChatGPT assisted with draft requirements, diagrams, scaffolding, implementation, testing guidance and design documentation. The student should review the entire repository, verify behavior, record genuine feedback and disclose the actual assistance in the final individual reflection.

## Milestone 5.5: Visual availability studio

User feedback led to a deliberate visual redesign (change request [`CR-001`](docs/change-management/CR-001-visual-availability.md)). An original resource illustration atlas provides real imagery on the login, catalogue and detail pages, with a clickable **Availability studio** in the sidebar.

The Studio is **not** a real physical campus floor plan: placements are illustrative, and status comes from confirmed reservation records rather than occupancy sensors. Green = available now, yellow = confirmed booking within the next 15 minutes, red = confirmed booking active now, grey = disabled. Pending approvals do not hold capacity. The read-only browser view refreshes every 30 seconds; the database transaction still makes the final decision.

See the [UI review notes](docs/ui/M55_VISUAL_REVIEW.md) and [owner feedback log](docs/ui/UI_FEEDBACK_LOG.md). The owner has not yet reviewed the revised interface.

## Milestone 6: Formal test and coverage evidence

The test package includes a [formal test plan](docs/testing/TEST_PLAN.md), [traceable test cases](docs/testing/TEST_CASES.md), [verified CI test report](docs/testing/M6_TEST_REPORT.md), [measured performance report](docs/testing/M6_PERFORMANCE_REPORT.md) and [defect log](docs/testing/DEFECT_LOG.md). Run `python scripts/measure_latency.py` to repeat the NFR-001 200-request probe. This does **not** claim full user-study or keyboard-accessibility verification; those require real manual sessions and are explicitly marked unmeasured.

## Milestone 7: Traceability and design reconciliation

[Requirement-to-design-to-code-to-test matrix](docs/traceability/MATRIX.md) maps all 11 Must functional requirements to use cases, PlantUML models, real files and verified CI tests. The supplementary [CR-001 sequence](docs/diagrams/source/14-seq-CR-001-studio.puml) documents the new Studio status API. Known differences between conceptual design patterns and the implementation are disclosed; physical checkout and quota extensions remain deferred, and human usability/accessibility measurements remain open.

### Rebuild PDFs on your own machine

The source PDFs and diagrams are committed to `docs/submission/`. To regenerate with Python 3.11+, run:

```powershell
python -m pip install reportlab pypdf Pillow
python scripts/build_submission_docs.py
python scripts/validate_submission.py
```

These commands are for documentation generation only; the web UI continues to run with `requirements-dev.txt`. The reflection PDF is a **draft requiring the student's personal review** and the non-measured usability/keyboard checks must not be represented as completed.
