# UniReserve

**Campus study-space reservations**  
**Student:** Suleyman Shafizada · Group m666i1  
**Software Engineering project · Deadline: 2 December 2026**

UniReserve lets students reserve individual library seats, desktop computers and study rooms. Administrators manage booking approvals, opening hours, closures, room inventory and account access. The interface includes interactive room plans, live current-status indicators, a date-specific booking calendar, and a personal seven-day schedule.

## Start on Windows / VS Code

From an existing clone of this repository:

```powershell
git pull origin main
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/serve_local.py
```

Open **http://127.0.0.1:5000** and press Ctrl+C to stop. The local server uses **Waitress**, not Flask's development server. The first local launch initializes the four sample study areas only if the database has no areas. Existing accounts, reservations, approval events and space edits are retained.

For first-time setup:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/seed_demo.py
.\.venv\Scripts\python.exe scripts/serve_local.py
```

`seed_demo.py` creates synthetic accounts with random passwords displayed once in the terminal. **Do not use these accounts for a public site.** The default SQLite file is `instance/unireserve.sqlite3`, which Git ignores.

## Initialize an actual instance without sample users

1. Install dependencies and configure `UNIRESERVE_DB_PATH` to a persistent location.
2. Create a real administrator account, with a password entered privately:

```powershell
.\.venv\Scripts\python.exe scripts/create_account.py --email admin@your-university.edu --role ADMIN
```

3. Log in to **Administration → Add an area** and configure the real room name, type and working hours. Use **Add a resource** to create each bookable seat or PC.
4. Provision other accounts using `scripts/create_account.py --email ADDRESS --role STUDENT` or `STAFF`.
5. Confirm the real institution's access, scheduling and privacy policies before going public.

## Managed HTTPS deployment baseline

The production WSGI launcher is `scripts/serve_production.py`, which binds Waitress to **127.0.0.1:8080** and requires a separate **HTTPS reverse proxy**. It does not deploy a publicly reachable site or issue certificates.

Configure these settings through your host's service/secret manager (not in Git):

```text
UNIRESERVE_MODE=production
UNIRESERVE_SECRET_KEY=<secure-persistent-random-secret>
UNIRESERVE_TRUSTED_HOSTS=reservations.your-university.edu
UNIRESERVE_DB_PATH=instance/unireserve.sqlite3
UNIRESERVE_AUTO_SAMPLE_CATALOG=0
UNIRESERVE_PROXY_COUNT=1
```

Use `UNIRESERVE_PROXY_COUNT=1` **only** behind exactly one trusted proxy that replaces client-supplied forwarded headers. Production mode requires a secret of at least 32 characters, allowed hosts, HTTPS-only session cookies and prevents sample seeding. CSP, HSTS, anti-framing, no-sniff, and referrer headers are applied. See [Operations and Deployment](docs/deployment/OPERATIONS.md) for the architecture, account provisioning, backups and remaining release gates.

**Important:** A production-styled interface and WSGI configuration are not the same as public deployment or production accreditation. An institution-hosted service still needs domain/TLS ownership, account recovery/SSO, rate limiting, audited backups, monitoring, security testing and real campus authorization.

## Calendar and reservation-status behavior

Select a seat, PC or group room and use **Availability calendar** below **Choose your time** to view confirmed reservations for a specific date (within the next 14 days). Green half-hour tiles are free; red tiles already have a confirmed booking; gray tiles are closed/past; amber tiles overlap another confirmed study-space reservation you own. Click a green tile to fill the reservation form, adjust times if required, then check or submit. Pending approvals do not block capacity; confirmation rechecks conflicts atomically.

The sidebar's live map uses current-moment status, so a booking for tomorrow will not incorrectly turn a room red today. **My reservations** now shows a seven-day upcoming agenda above full booking history. No data about who booked another user's room is exposed by the schedule endpoint.

## Run validation

```powershell
.\.venv\Scripts\python.exe scripts/run_tests.py
.\.venv\Scripts\python.exe scripts/validate_models.py
.\.venv\Scripts\python.exe scripts/validate_traceability.py
.\.venv\Scripts\python.exe -m coverage run --source=src/unireserve scripts/run_tests.py
.\.venv\Scripts\python.exe -m coverage report --fail-under=80
```

GitHub Actions checks the booking engine, parallel request races, approval states, user permissions, opening-hour rules, web views, requirement/design mapping and synthetic HTTP latency. See the [current Actions runs](https://github.com/thelifeofsuleyman/UniReserve/actions) rather than assuming historic coverage numbers apply to every later commit.

## Documentation

- [Requirements and use cases](docs/requirements/)
- [UML, ERDs and architecture](docs/diagrams/)
- [Test plan and results](docs/testing/)
- [Traceability](docs/traceability/)
- [Changes CR-001–CR-005](docs/change-management/)
- [Deployment](docs/deployment/OPERATIONS.md)
- [Six assessed PDFs](docs/submission/)
- [AI-assisted individual reflection draft](docs/reflection/REFLECTION_DRAFT.md)

Actual AzTU reservation rights, precise room geometry, booking schedules and real-time physical occupancy **have not been verified**. These facts and original AI image-generation assistance are documented in the academic materials and on the site's dedicated **Service information** page instead of repeated across every booking screen. The project is not an official AzTU service.
