# Models directory

**Source of truth:** [Architecture design index](diagrams/README.md).  
All 13 UML/ER diagrams are stored in [PlantUML sources](diagrams/source/) and automatically exported to [PNG/SVG](diagrams/rendered/). The source scripts and images must stay aligned.

The current application implements only an overlap rule. The diagrams describe **planned** services, database schema and workflows; do not claim those features pass until integration tests demonstrate them.

Run:
```
python scripts/validate_models.py
python scripts/run_tests.py
```
