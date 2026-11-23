"""Idempotent AzTU-inspired SEAT/PC demo catalogue; no data is deleted.

This is not an authoritative list of AzTU rooms, seat counts or timetables.
Existing requests and audit records always retain their resource foreign keys.
"""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.engine import Engine
from unireserve.storage.db import write_transaction
from unireserve.storage.models import Resource, Space

# Official site describes library facilities and computer labs, not verified
# room numbers or any actual individual-seat booking service.
AREAS = (
    ("LIB-READ", "Library · Reading Area", "LIBRARY_SEAT", "09:00", "17:30",
     "Study seats available during posted opening hours."),
    ("LIB-COMP", "Library · Computer Area", "LIBRARY_PC", "09:00", "17:30",
     "Computer access is subject to current room availability."),
    ("LAB-PC", "Computer Teaching Lab", "COMPUTER_LAB", "09:00", "18:00",
     "Administrator approval required; class periods may restrict bookings."),
    ("LIB-GROUP", "Library Group Study", "STUDY_ROOM", "09:00", "17:30",
     "The reservation covers the entire room; approval required."),
)
# No seat count, laboratory number, or floor position here is represented
# as a factual AzTU inventory. Each resource is one bookable unit.
UNITS = (
    *[(f"AZ-LS-{n:02d}", f"Reading Seat {n:02d}", "ROOM", "LIB-READ", False)
      for n in range(1, 9)],
    *[(f"AZ-LP-{n:02d}", f"Library PC {n:02d}", "EQUIPMENT", "LIB-COMP", False)
      for n in range(1, 7)],
    *[(f"AZ-CP-{n:02d}", f"Lab Workstation {n:02d}", "EQUIPMENT", "LAB-PC", True)
      for n in range(1, 9)],
    ("AZ-GR-01", "Group Study Room 01", "ROOM", "LIB-GROUP", True),
)
# Archive *only* known starter fixtures; don't touch administrator-added units.
LEGACY_STARTER_CODES = frozenset({
    "ROOM-101", "ROOM-202", "EQ-CAM-01", "EQ-LAP-01", "EQ-MIC-01", "EQ-PROJ-01",
})


def sync_demo_catalog(engine: Engine) -> dict[str, int]:
    """Safely upsert demo units and archive legacy starter items in one transaction.

    A second run makes no changes. Historical reservations are never deleted,
    even when an old starter resource is hidden and disabled.
    """
    created_spaces = created_resources = archived = 0
    with write_transaction(engine) as session:
        existing_spaces = {s.public_code: s for s in session.scalars(select(Space)).all()}
        for code, name, kind, opens, closes, note in AREAS:
            if code not in existing_spaces:
                s = Space(public_code=code, name=name, kind=kind,
                          opens_at=opens, closes_at=closes, open_days=31,
                          policy_note=note, is_enabled=True)
                session.add(s)
                session.flush()
                existing_spaces[code] = s
                created_spaces += 1
        existing_resources = {r.public_code: r for r in session.scalars(select(Resource)).all()}
        for code, name, category, area_code, approval in UNITS:
            if code not in existing_resources:
                session.add(Resource(public_code=code, name=name, category=category,
                                     requires_approval=approval, is_enabled=True,
                                     is_listed=True, space_id=existing_spaces[area_code].id))
                created_resources += 1
        for code in LEGACY_STARTER_CODES:
            r = existing_resources.get(code)
            if r is not None and (r.is_listed or r.is_enabled):
                r.is_listed = False
                r.is_enabled = False
                archived += 1
    return {"spaces_created": created_spaces, "units_created": created_resources,
            "legacy_starter_units_archived": archived}
