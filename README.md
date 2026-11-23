# UniReserve

A small, locally runnable **University Equipment and Room Reservation System** developed for a Software Engineering individual project.

**Student:** Suleyman Shafizada · **Group:** m666i1  
**Submission deadline:** 2 December 2026  
**Status:** Milestone 5 — working local web UI backed by a tested SQLite/SQLAlchemy reservation engine; final coursework test/report/traceability packages still in progress.

## Start the web UI (Windows 10/11)

Install **Python 3.11 or later** and Git. Open **PowerShell** (or VS Code Terminal) and run:

```powershell
git clone https://github.com/thelifeofsuleyman/UniReserve.git
cd UniReserve
py -m venv .venv
.venv\Scripts\Activate.ps1
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
5. **Double booking**: attempt a second booking for the same room and time using another user; the engine must reject the conflict.

All booking times in the web UI are explicitly interpreted in **Asia/Baku** by default. Times are stored as UTC in SQLite and shown back in the configured display timezone. The app only runs on the local machine by default (`127.0.0.1`).

## Test the system

```powershell
python scripts/run_tests.py
python scripts/validate_models.py
coverage run --source=src/unireserve scripts/run_tests.py
coverage report -m --fail-under=80
```

The test suite includes Python domain/unit tests, SQLite transaction/integration tests, 50 repeated concurrent-booking race trials, and Flask HTTP integration tests for sessions, CSRF, admin/ownership controls, and major UI flows. GitHub Actions runs the same test command and reports coverage. Run results are available in the repository's **Actions** tab. Milestone-specific testing notes are in [`docs/testing/M5_WEB_TEST_REPORT.md`](docs/testing/M5_WEB_TEST_REPORT.md).

## Architecture and documentation

- **SRS and use cases:** [`docs/requirements/`](docs/requirements/)
- **UML, ERDs and sequence diagrams:** [`docs/diagrams/`](docs/diagrams/)
- **Database and service decision records:** [`docs/architecture/`](docs/architecture/)
- **UI/user-feedback and manual trial instructions:** [`docs/ui/M5_UI_GUIDE.md`](docs/ui/M5_UI_GUIDE.md)
- **AI and change-management evidence:** to be consolidated in the final reflection and traceability milestone.

The project is a **Flask modular monolith**. The browser calls Flask routes, which derive the actor identity from the signed session and call the tested booking service. That service handles UTC interval rules, resource access, approvals, and transaction-safe changes using SQLite's `BEGIN IMMEDIATE`. Audit events use database triggers to prevent modification/deletion. The template layer never directly takes a user ID from submitted forms.

## UI review and feedback

Please use the interface and share opinions about (1) navigation and appearance, (2) booking/approval clarity, (3) features that are confusing or missing, and (4) any errors. Screenshots are particularly helpful. Feedback will be logged in [`docs/ui/UI_FEEDBACK_LOG.md`](docs/ui/UI_FEEDBACK_LOG.md) with requirement/diagram/code/test impact for the final change-control report. **No feedback is fabricated.**

## Security and deployment limits

This is a **local coursework demo**, not an internet-facing production system: no TLS termination or production-grade rate limiting, no university SSO, no automated backups, and no account recovery. Flask development server runs on localhost only. For an actual deployment, use HTTPS with `SESSION_COOKIE_SECURE=True`, rate limiting, deployment secrets, password reset and institution-specific data/retention policies.

## AI use disclosure

ChatGPT assisted with draft requirements, diagrams, scaffolding, implementation, testing guidance and design documentation. The student should review the entire repository, verify behavior, record genuine feedback and disclose the actual assistance in the final individual reflection.


## CR-002: AzTU-inspired library seats and computer labs (demo)

Research was based on AzTU's public **campus**, **Library Information Center** and **contact** pages. The system uses real facility *types* but **not verified AzTU room numbers, seat counts or official individual-seat booking permissions**. The Library Information Center lists 09:00–17:30; generic AzTU administrative office hours are Mon–Fri 09:00–18:00, not guaranteed PC laboratory hours. Our hours are configurable **demonstration policies**. See `docs/change-management/CR-002-aztu-seat-reservations.md`.

### Upgrade your existing local demo (preserves account passwords and bookings)

After `git pull origin main`, run this **once** from the repository folder:

```powershell
.\.venv\Scripts\python.exe scripts/sync_aztu_demo.py
.\.venv\Scripts\python.exe scripts/run_web.py
```

Or run `python scripts/seed_demo.py` again; if demo users exist, it **does not change passwords**, but safely synchronizes the sample catalogue. Always back up a locally valuable SQLite database before any migration. The change adds `spaces`, `space_closures` and nullable `resource.space_id` / `is_listed` columns; it is additive, not destructive. It archives only six known initial starter assets; all reservation history remains intact.

The 2D map displays individually bookable Library Reading Seats, Library PCs, Teaching Lab PC workstations, and a sample study room. The seeded units and floor arrangement are **illustrations**; there is no university API, student-card verification or physical presence sensor. **CLOSED** shows after hours / school closures; green/yellow/red convey confirmed reservations only. An administrator can update example opening times and create teaching/maintenance closures without invalidating confirmed bookings. Existing admin/student passwords remain unchanged.

**References:** https://aztu.edu.az/az/page/kampus-202 · https://aztu.edu.az/az/idareetme/ofis-ve-merkezler/kitabxana-informasiya-merkezi · https://aztu.edu.az/az/elaqe


### CR-003 — UI refinements and fair-use review

After pulling the latest `main`, restart Flask (no re-seeding or schema migration needed). The updated local-image-based UI includes zone filters on the 2D map and availability badges whose color and text update together. **Status colors show global current booking status, not ownership or future guaranteed availability.** In the demo only, a user may hold at most one overlapping confirmed seat/PC/room. Different users may book distinct spots at the same time, pending approval still does not reserve the unit, and administrators cannot move confirmed future bookings to incompatible hours. See `docs/change-management/CR-003-ux-and-integrity.md` for decisions and known gaps.


## CR-004: room-first catalogue, matching photos, and automatic local demo sync

After `git pull origin main`, restart `python scripts/run_web.py`. The **local demo launcher** now detects an old empty-area database and automatically applies the idempotent four-area sample catalogue. You no longer have to remember to run `sync_aztu_demo.py` to get the clickable 2D room maps. It preserves existing users, passwords, booking history and audit events; it only archives the six known obsolete starter fixture codes. It does not reseed on every restart, and it never overwrites administrator changes to existing sample spaces. Opt out with `UNIRESERVE_AUTO_SAMPLE_CATALOG=0` in a terminal before running the demo.

Four **different original illustrative photographs** correspond to: reading seats (8), library PCs (6), teaching lab PCs (8), and one group study room. These are **not verified images of AzTU buildings**. Catalogue cards represent each area once, followed by a searchable list of individually bookable units. The clickable 2D maps use two desk banks and an access aisle (or one group table) instead of generic rows of tiles. The booking logic still checks actual stored reservations and operating hours in the database.

See `docs/change-management/CR-004-space-first-rooms.md` for the product-owner screenshots, rationale, test plan and remaining limitations.
