"""Pure, testable status indicator rules for the visual resource map.

These indicators are calculated from confirmed reservations, not from sensors.
They are informational; every booking must still be checked transactionally.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable


@dataclass(frozen=True)
class ConfirmedInterval:
    start: datetime
    end: datetime


@dataclass(frozen=True)
class StatusView:
    state: str  # AVAILABLE, SOON, OCCUPIED, DISABLED
    next_start: datetime | None
    current_end: datetime | None


def current_status(is_enabled: bool, intervals: Iterable[ConfirmedInterval], now: datetime) -> StatusView:
    """Priority DISABLED > OCCUPIED > SOON (<=15 minutes) > AVAILABLE.

    An interval is active for start <= now < end. Pending reservations are
    filtered out before calling this function.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if not is_enabled:
        return StatusView("DISABLED", None, None)
    starts = []
    ends = []
    for item in intervals:
        if item.start.tzinfo is None or item.end.tzinfo is None:
            raise ValueError("booking timestamps must be timezone-aware")
        if item.start <= now < item.end:
            ends.append(item.end)
        elif item.start > now:
            starts.append(item.start)
    soonest = min(starts) if starts else None
    if ends:
        return StatusView("OCCUPIED", soonest, min(ends))
    if soonest is not None and soonest <= now + timedelta(minutes=15):
        return StatusView("SOON", soonest, None)
    return StatusView("AVAILABLE", soonest, None)
