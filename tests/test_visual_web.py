"""CR-001: HTTP contract and visual availability labels are testable."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from sqlalchemy.orm import Session

from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.models import Reservation
from unireserve.services.booking import BookingService
from unireserve.web.app import create_app


class VisualStudioIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-only-visual-key", "DB_PATH": str(Path(self.tmp.name) / "visual.sqlite3")})
        self.engine = self.app.extensions["unireserve_engine"]
        self.student = provision_demo_user(self.engine, "student@unireserve.test", "password-not-for-real", "STUDENT")
        self.admin = provision_demo_user(self.engine, "admin@unireserve.test", "password-not-for-real", "ADMIN")
        self.svc = BookingService(self.engine)
        self.camera = self.svc.create_resource(self.admin,"EQ-CAM-02","Cinema Camera", "EQUIPMENT", requires_approval=True)
        self.room = self.svc.create_resource(self.admin,"ROOM-01","North Study Room","ROOM")
        self.client = self.app.test_client()

    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()

    def login(self):
        self.client.get('/login')
        with self.client.session_transaction() as s:
            csrf = s['csrf_token']
        return self.client.post('/login',data={"email":"student@unireserve.test","password":"password-not-for-real","csrf_token":csrf})

    def test_studio_requires_authentication(self):
        self.assertIn('/login',self.client.get('/studio').location)
        self.assertIn('/login',self.client.get('/api/availability-status').location)

    def test_studio_renders_equipment_rooms_and_survey_warning(self):
        self.login()
        page=self.client.get('/studio')
        self.assertEqual(page.status_code,200)
        self.assertIn(b'No rooms available',page.data)
        self.assertIn(b'2D',page.data)
        self.assertIn(b'No rooms available',page.data)
        self.assertIn(b'Starts within 15 min',page.data)

    def test_status_endpoint_is_private_and_not_cached(self):
        self.login()
        response=self.client.get('/api/availability-status')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        data=response.get_json()
        self.assertEqual(data['resources'][str(self.camera.id)]['state'], 'AVAILABLE')
        self.assertNotIn('user_email',response.get_data(as_text=True))
        self.assertNotIn('student@unireserve.test',response.get_data(as_text=True))

    def test_pending_request_does_not_change_current_status(self):
        from unireserve.domain.availability import TimeWindow
        now=datetime.now(timezone.utc)
        self.svc.request(self.student,self.camera.id,TimeWindow(now+timedelta(minutes=10),now+timedelta(minutes=30)))
        self.login()
        payload=self.client.get('/api/availability-status').get_json()
        self.assertEqual(payload['resources'][str(self.camera.id)]['state'],'AVAILABLE')

    def test_current_reservation_produces_occupied(self):
        now=datetime.now(timezone.utc).replace(tzinfo=None)
        with Session(self.engine) as db:
            db.add(Reservation(user_id=self.student,resource_id=self.room.id,
              start_utc=now-timedelta(minutes=5),end_utc=now+timedelta(minutes=40),
              status='CONFIRMED', created_utc=now-timedelta(hours=1)))
            db.commit()
        self.login()
        self.assertEqual(self.client.get('/api/availability-status').get_json()['resources'][str(self.room.id)]['state'],'OCCUPIED')
        self.assertIn(b'Booked now',self.client.get('/resources').data)

    def test_disabled_takes_priority_over_reservations(self):
        self.svc.update_resource(self.admin,self.room.id,is_enabled=False)
        self.login()
        payload=self.client.get('/api/availability-status').get_json()
        self.assertEqual(payload['resources'][str(self.room.id)]['state'],'DISABLED')
        self.assertIn(b'Unavailable',self.client.get('/resources').data)

    def test_resources_are_linked_from_map_to_booking_page(self):
        self.login()
        response=self.client.get('/studio')
        self.assertIn(b'No rooms available',response.data)
        self.assertNotIn(b'Cinema Camera',response.data)
        page=self.client.get(f'/resources/{self.camera.id}')
        self.assertIn(b'Seat map',page.data)
        self.assertIn(b'datetime-local',page.data)

if __name__=='__main__':
    unittest.main()
