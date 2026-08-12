#!/usr/bin/env python3
"""Independent structural checker for FOUNDATIONAL_INTERSECTION_CUBE_V1."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
V0 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
STATUSES = {"LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "MIGRATION_UNRESOLVED"}
ONE_TO_ONE = {"KINEMATICS_OBSERVABLES", "GAUGE_BV_COHOMOLOGY", "RECONSTRUCTION_LIMITS"}
EXPECTED_OVERLAYS = {
    ("CLASSICAL_STANDARD", "FINITE_EXACT", "INTERACTION_CONSTRUCTION"),
    ("WEAK_ARITHMETIC", "FINITE_EXACT", "INTERACTION_CONSTRUCTION"),
    ("WEAK_CHOICE_ZF", "FINITE_EXACT", "INTERACTION_CONSTRUCTION"),
    ("CONSTRUCTIVE_COMPUTABLE", "FINITE_EXACT", "INTERACTION_CONSTRUCTION"),
    ("FINITE_DISCRETE", "FINITE_EXACT", "INTERACTION_CONSTRUCTION"),
    ("WEAK_ARITHMETIC", "FINITE_EXACT", "GENERATOR_SPECTRAL_DYNAMICS"),
    ("WEAK_ARITHMETIC", "FINITE_EXACT", "EVOLUTION_WELLPOSEDNESS"),
    ("WEAK_ARITHMETIC", "SMOOTH_DISTRIBUTIONAL", "EVOLUTION_WELLPOSEDNESS"),
    ("WEAK_ARITHMETIC", "SMOOTH_DISTRIBUTIONAL", "CAUSAL_PROPAGATION_GREEN"),
    ("CONSTRUCTIVE_COMPUTABLE", "SMOOTH_DISTRIBUTIONAL", "EVOLUTION_WELLPOSEDNESS"),
    ("CONSTRUCTIVE_COMPUTABLE", "SMOOTH_DISTRIBUTIONAL", "CAUSAL_PROPAGATION_GREEN"),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canonical_digest(cells: list[dict[str, Any]]) -> str:
    payload = [(x.get("foundation"), x.get("carrier"), x.get("obligation"), x.get("status"), x.get("migration_relation"), x.get("evidence")) for x in cells]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None, v0: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if result is None else result
    v0 = load(V0) if v0 is None else v0
    errors: list[str] = []
    axes = result.get("axes", [])
    if [axis.get("id") for axis in axes] != ["FOUNDATION", "CARRIER", "REFINED_OBLIGATION"]:
        errors.append("axis identity/order")
    keys = {axis.get("id"): {item.get("id") for item in axis.get("keys", [])} for axis in axes}
    if [len(keys.get(axis, set())) for axis in ("FOUNDATION", "CARRIER", "REFINED_OBLIGATION")] != [6, 6, 16]:
        errors.append("axis dimensions")
    if any(not item.get("label") or not item.get("meaning") for axis in axes for item in axis.get("keys", [])):
        errors.append("axis key explanations")
    cells = result.get("cells", [])
    coordinates = [(x.get("foundation"), x.get("carrier"), x.get("obligation")) for x in cells]
    if len(coordinates) != len(set(coordinates)):
        errors.append("duplicate coordinates")
    for cell in cells:
        if cell.get("foundation") not in keys.get("FOUNDATION", set()) or cell.get("carrier") not in keys.get("CARRIER", set()) or cell.get("obligation") not in keys.get("REFINED_OBLIGATION", set()):
            errors.append("coordinate closure")
        if cell.get("status") not in STATUSES or not cell.get("summary") or not cell.get("boundary") or not isinstance(cell.get("evidence"), list):
            errors.append("cell structure")
        if cell.get("parent_obligation") in ONE_TO_ONE and cell.get("migration_relation") not in {"EXACT_ONE_TO_ONE", "REVIEWED_V1_OVERLAY"}:
            errors.append("one-to-one relation")
        if cell.get("parent_obligation") not in ONE_TO_ONE and cell.get("migration_relation") == "EXACT_ONE_TO_ONE":
            errors.append("blind split inheritance")
    by_coordinate = {coordinate: cell for coordinate, cell in zip(coordinates, cells)}
    for parent in v0.get("cells", []):
        if parent.get("obligation") not in ONE_TO_ONE:
            continue
        coordinate = (parent.get("foundation"), parent.get("carrier"), parent.get("obligation"))
        child = by_coordinate.get(coordinate, {})
        if child.get("status") != parent.get("status") or child.get("evidence") != parent.get("evidence") or child.get("migration_relation") != "EXACT_ONE_TO_ONE":
            errors.append("exact one-to-one migration")
    overlays = {coordinate for coordinate, cell in by_coordinate.items() if cell.get("migration_relation") == "REVIEWED_V1_OVERLAY"}
    if overlays != EXPECTED_OVERLAYS:
        errors.append("overlay set")
    digest = canonical_digest(cells)
    if digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    counts = Counter(x.get("status") for x in cells)
    dimensions = result.get("dimensions", {})
    if dimensions.get("axis_sizes") != [6, 6, 16] or dimensions.get("cartesian_total") != 576 or dimensions.get("migrated_or_overlaid_cells") != len(cells) or dimensions.get("status_counts") != dict(sorted(counts.items())):
        errors.append("declared dimensions/counts")
    return errors, {"digest": digest, "cells": len(cells), "cartesian_total": 576, "status_counts": dict(sorted(counts.items())), "overlays": len(overlays)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
