# CR-005 — Traceability

| Requirement or finding | Code / design | Tests |
|---|---|---|
| FR-001, FR-010, NFR-003/004: signed sessions and secure hosting | `web/app.py`, `storage/accounts.py`, `scripts/create_account.py`, `scripts/serve_production.py` | `tests/test_cr005_production.py` and existing web security tests |
| FR-002/003: understandable availability interface | Jinja templates, `/about`, existing `studio.js` status logic | CR-005 public copy and earlier visual tests |
| FR-009 / UC-06: admin-manageable Spaces and Resource items | `BookingService.create_space`, `/admin/spaces`, `admin.html` | `tests/test_cr005_spacemanagement.py` |
| NFR-005 and operational durability | Persisted SQLite path, `/healthz`, Waitress and documented backup plan | Production health/config test; backup restoration remains an operational gap |
| Change management | CR-005 log, SRS addendum, test/trace addenda, refreshed PDFs | `scripts/build_submission_docs.py`, GitHub PDF validator |

No new ERD entity or change to pending/confirmed overlap semantics; deployment is a separate concern from booking logic.
