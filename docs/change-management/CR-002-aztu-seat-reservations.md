# CR-002 — AzTU-Inspired Study Seats and PC Workstations

**Source:** Direct owner request on 23 November 2026. **Status:** Implemented in code, owner visual acceptance pending. **Course:** Software Engineering, UniReserve.  
**Reason:** The owner's feedback requested a more realistic AzTU model: computer rooms, library PCs, bookable individual seats, working-hour restrictions, and removal of unnecessary camera/microphone/projector items.

## Documented sources versus design assumptions

**Verified public information (official university sources):**

1. [AzTU campus](https://aztu.edu.az/az/page/kampus-202) shows computer labs and library facilities (campus photo includes computers at individual desks).
2. [AzTU Library Information Center](https://aztu.edu.az/az/idareetme/ofis-ve-merkezler/kitabxana-informasiya-merkezi) describes a reading hall and shows **09:00–17:30** as its work hours. This is not a published seat-booking guarantee or a complete room-by-room weekly timetable.
3. [AzTU general contact page](https://aztu.edu.az/az/elaqe) lists the university's **administrative office hours** as Monday–Friday **09:00–18:00**. These are *not* confirmed computer laboratory public-access hours.
4. [AzTU official Library site](https://library.aztu.edu.az/) includes library facilities and room-reservation-related navigation. UniReserve is a separate student project, **not** integrated with AzTU's systems.
5. [AzTU technical accreditation text](https://www.aztu.edu.az/sub_site/web_admin/upload/files/aztu.edu.az/menus/11-2024/AzTU_Yekun%20Hesabat_TKTA_sayt_compressed.pdf) refers to computer laboratories and educational software. It does not publish verified seat labels.

**Clearly stated demo assumptions:** The library and classroom zones in this implementation are *illustrative examples*; their IDs, number of seats/PCs, 2D floor positions, reservability, approvals, and Mon–Fri schedule are **not factual inventory or confirmed policy**. The lab zone adopts 09:00–18:00 as an adjustable **demo assumption**, not an official lab-access window. The library zone adopts 09:00–17:30 as a reference time but assumes weekdays. The initial weekend closure is a conservative demo rule; an administrator can configure it.

## Decision and rationale

Replace the equipment-bay-first demo catalogue with **individual reservable units** grouped by physical space. Model four sample areas: Library Reading Area (8 seats), Library Computer Area (6 PCs), Teaching PC Lab (8 workstations), and one Group Study Room. The exact numbers are illustrative and are not campus capacity statements.

A user reserves an individual **seat or workstation**. A teaching lab PC needs admin approval, and an admin can block the entire lab for classes or maintenance. No booking may start before opening or end after closing; same-day bookable intervals only, and weekday policies are evaluated in **Asia/Baku**. The existing two-hour room session limit now also applies to seats/PCs; the 14-day booking horizon remains. Approval rechecks **hours, closure and confirmed conflicts inside the write transaction**.

**Legacy demo resources** (`ROOM-101`, `ROOM-202`, `EQ-CAM-01`, `EQ-LAP-01`, `EQ-MIC-01`, `EQ-PROJ-01`) are archived (`is_listed=false`, `is_enabled=false`) by the explicit idempotent demo sync. They are **never deleted**: historic confirmed reservations and audit events retain their foreign-key references. Unrecognized or instructor-created resources are untouched.

## New design rules (SRS extension)

| ID | Rule | Verification |
|---|---|---|
| AZ-01 | Every published sample library seat or PC is its own reservation unit associated with exactly one Area (`Space`). | Distinct PC and seat booking integration tests; `Resource.space_id` FK |
| AZ-02 | Reject booking windows outside configured local opening hours, across dates, or on non-open days. | Before-open, exactly-at-open, exactly-at-close, after-close, weekend and midnight boundary tests |
| AZ-03 | Administrators can block a space for teaching or maintenance. No new booking or pending approval may be confirmed over a closure. | Closure/approval integration tests |
| AZ-04 | Admin schedule edits cannot silently invalidate existing future confirmed reservations. | Update hours rollback test |
| AZ-05 | Preserve old reservation history while hiding irrelevant legacy demo inventory from the student catalogue. | Idempotent migration and FK-history tests |
| AZ-06 | Show a separate **CLOSED** indicator outside operating hours or during a scheduled closure; continue AVAILABLE/SOON/OCCUPIED/DISABLED where appropriate. | Status tests, API tests, responsive map checks |

**Requirement impact:** FR-002/003 resource catalogue and availability now include area and hours; FR-004/005 book specific seats/PCs and validate hours atomically; FR-008 requires checking a closure before approval; FR-009 adds admin closure/schedule controls; FR-010 protects these operations. No already-passed requirement or test was retroactively represented as owner-approved for physical campus use.

## Architecture / 3NF impact

Added 4 normalized `spaces` (code, name, kind, office hours, weekday **bitmask**, policy note, enabled) and `space_closures` (space FK, start, end, reason). Each resource gains a nullable `space_id` FK and an `is_listed` flag; the category remains backward compatible (`ROOM`/`EQUIPMENT`). The weekday bitmask is a single scalar rather than a comma-separated repeating field. The 3NF model still stores user and resource names only once, and all changes are service-layer controlled. See diagram **15** and booking/closure sequence **16**.

`create_schema` performs **additive SQLite migration** for the original Resource columns without dropping tables. `sync_aztu_demo.py` is intentionally separate from app startup; it operates on the local demo database only. The existing 2D map is replaced with one section per example Area, not coordinates claimed as surveyed.

## Impact / test strategy

| Area | Change | Test / evidence |
|---|---|---|
| Schema | Two new tables, two Resource fields, non-destructive migration | Old-schema migration test and FK-history check |
| Domain/service | Weekday hours, closures, approval revalidation | `test_aztu_policy.py` plus original 50 two-client conflict trials |
| UI | New library-seat and PC cards, map grouped by Area, `CLOSED` indicator | `test_aztu_web.py` and existing HTTP regression suite |
| Admin | Hours/weekday updates and teaching closures | Admin-only HTTP and service tests |
| Documentation | SRS addendum, diagram extension, traceability and final PDF re-export | `validate_aztu.py`, `validate_models.py`, submission PDF workflow |
| Risk | Unverified labels/hours misrepresented as official; stale 30-second status | Prominent demo disclaimers and booking-time recheck; admin can configure policies |

**Open for owner:** Confirm whether the aesthetics match expectations and whether the campus's actual public library/PC schedules differ. A manual visit, staff confirmation, or authenticated published resource list is needed before claiming exact floor numbers, hours or official rights to reserve workstations.
