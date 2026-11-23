"""Password encoding and provisioning tests (preparation for web login)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy.orm import Session
from unireserve.storage.accounts import hash_password, verify_password, provision_demo_user
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import User


class PasswordTests(unittest.TestCase):
    def test_salted_hash_and_verify(self):
        raw = "correct-horse-student-password"
        a = hash_password(raw)
        b = hash_password(raw)
        self.assertNotEqual(a, b)
        self.assertNotIn(raw, a)
        self.assertTrue(verify_password(raw, a))
        self.assertFalse(verify_password("another password", a))
        self.assertFalse(verify_password(raw, "invalid"))

    def test_provisioning_does_not_store_plaintext(self):
        with TemporaryDirectory() as tmp:
            engine = make_engine(Path(tmp) / "accounts.sqlite")
            create_schema(engine)
            uid = provision_demo_user(engine, " Student@Example.invalid ", "a-long-demo-password", "STUDENT")
            with Session(engine) as session:
                user = session.get(User, uid)
                self.assertEqual(user.email, "student@example.invalid")
                self.assertTrue(verify_password("a-long-demo-password", user.password_hash))
                self.assertNotEqual(user.password_hash, "a-long-demo-password")
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
