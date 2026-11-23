# UniReserve — Operations and Deployment (CR-005)

**Scope:** Managed HTTPS deployment plan and configurations; not proof that any public website is currently online.

## Startup modes

| Feature | Local workstation | Managed HTTPS |
|---|---|---|
| Entry point | `python scripts/serve_local.py` | `python scripts/serve_production.py` |
| WSGI | Waitress, 127.0.0.1:5000 | Waitress, 127.0.0.1:8080 |
| Session | HttpOnly, SameSite=Lax | Same plus Secure and HSTS |
| Host validation | Local testing | `UNIRESERVE_TRUSTED_HOSTS` required |
| Secret | Temporary per-process | Stable secret ≥32 chars required |
| Initial rooms | Only local first launch if no Spaces | Sample auto-seeding refused |
| Client access | Browser on the machine | Reverse proxy must provide HTTPS |

## Configure hosting

1. Register a trusted domain and configure **HTTPS/TLS** at Nginx, Caddy or the hosting platform.
2. Bind the WSGI service to loopback only. The public reverse proxy should be the only process able to reach Waitress. Never expose backend port 8080 directly.
3. Generate a random key: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Set `UNIRESERVE_SECRET_KEY` as a **persistent private environment secret**, not a committed file.
4. Set `UNIRESERVE_MODE=production`, `UNIRESERVE_TRUSTED_HOSTS=your-domain`, and `UNIRESERVE_AUTO_SAMPLE_CATALOG=0`.
5. If your trusted reverse proxy replaces the HTTPS scheme and host forwarding headers, set `UNIRESERVE_PROXY_COUNT=1` (or the actual number of trusted proxies, maximum three). **Do not enable trusted forwarded headers for arbitrary public clients.**
6. Set `UNIRESERVE_DB_PATH` to a persistent, access-restricted SQLite database on a backed-up disk. Do not run `seed_demo.py` on real data.
7. Provision a trusted administrator: `python scripts/create_account.py --email YOUR_ADMIN_EMAIL --role ADMIN`. The password is collected with `getpass`, is hashed and is not echoed.
8. In Administration, create a room/area with legitimate opening hours and weekdays, then add its separately bookable desks or PCs. Provision only approved users.
9. Configure host service restart, centralized logs, health checks (`GET /healthz`), rollback procedures, privacy policy and an incident-response owner.

## Safety and operational constraints

The app checks booking conflicts under SQLite `BEGIN IMMEDIATE` and records audit events transactionally. It has CSRF checks and role/ownership checks. Nevertheless, **public release requires additional work**: institutional identity provider or recovery flow, brute-force/rate limits, data-retention policy, production penetration testing, recovery drills, and load testing for the intended population. A SQLite single-writer design may not suit a large campus-wide deployment.

Images and map geometry supplied with the project are configured examples, not survey-verified AzTU rooms or proof of official opening hours. The site displays concise booking instructions, while the dedicated Service information page preserves this distinction.

## Sources

- Flask deploying: https://flask.palletsprojects.com/en/stable/deploying/
- Flask Waitress: https://flask.palletsprojects.com/en/stable/deploying/waitress/
- Flask app configuration: https://flask.palletsprojects.com/en/stable/config/
- Flask trusted reverse proxy: https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/
