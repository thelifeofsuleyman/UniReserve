"""Demonstrate a pending booking, an administrator decision, and audit trail.

This deliberately uses fake accounts and a temporary database. No external
services, real personal data, or Flask server are required.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from unireserve.domain.availability import TimeWindow
from unireserve.services.booking import BookingService
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.db import create_schema, make_engine


def main() -> None:
    with TemporaryDirectory(prefix="unireserve-demo-") as tmp:
        engine = make_engine(Path(tmp) / "demo.sqlite")
        create_schema(engine)
        user = provision_demo_user(engine, "student@example.invalid", "demo-password-for-student", "STUDENT")
        admin = provision_demo_user(engine, "admin@example.invalid", "demo-password-for-admin", "ADMIN")
        service = BookingService(engine)
        cam = service.create_resource(admin, "CAM-01", "Camera A", "EQUIPMENT", requires_approval=True)
        now = datetime.now(timezone.utc)
        window = TimeWindow(now + timedelta(days=1), now + timedelta(days=1, hours=2))
        reservation = service.request(user, cam.id, window)
        print("Request status:", reservation.status)
        decided = service.decide(admin, reservation.id, approve=True)
        print("Final status:  ", decided.status)
        print("Audit events:  ", service.events(user, reservation.id))
        engine.dispose()


if __name__ == "__main__":
    main()
