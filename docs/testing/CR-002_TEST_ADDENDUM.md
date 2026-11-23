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

**Execution evidence:** Do not treat this paragraph as a test pass. The final verified count and GitHub Actions link will be entered only after the current pull request CI completes. Previous report figures of 85 tests / 94% coverage apply to the earlier version, not this one.

**Outstanding manual review:** Owner evaluation of new room/seat plan, keyboard and mobile walkthrough, and confirmation of any real campus schedule by authorized staff. None is represented as completed.
