"""Apply AzTU-inspired catalogue to existing demo DB; preserve every booking.

Usage: python scripts/sync_aztu_demo.py
       python scripts/sync_aztu_demo.py --db instance/unireserve.sqlite3
This script should be run only against an intended local demo database.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from unireserve.storage.db import make_engine, create_schema
from unireserve.storage.aztu_demo import sync_demo_catalog

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "instance" / "unireserve.sqlite3"))
    args = parser.parse_args()
    engine = make_engine(args.db)
    create_schema(engine)
    print(sync_demo_catalog(engine))
    print("Old demo gear archived, not deleted. Existing reservations kept. New sample seats and PCs listed.")
