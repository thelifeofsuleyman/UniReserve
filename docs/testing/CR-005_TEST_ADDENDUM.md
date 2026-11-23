# CR-005 — Deployment and product copy test addendum

| Test ID | Level | Expected outcome |
|---|---|---|
| CR005-01 | Config negative | Production without stable secret refuses startup. |
| CR005-02 | Config negative | Production without trusted hosts refuses startup. |
| CR005-03 | Config negative | Production with sample auto-seeding refuses startup. |
| CR005-04 | HTTP/security | Secure session cookies, HSTS/CSP and host validation work in production mode. |
| CR005-05 | Integration | Empty production database starts without fictional sample rooms; `/healthz` reports status. |
| CR005-06 | Presentation | Login, catalogue and map omit repeating implementation/setup warnings. |
| CR005-07 | User-information | Independent-service/source caveats remain reachable through `/about`. |
| CR005-08 | Authorization/validation | Admin can create an area and bookable resource; student cannot; invalid/duplicate data is rejected. |
| CR005-09 | Regression | Booking integrity, approvals, cancellations, operating hours, room maps and prior test techniques continue passing. |

**Test source:** `tests/test_cr005_production.py`, `tests/test_cr005_spacemanagement.py` and the full existing `tests/` suite.

**Claims policy:** Record actual pass/fail counts and coverage from the matching GitHub Actions run. Do not treat configuration tests as evidence of actual internet hosting, penetration testing or five-volunteer usability.
