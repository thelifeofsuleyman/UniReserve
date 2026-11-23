# Individual Reflection — UniReserve

**Student:** Suleyman Shafizada (m666i1)  
**Software Engineering individual project · Draft for my own review before submission**  
**Date:** 23 November 2026

## Requirements I discovered late and their cost

The short project idea initially sounded like a simple calendar for reserving university rooms and equipment. The first serious problem was deciding what an unapproved request meant. If pending requests blocked capacity, unused requests could occupy a resource indefinitely. I selected the alternative: only confirmed reservations block time, and approval checks availability again inside a SQLite write transaction. This required careful state transitions, an additional approval error path, and concurrency and rollback tests.

The more significant change came from reviewing the actual interface. The first version was functional but too generic, with repetitive equipment cards. I wanted a more useful visual model of university study spaces, particularly PCs and individual library desks. That led to four change requests: a 2D live-status view (CR-001); an AzTU-inspired focus on study seats, PCs and hours (CR-002); clearer visuals and fair-use restrictions (CR-003); and matching photographs plus logically arranged room plans (CR-004). The first room map also appeared empty on my existing local database because the new sample catalogue had not yet been synchronized. This exposed an onboarding problem, not a lack of booking logic. We added an idempotent local demo sync that archives obsolete sample equipment without deleting existing reservations or audit history.

The cost was substantial relative to the small assignment: requirements, diagrams, UI, database tables, tests and documentation all needed reconciliation. Public AzTU material confirmed facility types but not exact seats, reservation permissions or class schedules, so the application must call these **demonstration assumptions**, not official university rules.

## Design and implementation differences

My first design used four core entities and separate repository interfaces and service classes. As the requirements evolved, the working SQLAlchemy model gained \`Space\` and \`SpaceClosure\` for operating hours and teaching/maintenance closures, bringing the current schema to six main tables. Some conceptual repository abstractions remain design-level patterns rather than one-to-one Python classes. The implementation uses SQLAlchemy sessions, Flask's signed sessions and a transaction context manager to stay manageable for an individual project.

The 2D maps deliberately use schematic desks, aisles, a teaching board and one whole-room booking control for the group room. The six chairs pictured in the group room are **not** six separate booking units. The images are original AI-generated illustrations, not surveyed AzTU photographs. Availability colors are calculated from stored confirmed bookings, not physical occupancy sensors.

## How I checked quality and what I would do differently

My most important tests address race conditions, denial of unauthorized actions, double booking, approval after another booking, invalid opening hours, audit rollback and legacy database migration. The final recorded GitHub Actions run passed **123 automated tests with 94% statement coverage** and a synthetic 200-request latency check, but coverage cannot prove that a student finds the interface easy to use or that it is production-secure. A five-volunteer usability experiment and complete keyboard-only review remain unmeasured and must not be claimed.

If I repeated the project, I would agree on booking scope and actual campus policies earlier, prototype representative room layouts before building a large resource list, and test an upgrade from the old demo database sooner. For a real campus deployment I would also plan university authentication, tested backups and stronger production infrastructure.

## AI assistance disclosure

ChatGPT contributed extensively to requirements drafting, external-system comparisons, implementation, UML plans, generated imagery, automated-test development, code review and documentation. I supplied product direction and feedback during development. GitHub commits and CI runs provide independently inspectable technical evidence; they are not evidence that I performed unrecorded interviews or independent usability studies. **Before submission, I must read, revise and approve this reflection in my own words and be able to explain the main decisions and code.**
