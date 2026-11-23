"""Test administrator onboarding of a real configurable study area."""
from __future__ import annotations
import tempfile
from pathlib import Path
import unittest
from unireserve.web.app import create_app
from unireserve.storage.accounts import provision_user
from unireserve.services.booking import BookingService


class SpaceManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.app=create_app({"TESTING":True,"SECRET_KEY":"test-config-management",
            "DB_PATH":str(Path(self.temp.name)/"spaces.sqlite3")})
        self.engine=self.app.extensions["unireserve_engine"]
        self.admin=provision_user(self.engine,"admin@example.invalid","test-password-1234","ADMIN")
        self.student=provision_user(self.engine,"student@example.invalid","test-password-1234","STUDENT")
        self.svc=BookingService(self.engine)
        self.client=self.app.test_client()

    def tearDown(self):
        self.engine.dispose()
        self.temp.cleanup()

    def login(self,email):
        self.client.get("/login")
        with self.client.session_transaction() as ss:
            token=ss["csrf_token"]
        return self.client.post("/login",data={"csrf_token":token,"email":email,
            "password":"test-password-1234"})

    def post_area(self,**values):
        defaults={"code":"LIB-EAST","name":"Library East Wing","kind":"LIBRARY_SEAT",
                  "opens_at":"09:00","closes_at":"18:00","open_days":"0,1,2,3,4"}
        defaults.update(values)
        with self.client.session_transaction() as ss:
            defaults["csrf_token"]=ss["csrf_token"]
        return self.client.post("/admin/spaces",data=defaults,follow_redirects=True)

    def test_admin_adds_area_then_places_can_be_added(self):
        self.login("admin@example.invalid")
        result=self.post_area()
        self.assertEqual(result.status_code,200)
        self.assertIn(b"Space created.",result.data)
        spaces=self.svc.list_spaces(self.admin)
        self.assertEqual(len(spaces),1)
        self.assertEqual(spaces[0].name,"Library East Wing")
        self.assertEqual(spaces[0].open_days,"0,1,2,3,4")
        self.svc.create_resource(self.admin,"LIB-E-01","East Seat 01","ROOM",space_id=spaces[0].id)
        self.assertIn(b"East Seat 01",self.client.get("/resources").data)
        self.assertIn(b"East Seat 01",self.client.get("/studio").data)

    def test_duplicate_code_rejected_without_mutation(self):
        self.login("admin@example.invalid")
        self.post_area()
        result=self.post_area(name="Duplicate")
        self.assertIn(b"area code already exists",result.data)
        self.assertEqual(len(self.svc.list_spaces(self.admin)),1)

    def test_student_cannot_add_area(self):
        self.login("student@example.invalid")
        result=self.post_area()
        self.assertEqual(result.status_code,403)
        self.assertEqual(self.svc.list_spaces(self.student),[])

    def test_bad_hours_do_not_persist(self):
        self.login("admin@example.invalid")
        result=self.post_area(opens_at="18:00",closes_at="09:00")
        self.assertIn(b"valid HH:MM",result.data)
        self.assertEqual(self.svc.list_spaces(self.admin),[])


if __name__=="__main__":
    unittest.main()
