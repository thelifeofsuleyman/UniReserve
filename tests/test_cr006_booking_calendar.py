"""CR-006: future reservation calendar, privacy, rules, and personal agenda."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from unireserve.domain.availability import TimeWindow
from unireserve.domain.operating_hours import BAKU
from unireserve.services.booking import BookingService, InvalidRequest, MissingRecord
from unireserve.storage.accounts import provision_user
from unireserve.storage.aztu_demo import sync_demo_catalog
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import ReservationEvent
from unireserve.web.app import create_app


NOW = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)  # Monday 11:00 Baku
DAY = date(2026, 11, 24)  # Tuesday


def time_window(start=10, end=11):
    return TimeWindow(datetime(2026, 11, 24, start, tzinfo=BAKU),
                      datetime(2026, 11, 24, end, tzinfo=BAKU))


def state(slots, time):
    return next(slot["state"] for slot in slots if slot["label"] == time)


class CalendarServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.engine = make_engine(Path(self.tmp.name) / "cal.sqlite3")
        create_schema(self.engine)
        sync_demo_catalog(self.engine)
        self.owner = provision_user(self.engine,"owner@private.invalid","password-demo-123","STUDENT")
        self.other = provision_user(self.engine,"other@private.invalid","password-demo-456","STUDENT")
        self.admin = provision_user(self.engine,"admin@private.invalid","password-demo-789","ADMIN")
        self.service = BookingService(self.engine, clock=lambda: NOW)
        self.units = {r.public_code: r for r in self.service.list_resources(self.owner)}
        self.spaces = {s.public_code: s for s in self.service.list_spaces(self.owner)}

    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()

    def calendar(self, user, code, when=DAY):
        return self.service.calendar_day(user,self.units[code].id,when,now=NOW)["slots"]

    def test_future_booking_is_red_to_other_users_but_not_prior_half_hour(self):
        self.service.request(self.owner,self.units["AZ-LP-01"].id,time_window(),now=NOW)
        other = self.calendar(self.other,"AZ-LP-01")
        self.assertEqual(state(other,"09:30"),"AVAILABLE")
        self.assertEqual(state(other,"10:00"),"BOOKED")
        self.assertEqual(state(other,"10:30"),"BOOKED")
        self.assertEqual(state(other,"11:00"),"AVAILABLE")

    def test_booked_slot_stays_red_after_start_but_before_end(self):
        self.service.request(self.owner,self.units["AZ-LP-01"].id,time_window(),now=NOW)
        during = datetime(2026,11,24,10,15,tzinfo=BAKU)
        slots = self.service.calendar_day(
            self.other,self.units["AZ-LP-01"].id,DAY,now=during
        )["slots"]
        self.assertEqual(state(slots,"10:00"),"BOOKED")
        self.assertEqual(state(slots,"10:30"),"BOOKED")
        self.assertEqual(state(slots,"09:30"),"PAST")

    def test_cancelled_booking_releases_red_slots(self):
        booking=self.service.request(self.owner,self.units["AZ-LS-01"].id,time_window(),now=NOW)
        self.assertEqual(state(self.calendar(self.other,"AZ-LS-01"),"10:00"),"BOOKED")
        self.service.cancel(self.owner,booking.id,now=NOW)
        self.assertEqual(state(self.calendar(self.other,"AZ-LS-01"),"10:00"),"AVAILABLE")

    def test_pending_does_not_turn_red_until_approval(self):
        booking=self.service.request(self.owner,self.units["AZ-GR-01"].id,time_window(),now=NOW)
        self.assertEqual(booking.status,"PENDING_APPROVAL")
        self.assertEqual(state(self.calendar(self.other,"AZ-GR-01"),"10:00"),"AVAILABLE")
        self.service.decide(self.admin,booking.id,approve=True,now=NOW)
        self.assertEqual(state(self.calendar(self.other,"AZ-GR-01"),"10:00"),"BOOKED")

    def test_admin_closure_marks_lab_slots_closed(self):
        self.service.create_closure(self.admin,self.spaces["LAB-PC"].id,time_window(),"Class in progress")
        self.assertEqual(state(self.calendar(self.other,"AZ-CP-02"),"10:00"),"CLOSED")
        self.assertEqual(state(self.calendar(self.other,"AZ-CP-02"),"09:30"),"AVAILABLE")

    def test_owner_other_study_booking_is_amber_but_other_student_sees_green(self):
        self.service.request(self.owner,self.units["AZ-LP-01"].id,time_window(),now=NOW)
        self.assertEqual(state(self.calendar(self.owner,"AZ-LS-01"),"10:00"),"OWN_BOOKING")
        self.assertEqual(state(self.calendar(self.other,"AZ-LS-01"),"10:00"),"AVAILABLE")

    def test_weekend_is_closed_even_if_no_confirmed_booking(self):
        saturday=date(2026,11,28)
        self.assertEqual(state(self.calendar(self.other,"AZ-LP-01",saturday),"10:00"),"CLOSED")

    def test_today_slots_in_past_are_unavailable(self):
        slots=self.calendar(self.owner,"AZ-LP-01",NOW.astimezone(BAKU).date())
        self.assertEqual(state(slots,"10:00"),"PAST")
        self.assertEqual(state(slots,"12:00"),"AVAILABLE")

    def test_invalid_dates_and_unlisted_resource_do_not_leak_availability(self):
        code="AZ-LS-01"
        for d in [date(2026,11,22),date(2026,12,15)]:
            with self.assertRaises(InvalidRequest):
                self.calendar(self.other,code,d)
        self.service.update_resource(self.admin,self.units[code].id,is_listed=False)
        with self.assertRaises(MissingRecord):
            self.calendar(self.other,code)

    def test_read_only_no_events_and_no_identifying_fields(self):
        self.service.request(self.owner,self.units["AZ-LP-01"].id,time_window(),now=NOW)
        before=0
        with Session(self.engine) as session:
            before=len(session.scalars(select(ReservationEvent)).all())
        payload=self.service.calendar_day(self.other,self.units["AZ-LP-01"].id,DAY,now=NOW)
        self.assertEqual(payload["timezone"],"Asia/Baku")
        self.assertEqual(len(payload["slots"]),17)
        self.assertTrue(all(set(slot)=={"start","end","label","state"} for slot in payload["slots"]))
        self.assertNotIn("email",str(payload).lower())
        self.assertNotIn("user_id",str(payload))
        with Session(self.engine) as session:
            self.assertEqual(before,len(session.scalars(select(ReservationEvent)).all()))


class CalendarHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.app=create_app({"TESTING":True,"SECRET_KEY":"cr-006-browser-key",
            "DB_PATH":str(Path(self.temp.name)/"web-cal.sqlite3")})
        self.engine=self.app.extensions["unireserve_engine"]
        sync_demo_catalog(self.engine)
        self.owner=provision_user(self.engine,"owner@private.invalid","password-demo-123","STUDENT")
        self.other=provision_user(self.engine,"other@private.invalid","password-demo-456","STUDENT")
        self.service=BookingService(self.engine)
        self.room={r.public_code:r for r in self.service.list_resources(self.owner)}["AZ-LP-01"]
        self.client=self.app.test_client()
        now=datetime.now(BAKU)
        self.day=now.date()+timedelta(days=1)
        while self.day.weekday() >= 5:
            self.day+=timedelta(days=1)
        self.window=TimeWindow(
            datetime.combine(self.day,datetime.min.time(),tzinfo=BAKU)+timedelta(hours=10),
            datetime.combine(self.day,datetime.min.time(),tzinfo=BAKU)+timedelta(hours=11))

    def tearDown(self):
        self.engine.dispose()
        self.temp.cleanup()

    def login(self,email,password):
        self.client.get("/login")
        with self.client.session_transaction() as ss: token=ss["csrf_token"]
        result=self.client.post("/login",data={"csrf_token":token,"email":email,"password":password})
        self.assertEqual(result.status_code,302)

    def test_schedule_is_private_and_http_no_store(self):
        self.assertEqual(self.client.get(f"/api/resources/{self.room.id}/calendar?date={self.day}").status_code,302)
        self.service.request(self.owner,self.room.id,self.window)
        self.login("other@private.invalid","password-demo-456")
        result=self.client.get(f"/api/resources/{self.room.id}/calendar?date={self.day}")
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.headers["Cache-Control"],"no-store")
        payload=result.get_json()
        self.assertEqual(state(payload["slots"],"10:00"),"BOOKED")
        self.assertNotIn("owner@private.invalid",result.get_data(as_text=True))
        self.assertNotIn("user_id",result.get_data(as_text=True))
        self.assertNotIn("reservation_id",result.get_data(as_text=True))

    def test_calendar_route_rejects_invalid_or_out_of_range_date(self):
        self.login("other@private.invalid","password-demo-456")
        for value in ("garbage","2026-1-1","2000-01-01","2099-12-30"):
            result=self.client.get(f"/api/resources/{self.room.id}/calendar?date={value}")
            self.assertEqual(result.status_code,400)
        self.assertEqual(self.client.get(f"/api/resources/999999/calendar?date={self.day}").status_code,404)

    def test_booking_page_shows_clickable_calendar_and_script(self):
        self.login("other@private.invalid","password-demo-456")
        result=self.client.get(f"/resources/{self.room.id}")
        self.assertEqual(result.status_code,200)
        for term in (b"Availability calendar",b"calendar-date",b"calendar-slots",
                     b"booking-calendar.js",b"reservation-form",b"datetime-local"):
            self.assertIn(term,result.data)
        script=(Path(__file__).resolve().parents[1]/"src/unireserve/web/static/booking-calendar.js").read_text()
        self.assertIn("startInput.value = slot.start",script)
        self.assertIn("endInput.value =",script)

    def test_my_reservations_shows_weekly_plan_with_link_and_time(self):
        self.service.request(self.owner,self.room.id,self.window)
        self.login("owner@private.invalid","password-demo-123")
        response=self.client.get("/my-reservations")
        self.assertEqual(response.status_code,200)
        self.assertIn(b"Your next 7 days",response.data)
        self.assertIn(b"Library PC 01",response.data)
        self.assertIn(b"class=\"my-week__entry",response.data)


if __name__=="__main__":
    unittest.main()
