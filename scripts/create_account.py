"""Provision an actual login without generating published sample accounts.

Usage: python scripts/create_account.py --email admin@example.edu --role ADMIN
"""
from __future__ import annotations
import argparse
from getpass import getpass
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from unireserve.storage.accounts import provision_user
from unireserve.storage.db import make_engine,create_schema

def main() -> None:
    p=argparse.ArgumentParser(description="Provision a single UniReserve account")
    p.add_argument("--email",required=True)
    p.add_argument("--role",choices=("STUDENT","STAFF","ADMIN"),required=True)
    p.add_argument("--db",default=os.environ.get("UNIRESERVE_DB_PATH",str(ROOT/"instance"/"unireserve.sqlite3")))
    args=p.parse_args()
    first=getpass("New password (12+ characters recommended): ")
    second=getpass("Confirm password: ")
    if first != second:
        raise SystemExit("Passwords did not match; no account created")
    if len(first) < 12:
        raise SystemExit("Choose a password with at least 12 characters")
    engine=make_engine(args.db)
    try:
        create_schema(engine)
        new_id=provision_user(engine,args.email,first,args.role)
    finally:
        engine.dispose()
    print(f"Created {args.role} account {args.email} (ID {new_id}). No password was printed.")

if __name__=="__main__":
    main()
