#!/usr/bin/env python3
"""Independent checker for the v2 migration decision ledger."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
V0 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
V1 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(decisions: list[dict[str, Any]]) -> str:
    payload = [(x.get("coordinate"), x.get("v0_parent_status"), x.get("review_batch"), x.get("decision"), x.get("resulting_coverage_status"), x.get("parent_evidence")) for x in decisions]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if result is None else result
    v0, v1 = load(V0), load(V1)
    errors: list[str] = []
    pending = {"|".join(x[k] for k in ("foundation", "carrier", "obligation")): x for x in v1["cells"] if x["status"] == "MIGRATION_UNRESOLVED"}
    decisions = result.get("decisions", [])
    by_coordinate = {x.get("coordinate"): x for x in decisions}
    if len(pending) != 112 or len(decisions) != 112 or len(by_coordinate) != 112 or set(by_coordinate) != set(pending):
        errors.append("112-coordinate pending partition")
    parents = {(x["foundation"], x["carrier"], x["obligation"]): x for x in v0["cells"]}
    for coordinate, decision in by_coordinate.items():
        cell = pending.get(coordinate, {})
        parent = parents.get((cell.get("foundation"), cell.get("carrier"), cell.get("parent_obligation")), {})
        if decision.get("v0_parent_status") != parent.get("status") or decision.get("parent_evidence") != cell.get("evidence"):
            errors.append("v0/v1 reconstruction " + str(coordinate))
        if decision.get("decision") == "REVIEWED_NO_TRANSFER":
            if not decision.get("parent_evidence") or decision.get("resulting_coverage_status") != "NOT_MAPPED" or "not a literature-absence claim" not in decision.get("boundary", ""):
                errors.append("no-transfer boundary " + str(coordinate))
        elif decision.get("decision") == "REVIEWED_CHILD_GAP":
            if decision.get("parent_evidence") or parent.get("status") != "PRIORITY_GAP" or decision.get("resulting_coverage_status") != "PRIORITY_GAP" or "not proof of literature absence" not in decision.get("boundary", ""):
                errors.append("child-gap boundary " + str(coordinate))
        else:
            errors.append("decision closure " + str(coordinate))
        if not decision.get("rationale"):
            errors.append("missing rationale " + str(coordinate))
    counts = Counter(x.get("decision") for x in decisions)
    priorities = Counter(x.get("review_priority") for x in decisions)
    batches = result.get("evidence_batches", [])
    if len(batches) != 18 or len({x.get("id") for x in batches}) != 18 or sum(x.get("cell_count", 0) for x in batches) != 88:
        errors.append("18 evidence batches")
    expected_counts = {"REVIEWED_CHILD_GAP": 24, "REVIEWED_NO_TRANSFER": 88}
    expected_priorities = {"EMPTY_PARENT_GAP_DECOMPOSITION": 24, "PIECES_DESCENDANT_BATCH": 76, "RESULT_DESCENDANT_FIRST": 12}
    summary = result.get("summary", {})
    if dict(sorted(counts.items())) != expected_counts or summary.get("decision_counts") != expected_counts:
        errors.append("decision counts")
    if dict(sorted(priorities.items())) != expected_priorities or summary.get("priority_counts") != expected_priorities:
        errors.append("priority counts")
    calculated = digest(decisions)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "decisions": len(decisions), "reviewed_no_transfer": counts["REVIEWED_NO_TRANSFER"], "reviewed_child_gap": counts["REVIEWED_CHILD_GAP"], "evidence_batches": len(batches), "result_descendants": priorities["RESULT_DESCENDANT_FIRST"], "pieces_descendants": priorities["PIECES_DESCENDANT_BATCH"], "pending_after": summary.get("pending_after_audit")}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
