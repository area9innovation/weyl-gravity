#!/usr/bin/env python3
"""Independently verify the full Cartesian reviewed-gap assessment."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def coord(cell: dict[str, Any]) -> tuple[str, str, str]:
    return cell["foundation"], cell["carrier"], cell["obligation"]


def key(value: tuple[str, str, str]) -> str:
    return "|".join(value)


def digest_payload(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    source = load(SOURCE)
    errors: list[str] = []
    axes = {axis["id"]: [item["id"] for item in axis["keys"]] for axis in source["axes"]}
    all_coords = {
        (foundation, carrier, obligation)
        for foundation in axes["FOUNDATION"]
        for carrier in axes["CARRIER"]
        for obligation in axes["REFINED_OBLIGATION"]
    }
    current = {coord(cell): cell for cell in source["cells"]}
    expected = {coordinate for coordinate in all_coords if coordinate not in current or current[coordinate]["status"] == "NOT_MAPPED"}
    classified = {coordinate for coordinate, cell in current.items() if cell["status"] != "NOT_MAPPED"}
    decisions = result.get("decisions", [])
    mapped = {coord(item.get("coordinate", {})): item for item in decisions if set(item.get("coordinate", {})) == {"foundation", "carrier", "obligation"}}
    if len(all_coords) != 576:
        errors.append("Cartesian closure")
    if len(decisions) != 175 or len(mapped) != 175 or set(mapped) != expected:
        errors.append("exact 175-decision complement")
    prior = Counter(item.get("prior_surface_state") for item in decisions)
    if prior != {"EMITTED_NOT_MAPPED": 51, "SYNTHETIC_NOT_EMITTED": 124}:
        errors.append("51/124 prior partition")
    for coordinate, item in mapped.items():
        old = current.get(coordinate)
        expected_prior = "EMITTED_NOT_MAPPED" if old is not None else "SYNTHETIC_NOT_EMITTED"
        if item.get("prior_surface_state") != expected_prior:
            errors.append("prior state " + key(coordinate))
        if item.get("review_class") != "COHERENT_TYPED_GAP" or item.get("new_status") != "REVIEWED_GAP" or item.get("evidence_role") != "SUPPORTING":
            errors.append("gap-only grade " + key(coordinate))
        if not all(item.get(field) for field in ("research_question", "foundation_requirement", "carrier_requirement", "missing_certificate", "finding", "boundary")):
            errors.append("typed fields " + key(coordinate))
        if coordinate[0] not in item.get("research_question", "") or coordinate[1] not in item.get("research_question", ""):
            errors.append("typed question " + key(coordinate))
        neighbors = sorted(
            key(other) for other in classified
            if sum(left != right for left, right in zip(coordinate, other)) == 1
        )
        if item.get("nearest_assessed_coordinates") != neighbors or item.get("nearest_neighbor_count") != len(neighbors):
            errors.append("one-axis neighbors " + key(coordinate))
        if "not a result" not in item.get("boundary", "") or "literature-absence" not in item.get("boundary", "") or "transfer" not in item.get("boundary", ""):
            errors.append("nonresult boundary " + key(coordinate))
    status = result.get("status_definition", {})
    if status.get("id") != "REVIEWED_GAP" or status.get("mark") != "O" or status.get("rank") != "OPEN_NONRESULT":
        errors.append("reviewed-gap definition")
    flags = result.get("claim_flags", {})
    for name in ("all_175_remaining_coordinates_reviewed", "all_576_coordinates_formulated", "new_reviewed_gap_status_defined"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("direct_results_added", "pieces_only_results_added", "priority_assignments_added", "literature_complete", "literature_absence_proved", "all_physical_obligations_solved", "complete_theory_identified", "new_lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    projection = {
        "coordinates": [list(coordinate) for coordinate in sorted(mapped)],
        "prior_counts": dict(sorted(prior.items())),
        "foundation_counts": dict(sorted(Counter(c[0] for c in mapped).items())),
        "carrier_counts": dict(sorted(Counter(c[1] for c in mapped).items())),
        "obligation_counts": dict(sorted(Counter(c[2] for c in mapped).items())),
        "neighbor_digest": digest_payload({key(c): mapped[c].get("nearest_assessed_coordinates") for c in sorted(mapped)}),
        "new_status": "REVIEWED_GAP",
        "positive_grades_added": 0,
    }
    return errors, {**projection, "digest": digest_payload(projection)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
