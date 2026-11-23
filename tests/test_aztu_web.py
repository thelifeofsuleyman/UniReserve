"""HTTP-level checks for the new site map, hour rules, and staff closures."""
from datetime import datetime,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo
from unireserve.web.app import create_app
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.aztu_demo import sync_demo_catalog
from unireserve.services.booking import BookingService

class AzTUWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.app=create_app({'TESTING':True,'SECRET_KEY':'web-demo-test',
                             'DB_PATH':str(Path(self.tmp.name)/'aztu.db')})
        self.engine=self.app.extensions['unireserve_engine']
        sync_demo_catalog(self.engine)
        self.student=provision_demo_user(self.engine,'u@test.invalid','pass-for-demo','STUDENT')
        self.admin=provision_demo_user(self.engine,'admin@test.invalid','admin-demo-pass','ADMIN')
        self.svc=BookingService(self.engine)
        self.client=self.app.test_client()
    def tearDown(self):
        self.engine.dispose();self.tmp.cleanup()
    def signin(self,email='u@test.invalid',password='pass-for-demo'):
        self.client.get('/login')
        with self.client.session_transaction() as s:token=s['csrf_token']
        return self.client.post('/login',data={'csrf_token':token,'email':email,'password':password})
    def form(self,**kwargs):
        with self.client.session_transaction() as s:token=s['csrf_token']
        return {'csrf_token':token,**kwargs}
    def test_studio_lists_zone_seats_and_not_camera_gear(self):
        self.signin()
        page=self.client.get('/studio')
        self.assertEqual(page.status_code,200)
        self.assertIn(b'Reading Seat 01',page.data)
        self.assertIn(b'Library PC 01',page.data)
        self.assertIn(b'Lab Workstation 01',page.data)
        self.assertNotIn(b'Sony Mirrorless Camera',page.data)
        self.assertIn(b'ROOM LAYOUT',page.data)
    def test_library_category_filter(self):
        self.signin()
        page=self.client.get('/resources?category=SEAT')
        self.assertIn(b'Reading Seat 01',page.data)
        self.assertNotIn(b'Library PC 01',page.data)
        self.assertNotIn(b'Lab Workstation 01',page.data)
    def test_invalid_weekend_booking_rejected_via_web(self):
        self.signin()
        seat=next(x for x in self.svc.list_resources(self.student) if x.public_code=='AZ-LS-01')
        zone=ZoneInfo('Asia/Baku')
        now=datetime.now(zone)
        day=now.date()+timedelta(days=1)
        while day.weekday()!=5:day+=timedelta(days=1)
        form={'start':f'{day}T10:00','end':f'{day}T11:00'}
        res=self.client.post(f'/resources/{seat.id}/book',data=self.form(**form),follow_redirects=True)
        self.assertIn(b'closed day',res.data)
    def test_studio_api_can_report_closed(self):
        self.signin()
        response=self.client.get('/api/availability-status')
        self.assertEqual(response.status_code,200)
        self.assertIn('resources',response.get_json())
    def test_admin_can_create_a_closure_with_csrf(self):
        self.signin('admin@test.invalid','admin-demo-pass')
        area=next(x for x in self.svc.list_spaces(self.admin) if x.public_code=='LAB-PC')
        zone=ZoneInfo('Asia/Baku')
        day=datetime.now(zone).date()+timedelta(days=1)
        while day.weekday()>=5:day+=timedelta(days=1)
        res=self.client.post(f'/admin/spaces/{area.id}/closures',data=self.form(start=f'{day}T11:00',end=f'{day}T12:00',reason='Demo teaching session'),follow_redirects=True)
        self.assertEqual(res.status_code,200)
        self.assertIn(b'closure saved',res.data)
    def test_student_cannot_create_closure(self):
        self.signin()
        self.assertEqual(self.client.post('/admin/spaces/1/closures',data=self.form(start='2026-11-24T10:00',end='2026-11-24T11:00',reason='hack')).status_code,403)
