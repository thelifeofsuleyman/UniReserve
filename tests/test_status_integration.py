"""SQLite-backed indicator behavior, independent of the Flask presentation."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile,unittest
from sqlalchemy.orm import Session
from unireserve.storage.db import make_engine, create_schema
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.models import Reservation
from unireserve.services.booking import BookingService

T0 = datetime(2026, 11, 25, 10, 0, tzinfo=timezone.utc)

class StatusDatabaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.engine=make_engine(Path(self.tmp.name)/'status.sqlite3')
        create_schema(self.engine)
        self.user=provision_demo_user(self.engine,'viewer@uni.test','secure-mock-password','STUDENT')
        self.admin=provision_demo_user(self.engine,'admin@uni.test','admin-password-demo','ADMIN')
        self.svc=BookingService(self.engine)
        self.room=self.svc.create_resource(self.admin,'R100','Quiet Study','ROOM')
        self.camera=self.svc.create_resource(self.admin,'E100','Video Camera','EQUIPMENT',requires_approval=True)

    def tearDown(self):
        self.engine.dispose();self.tmp.cleanup()

    def insert(self,resource_id,offset,duration,status='CONFIRMED'):
        with Session(self.engine) as db:
            db.add(Reservation(user_id=self.user,resource_id=resource_id,
                start_utc=(T0+timedelta(minutes=offset)).replace(tzinfo=None),
                end_utc=(T0+timedelta(minutes=offset+duration)).replace(tzinfo=None),
                status=status,created_utc=(T0-timedelta(hours=1)).replace(tzinfo=None)))
            db.commit()

    def test_pending_ignored_and_confirmed_reported(self):
        self.insert(self.camera.id,-3,30,'PENDING_APPROVAL')
        self.insert(self.room.id,14,60)
        overview=self.svc.status_overview(self.user,now=T0)
        self.assertEqual(overview[self.camera.id].state,'AVAILABLE')
        self.assertEqual(overview[self.room.id].state,'SOON')
        self.assertEqual(overview[self.room.id].next_start,T0+timedelta(minutes=14))

    def test_occupied_precedes_future_booking(self):
        self.insert(self.room.id,-2,10)
        self.insert(self.room.id,11,10)
        overview=self.svc.status_overview(self.user,now=T0)
        self.assertEqual(overview[self.room.id].state,'OCCUPIED')
        self.assertEqual(overview[self.room.id].current_end,T0+timedelta(minutes=8))
        self.assertEqual(overview[self.room.id].next_start,T0+timedelta(minutes=11))

    def test_disabled_overrides_and_no_user_data_leaks(self):
        self.insert(self.room.id,0,60)
        self.svc.update_resource(self.admin,self.room.id,is_enabled=False)
        overview=self.svc.status_overview(self.user,now=T0)
        self.assertEqual(overview[self.room.id].state,'DISABLED')
        self.assertFalse(hasattr(overview[self.room.id],'user_email'))

    def test_inactive_account_denied(self):
        from sqlalchemy import update
        from unireserve.storage.models import User
        from unireserve.services.booking import AccessDenied
        with self.engine.begin() as conn:
            conn.execute(update(User).where(User.id==self.user).values(is_active=False))
        with self.assertRaises(AccessDenied):
            self.svc.status_overview(self.user,now=T0)

if __name__=='__main__': unittest.main()
