#!/usr/bin/env python3
"""Independent preservation and overlay checker for cube v6."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json"
V5 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json"
INTERFACE = ROOT / "foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
SOURCE = "CLASSICAL_STANDARD|KREIN_INDEFINITE|PHYSICAL_STATE_SELECTION"
TARGET = "CLASSICAL_STANDARD|KREIN_INDEFINITE|GENERATOR_SPECTRAL_DYNAMICS"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("interface_revision")) for cell in cells],
        "interfaces": interfaces,
    }
    encoded = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old = load(V5)
    interface = load(INTERFACE)["interface"]
    errors: list[str] = []
    cells = result.get("cells", [])
    current = {coordinate(cell): cell for cell in cells}
    prior = {coordinate(cell): cell for cell in old["cells"]}
    if len(cells) != 452 or set(current) != set(prior):
        errors.append("v5 coordinate preservation")
    for key, cell in current.items():
        source = prior[key]
        for field in ("migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation"):
            if cell.get(field) != source.get(field):
                errors.append("migration preservation " + key)
                break
        if key not in (SOURCE, TARGET) and cell != source:
            errors.append("untouched cell drift " + key)
            break
    for key, role in ((SOURCE, "SOURCE"), (TARGET, "TARGET")):
        cell = current.get(key, {})
        revision = cell.get("interface_revision", {})
        if cell.get("status") != "LOCAL_RESULT" or cell.get("evidence_roles", {}).get(EVIDENCE_ID) != "DIRECT_LOCAL" or revision.get("role") != role or revision.get("status_change") is not False:
            errors.append("endpoint overlay " + key)
    interfaces = result.get("certified_interfaces", [])
    if interfaces != [*old.get("certified_interfaces", []), interface] or [item.get("id") for item in interfaces] != ["STATE_TO_PROBABILITY", "SELECTION_TO_DYNAMICS"]:
        errors.append("interface ledger preservation/append")
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
    if dimensions.get("coverage_classified_cells") != 371 or dimensions.get("certified_cross_cell_interfaces") != 2 or dimensions.get("new_interface_target_promotions") != 0:
        errors.append("interface dimensions")
    calculated = digest(cells, interfaces)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(cells), "coverage_classified": dimensions.get("coverage_classified_cells"), "certified_interfaces": dimensions.get("certified_cross_cell_interfaces"), "target_promotions": dimensions.get("new_interface_target_promotions"), "status_counts": counts}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
