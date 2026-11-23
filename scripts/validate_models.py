#!/usr/bin/env python3
"""Static consistency tests for the UniReserve engineering design.

This is a DOCUMENT consistency gate, not a substitute for integration tests or
PlantUML rendering. CI also parses and exports every PlantUML source.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "diagrams" / "source"
SRS = ROOT / "docs" / "requirements" / "SRS-v1.md"
USECASES = ROOT / "docs" / "requirements" / "USE_CASES-v1.md"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    srs = SRS.read_text(encoding="utf-8")
    usecases = USECASES.read_text(encoding="utf-8")
    diagrams = {p.name: p.read_text(encoding="utf-8") for p in SRC.glob("*.puml")}
    check(len(diagrams) == 16, f"expected 16 diagrams, got {len(diagrams)}")
    for name, body in diagrams.items():
        check(body.count("@startuml") == 1 and body.count("@enduml") == 1, f"invalid wrapper {name}")
        check("title " in body, f"missing diagram title {name}")
    fr = set(re.findall(r"^\|\s*(FR-\d{3})\s*\|", srs, re.M))
    nfr = set(re.findall(r"^\|\s*(NFR-\d{3})\s*\|", srs, re.M))
    check(fr == {f"FR-{i:03}" for i in range(1, 19)}, "incomplete SRS FR IDs")
    check(nfr == {f"NFR-{i:03}" for i in range(1, 9)}, "incomplete SRS NFR IDs")
    check("### 5.1 Must requirement acceptance criteria" in srs, "missing acceptance criteria")
    must_ids = set(re.findall(r"^\|\s*(FR-\d{3})\s*\|\s*Must\s*\|", srs, re.M))
    ac_area = srs.split("### 5.1 Must requirement acceptance criteria", 1)[1].split("## 6.", 1)[0]
    for ident in must_ids:
        check(bool(re.search(r"^\|\s*" + re.escape(ident) + r"\s*\|", ac_area, re.M)), f"missing acceptance criteria {ident}")

    check("CR-001" in diagrams["14-seq-CR-001-studio.puml"], "CR-001 sequence missing")
    check("entity \"spaces\"" in diagrams["15-aztu-space-extension.puml"] and "entity \"space_closures\"" in diagrams["15-aztu-space-extension.puml"], "AzTU extension missing area or closure")
    check("BEGIN IMMEDIATE" in diagrams["16-aztu-booking-hours-sequence.puml"], "AzTU booking sequence must recheck inside transaction")
    uc_diagram = diagrams["01-use-cases.puml"]
    for n in range(1, 7):
        code = f"UC-{n:02}"
        check(code in usecases, f"missing textual use case {code}")
        check(code in uc_diagram, f"missing UML use case {code}")
        matches = [name for name in diagrams if f"seq-{code}-" in name]
        check(len(matches) == 1, f"missing or duplicate sequence diagram {code}")
        check(code in diagrams[matches[0]], f"missing sequence use-case label {code}")

    # Conceptual entities match the logical ERD and named design classes.
    for entity in ("User", "Resource", "Reservation", "ReservationEvent"):
        for f in ("02-domain-model.puml", "04-erd-conceptual.puml", "05-erd-logical-3nf.puml", "06-design-classes.puml"):
            check(entity in diagrams[f], f"{entity} missing from {f}")

    logical = diagrams["05-erd-logical-3nf.puml"]
    for fk in ("user_id", "resource_id", "reservation_id", "actor_user_id"):
        check(fk in logical, f"missing FK {fk}")
    check("start_utc < end_utc" in logical, "missing time range constraint")
    check("UNIQUE" in logical, "missing candidate key uniqueness")

    state = diagrams["03-reservation-states.puml"]
    for name in ("PENDING_APPROVAL", "CONFIRMED", "REJECTED", "CANCELLED"):
        check(name in state and name in srs, f"status mismatch {name}")
    for edge in ("PENDING_APPROVAL --> CONFIRMED", "PENDING_APPROVAL --> REJECTED",
                 "PENDING_APPROVAL --> CANCELLED", "CONFIRMED --> CANCELLED"):
        check(edge in state, f"required transition missing {edge}")
    check("rechecked atomically" in state, "approval transaction invariant not documented")

    booking = diagrams["10-seq-UC-03-request.puml"]
    approval = diagrams["12-seq-UC-05-approve.puml"]
    for label, source in (("request", booking), ("approval", approval)):
        for phrase in ("BEGIN IMMEDIATE", "find_confirmed_overlaps", "rollback()", "commit()", "append"):
            check(phrase in source, f"{label} lacks {phrase}")
    check("PENDING_APPROVAL" in booking and "CONFIRMED" in booking, "request path status mismatch")
    check("remains pending" in approval, "approval conflict must not silently reject request")
    check("actor" in diagrams["06-design-classes.puml"].lower(), "actor link in design model missing")
    check("SQLiteUnitOfWork" in diagrams["07-architecture.puml"], "missing transactional component")
    check("3NF" in (ROOT / "docs" / "diagrams" / "README.md").read_text(encoding="utf-8"), "missing normalization explanation")
    print(f"Model consistency PASS: {len(diagrams)} PlantUML sources, {len(fr)} FRs, {len(nfr)} NFRs, 6 use cases, {len(must_ids)} Must acceptance criteria.")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, OSError) as exc:
        print(f"Model consistency FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
