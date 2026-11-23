# CR-002 — Additional Test Plan and Execution Record

**Change:** AzTU-inspired individual seat/PC reservations with configurable operating hours, teaching closures, and non-destructive demo catalogue migration.

## New test design techniques

| Technique | Test data / oracle |
|---|---|
| Boundary values | At opening (accepted), before opening (rejected), exactly at closing (accepted), after closing (rejected), crossing midnight (rejected), 2 h versus 2 h + 1 min |
| Equivalence partitioning | Library seat/PC, restricted teaching lab workstation, study room; listed versus archived demo unit; open versus closed day |
| State transition | Pending lab PC approval succeeds only if the area is open and no teaching closure / confirmed overlap now exists |
| Decision table | Role student/admin × venue open/closed × closure yes/no × existing confirmed booking yes/no |
| Concurrency/regression | Existing 50 synchronized booking race trials must continue to pass; independent seat IDs must not conflict with one another |
| Migration | Old SQLite resource table receives new nullable/defaulted fields without deleting reservations; idempotent catalog sync retains historical FKs |

**Tests:** `tests/test_aztu_policy.py` and `tests/test_aztu_web.py`. Execute with `python scripts/run_tests.py` plus `python scripts/validate_models.py` and `python scripts/validate_traceability.py`.

**Execution evidence (verified):** On GitHub Actions, PR #9 revision `cd023fdad` completed **109/109 automated tests** with **94% statement coverage** on Python **3.11.18**. Existing synchronized 50-pair concurrency tests passed, as did the new space, closure, boundary, API and migration tests. The NFR-001 local-runner probe reported **200/200 requests within 1 second** (p95 **0.03083 s**) with 100 resources and 1,000 reservations. Source: https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45107393930. The export/validation runs also passed on this PR, including 16 diagrams and six generated PDFs. **This is CI evidence, not a volunteer usability evaluation or verification of real AzTU lab opening hours.**

**Outstanding manual review:** Owner evaluation of new room/seat plan, keyboard and mobile walkthrough, and confirmation of any real campus schedule by authorized staff. None is represented as completed.
