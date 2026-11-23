"""Milestone 5: Flask HTTP integration, role, ownership, CSRF and form tests.

Distinct from pure booking tests, these issue real requests to a Flask test client.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from unireserve.domain.availability import TimeWindow
from unireserve.services.booking import BookingService
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.models import User, Resource, Reservation
from unireserve.web.app import create_app
from sqlalchemy import select, func
from sqlalchemy.orm import Session


class WebIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-only-key", "DB_PATH": str(Path(self.tmp.name) / "web.sqlite3")})
        self.engine = self.app.extensions["unireserve_engine"]
        self.student_id = provision_demo_user(self.engine, "student@unireserve.test", "student-password-123", "STUDENT")
        self.other_id = provision_demo_user(self.engine, "other@unireserve.test", "other-password-123", "STAFF")
        self.admin_id = provision_demo_user(self.engine, "admin@unireserve.test", "admin-password-123", "ADMIN")
        self.svc = BookingService(self.engine)
        self.room = self.svc.create_resource(self.admin_id, "ROOM-101", "Quiet Study Room", "ROOM")
        self.camera = self.svc.create_resource(self.admin_id, "EQ-CAM-01", "Camera Kit", "EQUIPMENT", requires_approval=True)
        self.client = self.app.test_client()

    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()

    def _token(self):
        with self.client.session_transaction() as sess:
            return sess.get("csrf_token")

    def _post(self, path, data=None, *, csrf=True, follow_redirects=False):
        payload = dict(data or {})
        if csrf:
            payload["csrf_token"] = self._token()
        return self.client.post(path, data=payload, follow_redirects=follow_redirects)

    def _login(self, email="student@unireserve.test", password="student-password-123"):
        self.client.get("/login")
        return self._post("/login", {"email": email, "password": password})

    def _change_user(self, email, password):
        self._post("/logout")
        return self._login(email, password)

    def _window_form(self):
        zone = ZoneInfo("Asia/Baku")
        now = datetime.now(zone)
        start = (now + timedelta(hours=3)).replace(second=0, microsecond=0)
        end = start + timedelta(hours=1)
        return {"start": start.strftime("%Y-%m-%dT%H:%M"), "end": end.strftime("%Y-%m-%dT%H:%M")}

    def _window(self):
        d = self._window_form()
        zone = ZoneInfo("Asia/Baku")
        return TimeWindow(datetime.strptime(d["start"], "%Y-%m-%dT%H:%M").replace(tzinfo=zone),
                          datetime.strptime(d["end"], "%Y-%m-%dT%H:%M").replace(tzinfo=zone))

    def _counts(self):
        with Session(self.engine) as db:
            return db.scalar(select(func.count(Reservation.id)))

    def test_signin_page_is_accessible_without_account(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back", response.data)
        self.assertIn(b"csrf_token", response.data)
        self.assertIn(b"password", response.data)

    def test_anonymous_access_redirects_and_cannot_create_booking(self):
        self.assertEqual(self.client.get("/resources").status_code, 302)
        self.assertIn("/login", self.client.get("/my-reservations").location)
        self.client.get("/login")
        result = self._post(f"/resources/{self.room.id}/book", self._window_form())
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self._counts(), 0)

    def test_valid_login_and_logout(self):
        response = self._login()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/resources", response.location)
        self.assertEqual(self.client.get("/resources").status_code, 200)
        self.assertEqual(self._post("/logout").status_code, 302)
        self.assertIn("/login", self.client.get("/resources").location)

    def test_invalid_password_does_not_create_session(self):
        response = self._login(password="incorrect-password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Incorrect email or password", response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn("uid", sess)

    def test_inactive_account_revoked_on_every_request(self):
        self._login()
        with self.engine.begin() as conn:
            conn.exec_driver_sql("UPDATE users SET is_active=0 WHERE id=?", (self.student_id,))
        response = self.client.get("/resources")
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as sess:
            self.assertNotIn("uid", sess)

    def test_csrf_missing_or_invalid_is_rejected_before_mutation(self):
        self._login()
        before = self._counts()
        self.assertEqual(self._post(f"/resources/{self.room.id}/book", self._window_form(), csrf=False).status_code, 400)
        bad = dict(self._window_form(), csrf_token="garbage")
        self.assertEqual(self.client.post(f"/resources/{self.room.id}/book", data=bad).status_code, 400)
        self.assertEqual(self._counts(), before)

    def test_get_cannot_logout_or_cancel_or_approve(self):
        self._login()
        self.assertEqual(self.client.get("/logout").status_code, 405)
        self.assertEqual(self.client.get("/reservations/1/cancel").status_code, 405)
        self.assertEqual(self.client.get("/admin/requests/1/approve").status_code, 405)

    def test_catalogue_lists_resources_and_filters(self):
        self._login()
        page = self.client.get("/resources")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Quiet Study Room", page.data)
        self.assertIn(b"Camera Kit", page.data)
        filtered = self.client.get("/resources?category=ROOM&q=quiet")
        self.assertIn(b"Quiet Study Room", filtered.data)
        self.assertNotIn(b"Camera Kit", filtered.data)

    def test_resource_detail_shows_form_and_timezone(self):
        self._login()
        response = self.client.get(f"/resources/{self.room.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Asia/Baku", response.data)
        self.assertIn(b'datetime-local', response.data)

    def test_check_availability_does_not_create_reservation(self):
        self._login()
        result = self._post(f"/resources/{self.room.id}/availability", self._window_form(), follow_redirects=True)
        self.assertIn(b"This time slot is available", result.data)
        self.assertEqual(self._counts(), 0)

    def test_availability_check_preserves_selected_form_times(self):
        self._login()
        form = self._window_form()
        response = self._post(f"/resources/{self.room.id}/availability", form, follow_redirects=True)
        self.assertIn(b"This time slot is available", response.data)
        self.assertIn(f'value="{form["start"]}"'.encode(), response.data)
        self.assertIn(f'value="{form["end"]}"'.encode(), response.data)
        self.assertEqual(self._counts(), 0)

    def test_validation_failure_preserves_selected_form_times(self):
        self._login()
        form = self._window_form()
        form["end"] = form["start"]
        response = self._post(f"/resources/{self.room.id}/book", form, follow_redirects=True)
        self.assertIn(b"Enter valid start and end times", response.data)
        self.assertIn(f'value="{form["start"]}"'.encode(), response.data)
        self.assertEqual(self._counts(), 0)

    def test_standard_reservation_confirmed_and_own_listed(self):
        self._login()
        result = self._post(f"/resources/{self.room.id}/book", self._window_form(), follow_redirects=True)
        self.assertIn(b"Reservation confirmed", result.data)
        self.assertIn(b"Quiet Study Room", result.data)
        self.assertIn(b"Confirmed", result.data)
        self.assertEqual(self._counts(), 1)

    def test_duplicate_booking_rejected_without_second_row(self):
        self._login()
        payload = self._window_form()
        self._post(f"/resources/{self.room.id}/book", payload)
        response = self._post(f"/resources/{self.room.id}/book", payload, follow_redirects=True)
        self.assertIn(b"already reserved", response.data)
        self.assertEqual(self._counts(), 1)

    def test_pending_request_visible_to_admin_and_owner(self):
        self._login()
        response = self._post(f"/resources/{self.camera.id}/book", self._window_form(), follow_redirects=True)
        self.assertIn(b"Request sent", response.data)
        self.assertIn(b"Pending Approval", response.data)
        self._change_user("admin@unireserve.test", "admin-password-123")
        admin_page = self.client.get("/admin")
        self.assertEqual(admin_page.status_code, 200)
        self.assertIn(b"student@unireserve.test", admin_page.data)
        self.assertIn(b"Camera Kit", admin_page.data)

    def test_student_cannot_open_admin_or_decide_requests(self):
        self._login()
        booking = self.svc.request(self.student_id, self.camera.id, self._window())
        self.assertEqual(self.client.get("/admin").status_code, 403)
        result = self._post(f"/admin/requests/{booking.id}/approve")
        self.assertEqual(result.status_code, 403)
        self.assertEqual(self.svc.get_own(self.student_id, booking.id).status, "PENDING_APPROVAL")

    def test_admin_cannot_submit_student_booking_even_with_form(self):
        self._login("admin@unireserve.test", "admin-password-123")
        self.assertIn(b"Admin accounts", self.client.get(f"/resources/{self.room.id}").data)
        self.assertEqual(self._post(f"/resources/{self.room.id}/book", self._window_form()).status_code, 403)
        self.assertEqual(self._counts(), 0)

    def test_admin_can_approve_and_audit_is_visible_to_owner(self):
        self._login()
        booking = self.svc.request(self.student_id, self.camera.id, self._window())
        self._change_user("admin@unireserve.test", "admin-password-123")
        response = self._post(f"/admin/requests/{booking.id}/approve", follow_redirects=True)
        self.assertIn(b"Request approved", response.data)
        self._change_user("student@unireserve.test", "student-password-123")
        detail = self.client.get(f"/reservations/{booking.id}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"Approved", detail.data)
        self.assertIn(b"Confirmed", detail.data)

    def test_admin_can_reject_pending_request(self):
        self._login()
        booking = self.svc.request(self.student_id, self.camera.id, self._window())
        self._change_user("admin@unireserve.test", "admin-password-123")
        response = self._post(f"/admin/requests/{booking.id}/reject", follow_redirects=True)
        self.assertIn(b"Request rejected", response.data)
        self.assertEqual(self.svc.get_own(self.student_id, booking.id).status, "REJECTED")

    def test_cancel_own_booking_releases_slot(self):
        self._login()
        booking = self.svc.request(self.student_id, self.room.id, self._window())
        result = self._post(f"/reservations/{booking.id}/cancel", follow_redirects=True)
        self.assertIn(b"has been cancelled", result.data)
        self.assertEqual(self.svc.get_own(self.student_id, booking.id).status, "CANCELLED")
        self.assertEqual(self.svc.request(self.other_id, self.room.id, self._window()).status, "CONFIRMED")

    def test_other_user_cannot_see_or_cancel_owners_booking(self):
        self._login()
        booking = self.svc.request(self.student_id, self.room.id, self._window())
        self._change_user("other@unireserve.test", "other-password-123")
        self.assertNotIn(b"Quiet Study Room", self.client.get("/my-reservations").data)
        self.assertEqual(self.client.get(f"/reservations/{booking.id}").status_code, 404)
        self.assertEqual(self._post(f"/reservations/{booking.id}/cancel").status_code, 404)
        self.assertEqual(self.svc.get_own(self.student_id, booking.id).status, "CONFIRMED")

    def test_admin_can_create_resource_and_disable_it(self):
        self._login("admin@unireserve.test", "admin-password-123")
        add = self._post("/admin/resources", {"code":"ROOM-500", "name":"Design Workshop", "category":"ROOM", "requires_approval":"on"}, follow_redirects=True)
        self.assertIn(b"Resource added", add.data)
        new = next(x for x in self.svc.list_resources(self.admin_id) if x.public_code == "ROOM-500")
        self.assertTrue(new.requires_approval)
        edit = self._post(f"/admin/resources/{new.id}", {"name":"Design Space", "category":"ROOM"}, follow_redirects=True)
        self.assertIn(b"Resource settings saved", edit.data)
        self.assertFalse(self.svc.get_resource(self.admin_id, new.id).is_enabled)
        self.assertIn(b"Design Space", self.client.get("/resources").data)

    def test_nonadmin_cannot_mutate_resource_through_http(self):
        self._login()
        self.assertEqual(self._post("/admin/resources", {"code":"HACK", "name":"Hack", "category":"ROOM"}).status_code, 403)
        self.assertEqual(self._post(f"/admin/resources/{self.room.id}", {"name":"Hacked", "category":"ROOM"}).status_code, 403)
        self.assertEqual(self.svc.get_resource(self.student_id, self.room.id).name, "Quiet Study Room")

    def test_invalid_interval_creates_nothing(self):
        self._login()
        payload = self._window_form()
        payload["end"] = payload["start"]
        resp = self._post(f"/resources/{self.room.id}/book", payload, follow_redirects=True)
        self.assertIn(b"Enter valid start and end", resp.data)
        self.assertEqual(self._counts(), 0)

    def test_resource_name_uses_html_escaping(self):
        self._login("admin@unireserve.test", "admin-password-123")
        self._post("/admin/resources", {"code":"ESCAPE-01", "name":"<script>alert(1)</script>", "category":"ROOM"})
        result = self.client.get("/resources")
        self.assertNotIn(b"<script>alert(1)</script>", result.data)
        self.assertIn(b"&lt;script&gt;", result.data)

    def test_forged_session_user_id_does_not_escalate_privileges(self):
        self._login()
        # The browser cannot forge a valid Flask signed cookie; test that
        # a posted user_id value never supersedes the authenticated identity.
        data = self._window_form()
        data["actor_id"] = str(self.admin_id)
        response = self._post(f"/resources/{self.room.id}/book", data)
        self.assertEqual(response.status_code, 302)
        with Session(self.engine) as db:
            row = db.scalar(select(Reservation).order_by(Reservation.id.desc()))
            self.assertEqual(row.user_id, self.student_id)

    def test_pending_list_service_denied_to_normal_user(self):
        from unireserve.services.booking import AccessDenied
        with self.assertRaises(AccessDenied):
            self.svc.list_pending(self.student_id)

    def test_unknown_booking_returns_404(self):
        self._login()
        self.assertEqual(self.client.get("/reservations/999").status_code, 404)
        self.assertEqual(self._post("/reservations/999/cancel").status_code, 404)


if __name__ == "__main__":
    unittest.main()
