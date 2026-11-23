"""Starter boundary-value tests for requirement FR-003."""

from datetime import datetime, timedelta, timezone
import unittest

from unireserve.domain.availability import TimeWindow


T0 = datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc)


class TimeWindowTests(unittest.TestCase):
    def test_partial_overlap_is_rejected(self) -> None:
        existing = TimeWindow(T0, T0 + timedelta(hours=2))
        incoming = TimeWindow(T0 + timedelta(hours=1), T0 + timedelta(hours=3))
        self.assertTrue(existing.overlaps(incoming))
        self.assertTrue(incoming.overlaps(existing))

    def test_adjacent_windows_do_not_overlap(self) -> None:
        earlier = TimeWindow(T0, T0 + timedelta(hours=2))
        later = TimeWindow(T0 + timedelta(hours=2), T0 + timedelta(hours=3))
        self.assertFalse(earlier.overlaps(later))
        self.assertFalse(later.overlaps(earlier))

    def test_identical_windows_overlap(self) -> None:
        first = TimeWindow(T0, T0 + timedelta(minutes=30))
        self.assertTrue(first.overlaps(first))

    def test_disjoint_windows_do_not_overlap(self) -> None:
        first = TimeWindow(T0, T0 + timedelta(minutes=30))
        later = TimeWindow(T0 + timedelta(hours=1), T0 + timedelta(hours=2))
        self.assertFalse(first.overlaps(later))

    def test_zero_length_interval_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "start must be earlier"):
            TimeWindow(T0, T0)

    def test_reversed_interval_fails(self) -> None:
        with self.assertRaises(ValueError):
            TimeWindow(T0 + timedelta(hours=1), T0)

    def test_naive_datetime_fails(self) -> None:
        naive = datetime(2026, 11, 24, 10, 0)
        with self.assertRaisesRegex(ValueError, "time zone"):
            TimeWindow(naive, T0 + timedelta(hours=1))

    def test_equivalent_utc_offsets_work(self) -> None:
        utc_plus_four = timezone(timedelta(hours=4))
        first = TimeWindow(T0, T0 + timedelta(hours=1))
        local_start = (T0 + timedelta(minutes=30)).astimezone(utc_plus_four)
        second = TimeWindow(local_start, local_start + timedelta(minutes=30))
        self.assertTrue(first.overlaps(second))


if __name__ == "__main__":
    unittest.main()
