#!/usr/bin/env python3
"""Independent preservation and import checker for cube v10."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json"
V9 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json"
IMPORT = ROOT / "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def key(coordinate: dict[str, str]) -> str:
    return "|".join(coordinate[name] for name in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], cross_interfaces: list[dict[str, Any]], carrier_interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(key(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision"), cell.get("bt_euclidean_revision")) for cell in cells],
        "cross_interfaces": cross_interfaces,
        "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old, imported = load(V9), load(IMPORT)
    errors: list[str] = []
    current = {key(cell): cell for cell in result.get("cells", [])}
    prior = {key(cell): cell for cell in old["cells"]}
    decisions = {key(item["coordinate"]): item for item in imported["capability_decisions"]}
    if len(current) != 576 or set(current) != set(prior):
        errors.append("exact preserved 576-cell surface")
    changed = 0
    for coordinate_key, old_cell in prior.items():
        cell = current.get(coordinate_key)
        if cell is None:
            continue
        decision = decisions.get(coordinate_key)
        if decision is None:
            if cell != old_cell:
                errors.append("undeclared v9 cell drift " + coordinate_key)
                break
            continue
        changed += 1
        revision = cell.get("bt_euclidean_revision", {})
        expected_revision = {
            "certificate": EVIDENCE_ID,
            "previous_status": old_cell["status"],
            "new_status": decision["new_status"],
            "evidence_role": decision["evidence_role"],
            "status_change": decision["status_change"],
        }
        if revision != expected_revision or cell.get("status") != decision["new_status"]:
            errors.append("declared revision " + coordinate_key)
            break
        if cell.get("evidence_roles", {}).get(EVIDENCE_ID) != decision["evidence_role"] or EVIDENCE_ID not in cell.get("evidence", []):
            errors.append("import evidence role " + coordinate_key)
            break
        if cell.get("summary") != decision["finding"] or cell.get("boundary") != decision["boundary"]:
            errors.append("import decision text " + coordinate_key)
            break
        for field in ("foundation", "carrier", "obligation", "migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation", "classification_revision", "interface_revision"):
            if cell.get(field) != old_cell.get(field):
                errors.append("unscoped field drift " + coordinate_key + " " + field)
                break

    for coordinate_key, cell in current.items():
        if sorted(cell.get("evidence_roles", {})) != sorted(cell.get("evidence", [])):
            errors.append("evidence role closure " + coordinate_key)
            break
    counts_counter = Counter(cell.get("status") for cell in current.values())
    expected_counts = {"LITERATURE_RESULT": 91, "LOCAL_RESULT": 120, "NOT_MAPPED": 0, "PIECES_ONLY": 163, "PRIORITY_GAP": 30, "REVIEWED_GAP": 172}
    counts = {name: counts_counter.get(name, 0) for name in expected_counts}
    if counts != expected_counts or result.get("dimensions", {}).get("status_counts") != dict(sorted(expected_counts.items())):
        errors.append("status counts")
    if changed != 6:
        errors.append("exact six changed cells")
    if result.get("certified_interfaces") != old.get("certified_interfaces"):
        errors.append("cross-cell interface preservation")
    carrier_interfaces = result.get("certified_carrier_interfaces", [])
    if carrier_interfaces != [imported.get("carrier_interface")]:
        errors.append("carrier interface projection")
    calculated = digest(result.get("cells", []), result.get("certified_interfaces", []), carrier_interfaces)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(current), "changed_cells": changed, "status_counts": counts}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
