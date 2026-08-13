#!/usr/bin/env python3
"""Independent preservation and ten-promotion checker for cube v7."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json"
V6 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json"
CLOSURE = ROOT / "foundations/results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {"cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision")) for cell in cells], "interfaces": interfaces}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old, closure = load(V6), load(CLOSURE)
    errors: list[str] = []
    cells = result.get("cells", [])
    current = {coordinate(cell): cell for cell in cells}
    prior = {coordinate(cell): cell for cell in old["cells"]}
    decisions = {"|".join(item["coordinate"].values()): item for item in closure["promotions"]}
    if len(cells) != 452 or set(current) != set(prior):
        errors.append("v6 coordinate preservation")
    if len(decisions) != 10:
        errors.append("ten closure decisions")
    changed = set()
    for key, cell in current.items():
        source = prior[key]
        for field in ("migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation"):
            if cell.get(field) != source.get(field):
                errors.append("migration preservation " + key)
                break
        if key not in decisions:
            if cell != source:
                errors.append("untouched cell drift " + key)
                break
            continue
        changed.add(key)
        decision = decisions[key]
        revision = cell.get("classification_revision", {})
        if source.get("status") != "NOT_MAPPED" or cell.get("status") != decision.get("new_status"):
            errors.append("classification status " + key)
        if cell.get("evidence_roles", {}).get(EVIDENCE_ID) != decision.get("evidence_role") or EVIDENCE_ID not in cell.get("evidence", []):
            errors.append("classification evidence " + key)
        if revision != {"certificate": EVIDENCE_ID, "previous_status": "NOT_MAPPED", "new_status": decision.get("new_status"), "evidence_role": decision.get("evidence_role"), "status_change": True}:
            errors.append("classification revision " + key)
        if cell.get("summary") != decision.get("finding") or cell.get("boundary") != decision.get("boundary"):
            errors.append("classification prose " + key)
    if changed != set(decisions):
        errors.append("exact changed coordinates")
    if result.get("certified_interfaces") != old.get("certified_interfaces"):
        errors.append("certified interface preservation")
    for key, cell in current.items():
        roles = cell.get("evidence_roles", {})
        if sorted(roles) != sorted(cell.get("evidence", [])):
            errors.append("evidence role closure " + key)
            break
        direct = [role for role in ("DIRECT_LOCAL", "DIRECT_LITERATURE") if role in roles.values()]
        expected = {"DIRECT_LOCAL": "LOCAL_RESULT", "DIRECT_LITERATURE": "LITERATURE_RESULT"}
        if direct and cell.get("status") != expected[direct[0]]:
            errors.append("role/status agreement " + key)
            break
    counts = dict(sorted(Counter(cell["status"] for cell in cells).items()))
    expected_counts = {"LITERATURE_RESULT": 93, "LOCAL_RESULT": 98, "NOT_MAPPED": 71, "PIECES_ONLY": 160, "PRIORITY_GAP": 30}
    dimensions = result.get("dimensions", {})
    if counts != expected_counts or dimensions.get("status_counts") != expected_counts:
        errors.append("status counts")
    expected_dimension_values = {"coverage_classified_cells": 381, "newly_classified_cells": 10, "new_local_result_cells": 9, "new_pieces_only_cells": 1, "reviewed_no_transfer_unmapped_cells": 71, "reviewed_no_transfer_classified_cells": 17, "certified_cross_cell_interfaces": 2}
    for key, expected in expected_dimension_values.items():
        if dimensions.get(key) != expected:
            errors.append("dimension " + key)
    calculated = digest(cells, result.get("certified_interfaces", []))
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    summary = {"digest": calculated, "cells": len(cells), "changed": len(changed), "coverage_classified": dimensions.get("coverage_classified_cells"), "reviewed_no_transfer_unmapped": dimensions.get("reviewed_no_transfer_unmapped_cells"), "status_counts": counts}
    return errors, summary


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
