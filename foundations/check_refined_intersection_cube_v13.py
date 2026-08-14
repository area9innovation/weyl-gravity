#!/usr/bin/env python3
"""Independent preservation checker for foundations cube v13."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json"
V12 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V12.json"
THEOREM = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1"
EXPECTED = {
    "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|KINEMATICS_OBSERVABLES": ("LOCAL_RESULT", "LOCAL_RESULT", "DIRECT_LOCAL"),
    "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|STATE_REPRESENTATION": ("REVIEWED_GAP", "LOCAL_RESULT", "DIRECT_LOCAL"),
    "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS": ("PIECES_ONLY", "LOCAL_RESULT", "DIRECT_LOCAL"),
    "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|RECONSTRUCTION_LIMITS": ("PIECES_ONLY", "PIECES_ONLY", "SUPPORTING"),
}


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text())
def key(cell: dict[str, Any]) -> str: return "|".join(cell[name] for name in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]], carrier_interfaces: list[dict[str, Any]]) -> str:
    projection = {"cells": [(key(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision"), cell.get("bt_euclidean_revision"), cell.get("observable_reconstruction_revision"), cell.get("local_weak_wave_revision"), cell.get("h2_test_completion_revision")) for cell in cells], "interfaces": interfaces, "carrier_interfaces": carrier_interfaces}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old, theorem = load(V12), load(THEOREM)
    errors: list[str] = []
    current, prior = ({key(cell): cell for cell in data.get("cells", [])} for data in (result, old))
    if len(current) != 576 or set(current) != set(prior): errors.append("exact preserved 576-cell surface")
    changed = status_changes = 0
    preserved_fields = ("foundation", "carrier", "obligation", "migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation", "classification_revision", "interface_revision", "bt_euclidean_revision", "observable_reconstruction_revision", "local_weak_wave_revision")
    for coordinate, old_cell in prior.items():
        cell = current.get(coordinate)
        if cell is None: continue
        if coordinate not in EXPECTED:
            if cell != old_cell: errors.append("undeclared v12 cell drift " + coordinate); break
            continue
        changed += 1
        previous, new, role = EXPECTED[coordinate]; status_changes += previous != new
        expected_revision = {"previous_status": previous, "new_status": new, "evidence_role": role, "certificate": EVIDENCE_ID}
        if old_cell.get("status") != previous or cell.get("status") != new or cell.get("h2_test_completion_revision") != expected_revision:
            errors.append("declared H2 revision " + coordinate)
        if EVIDENCE_ID not in cell.get("evidence", []) or cell.get("evidence_roles", {}).get(EVIDENCE_ID) != role:
            errors.append("typed H2 evidence " + coordinate)
        for field in preserved_fields:
            if cell.get(field) != old_cell.get(field): errors.append("unscoped field drift " + coordinate + " " + field); break
    if changed != 4 or status_changes != 2: errors.append("exact four evidence augmentations and two status changes")
    for coordinate, cell in current.items():
        if sorted(cell.get("evidence", [])) != sorted(cell.get("evidence_roles", {})): errors.append("evidence-role closure " + coordinate); break
    expected_counts = {"LITERATURE_RESULT": 90, "LOCAL_RESULT": 125, "NOT_MAPPED": 0, "PIECES_ONLY": 162, "PRIORITY_GAP": 30, "REVIEWED_GAP": 169}
    counter = Counter(cell.get("status") for cell in current.values()); counts = {name: counter.get(name, 0) for name in expected_counts}
    if counts != expected_counts or result.get("dimensions", {}).get("status_counts") != dict(sorted(expected_counts.items())): errors.append("status counts")
    if result.get("certified_interfaces") != old.get("certified_interfaces") or result.get("certified_carrier_interfaces") != old.get("certified_carrier_interfaces"): errors.append("interface preservation")
    flags = theorem.get("claim_flags", {})
    if flags.get("weak_solution_extended_to_every_named_h2_test") is not True or flags.get("full_lf_test_topology_reconstructed") is not False or flags.get("strict_causal_support_proved") is not False: errors.append("source theorem boundary")
    calculated = digest(result.get("cells", []), result.get("certified_interfaces", []), result.get("certified_carrier_interfaces", []))
    if calculated != result.get("independent_checker", {}).get("expected_digest"): errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(current), "evidence_augmented_cells": changed, "status_changes": status_changes, "status_counts": counts}


def main() -> int:
    errors, summary = check(); print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True)); return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
