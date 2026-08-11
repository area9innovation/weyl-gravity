#!/usr/bin/env python3
"""Independent structural checker for the pair-frontier analysis."""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations, product
import json
from typing import Any

AXES = ("FOUNDATION", "CARRIER", "OBLIGATION")
FIELDS = {"FOUNDATION": "foundation", "CARRIER": "carrier", "OBLIGATION": "obligation"}
STATUSES = ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "NOT_MAPPED")
BRIDGE_CLASSES = {
    "NEAR_TERM_LOCAL_BRIDGE",
    "NEAR_TERM_LITERATURE_BRIDGE",
    "PIECES_ONLY_FRONTIER",
}


def digest(result: dict[str, Any]) -> str:
    body = {
        "projections": [
            (
                row.get("id"),
                tuple((entry.get("axis"), entry.get("key")) for entry in row.get("fixed_axes", [])),
                row.get("scan_axis"),
                tuple(row.get("counts", {}).get(status) for status in STATUSES),
                row.get("seed_strength"),
                row.get("open_demand"),
                row.get("bridge_score"),
                row.get("classification"),
            )
            for row in result.get("projections", [])
        ],
        "recommendations": [
            (
                row.get("foundation"),
                row.get("carrier"),
                row.get("obligation"),
                row.get("status"),
                row.get("aggregate_bridge_score"),
                tuple(row.get("supporting_pair_ids", [])),
            )
            for row in result.get("recommended_cells", [])
        ],
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def expected_class(counts: Counter[str]) -> str:
    if counts["PIECES_ONLY"] + counts["PRIORITY_GAP"] == 0:
        return "NO_FRONTIER"
    if counts["LOCAL_RESULT"] > 0:
        return "NEAR_TERM_LOCAL_BRIDGE"
    if counts["LITERATURE_RESULT"] > 0:
        return "NEAR_TERM_LITERATURE_BRIDGE"
    if counts["PIECES_ONLY"] > 0:
        return "PIECES_ONLY_FRONTIER"
    return "UNSEEDED_IMPORTANT_GAP"


def expected_scores(counts: Counter[str]) -> tuple[int, int, int]:
    seed = 4 * counts["LOCAL_RESULT"] + 3 * counts["LITERATURE_RESULT"] + counts["PIECES_ONLY"]
    demand = 4 * counts["PRIORITY_GAP"] + 2 * counts["PIECES_ONLY"]
    bridge = 2 * min(seed, demand) + 2 * counts["PIECES_ONLY"] + counts["PRIORITY_GAP"] if seed else 0
    return seed, demand, bridge


def record_coordinate(record: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    return record.get("foundation"), record.get("carrier"), record.get("obligation")


def check(result: dict[str, Any], cube: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    cube_axes = {axis.get("id"): [key.get("id") for key in axis.get("keys", [])] for axis in cube.get("axes", [])}
    if tuple(cube_axes) != AXES or any(len(cube_axes.get(axis, [])) != 6 for axis in AXES):
        errors.append("source cube axes")
        return errors, {}
    cube_cells = {
        (row.get("foundation"), row.get("carrier"), row.get("obligation")): row
        for row in cube.get("cells", [])
    }
    expected: dict[str, dict[str, Any]] = {}
    for left_axis, right_axis in combinations(AXES, 2):
        scan_axis = next(axis for axis in AXES if axis not in (left_axis, right_axis))
        for left_key, right_key in product(cube_axes[left_axis], cube_axes[right_axis]):
            pair_id = f"PAIR-{left_axis}-{left_key}-{right_axis}-{right_key}"
            statuses = []
            coordinates = []
            for scan_key in cube_axes[scan_axis]:
                fixed = {left_axis: left_key, right_axis: right_key, scan_axis: scan_key}
                coord = tuple(fixed[axis] for axis in AXES)
                coordinates.append(coord)
                statuses.append(cube_cells.get(coord, {}).get("status", "NOT_MAPPED"))
            counts = Counter(statuses)
            seed, demand, bridge = expected_scores(counts)
            expected[pair_id] = {
                "fixed_axes": [(left_axis, left_key), (right_axis, right_key)],
                "scan_axis": scan_axis,
                "counts": {status: counts[status] for status in STATUSES},
                "seed": seed,
                "demand": demand,
                "bridge": bridge,
                "classification": expected_class(counts),
                "evidence": {coord for coord, status in zip(coordinates, statuses) if status in ("LOCAL_RESULT", "LITERATURE_RESULT")},
                "candidate": {coord for coord, status in zip(coordinates, statuses) if status in ("PIECES_ONLY", "PRIORITY_GAP")},
                "not_mapped": {coord for coord, status in zip(coordinates, statuses) if status == "NOT_MAPPED"},
            }

    projections = result.get("projections", [])
    actual_ids = [row.get("id") for row in projections]
    if len(projections) != 108 or len(set(actual_ids)) != 108 or set(actual_ids) != set(expected):
        errors.append("projection identity/coverage")
    actual_by_id = {row.get("id"): row for row in projections}

    expected_families = []
    for left_axis, right_axis in combinations(AXES, 2):
        scan_axis = next(axis for axis in AXES if axis not in (left_axis, right_axis))
        family_ids = [
            f"PAIR-{left_axis}-{left_key}-{right_axis}-{right_key}"
            for left_key, right_key in product(cube_axes[left_axis], cube_axes[right_axis])
        ]
        expected_families.append(
            {"fixed_axes": [left_axis, right_axis], "scan_axis": scan_axis, "projection_ids": family_ids}
        )
    if result.get("pair_families") != expected_families:
        errors.append("pair-family partitions")

    for pair_id, wanted in expected.items():
        row = actual_by_id.get(pair_id)
        if not row:
            continue
        fixed = [(entry.get("axis"), entry.get("key")) for entry in row.get("fixed_axes", [])]
        if fixed != wanted["fixed_axes"] or row.get("scan_axis") != wanted["scan_axis"]:
            errors.append("projection coordinates " + pair_id)
        if row.get("counts") != wanted["counts"] or sum(row.get("counts", {}).values()) != 6:
            errors.append("projection counts " + pair_id)
        if (row.get("seed_strength"), row.get("open_demand"), row.get("bridge_score")) != (wanted["seed"], wanted["demand"], wanted["bridge"]):
            errors.append("projection score " + pair_id)
        if row.get("classification") != wanted["classification"]:
            errors.append("projection classification " + pair_id)
        for field, expected_coords in (("evidence_cells", wanted["evidence"]), ("candidate_cells", wanted["candidate"]), ("not_mapped_cells", wanted["not_mapped"])):
            if {record_coordinate(item) for item in row.get(field, [])} != expected_coords:
                errors.append(f"projection {field} {pair_id}")

    expected_ranked = [
        pair_id
        for pair_id, wanted in sorted(expected.items(), key=lambda entry: (-entry[1]["bridge"], entry[0]))
        if wanted["classification"] in BRIDGE_CLASSES
    ]
    if result.get("ranked_frontier_ids") != expected_ranked:
        errors.append("ranked frontier order")
    expected_unseeded = [
        pair_id
        for pair_id, wanted in sorted(expected.items(), key=lambda entry: (-entry[1]["demand"], entry[0]))
        if wanted["classification"] == "UNSEEDED_IMPORTANT_GAP"
    ]
    if result.get("unseeded_gap_ids") != expected_unseeded:
        errors.append("unseeded gap order")

    expected_recommendations = []
    for coord, source in cube_cells.items():
        if source.get("status") not in ("PIECES_ONLY", "PRIORITY_GAP"):
            continue
        containing = []
        values = dict(zip(AXES, coord))
        for left_axis, right_axis in combinations(AXES, 2):
            pair_id = f"PAIR-{left_axis}-{values[left_axis]}-{right_axis}-{values[right_axis]}"
            if expected[pair_id]["bridge"]:
                containing.append(pair_id)
        expected_recommendations.append((coord, source["status"], sum(expected[item]["bridge"] for item in containing), tuple(sorted(containing))))
    expected_recommendations.sort(key=lambda item: (-item[2], 0 if item[1] == "PRIORITY_GAP" else 1, *item[0]))
    actual_recommendations = [
        (record_coordinate(row), row.get("status"), row.get("aggregate_bridge_score"), tuple(row.get("supporting_pair_ids", [])))
        for row in result.get("recommended_cells", [])
    ]
    if actual_recommendations != expected_recommendations:
        errors.append("recommended open cells")
    if any(item[1] == "NOT_MAPPED" for item in actual_recommendations):
        errors.append("not-mapped recommendation")

    class_counts = Counter(item["classification"] for item in expected.values())
    summary = result.get("summary", {})
    wanted_summary = {
        "pair_families": 3,
        "projections": 108,
        "cells_per_projection": 6,
        "classification_counts": {
            key: class_counts[key]
            for key in (
                "NEAR_TERM_LOCAL_BRIDGE",
                "NEAR_TERM_LITERATURE_BRIDGE",
                "PIECES_ONLY_FRONTIER",
                "UNSEEDED_IMPORTANT_GAP",
                "NO_FRONTIER",
            )
        },
        "ranked_bridge_frontiers": len(expected_ranked),
        "unseeded_important_gaps": len(expected_unseeded),
        "assessed_open_cells": len(expected_recommendations),
    }
    if summary != wanted_summary:
        errors.append("summary")
    computed_digest = digest(result)
    if computed_digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {**wanted_summary, "digest": computed_digest}


def main() -> int:
    from pathlib import Path

    base = Path(__file__).resolve().parent
    result = json.loads((base / "results/FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0.json").read_text())
    cube = json.loads((base / "results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json").read_text())
    errors, summary = check(result, cube)
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
