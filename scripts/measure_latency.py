"""Reproducible local HTTP latency probe for NFR-001.

The 200 requests are sequential, not a throughput or multi-user benchmark.
Used on GitHub Actions Ubuntu/Python 3.11; results are environment-specific.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import json
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy.orm import Session
from unireserve.storage.accounts import provision_demo_user
from unireserve.storage.models import Resource, Reservation
from unireserve.web.app import create_app


def run_probe() -> dict:
    with TemporaryDirectory(prefix="uni-perf-") as tmp:
        app = create_app({"TESTING": True, "SECRET_KEY": "nfr001-test-key", "DB_PATH": str(Path(tmp) / "performance.sqlite3")})
        engine = app.extensions["unireserve_engine"]
        uid = provision_demo_user(engine, "perf@unireserve.test", "non-production-secret-for-test", "STUDENT")
        moment = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
        # 100 resources and 1,000 reservations: 10 nonoverlapping future
        # intervals per resource, spanning 10 days. These are synthetic rows.
        with Session(engine) as db:
            resources = [Resource(public_code=f"PERF-{i:03}", name=f"Room or equipment {i}",
                category="ROOM" if i % 2 else "EQUIPMENT", requires_approval=False, is_enabled=True)
                for i in range(100)]
            db.add_all(resources)
            db.flush()
            for resource in resources:
                for n in range(10):
                    start = moment + timedelta(days=n + 1, hours=1)
                    db.add(Reservation(user_id=uid, resource_id=resource.id,
                        start_utc=start, end_utc=start + timedelta(minutes=30),
                        status="CONFIRMED", created_utc=moment))
            db.commit()
        client = app.test_client()
        client.get('/login')
        with client.session_transaction() as sess:
            token = sess["csrf_token"]
        login = client.post('/login', data={"email": "perf@unireserve.test",
                           "password": "non-production-secret-for-test", "csrf_token": token})
        if login.status_code != 302:
            raise RuntimeError(f"Performance login failed: HTTP {login.status_code}")
        paths = ['/resources', '/api/availability-status']
        timings = []
        # 5 warm-up requests excluded from timing.
        for i in range(5):
            response = client.get(paths[i % 2])
            if response.status_code != 200:
                raise RuntimeError("Warm-up HTTP failure")
        for i in range(200):
            start = perf_counter()
            response = client.get(paths[i % 2])
            elapsed = perf_counter() - start
            if response.status_code != 200:
                raise RuntimeError(f"Request #{i} returned HTTP {response.status_code}")
            timings.append(elapsed)
        sorted_times = sorted(timings)
        p95 = sorted_times[ceil(0.95 * len(sorted_times)) - 1]
        result = {
            "requirement": "NFR-001", "resource_count": 100,
            "reservation_count": 1000, "requests": 200,
            "catalogue_requests": 100, "availability_requests": 100,
            "sequential": True, "warmup_requests_excluded": 5,
            "python": platform.python_version(), "system": platform.platform(),
            "p95_seconds": round(p95, 5),
            "max_seconds": round(max(timings), 5),
            "mean_seconds": round(sum(timings) / len(timings), 5),
            "within_1s_count": sum(x <= 1.0 for x in timings),
            "within_1s_fraction": round(sum(x <= 1.0 for x in timings) / len(timings), 3),
            "target_95pct_below_1s": sum(x <= 1.0 for x in timings) >= 190,
        }
        engine.dispose()
        return result


if __name__ == '__main__':
    result = run_probe()
    print('PERF_RESULT=' + json.dumps(result, sort_keys=True))
    if not result['target_95pct_below_1s']:
        print('NFR-001 latency target not reached', file=sys.stderr)
        raise SystemExit(1)
