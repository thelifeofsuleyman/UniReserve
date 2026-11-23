# NFR-001 HTTP Latency Probe

**Source:** `scripts/measure_latency.py`  
**Method:** Seed 100 resources and 1,000 synthetic confirmed reservations into a temporary SQLite database. Authenticate one test user, warm up five HTTP requests, then time 200 **sequential** Flask test-client requests (100 catalogue and 100 current-status queries). The target from the SRS is >=95% of requests completing within 1.0 second, server side. This is not a network latency, multi-user load or physical occupancy test.

**Measured result:** **PASS** in [GitHub Actions run 45103990514](https://github.com/thelifeofsuleyman/UniReserve/actions/runs/45103990514), Python **3.11.18**, Ubuntu Linux-7.0.0-1020-azure-x86_64. Recorded 23 November 2026.

| Metric | Measured value |
|---|---:|
| Catalogue requests | 100 |
| Availability status requests | 100 |
| Resources / reservations | 100 / 1,000 |
| Warm-up excluded | 5 |
| p95 server-side elapsed | **0.03152 seconds** |
| Mean server-side elapsed | **0.01570 seconds** |
| Maximum elapsed | **0.03251 seconds** |
| Requests within 1.0 second | **200/200 (100%)** |
| >=95% below 1s target | **PASS** |

Exact machine-readable measurement is the `PERF_RESULT=` line in the CI job logs. One CI execution is not a production speed guarantee.

## Interpreting the result

Performance is runner-specific and may fluctuate. A measured local/CI pass is evidence for this synthetic fixture and environment only, not a scalability guarantee. SQLite's single-writer database model and the Flask development server are unsuitable for production workload claims.
