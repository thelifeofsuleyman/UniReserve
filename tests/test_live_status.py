"""State transitions and boundary values for CR-001 2D availability map."""
from datetime import datetime, timedelta, timezone
import unittest

from unireserve.domain.live_status import ConfirmedInterval, current_status


BASE = datetime(2026, 11, 25, 10, 0, tzinfo=timezone.utc)


def slot(minutes: int, duration: int = 30):
    return ConfirmedInterval(BASE + timedelta(minutes=minutes),
                             BASE + timedelta(minutes=minutes + duration))


class AvailabilityIndicatorTests(unittest.TestCase):
    def test_green_with_no_confirmed_bookings(self):
        self.assertEqual(current_status(True, [], BASE).state, "AVAILABLE")

    def test_green_when_more_than_fifteen_minutes_out(self):
        self.assertEqual(current_status(True, [slot(16)], BASE).state, "AVAILABLE")

    def test_yellow_when_exactly_fifteen_minutes_out(self):
        status = current_status(True, [slot(15)], BASE)
        self.assertEqual(status.state, "SOON")
        self.assertEqual(status.next_start, BASE + timedelta(minutes=15))

    def test_yellow_when_one_second_before_booking(self):
        self.assertEqual(current_status(True, [slot(0)], BASE-timedelta(seconds=1)).state, "SOON")

    def test_red_when_booking_starts_now(self):
        status = current_status(True, [slot(0)], BASE)
        self.assertEqual(status.state, "OCCUPIED")
        self.assertEqual(status.current_end, BASE + timedelta(minutes=30))

    def test_green_when_booking_ends_now(self):
        self.assertEqual(current_status(True, [slot(-30)], BASE).state, "AVAILABLE")

    def test_red_takes_precedence_over_upcoming_yellow(self):
        self.assertEqual(current_status(True, [slot(-10), slot(5)], BASE).state, "OCCUPIED")

    def test_gray_overrides_current_occupancy(self):
        self.assertEqual(current_status(False, [slot(-10)], BASE).state, "DISABLED")

    def test_order_of_intervals_does_not_change_next_start(self):
        status = current_status(True, [slot(60), slot(10), slot(20)], BASE)
        self.assertEqual(status.state, "SOON")
        self.assertEqual(status.next_start, BASE + timedelta(minutes=10))

    def test_naive_now_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            current_status(True, [], BASE.replace(tzinfo=None))

    def test_naive_booking_is_rejected(self):
        broken = ConfirmedInterval(BASE.replace(tzinfo=None), BASE+timedelta(hours=1))
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            current_status(True, [broken], BASE)


if __name__ == "__main__":
    unittest.main()
