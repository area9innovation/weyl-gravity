#!/usr/bin/env python3
"""Independent preservation checker for foundations cube v11."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json"
V10 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json"
THEOREM = ROOT / "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1"

EXPECTED = {
    "WEAK_ARITHMETIC|HILBERT_OPERATOR|KINEMATICS_OBSERVABLES": ("PIECES_ONLY", "LOCAL_RESULT"),
    "WEAK_ARITHMETIC|HILBERT_OPERATOR|RECONSTRUCTION_LIMITS": ("LITERATURE_RESULT", "LOCAL_RESULT"),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def key(cell: dict[str, Any]) -> str:
    return "|".join(cell[name] for name in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]], carrier_interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(key(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision"), cell.get("bt_euclidean_revision"), cell.get("observable_reconstruction_revision")) for cell in cells],
        "interfaces": interfaces,
        "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old, theorem = load(V10), load(THEOREM)
    errors: list[str] = []
    current = {key(cell): cell for cell in result.get("cells", [])}
    prior = {key(cell): cell for cell in old.get("cells", [])}
    if len(current) != 576 or set(current) != set(prior):
        errors.append("exact preserved 576-cell surface")
    changed = 0
    for coordinate, old_cell in prior.items():
        cell = current.get(coordinate)
        if cell is None:
            continue
        if coordinate not in EXPECTED:
            if cell != old_cell:
                errors.append("undeclared v10 cell drift " + coordinate)
                break
            continue
        changed += 1
        previous, new = EXPECTED[coordinate]
        revision = cell.get("observable_reconstruction_revision", {})
        if old_cell.get("status") != previous or cell.get("status") != new or revision != {"certificate": EVIDENCE_ID, "previous_status": previous, "new_status": new, "evidence_role": "DIRECT_LOCAL"}:
            errors.append("declared reconstruction revision " + coordinate)
        if EVIDENCE_ID not in cell.get("evidence", []) or cell.get("evidence_roles", {}).get(EVIDENCE_ID) != "DIRECT_LOCAL":
            errors.append("direct local reconstruction evidence " + coordinate)
        for field in ("foundation", "carrier", "obligation", "migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation", "classification_revision", "interface_revision", "bt_euclidean_revision"):
            if cell.get(field) != old_cell.get(field):
                errors.append("unscoped field drift " + coordinate + " " + field)
                break
    if changed != 2:
        errors.append("exact two changed cells")
    for coordinate, cell in current.items():
        if sorted(cell.get("evidence", [])) != sorted(cell.get("evidence_roles", {})):
            errors.append("evidence-role closure " + coordinate)
            break
    counts_counter = Counter(cell.get("status") for cell in current.values())
    expected_counts = {"LITERATURE_RESULT": 90, "LOCAL_RESULT": 122, "NOT_MAPPED": 0, "PIECES_ONLY": 162, "PRIORITY_GAP": 30, "REVIEWED_GAP": 172}
    counts = {name: counts_counter.get(name, 0) for name in expected_counts}
    if counts != expected_counts or result.get("dimensions", {}).get("status_counts") != dict(sorted(expected_counts.items())):
        errors.append("status counts")
    if result.get("certified_interfaces") != old.get("certified_interfaces") or result.get("certified_carrier_interfaces") != old.get("certified_carrier_interfaces"):
        errors.append("interface preservation")
    flags = theorem.get("claim_flags", {})
    if flags.get("uniform_bounded_time_convergence_proved") is not True or flags.get("explicit_cutoff_function_proved") is not True or flags.get("causal_support_proved") is not False:
        errors.append("source theorem boundary")
    calculated = digest(result.get("cells", []), result.get("certified_interfaces", []), result.get("certified_carrier_interfaces", []))
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(current), "changed_cells": changed, "status_counts": counts}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
