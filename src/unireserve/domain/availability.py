"""Time-range rules for resource reservations.

This module only checks interval boundaries. Database-level conflict prevention,
reservation status filtering, and user permissions belong to later milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeWindow:
    """A half-open [start, end) booking interval using aware datetimes."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("start must include a time zone")
        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("end must include a time zone")
        if self.start >= self.end:
            raise ValueError("start must be earlier than end")

    def overlaps(self, other: TimeWindow) -> bool:
        """Return True only if intervals share a non-zero amount of time."""
        return self.start < other.end and other.start < self.end
