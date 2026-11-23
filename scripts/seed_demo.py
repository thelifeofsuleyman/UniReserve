"""Create demo users and resources once, printing randomized login credentials.

Usage: python scripts/seed_demo.py
       python scripts/seed_demo.py --db instance/unireserve.sqlite3
"""
from __future__ import annotations

import argparse
from pathlib import Path
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import User, Resource
from unireserve.services.booking import BookingService


def seed(db_path: str):
    engine = make_engine(db_path)
    create_schema(engine)
    with Session(engine) as db:
        if db.scalar(select(func.count(User.id))):
            print("This database already has user accounts; no accounts or passwords were changed.")
            print("To start fresh, use a NEW database filename rather than overwriting existing bookings.")
            return
    users = {}
    for email, role in (("student@unireserve.test", "STUDENT"),
                        ("staff@unireserve.test", "STAFF"),
                        ("admin@unireserve.test", "ADMIN")):
        password = secrets.token_urlsafe(15)
        uid = provision_demo_user(engine, email, password, role)
        users[email] = (password, uid)
    svc = BookingService(engine)
    resource_specs = (
        ("ROOM-101", "North Study Room", "ROOM", False),
        ("ROOM-202", "Creative Studio", "ROOM", True),
        ("EQ-CAM-01", "Sony Mirrorless Camera", "EQUIPMENT", True),
        ("EQ-LAP-01", "Development Laptop", "EQUIPMENT", False),
        ("EQ-MIC-01", "Podcast Microphone", "EQUIPMENT", False),
        ("EQ-PROJ-01", "Portable Projector", "EQUIPMENT", True),
    )
    for code, name, category, needs_approval in resource_specs:
        svc.create_resource(users["admin@unireserve.test"][1], code, name, category,
                            requires_approval=needs_approval)
    print(f"Created 3 users and {len(resource_specs)} resources in {db_path}")
    print("DEMO CREDENTIALS — keep these private; they are shown only once:\n")
    for email, (password, _) in users.items():
        print(f"  {email}  /  {password}")
    print("\nStart: python scripts/run_web.py  |  Browser: http://127.0.0.1:5000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "instance" / "unireserve.sqlite3"))
    args = parser.parse_args()
    seed(args.db)
