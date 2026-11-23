# NFR-001 HTTP Latency Probe

**Source:** `scripts/measure_latency.py`  
**Method:** Seed 100 resources and 1,000 synthetic confirmed reservations into a temporary SQLite database. Authenticate one test user, warm up five HTTP requests, then time 200 **sequential** Flask test-client requests (100 catalogue and 100 current-status queries). The target from the SRS is >=95% of requests completing within 1.0 second, server side. This is not a network latency, multi-user load or physical occupancy test.

**Measured result:** pending first verified CI performance run. Capture the exact `PERF_RESULT` line, GitHub run, runner Python version and measured outcome here. Do not substitute an estimated number for a measurement.

## Interpreting the result

Performance is runner-specific and may fluctuate. A measured local/CI pass is evidence for this synthetic fixture and environment only, not a scalability guarantee. SQLite's single-writer database model and the Flask development server are unsuitable for production workload claims.
