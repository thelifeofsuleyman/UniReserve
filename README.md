# UniReserve

**University Equipment and Room Reservation System**

**Student:** Suleyman Shafizada  
**Group:** m666i1  
**Course:** Software Engineering — Individual Project  
**Submission deadline:** 2 December 2026

## Goal

UniReserve is a planned small web application where students and staff can reserve university rooms and equipment. Administrators will manage resources and approve restricted bookings.

**Project status:** Initial development milestone. This is not yet a complete reservation application.

## Proposed stack

- Python 3.11+
- Flask for the web interface
- SQLAlchemy + SQLite for persistent storage
- Python `unittest` for the starter tests
- Modular monolith: presentation, application services, domain logic and persistence

## Run starter tests

```bash
python scripts/run_tests.py
```

The starter business-rule tests use only Python's standard library; full app dependencies will be introduced in later milestones.

## Development priorities

1. Complete requirements specification, assumptions, acceptance criteria and MoSCoW priorities.
2. Analyze at least two existing resource-booking systems.
3. Prepare use cases, UML diagrams, conceptual/logical ERDs and architecture documentation.
4. Implement authentication, resources, reservations, approval, and conflict-safe transactions.
5. Add integration/system testing, coverage, change-management evidence and requirement traceability.

Work is being developed incrementally with Git branches and reviewed changes. Git history should represent actual work, not retroactively manufactured activity.

## Academic integrity

Initial scaffolding and documentation were prepared with ChatGPT assistance. The individual project reflection must accurately disclose AI use, and the student must review and understand all code and design decisions.
