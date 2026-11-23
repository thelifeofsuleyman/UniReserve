# CR-004 — Requirement and code impact

| Requirement/change | Design / code | Verification |
|---|---|---|
| FR-002 resource browsing | Four Space context cards; filtered compact Resource directory. Resource/Space conceptual relationship unchanged. | `test_cr004_room_layout.py`: catalogue images, unit names, cardinalities. |
| FR-003 availability status | Existing server status provider, color labels and per-resource IDs retained. No client-derived availability claims. | Existing `test_visual_web.py`, `test_aztu_web.py`. |
| FR-004 booking a specific resource | Each of 22 seats/PCs has a distinct resource page and exactly one booking unit for group room. | Test counts and HTML `href` mappings; existing booking integration tests. |
| FR-005 concurrency/owner fairness | CR-004 makes no change to transactional booking logic. Existing requirements and tests remain authoritative. | CI: tests and 50 repeated race trials. |
| CR-004 first-run usability | Demo launcher initializes four areas only when no Space records exist. Historical foreign keys remain intact. | Tests for automatic sync, idempotence, preserved legacy booking. |
| CR-004 visual design | Four purpose-specific original illustrations; two-bank reading/PC floor diagrams and one-table group booking map. | HTML/CSS and static asset tests, visual owner review outstanding. |

No real-world AzTU room survey, occupancy sensors, or university identity system is claimed.
