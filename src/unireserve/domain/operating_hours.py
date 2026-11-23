"""AzTU-inspired demo operating policies; not verified room-specific hours.

The university provides reference hours for its Library Information Center and
administrative offices. Teaching-lab availability and days are configurable demo
assumptions. Weekend access is conservatively disabled in the demo.
"""
from __future__ import annotations
from datetime import datetime, time
from zoneinfo import ZoneInfo

BAKU = ZoneInfo("Asia/Baku")


def open_at(space, when: datetime) -> bool:
    """Is the space open at *this instant*? end is exclusive."""
    local = when.astimezone(BAKU)
    days = {day for day in range(7) if space.open_days & (1 << day)}
    clock = local.strftime("%H:%M")
    return bool(space.is_enabled and local.weekday() in days and
                space.opens_at <= clock < space.closes_at)


def within_hours(space, start: datetime, end: datetime) -> bool:
    """Require the entire half-open booking to fit one local business day."""
    first, last = start.astimezone(BAKU), end.astimezone(BAKU)
    days = {day for day in range(7) if space.open_days & (1 << day)}
    return bool(space.is_enabled and first.date() == last.date()
                and first.weekday() in days
                and time.fromisoformat(space.opens_at) <= first.time()
                and last.time() <= time.fromisoformat(space.closes_at))
