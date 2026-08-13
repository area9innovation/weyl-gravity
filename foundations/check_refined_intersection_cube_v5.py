#!/usr/bin/env python3
"""Independent preservation and promotion checker for cube v5."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json"
V4 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json"
INTERFACE = ROOT / "foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
SOURCE = "CLASSICAL_STANDARD|ALGEBRAIC_CSTAR|STATE_REPRESENTATION"
TARGET = "CLASSICAL_STANDARD|KREIN_INDEFINITE|PROBABILITY_RULE"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]]) -> str:
    projection = [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("interface_revision")) for cell in cells]
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old = load(V4)
    interface = load(INTERFACE)["interface"]
    errors: list[str] = []
    cells = result.get("cells", [])
    current = {coordinate(cell): cell for cell in cells}
    prior = {coordinate(cell): cell for cell in old["cells"]}
    if len(cells) != 452 or set(current) != set(prior):
        errors.append("v4 coordinate preservation")
    for key, cell in current.items():
        source = prior[key]
        for field in ("migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation"):
            if cell.get(field) != source.get(field):
                errors.append("migration preservation " + key)
                break
        if key not in (SOURCE, TARGET) and cell != source:
            errors.append("untouched cell drift " + key)
            break
    if current.get(SOURCE, {}).get("status") != "LOCAL_RESULT" or current.get(SOURCE, {}).get("evidence_roles", {}).get(EVIDENCE_ID) != "DIRECT_LOCAL":
        errors.append("source overlay")
    if prior.get(TARGET, {}).get("status") != "PIECES_ONLY" or current.get(TARGET, {}).get("status") != "LOCAL_RESULT" or current.get(TARGET, {}).get("evidence_roles", {}).get(EVIDENCE_ID) != "DIRECT_LOCAL":
        errors.append("target promotion")
    if result.get("certified_interfaces") != [interface] or interface.get("status") != "CERTIFIED" or interface.get("relation") != "CONDITIONAL_BRIDGE":
        errors.append("certified interface projection")
    for key, cell in current.items():
        roles = cell.get("evidence_roles", {})
        if sorted(roles) != sorted(cell.get("evidence", [])):
            errors.append("evidence role closure " + key)
            break
        direct = [role for role in ("DIRECT_LOCAL", "DIRECT_LITERATURE") if role in roles.values()]
        expected_status = {"DIRECT_LOCAL": "LOCAL_RESULT", "DIRECT_LITERATURE": "LITERATURE_RESULT"}
        if direct and cell.get("status") != expected_status[direct[0]]:
            errors.append("role/status agreement " + key)
            break
    counts = dict(sorted(Counter(cell["status"] for cell in cells).items()))
    expected = {"LITERATURE_RESULT": 93, "LOCAL_RESULT": 89, "NOT_MAPPED": 81, "PIECES_ONLY": 159, "PRIORITY_GAP": 30}
    if counts != expected or result.get("dimensions", {}).get("status_counts") != expected:
        errors.append("status counts")
    dimensions = result.get("dimensions", {})
    if dimensions.get("coverage_classified_cells") != 371 or dimensions.get("certified_cross_cell_interfaces") != 1 or dimensions.get("interface_target_promotions") != 1:
        errors.append("interface dimensions")
    calculated = digest(cells)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(cells), "coverage_classified": dimensions.get("coverage_classified_cells"), "certified_interfaces": dimensions.get("certified_cross_cell_interfaces"), "target_promotions": dimensions.get("interface_target_promotions"), "status_counts": counts}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
