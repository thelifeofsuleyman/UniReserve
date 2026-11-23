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
from unireserve.storage.aztu_demo import sync_demo_catalog


def seed(db_path: str):
    engine = make_engine(db_path)
    create_schema(engine)
    with Session(engine) as db:
        existing_accounts = bool(db.scalar(select(func.count(User.id))))
    if existing_accounts:
        summary = sync_demo_catalog(engine)
        print("Existing accounts and reservations preserved; no passwords changed.")
        print("AzTU-inspired demo catalogue synchronized:", summary)
        print("Note: sample seat counts and lab hours are not verified campus policies.")
        return
    users = {}
    for email, role in (("student@unireserve.test", "STUDENT"),
                        ("staff@unireserve.test", "STAFF"),
                        ("admin@unireserve.test", "ADMIN")):
        password = secrets.token_urlsafe(15)
        uid = provision_demo_user(engine, email, password, role)
        users[email] = (password, uid)
    summary = sync_demo_catalog(engine)
    print(f"Created 3 users and AzTU-inspired sample seat/PC catalogue in {db_path}:", summary)
    print("DEMO CREDENTIALS — keep these private; they are shown only once:\n")
    for email, (password, _) in users.items():
        print(f"  {email}  /  {password}")
    print("\nStart: python scripts/run_web.py  |  Browser: http://127.0.0.1:5000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "instance" / "unireserve.sqlite3"))
    args = parser.parse_args()
    seed(args.db)
