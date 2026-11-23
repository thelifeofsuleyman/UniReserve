# UniReserve — Defect and Issue Log

**Record basis:** genuine user feedback and failures actually observed; not a fabricated bug hunt. Severity and outcome are stated explicitly, including non-code incidents.

| ID | Kind | Severity | Discovery / symptoms | Cause | Resolution / verification | Status |
|---|---|---|---|---|---|---|
| ENV-001 | Setup/environment issue | Medium (blocks running) | User reported on Windows: `py` command missing; `python` resolved to `C:\msys64\ucrt64\bin\python.exe` without pip, Flask or SQLAlchemy. | Windows launcher not installed and MSYS2 interpreter selected. | Advised installing Windows Python 3.12, creating a `.venv`, installing `requirements-dev.txt`, selecting interpreter. User explicitly confirmed getting the application running. | Resolved by user; no code defect |
| UX-001 | Usability/design gap | Medium (visual clarity and engagement) | Owner stated that the original functional UI had no pictures and felt too generic; proposed 2D/3D placement and green/yellow/red statuses. | Previous UI represented resources with abstract glyph cards and lacked at-a-glance current status. | CR-001 introduces original imagery, clickable 2D resource studio, current/15-min status API and automated boundary tests. Owner review of the revised UI is still pending. | Implemented; awaiting owner acceptance |
| TOOL-001 | Development environment limitation | Low (test evidence workflow) | Local browser preview attempts returned `ERR_BLOCKED_BY_ADMINISTRATOR`; local container had no Flask package or network access to install it. | Hosted development execution restrictions, not an error in UniReserve itself. | Full Flask tests and coverage executed on GitHub Actions Ubuntu/Python 3.11. Do not claim local UI screenshot run from this environment. | Mitigated through CI |

## Functional defects observed so far

None confirmed in the verified test runs to date. It would be misleading to invent a database or authorization bug just to populate this log. If a future test finds a bug, record its reproduction, severity, expected/actual behavior, root cause, fixing commit and re-test link before marking it resolved.

## Severity definitions

- **Critical:** data corruption/security breach or global outage.
- **High:** Must requirement broken or security/booking integrity compromised.
- **Medium:** important workflow blocked or substantial usability gap.
- **Low:** non-blocking UI issue, spelling or developer tooling inconvenience.

## Suggested defect report template

`ID | severity | requirement | environment | steps | input | expected | actual | discovery test | cause | fix commit | retest result | status`.
