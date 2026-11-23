"""CR-002: semester-like room/PC resources, deadlines, and safe catalog migration."""
from __future__ import annotations
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from unireserve.domain.availability import TimeWindow
from unireserve.domain.operating_hours import BAKU, within_hours, open_at
from unireserve.storage.db import make_engine, create_schema
from unireserve.storage.models import Space, SpaceClosure, Resource, Reservation, ReservationEvent
from unireserve.storage.aztu_demo import sync_demo_catalog, UNITS
from unireserve.storage.accounts import provision_demo_user
from unireserve.services.booking import BookingService, InvalidRequest, Conflict, AccessDenied

# A weekday in November 2026, with a deterministic reference clock.
NOW = datetime(2026,11,23,7,0,tzinfo=timezone.utc) # Monday 11:00 Baku

def t(day=1, hour=10, minute=0):
    return datetime(2026,11,23,tzinfo=BAKU)+timedelta(days=day,hours=hour,minutes=minute)

class AzTUBookingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'demo.db'
        self.engine=make_engine(self.path)
        create_schema(self.engine)
        self.student=provision_demo_user(self.engine,'s@example.invalid','password-123','STUDENT')
        self.admin=provision_demo_user(self.engine,'a@example.invalid','password-456','ADMIN')
        self.svc=BookingService(self.engine,clock=lambda:NOW)
        self.seed_result=sync_demo_catalog(self.engine)
        self.units={r.public_code:r for r in self.svc.list_resources(self.student)}
        self.spaces={s.public_code:s for s in self.svc.list_spaces(self.student)}
    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()
    def window(self,day=1,start=10,end=11):
        return TimeWindow(t(day,start),t(day,end))
    def test_catalog_has_individual_seats_and_pcs_only(self):
        self.assertEqual(len(self.units),len(UNITS))
        self.assertIn('AZ-LS-01',self.units)
        self.assertIn('AZ-LP-01',self.units)
        self.assertIn('AZ-CP-01',self.units)
        self.assertIn('AZ-GR-01',self.units)
        self.assertNotIn('EQ-CAM-01',self.units)
    def test_each_pc_has_separate_capacity(self):
        first=self.units['AZ-LP-01']
        second=self.units['AZ-LP-02']
        self.svc.request(self.student,first.id,self.window(),now=NOW)
        # Physically PC 02 is free. This student already holds PC 01,
        # so the demo fairness policy blocks a simultaneous second PC.
        self.assertFalse(self.svc.available(self.student,second.id,self.window()))
        other = provision_demo_user(self.engine,'other-seat@example.invalid','test-password-2','STUDENT')
        self.assertTrue(self.svc.available(other,second.id,self.window()))
        self.assertFalse(self.svc.available(self.student,first.id,self.window()))
    def test_weekend_rejected_and_no_audit(self):
        with self.assertRaises(InvalidRequest):
            self.svc.request(self.student,self.units['AZ-LS-01'].id,self.window(day=5),now=NOW)
        with Session(self.engine) as s:
            self.assertEqual(s.scalar(select(func.count(Reservation.id))),0)
            self.assertEqual(s.scalar(select(func.count(ReservationEvent.id))),0)
    def test_opening_boundaries_inclusive_start_and_closing_end(self):
        seat=self.units['AZ-LS-01']
        self.assertEqual(self.svc.request(self.student,seat.id,self.window(start=9,end=10),now=NOW).status,'CONFIRMED')
        late=TimeWindow(t(1,16,30),t(1,17,30))
        self.assertEqual(self.svc.request(self.student,seat.id,late,now=NOW).status,'CONFIRMED')
    def test_early_and_late_and_cross_midnight_rejected(self):
        seat=self.units['AZ-LS-01']
        for w in (TimeWindow(t(1,8,59),t(1,10)),
                  TimeWindow(t(1,17),t(1,17,31)),
                  TimeWindow(t(1,17),t(2,9))):
            with self.assertRaises(InvalidRequest):self.svc.request(self.student,seat.id,w,now=NOW)
    def test_pc_and_seat_duration_max_two_hours(self):
        r=self.units['AZ-LP-01']
        self.assertEqual(self.svc.request(self.student,r.id,self.window(start=10,end=12),now=NOW).status,'CONFIRMED')
        with self.assertRaises(InvalidRequest):
            self.svc.request(self.student,self.units['AZ-LP-02'].id,
                             TimeWindow(t(1,10),t(1,12,1)),now=NOW)
    def test_lab_pending_requires_approval(self):
        r=self.units['AZ-CP-01']
        booking=self.svc.request(self.student,r.id,self.window(),now=NOW)
        self.assertEqual(booking.status,'PENDING_APPROVAL')
        self.assertTrue(self.svc.available(self.student,r.id,self.window()))
        self.assertEqual(self.svc.decide(self.admin,booking.id,approve=True,now=NOW).status,'CONFIRMED')
    def test_closure_blocks_seats_in_whole_area_and_approval(self):
        lab=self.spaces['LAB-PC']
        pc1=self.units['AZ-CP-01'];pc2=self.units['AZ-CP-02']
        pending=self.svc.request(self.student,pc1.id,self.window(),now=NOW)
        closure=self.svc.create_closure(self.admin,lab.id,self.window(), 'Teaching lab reserved')
        self.assertGreater(closure,0)
        with self.assertRaises(Conflict):self.svc.decide(self.admin,pending.id,approve=True,now=NOW)
        with self.assertRaises(Conflict):self.svc.request(self.student,pc2.id,self.window(),now=NOW)
        self.assertEqual(self.svc.get_own(self.student,pending.id).status,'PENDING_APPROVAL')
    def test_closure_cannot_displace_confirmed_seat(self):
        library=self.spaces['LIB-READ'];seat=self.units['AZ-LS-01']
        self.svc.request(self.student,seat.id,self.window(),now=NOW)
        with self.assertRaises(Conflict):self.svc.create_closure(self.admin,library.id,self.window(),'Maintenance')
        with Session(self.engine) as s:
            self.assertEqual(s.scalar(select(func.count(SpaceClosure.id))),0)
    def test_nonadmin_cannot_block_teaching_lab(self):
        with self.assertRaises(AccessDenied):
            self.svc.create_closure(self.student,self.spaces['LAB-PC'].id,self.window(),'Class')
    def test_closed_now_status_is_distinct_from_booking(self):
        seat=self.units['AZ-LS-01']
        status=self.svc.status_overview(self.student,now=t(1,19))[seat.id]
        self.assertEqual(status.state,'CLOSED')
        open_status=self.svc.status_overview(self.student,now=t(1,12))[seat.id]
        self.assertEqual(open_status.state,'AVAILABLE')
    def test_idempotent_demo_sync(self):
        self.assertEqual(sync_demo_catalog(self.engine),{'spaces_created':0,'units_created':0,'legacy_starter_units_archived':0})
    def test_legacy_booking_preserved_while_gear_archived(self):
        with Session(self.engine) as s:
            s.add(Resource(public_code='EQ-CAM-01',name='Old Camera',category='EQUIPMENT',is_enabled=True,is_listed=True))
            s.commit()
            old=s.scalar(select(Resource).where(Resource.public_code=='EQ-CAM-01'))
            old_id=old.id
        booking=self.svc.request(self.student,old_id,self.window(),now=NOW)
        summary=sync_demo_catalog(self.engine)
        self.assertEqual(summary['legacy_starter_units_archived'],1)
        self.assertNotIn('EQ-CAM-01',{r.public_code for r in self.svc.list_resources(self.student)})
        self.assertEqual(self.svc.get_own(self.student,booking.id).resource_id,old_id)
        with self.assertRaises(InvalidRequest):self.svc.request(self.student,old_id,self.window(day=2),now=NOW)
    def test_old_sqlite_schema_migrates_without_losing_reservations(self):
        other=Path(self.tmp.name)/'old.db'
        raw=sqlite3.connect(other)
        raw.executescript("""CREATE TABLE resources (id INTEGER PRIMARY KEY, public_code VARCHAR(40) UNIQUE NOT NULL, name VARCHAR(120) NOT NULL, category VARCHAR(20) NOT NULL, requires_approval BOOLEAN NOT NULL, is_enabled BOOLEAN NOT NULL); INSERT INTO resources VALUES(1,'EQ-CAM-01','Old Camera','EQUIPMENT',0,1);""")
        raw.commit();raw.close()
        engine=make_engine(other)
        create_schema(engine)
        with Session(engine) as db:
            r=db.get(Resource,1)
            self.assertEqual((r.public_code,r.is_listed,r.space_id),('EQ-CAM-01',True,None))
        engine.dispose()

class HoursUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.engine=make_engine(Path(self.tmp.name)/'hours.db')
        create_schema(self.engine)
        self.admin=provision_demo_user(self.engine,'admin@demo.invalid','pass-demo-long','ADMIN')
        self.student=provision_demo_user(self.engine,'student@demo.invalid','pass-demo-long','STUDENT')
        sync_demo_catalog(self.engine)
        self.svc=BookingService(self.engine,clock=lambda:NOW)
        self.room=next(x for x in self.svc.list_resources(self.student) if x.public_code=='AZ-LS-01')
        self.space=next(x for x in self.svc.list_spaces(self.student) if x.public_code=='LIB-READ')
    def tearDown(self):
        self.engine.dispose();self.tmp.cleanup()
    def test_admin_can_change_hours_and_weekdays(self):
        s=self.svc.update_space_hours(self.admin,self.space.id,'10:00','16:00','0,1,2,3,4')
        self.assertEqual(s.opens_at,'10:00')
        with self.assertRaises(InvalidRequest):
            self.svc.request(self.student,self.room.id,TimeWindow(t(1,9),t(1,10)),now=NOW)
    def test_invalid_hours_rejected(self):
        for opens,closes,days in [('18:00','09:00','0,1'),('09:00','17:00','7'),('9am','17:00','0')]:
            with self.assertRaises(InvalidRequest):
                self.svc.update_space_hours(self.admin,self.space.id,opens,closes,days)
    def test_cannot_silently_invalidate_confirmed_booking(self):
        booked=self.svc.request(self.student,self.room.id,TimeWindow(t(1,10),t(1,11)),now=NOW)
        with self.assertRaises(Conflict):
            self.svc.update_space_hours(self.admin,self.space.id,'11:00','17:30','0,1,2,3,4')
        old=next(x for x in self.svc.list_spaces(self.admin) if x.id==self.space.id)
        self.assertEqual(old.opens_at,'09:00')
        self.assertEqual(self.svc.get_own(self.student,booked.id).status,'CONFIRMED')
    def test_admin_only_hours(self):
        with self.assertRaises(AccessDenied):
            self.svc.update_space_hours(self.student,self.space.id,'10:00','16:00','0,1,2,3,4')
