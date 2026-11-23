"""Integration tests against a real on-disk SQLite database.

Trace: FR-002..011 / NFR-002, NFR-003, NFR-005; ADR-0002.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier
from tempfile import TemporaryDirectory
import sqlite3
import unittest
from unittest.mock import patch

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from unireserve.domain.availability import TimeWindow
from unireserve.services.booking import (
    AccessDenied, BookingService, Conflict, InvalidRequest, MissingRecord,
)
from unireserve.storage.db import create_schema, make_engine, write_transaction
from unireserve.storage.accounts import hash_password
from unireserve.storage.models import Reservation, ReservationEvent, Resource, User


NOW = datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
DEMO_HASH = hash_password("test-fixture-passphrase-2026")
WINDOW = TimeWindow(NOW + timedelta(days=1), NOW + timedelta(days=1, hours=1))


class BookingIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.path = Path(self.tmp.name) / "unireserve.sqlite"
        self.engine = make_engine(self.path)
        create_schema(self.engine)
        with write_transaction(self.engine) as s:
            s.add_all([
                User(id=1, email="student1@example.invalid", password_hash=DEMO_HASH, role="STUDENT", is_active=True),
                User(id=2, email="student2@example.invalid", password_hash=DEMO_HASH, role="STUDENT", is_active=True),
                User(id=3, email="admin@example.invalid", password_hash=DEMO_HASH, role="ADMIN", is_active=True),
                User(id=4, email="staff@example.invalid", password_hash=DEMO_HASH, role="STAFF", is_active=True),
                User(id=5, email="disabled@example.invalid", password_hash=DEMO_HASH, role="STUDENT", is_active=False),
                Resource(id=1, public_code="ROOM-A", name="Study Room A", category="ROOM", requires_approval=False, is_enabled=True),
                Resource(id=2, public_code="CAM-1", name="Camera 1", category="EQUIPMENT", requires_approval=True, is_enabled=True),
                Resource(id=3, public_code="ROOM-B", name="Room B", category="ROOM", requires_approval=False, is_enabled=False),
            ])
        self.svc = BookingService(self.engine, clock=lambda: NOW)

    def tearDown(self) -> None:
        self.engine.dispose()
        self.tmp.cleanup()

    def _counts(self):
        with Session(self.engine) as s:
            return (s.scalar(select(func.count(Reservation.id))),
                    s.scalar(select(func.count(ReservationEvent.id))))

    def test_confirm_standard_booking_and_atomic_event(self):
        record = self.svc.request(1, 1, WINDOW, now=NOW)
        self.assertEqual(record.status, "CONFIRMED")
        self.assertEqual(record.start_utc, WINDOW.start)
        self.assertEqual(self._counts(), (1, 1))
        self.assertEqual(self.svc.events(1, record.id), [("CREATED", None, "CONFIRMED")])
        self.assertFalse(self.svc.available(2, 1, WINDOW))

    def test_pending_request_does_not_hold_capacity(self):
        first = self.svc.request(1, 2, WINDOW, now=NOW)
        second = self.svc.request(2, 2, WINDOW, now=NOW)
        self.assertEqual((first.status, second.status), ("PENDING_APPROVAL", "PENDING_APPROVAL"))
        self.assertTrue(self.svc.available(4, 2, WINDOW))
        self.assertEqual(self._counts(), (2, 2))

    def test_approval_conflict_leaves_request_pending_and_no_event(self):
        first = self.svc.request(1, 2, WINDOW, now=NOW)
        second = self.svc.request(2, 2, WINDOW, now=NOW)
        self.assertEqual(self.svc.decide(3, first.id, approve=True, now=NOW).status, "CONFIRMED")
        with self.assertRaises(Conflict):
            self.svc.decide(3, second.id, approve=True, now=NOW)
        self.assertEqual(self.svc.get_own(2, second.id).status, "PENDING_APPROVAL")
        self.assertEqual(self._counts(), (2, 3))
        self.assertEqual(len(self.svc.events(3, second.id)), 1)

    def test_admin_rejection_is_terminal(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        rejected = self.svc.decide(3, pending.id, approve=False, now=NOW)
        self.assertEqual(rejected.status, "REJECTED")
        self.assertEqual(self.svc.events(1, pending.id)[-1], ("REJECTED", "PENDING_APPROVAL", "REJECTED"))
        with self.assertRaises(InvalidRequest):
            self.svc.decide(3, pending.id, approve=True, now=NOW)

    def test_adjacent_allowed_and_partial_overlap_rejected(self):
        self.svc.request(1, 1, WINDOW, now=NOW)
        after = TimeWindow(WINDOW.end, WINDOW.end + timedelta(minutes=30))
        self.assertEqual(self.svc.request(2, 1, after, now=NOW).status, "CONFIRMED")
        overlap = TimeWindow(WINDOW.start + timedelta(minutes=10), WINDOW.end + timedelta(minutes=10))
        with self.assertRaises(Conflict):
            self.svc.request(2, 1, overlap, now=NOW)
        self.assertEqual(self._counts(), (2, 2))

    def test_cancel_releases_capacity_and_tracks_event(self):
        booking = self.svc.request(1, 1, WINDOW, now=NOW)
        self.assertEqual(self.svc.cancel(1, booking.id, now=NOW).status, "CANCELLED")
        self.assertEqual(self.svc.events(1, booking.id)[-1], ("CANCELLED", "CONFIRMED", "CANCELLED"))
        self.assertEqual(self.svc.request(2, 1, WINDOW, now=NOW).status, "CONFIRMED")
        with self.assertRaises(InvalidRequest):
            self.svc.cancel(1, booking.id, now=NOW)

    def test_cancellation_at_start_fails(self):
        booking = self.svc.request(1, 1, WINDOW, now=NOW)
        with self.assertRaises(InvalidRequest):
            self.svc.cancel(1, booking.id, now=WINDOW.start)
        self.assertEqual(self._counts(), (1, 1))

    def test_cannot_cancel_another_users_booking(self):
        booking = self.svc.request(1, 1, WINDOW, now=NOW)
        with self.assertRaises(MissingRecord):
            self.svc.cancel(2, booking.id, now=NOW)
        with self.assertRaises(MissingRecord):
            self.svc.get_own(2, booking.id)
        with self.assertRaises(MissingRecord):
            self.svc.events(2, booking.id)
        self.assertEqual(self._counts(), (1, 1))

    def test_only_admin_may_approve_or_edit_resources(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        with self.assertRaises(AccessDenied):
            self.svc.decide(2, pending.id, approve=True, now=NOW)
        with self.assertRaises(AccessDenied):
            self.svc.create_resource(1, "LAB-4", "Lab 4", "ROOM")
        with self.assertRaises(AccessDenied):
            self.svc.update_resource(1, 1, is_enabled=False)
        self.assertEqual(self._counts(), (1, 1))

    def test_admin_cannot_request_student_booking(self):
        with self.assertRaises(AccessDenied):
            self.svc.request(3, 1, WINDOW, now=NOW)
        with self.assertRaises(AccessDenied):
            self.svc.request(5, 1, WINDOW, now=NOW)
        self.assertEqual(self._counts(), (0, 0))

    def test_resource_disabled_and_history_preserved(self):
        record = self.svc.request(1, 1, WINDOW, now=NOW)
        new = self.svc.update_resource(3, 1, is_enabled=False)
        self.assertFalse(new.is_enabled)
        self.assertFalse(self.svc.available(2, 1, WINDOW))
        with self.assertRaises(InvalidRequest):
            self.svc.request(2, 1, WINDOW, now=NOW)
        self.assertEqual(self.svc.get_own(1, record.id).status, "CONFIRMED")
        self.assertEqual(self._counts(), (1, 1))

    def test_resource_edit_and_duplicate_code(self):
        r = self.svc.create_resource(3, "LAB-2", "Lab 2", "ROOM", requires_approval=True)
        self.assertEqual(r.public_code, "LAB-2")
        updated = self.svc.update_resource(3, r.id, name="Electronics Lab", category="EQUIPMENT")
        self.assertEqual((updated.name, updated.category), ("Electronics Lab", "EQUIPMENT"))
        with self.assertRaises(InvalidRequest):
            self.svc.create_resource(3, "LAB-2", "Duplicate", "ROOM")
        self.assertTrue(any(v.public_code == "LAB-2" for v in self.svc.list_resources(1)))

    def test_invalid_booking_window_and_policy_limits(self):
        cases = [
            TimeWindow(NOW - timedelta(hours=1), NOW + timedelta(minutes=30)),
            TimeWindow(NOW + timedelta(days=15), NOW + timedelta(days=15, hours=1)),
            TimeWindow(WINDOW.start, WINDOW.start + timedelta(hours=2, seconds=1)),
        ]
        for window in cases:
            with self.subTest(window=window), self.assertRaises(InvalidRequest):
                self.svc.request(1, 1, window, now=NOW)
        self.assertEqual(self._counts(), (0, 0))

    def test_duration_limits_accept_exact_boundary(self):
        room = TimeWindow(WINDOW.start, WINDOW.start + timedelta(hours=2))
        equipment = TimeWindow(WINDOW.start, WINDOW.start + timedelta(hours=24))
        self.assertEqual(self.svc.request(1, 1, room, now=NOW).status, "CONFIRMED")
        self.assertEqual(self.svc.request(2, 2, equipment, now=NOW).status, "PENDING_APPROVAL")

    def test_approval_after_start_refused(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        with self.assertRaises(InvalidRequest):
            self.svc.decide(3, pending.id, approve=True, now=WINDOW.start)
        self.assertEqual(self._counts(), (1, 1))

    def test_write_failure_rolls_back_booking_and_audit(self):
        with patch.object(self.svc, "_event", side_effect=RuntimeError("audit insert failed")):
            with self.assertRaises(RuntimeError):
                self.svc.request(1, 1, WINDOW, now=NOW)
        self.assertEqual(self._counts(), (0, 0))

    def test_write_failure_rolls_back_state_change(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        with patch.object(self.svc, "_event", side_effect=RuntimeError("audit insert failed")):
            with self.assertRaises(RuntimeError):
                self.svc.decide(3, pending.id, approve=True, now=NOW)
        self.assertEqual(self.svc.get_own(1, pending.id).status, "PENDING_APPROVAL")
        self.assertEqual(self._counts(), (1, 1))

    def test_audit_events_cannot_be_edited_or_deleted_directly(self):
        booking = self.svc.request(1, 1, WINDOW, now=NOW)
        with sqlite3.connect(self.path) as db:
            event_id = db.execute(
                "SELECT id FROM reservation_events WHERE reservation_id=?", (booking.id,)
            ).fetchone()[0]
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE reservation_events SET action='HACKED' WHERE id=?", (event_id,))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM reservation_events WHERE id=?", (event_id,))
        self.assertEqual(self.svc.events(1, booking.id), [("CREATED", None, "CONFIRMED")])

    def test_database_foreign_key_and_checks(self):
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO reservations (user_id,resource_id,start_utc,end_utc,status,created_utc) VALUES (999,1,'2026-11-24 10:00:00','2026-11-24 11:00:00','CONFIRMED','2026-11-23 09:00:00')")
            connection.rollback()
        finally:
            connection.close()

    def test_persistence_across_engine_restart(self):
        first = self.svc.request(1, 1, WINDOW, now=NOW)
        self.engine.dispose()
        fresh = make_engine(self.path)
        try:
            other = BookingService(fresh, clock=lambda: NOW)
            self.assertEqual(other.get_own(1, first.id).status, "CONFIRMED")
            self.assertEqual(len(other.events(1, first.id)), 1)
        finally:
            fresh.dispose()

    def test_20_bookings_survive_restart_with_audit(self):
        ids = []
        for i in range(20):
            start = WINDOW.start + timedelta(hours=2 * i)
            booking = self.svc.request(1, 1, TimeWindow(start, start + timedelta(hours=1)), now=NOW)
            ids.append(booking.id)
        self.assertEqual(self._counts(), (20, 20))
        self.engine.dispose()
        new_engine = make_engine(self.path)
        try:
            other = BookingService(new_engine, clock=lambda: NOW)
            own = other.list_own(1)
            self.assertEqual([r.id for r in own], ids)
            self.assertEqual(len(own), 20)
            self.assertEqual(sum(len(other.events(1, booking_id)) for booking_id in ids), 20)
        finally:
            new_engine.dispose()

    def test_disabling_resource_blocks_approval_without_erasing_request(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        self.svc.update_resource(3, 2, is_enabled=False)
        with self.assertRaises(InvalidRequest):
            self.svc.decide(3, pending.id, approve=True, now=NOW)
        self.assertEqual(self.svc.get_own(1, pending.id).status, "PENDING_APPROVAL")
        self.assertEqual(self._counts(), (1, 1))

    def test_concurrent_approval_and_booking_never_both_confirm(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        self.svc.update_resource(3, 2, requires_approval=False)
        start_gate = Barrier(2)
        def approve():
            start_gate.wait(timeout=8)
            return self.svc.decide(3, pending.id, approve=True, now=NOW)
        def request():
            start_gate.wait(timeout=8)
            return self.svc.request(2, 2, WINDOW, now=NOW)
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(approve), pool.submit(request)]
            results = []
            for job in jobs:
                try:
                    results.append(job.result())
                except Conflict:
                    results.append("conflict")
        self.assertEqual(sum(r == "conflict" for r in results), 1)
        with Session(self.engine) as session:
            records = session.scalars(select(Reservation).where(
                Reservation.resource_id == 2, Reservation.status == "CONFIRMED"
            )).all()
            self.assertEqual(len(records), 1)

    def test_pending_owner_cancellation_and_staff_request(self):
        pending = self.svc.request(1, 2, WINDOW, now=NOW)
        self.assertEqual(self.svc.cancel(1, pending.id, now=NOW).status, "CANCELLED")
        staff = self.svc.request(4, 1, WINDOW, now=NOW)
        self.assertEqual(staff.status, "CONFIRMED")

    def test_50_two_client_races_never_double_confirm(self):
        for trial in range(50):
            resource = self.svc.create_resource(3, f"RACE-{trial}", f"Race room {trial}", "ROOM")
            start_gate = Barrier(2)
            def synchronized_request(uid):
                start_gate.wait(timeout=8)
                return self.svc.request(uid, resource.id, WINDOW, now=NOW)
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(synchronized_request, uid) for uid in (1, 2)]
                outcomes = []
                for future in futures:
                    try:
                        outcomes.append(future.result())
                    except Conflict:
                        outcomes.append("conflict")
            self.assertEqual(sum(isinstance(x, str) for x in outcomes), 1, f"trial {trial}")
            with Session(self.engine) as session:
                rows = session.scalars(select(Reservation).where(
                    Reservation.resource_id == resource.id, Reservation.status == "CONFIRMED"
                )).all()
                self.assertEqual(len(rows), 1, f"trial {trial}")


if __name__ == "__main__":
    unittest.main()
