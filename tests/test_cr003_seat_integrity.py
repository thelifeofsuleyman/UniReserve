"""CR-003 regression: one concurrent confirmed study space per user; safe resource edits."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from unireserve.domain.availability import TimeWindow
from unireserve.domain.operating_hours import BAKU
from unireserve.services.booking import BookingService, Conflict
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.aztu_demo import sync_demo_catalog
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import Reservation, ReservationEvent, Space

NOW = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)


def window(start=10, end=11):
    day = datetime(2026, 11, 24, tzinfo=BAKU)
    return TimeWindow(day + timedelta(hours=start), day + timedelta(hours=end))


class StudyPlaceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.engine = make_engine(Path(self.tmp.name) / "cr003.sqlite3")
        create_schema(self.engine)
        sync_demo_catalog(self.engine)
        self.student = provision_demo_user(self.engine, "student@invalid.test", "password-0001", "STUDENT")
        self.other = provision_demo_user(self.engine, "other@invalid.test", "password-0002", "STUDENT")
        self.admin = provision_demo_user(self.engine, "admin@invalid.test", "password-0003", "ADMIN")
        self.svc = BookingService(self.engine, clock=lambda: NOW)
        self.units = {r.public_code: r for r in self.svc.list_resources(self.student)}
        self.areas = {s.public_code: s for s in self.svc.list_spaces(self.student)}

    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()

    def test_student_cannot_book_two_simultaneous_library_pcs(self):
        one, two = self.units["AZ-LP-01"], self.units["AZ-LP-02"]
        first = self.svc.request(self.student, one.id, window(), now=NOW)
        self.assertFalse(self.svc.available(self.student, two.id, window()))
        with self.assertRaisesRegex(Conflict, "already have"):
            self.svc.request(self.student, two.id, window(), now=NOW)
        self.assertEqual(self.svc.get_own(self.student, first.id).status, "CONFIRMED")
        with Session(self.engine) as session:
            self.assertEqual(len(session.scalars(select(Reservation)).all()), 1)
            self.assertEqual(len(session.scalars(select(ReservationEvent)).all()), 1)

    def test_distinct_students_can_use_distinct_pcs_at_same_time(self):
        first, second = self.units["AZ-LP-01"], self.units["AZ-LP-02"]
        self.svc.request(self.student, first.id, window(), now=NOW)
        self.assertTrue(self.svc.available(self.other, second.id, window()))
        self.assertEqual(self.svc.request(self.other, second.id, window(), now=NOW).status, "CONFIRMED")

    def test_adjacent_own_bookings_are_valid(self):
        first, second = self.units["AZ-LS-01"], self.units["AZ-LP-01"]
        self.svc.request(self.student, first.id, window(10, 11), now=NOW)
        self.assertEqual(self.svc.request(self.student, second.id, window(11, 12), now=NOW).status, "CONFIRMED")

    def test_pending_request_does_not_hold_capacity_but_approval_rechecks(self):
        pending = self.svc.request(self.student, self.units["AZ-CP-01"].id, window(), now=NOW)
        self.assertEqual(pending.status, "PENDING_APPROVAL")
        confirmed = self.svc.request(self.student, self.units["AZ-LP-01"].id, window(), now=NOW)
        self.assertEqual(confirmed.status, "CONFIRMED")
        with self.assertRaisesRegex(Conflict, "requester already has"):
            self.svc.decide(self.admin, pending.id, approve=True, now=NOW)
        self.assertEqual(self.svc.get_own(self.student, pending.id).status, "PENDING_APPROVAL")
        self.assertEqual(len(self.svc.events(self.student, pending.id)), 1)

    def test_cannot_move_confirmed_booking_into_areas_closed_hours(self):
        resource = self.units["AZ-LS-01"]
        original = self.svc.request(self.student, resource.id, window(9, 10), now=NOW)
        with Session(self.engine) as session:
            new_area = Space(
                public_code="AFTERNOON-DEMO", name="PM-only demo area", kind="LIBRARY_SEAT",
                opens_at="12:00", closes_at="17:30", open_days=31,
                policy_note="Testing only", is_enabled=True,
            )
            session.add(new_area)
            session.commit()
            new_id = new_area.id
        with self.assertRaisesRegex(Conflict, "incompatible"):
            self.svc.update_resource(self.admin, resource.id, space_id=new_id)
        self.assertEqual(self.svc.get_resource(self.student, resource.id).space_id, self.areas["LIB-READ"].id)
        self.assertEqual(self.svc.get_own(self.student, original.id).status, "CONFIRMED")

    def test_category_change_does_not_shorten_confirmed_legacy_booking(self):
        item = self.svc.create_resource(self.admin, "EXTRA-LONG", "Legacy item", "EQUIPMENT")
        first = self.svc.request(self.student, item.id, window(10, 13), now=NOW)
        with self.assertRaisesRegex(Conflict, "maximum duration"):
            self.svc.update_resource(self.admin, item.id, category="ROOM")
        self.assertEqual(self.svc.get_resource(self.admin, item.id).category, "EQUIPMENT")
        self.assertEqual(self.svc.get_own(self.student, first.id).status, "CONFIRMED")

    def test_static_image_assets_are_local(self):
        css = (Path(__file__).resolve().parents[1] / "src/unireserve/web/static/refined.css").read_text("utf-8")
        self.assertIn("resource-editorial.jpg", css)
        self.assertNotIn("images.report.az", css)
        self.assertNotIn("web_admin/upload/files", css)


if __name__ == "__main__":
    unittest.main()
