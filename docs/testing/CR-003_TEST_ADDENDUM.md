# CR-003 — User-experience and integrity test addendum
**Source of request:** student's own review of UniReserve's UI, 23 November 2026.

| Case | Technique | Expectation / trace |
|---|---|---|
| TC-CR003-01 | Equivalence partition | FR-005: same user booking different PCs in same interval is rejected with no extra event |
| TC-CR003-02 | Equivalence partition | FR-005: different users can book different PCs simultaneously |
| TC-CR003-03 | Boundary value | BR-02: immediately adjacent bookings for the same user remain permitted |
| TC-CR003-04 | State transition | FR-008: a pending approval remains pending when its owner gets another confirmed booking |
| TC-CR003-05 | Invalid transition | FR-009: cannot reassign future confirmed booking to an incompatible area with different operating hours |
| TC-CR003-06 | Boundary value | FR-009: cannot reclassify legacy 3-hour booked equipment as a room capped at 2 hours |
| TC-CR003-07 | Source contract | User interface images are local/offline; no remote photo or font dependency |
| TC-CR003-08 | Manual UI review pending | Zone filtering and red/yellow/green/gray color+text updates, keyboard access, contrast and mobile view |

**Automation evidence:** `tests/test_cr003_seat_integrity.py`, adjusted `tests/test_aztu_policy.py`, existing Flask and model tests in GitHub Actions. The first PR CI attempt failed an existing wording assertion for the 2D map; the string was restored in the next development commit. This failure and correction are genuine process evidence, not a hidden or fabricated test. CI run: https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45108451448.

**Defects:**
- DEF-CR003-A, medium: live polling previously changed a badge's text without always changing its background class. UI fix synchronizes both, including CLOSED/DISABLED.
- DEF-CR003-B, medium: simultaneous bookings of two distinct workstations by one user were possible. A new atomic user-level check now rejects them.
- DEF-CR003-C, high: a resource could be moved to an incompatible area's hours or reclassified to a shorter booking limit with future confirmations. A guard now rolls back the administrator edit.
- DEF-CR003-D, low: external photo loading could fail and generic visual layout caused poor user experience. Use local imagery and more navigable cards.

**Still not measured:** real-student usability study, real-campus schedules/floor-plan accuracy, physical occupancy, production-scale account throttling or identity provider support. Do not claim a complete real-world accreditation or stakeholder acceptance.
