# CR-004 — Contextual imagery and room-plan integration tests

| Test | Technique | Expected |
|---|---|---|
| CR004-01 | State initialization | Fresh demo database receives exactly 4 spaces and 23 bookable resources. |
| CR004-02 | UI contract | Four distinct local illustrations match the four area kinds; no repeated unrelated equipment photo cards. |
| CR004-03 | ER/cardinality | Each room map contains exactly its published number of selectable units. Group room is one resource, despite six decorative chairs. |
| CR004-04 | Interaction / routing | Zone card contains `/studio?area=...` and JS selects a matching tab on entry. |
| CR004-05 | Idempotence | Recreating the app does not overwrite renamed Space labels or duplicate resources. |
| CR004-06 | Isolation | `create_app(TESTING=True)` without opt-in does not auto-populate unrelated test databases. |
| CR004-07 | Data migration | Starter gear becomes unlisted and disabled; historic confirmed reservations remain readable. |
| CR004-08 | Regressions | The existing test suite, diagram consistency and requirements trace checks remain successful. |

**Evidence:** `tests/test_cr004_room_layout.py` plus all existing `tests/`. Test status and coverage must be taken from the corresponding GitHub Actions run after merging, not assumed from the document.

**Residual work:** The owner still needs to judge photo appropriateness and actual rendered room layouts in the browser; automated HTML/route tests cannot establish subjective design quality. The floor plan is not verified AzTU geography or live occupancy sensing.
