"""CR-005: production WSGI config and minimal customer-facing copy."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from unittest.mock import patch

from unireserve.web.app import create_app


class ProductionConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "site.sqlite3")

    def tearDown(self):
        self.tmp.cleanup()

    def test_production_rejects_missing_secret(self):
        with patch.dict(os.environ, {"UNIRESERVE_MODE":"production", "UNIRESERVE_TRUSTED_HOSTS":"reservations.example.edu"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "UNIRESERVE_SECRET_KEY"):
                create_app({"DB_PATH":self.db})

    def test_production_rejects_missing_trusted_hosts(self):
        with patch.dict(os.environ, {"UNIRESERVE_MODE":"production", "UNIRESERVE_SECRET_KEY":"a" * 64}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "TRUSTED_HOSTS"):
                create_app({"DB_PATH":self.db})

    def test_production_rejects_auto_seed(self):
        with patch.dict(os.environ, {
            "UNIRESERVE_MODE":"production", "UNIRESERVE_SECRET_KEY":"a" * 64,
            "UNIRESERVE_TRUSTED_HOSTS":"reservations.example.edu",
            "UNIRESERVE_AUTO_SAMPLE_CATALOG":"1"
        }, clear=True):
            with self.assertRaisesRegex(RuntimeError, "disabled in production"):
                create_app({"DB_PATH":self.db})

    def test_https_cookie_hosts_headers_and_health(self):
        with patch.dict(os.environ, {
            "UNIRESERVE_MODE":"production", "UNIRESERVE_SECRET_KEY":"a" * 64,
            "UNIRESERVE_TRUSTED_HOSTS":"reservations.example.edu",
        }, clear=True):
            app=create_app({"DB_PATH":self.db})
            try:
                self.assertTrue(app.config["SESSION_COOKIE_SECURE"])
                self.assertEqual(app.config["TRUSTED_HOSTS"],["reservations.example.edu"])
                client=app.test_client()
                good=client.get("/healthz",base_url="https://reservations.example.edu")
                self.assertEqual(good.status_code,200)
                self.assertEqual(good.get_json()["status"],"ok")
                self.assertEqual(good.headers["Strict-Transport-Security"],"max-age=31536000")
                self.assertIn("frame-ancestors 'none'",good.headers["Content-Security-Policy"])
                self.assertEqual(good.headers["Cache-Control"],"no-store")
                bad=client.get("/healthz",base_url="https://evil.example")
                self.assertEqual(bad.status_code,400)
            finally:
                app.extensions["unireserve_engine"].dispose()

    def test_production_app_can_start_without_sample_catalogue(self):
        with patch.dict(os.environ, {
            "UNIRESERVE_MODE":"production", "UNIRESERVE_SECRET_KEY":"b" * 64,
            "UNIRESERVE_TRUSTED_HOSTS":"reservations.example.edu",
        }, clear=True):
            app=create_app({"DB_PATH":self.db})
            try:
                self.assertEqual(app.test_client().get("/healthz",
                    base_url="https://reservations.example.edu").status_code,200)
                from sqlalchemy.orm import Session
                from sqlalchemy import select
                from unireserve.storage.models import Space
                with Session(app.extensions["unireserve_engine"]) as db:
                    self.assertEqual(db.scalars(select(Space)).all(),[])
            finally:
                app.extensions["unireserve_engine"].dispose()

    def test_main_pages_drop_development_language(self):
        with patch.dict(os.environ, {"UNIRESERVE_MODE":"local"}, clear=True):
            app=create_app({"DB_PATH":self.db})
            try:
                response=app.test_client().get("/login")
                self.assertEqual(response.status_code,200)
                source=response.get_data(as_text=True)
                for phrase in ("coursework demonstration", "Demo credentials are", "python scripts/seed_demo.py", "Example campus"):
                    self.assertNotIn(phrase,source)
                self.assertEqual(app.test_client().get("/about").status_code,200)
                self.assertIn("not an official AzTU service",app.test_client().get("/about").get_data(as_text=True))
                self.assertIn("Service information",source if "Service information" in source else app.test_client().get("/about").get_data(as_text=True))
            finally:
                app.extensions["unireserve_engine"].dispose()

if __name__=="__main__":
    unittest.main()
