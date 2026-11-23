"""CR-004: realistic demo room catalogue and one-time local catalogue initialization.

The room photos/layouts are illustrative, and the seed step must not alter the
old reservation/audit records or leak into isolated test databases by default.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import Resource, Reservation, Space
from unireserve.web.app import create_app


ROOT = Path(__file__).resolve().parents[1]


class RoomExperienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / 'rooms.sqlite3'
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'room-tests-only',
                               'AUTO_SAMPLE_CATALOG': True, 'DB_PATH': str(self.path)})
        self.engine = self.app.extensions['unireserve_engine']
        self.user = provision_demo_user(self.engine, 'student@demo.invalid',
                                        'example-password-1', 'STUDENT')
        self.client = self.app.test_client()
        self.client.get('/login')
        with self.client.session_transaction() as sess:
            token = sess['csrf_token']
        response = self.client.post('/login', data={'email': 'student@demo.invalid',
            'password': 'example-password-1', 'csrf_token': token})
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.engine.dispose()
        self.temp.cleanup()

    def test_first_start_creates_four_areas_and_23_units(self):
        with Session(self.engine) as db:
            self.assertEqual(len(db.scalars(select(Space)).all()), 4)
            listed = db.scalars(select(Resource).where(Resource.is_listed.is_(True))).all()
            self.assertEqual(len(listed), 23)
            self.assertEqual(len({r.public_code for r in listed}), 23)

    def test_catalogue_has_four_distinct_matching_images(self):
        page = self.client.get('/resources').get_data(as_text=True)
        for filename in ('library-seats.jpg', 'library-pcs.jpg',
                         'teaching-lab.jpg', 'group-study.jpg'):
            self.assertIn(filename, page)
            image = ROOT / 'src' / 'unireserve' / 'web' / 'static' / filename
            self.assertTrue(image.is_file(), filename)
            self.assertGreater(image.stat().st_size, 5000, filename)
        self.assertIn('Reading Seat 01', page)
        self.assertIn('Library PC 01', page)
        self.assertNotIn('Sony Mirrorless Camera', page)
        self.assertIn('campus-zone-card', page)
        self.assertIn('campus-unit', page)
        self.assertNotIn('resource-grid editorial-grid', page)

    def test_each_room_has_its_own_logical_seat_count_and_layout(self):
        page = self.client.get('/studio').get_data(as_text=True)
        self.assertIn('EXAMPLE LAYOUT', page)
        self.assertIn('NOT TO SCALE', page)
        self.assertIn('ACCESS AISLE', page)
        self.assertIn('TEACHING SCREEN', page)
        self.assertIn('6 PERSON TABLE', page)
        for name, count in (('Reading Seat', 8), ('Library PC', 6),
                            ('Lab Workstation', 8), ('Group Study Room', 1)):
            self.assertEqual(page.count(f'class="pin-name">{name}'), count, name)
        self.assertEqual(page.count('class="room-plan room-plan--'), 4)
        self.assertEqual(page.count('class="room-plan__bank"'), 6)

    def test_zone_links_open_scoped_map(self):
        index = self.client.get('/resources').get_data(as_text=True)
        self.assertIn('/studio?area=', index)
        area_page = self.client.get('/studio?area=1')
        self.assertEqual(area_page.status_code, 200)
        self.assertIn(b'data-zone-id="1"', area_page.data)
        js = (ROOT / 'src/unireserve/web/static/studio.js').read_text('utf-8')
        self.assertIn("new URLSearchParams", js)
        self.assertIn("requestedZone", js)

    def test_seed_is_idempotent_and_does_not_replace_admin_edits(self):
        with Session(self.engine) as db:
            first = db.scalar(select(Space).where(Space.public_code == 'LIB-READ'))
            first.name = 'Library Reading Area (renamed by admin)'
            db.commit()
        second_app = create_app({'TESTING': True, 'SECRET_KEY': 'second-start',
            'AUTO_SAMPLE_CATALOG': True, 'DB_PATH': str(self.path)})
        try:
            with Session(second_app.extensions['unireserve_engine']) as db:
                spaces = db.scalars(select(Space)).all()
                self.assertEqual(len(spaces), 4)
                self.assertEqual(next(s.name for s in spaces if s.public_code == 'LIB-READ'),
                                 'Library Reading Area (renamed by admin)')
                self.assertEqual(len(db.scalars(select(Resource)).all()), 23)
        finally:
            second_app.extensions['unireserve_engine'].dispose()

    def test_isolated_test_app_has_no_auto_catalogue_unless_opted_in(self):
        other = Path(self.temp.name) / 'empty.sqlite3'
        app = create_app({'TESTING': True, 'SECRET_KEY': 'isolated', 'DB_PATH': str(other)})
        try:
            with Session(app.extensions['unireserve_engine']) as db:
                self.assertEqual(len(db.scalars(select(Space)).all()), 0)
        finally:
            app.extensions['unireserve_engine'].dispose()


class LegacyHistoryTests(unittest.TestCase):
    def test_auto_migration_archives_known_demo_gear_but_preserves_booking(self):
        with TemporaryDirectory() as folder:
            file = Path(folder) / 'legacy.sqlite3'
            engine = make_engine(file)
            create_schema(engine)
            user_id = provision_demo_user(engine, 'legacy@demo.invalid',
                                          'password-legacy-demo', 'STUDENT')
            with Session(engine) as db:
                old = Resource(public_code='EQ-CAM-01', name='Old Starter Camera',
                               category='EQUIPMENT', requires_approval=False,
                               is_enabled=True, is_listed=True)
                db.add(old)
                db.flush()
                old_id = old.id
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                old_booking = Reservation(user_id=user_id, resource_id=old_id,
                    start_utc=now+timedelta(days=2),end_utc=now+timedelta(days=2,hours=1),
                    status='CONFIRMED',created_utc=now)
                db.add(old_booking)
                db.commit()
                booking_id = old_booking.id
            engine.dispose()
            app = create_app({'TESTING': True, 'SECRET_KEY': 'migrate',
                              'AUTO_SAMPLE_CATALOG': True, 'DB_PATH': str(file)})
            try:
                with Session(app.extensions['unireserve_engine']) as db:
                    old = db.get(Resource, old_id)
                    record = db.get(Reservation, booking_id)
                    self.assertFalse(old.is_listed)
                    self.assertFalse(old.is_enabled)
                    self.assertEqual(record.resource_id, old_id)
                    self.assertEqual(record.status, 'CONFIRMED')
                    self.assertEqual(len(db.scalars(select(Space)).all()), 4)
            finally:
                app.extensions['unireserve_engine'].dispose()


if __name__ == '__main__':
    unittest.main()
