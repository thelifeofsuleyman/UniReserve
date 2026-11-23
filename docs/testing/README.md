# UniReserve testing deliverables

- [Test plan](TEST_PLAN.md) — levels, tools, entry/exit criteria and systematic techniques.
- [Test case catalogue](TEST_CASES.md) — ID, requirement, input, expected, actual, pass/fail and exact code test.
- [Test report](M6_TEST_REPORT.md) — verified CI evidence, 94% coverage, concurrency and status integrity.
- [Performance probe](M6_PERFORMANCE_REPORT.md) — NFR-001 measurements and limits.
- [Defect log](DEFECT_LOG.md) — real observed setup/design issues and the absence of invented bugs.

Run `python scripts/run_tests.py` then `python scripts/measure_latency.py`; the GitHub Actions workflow runs both with Python 3.11 and fails if the required checks are not satisfied.
