#!/usr/bin/env python3
"""Project the foundations cube onto pairs of axes and rank bridgeable frontiers."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CUBE_PATH = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0.json"
REPORT_PATH = ROOT / "foundations/reports/pair-frontier-analysis.md"

AXIS_ORDER = ("FOUNDATION", "CARRIER", "OBLIGATION")
AXIS_FIELD = {
    "FOUNDATION": "foundation",
    "CARRIER": "carrier",
    "OBLIGATION": "obligation",
}
AXIS_LABEL = {
    "FOUNDATION": "Mathematical regime",
    "CARRIER": "Carrier/analysis",
    "OBLIGATION": "Physical obligation",
}
STATUS_ORDER = (
    "LOCAL_RESULT",
    "LITERATURE_RESULT",
    "PIECES_ONLY",
    "PRIORITY_GAP",
    "NOT_MAPPED",
)
STATUS_LABEL = {
    "LOCAL_RESULT": "Local result",
    "LITERATURE_RESULT": "Literature result",
    "PIECES_ONLY": "Pieces only",
    "PRIORITY_GAP": "Priority gap",
    "NOT_MAPPED": "Not mapped",
}
CLASS_LABEL = {
    "NEAR_TERM_LOCAL_BRIDGE": "Near-term local bridge",
    "NEAR_TERM_LITERATURE_BRIDGE": "Near-term literature bridge",
    "PIECES_ONLY_FRONTIER": "Pieces-only synthesis frontier",
    "UNSEEDED_IMPORTANT_GAP": "Important but unseeded gap",
    "NO_FRONTIER": "No assessed bridge frontier",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(projections: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> str:
    payload = {
        "projections": [
            (
                item["id"],
                tuple((axis["axis"], axis["key"]) for axis in item["fixed_axes"]),
                item["scan_axis"],
                tuple(item["counts"][status] for status in STATUS_ORDER),
                item["seed_strength"],
                item["open_demand"],
                item["bridge_score"],
                item["classification"],
            )
            for item in projections
        ],
        "recommendations": [
            (
                item["foundation"],
                item["carrier"],
                item["obligation"],
                item["status"],
                item["aggregate_bridge_score"],
                tuple(item["supporting_pair_ids"]),
            )
            for item in recommendations
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def classify(counts: Counter[str]) -> str:
    open_count = counts["PIECES_ONLY"] + counts["PRIORITY_GAP"]
    if open_count == 0:
        return "NO_FRONTIER"
    if counts["LOCAL_RESULT"]:
        return "NEAR_TERM_LOCAL_BRIDGE"
    if counts["LITERATURE_RESULT"]:
        return "NEAR_TERM_LITERATURE_BRIDGE"
    if counts["PIECES_ONLY"]:
        return "PIECES_ONLY_FRONTIER"
    return "UNSEEDED_IMPORTANT_GAP"


def score(counts: Counter[str]) -> tuple[int, int, int]:
    seed_strength = (
        4 * counts["LOCAL_RESULT"]
        + 3 * counts["LITERATURE_RESULT"]
        + counts["PIECES_ONLY"]
    )
    open_demand = 4 * counts["PRIORITY_GAP"] + 2 * counts["PIECES_ONLY"]
    bridge_score = 0
    if seed_strength:
        bridge_score = (
            2 * min(seed_strength, open_demand)
            + 2 * counts["PIECES_ONLY"]
            + counts["PRIORITY_GAP"]
        )
    return seed_strength, open_demand, bridge_score


def coordinate_record(coordinates: dict[str, str], cell: dict[str, Any] | None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "foundation": coordinates["FOUNDATION"],
        "carrier": coordinates["CARRIER"],
        "obligation": coordinates["OBLIGATION"],
        "status": cell["status"] if cell else "NOT_MAPPED",
    }
    if cell:
        record.update(
            evidence=cell["evidence"],
            summary=cell["summary"],
            boundary=cell["boundary"],
        )
    return record


def build(cube: dict[str, Any]) -> dict[str, Any]:
    axes = {axis["id"]: axis for axis in cube["axes"]}
    axis_keys = {axis: [item["id"] for item in axes[axis]["keys"]] for axis in AXIS_ORDER}
    cells = {
        (cell["foundation"], cell["carrier"], cell["obligation"]): cell
        for cell in cube["cells"]
    }
    projections: list[dict[str, Any]] = []
    pair_families: list[dict[str, Any]] = []

    for left_index in range(len(AXIS_ORDER)):
        for right_index in range(left_index + 1, len(AXIS_ORDER)):
            left_axis = AXIS_ORDER[left_index]
            right_axis = AXIS_ORDER[right_index]
            scan_axis = next(axis for axis in AXIS_ORDER if axis not in (left_axis, right_axis))
            family_ids = []
            for left_key in axis_keys[left_axis]:
                for right_key in axis_keys[right_axis]:
                    fixed = {left_axis: left_key, right_axis: right_key}
                    records = []
                    for scan_key in axis_keys[scan_axis]:
                        coordinates = {**fixed, scan_axis: scan_key}
                        key = tuple(coordinates[axis] for axis in AXIS_ORDER)
                        records.append(coordinate_record(coordinates, cells.get(key)))
                    counts = Counter(record["status"] for record in records)
                    seed_strength, open_demand, bridge_score = score(counts)
                    projection_id = "PAIR-" + "-".join((left_axis, left_key, right_axis, right_key))
                    family_ids.append(projection_id)
                    projections.append(
                        {
                            "id": projection_id,
                            "fixed_axes": [
                                {"axis": left_axis, "key": left_key},
                                {"axis": right_axis, "key": right_key},
                            ],
                            "scan_axis": scan_axis,
                            "counts": {status: counts[status] for status in STATUS_ORDER},
                            "seed_strength": seed_strength,
                            "open_demand": open_demand,
                            "bridge_score": bridge_score,
                            "classification": classify(counts),
                            "evidence_cells": [
                                record
                                for record in records
                                if record["status"] in ("LOCAL_RESULT", "LITERATURE_RESULT")
                            ],
                            "candidate_cells": [
                                record
                                for record in records
                                if record["status"] in ("PIECES_ONLY", "PRIORITY_GAP")
                            ],
                            "not_mapped_cells": [
                                record for record in records if record["status"] == "NOT_MAPPED"
                            ],
                        }
                    )
            pair_families.append(
                {
                    "fixed_axes": [left_axis, right_axis],
                    "scan_axis": scan_axis,
                    "projection_ids": family_ids,
                }
            )

    projection_by_id = {item["id"]: item for item in projections}
    ranked = sorted(
        (
            item
            for item in projections
            if item["classification"]
            in (
                "NEAR_TERM_LOCAL_BRIDGE",
                "NEAR_TERM_LITERATURE_BRIDGE",
                "PIECES_ONLY_FRONTIER",
            )
        ),
        key=lambda item: (-item["bridge_score"], item["id"]),
    )
    unseeded = sorted(
        (item for item in projections if item["classification"] == "UNSEEDED_IMPORTANT_GAP"),
        key=lambda item: (-item["open_demand"], item["id"]),
    )

    recommendations = []
    for cell in cube["cells"]:
        if cell["status"] not in ("PIECES_ONLY", "PRIORITY_GAP"):
            continue
        containing = []
        for left_index in range(len(AXIS_ORDER)):
            for right_index in range(left_index + 1, len(AXIS_ORDER)):
                left_axis = AXIS_ORDER[left_index]
                right_axis = AXIS_ORDER[right_index]
                pair_id = "PAIR-" + "-".join(
                    (
                        left_axis,
                        cell[AXIS_FIELD[left_axis]],
                        right_axis,
                        cell[AXIS_FIELD[right_axis]],
                    )
                )
                if projection_by_id[pair_id]["bridge_score"]:
                    containing.append(pair_id)
        recommendations.append(
            {
                "foundation": cell["foundation"],
                "carrier": cell["carrier"],
                "obligation": cell["obligation"],
                "status": cell["status"],
                "aggregate_bridge_score": sum(
                    projection_by_id[pair_id]["bridge_score"] for pair_id in containing
                ),
                "supporting_pair_ids": sorted(containing),
                "evidence": cell["evidence"],
                "summary": cell["summary"],
                "boundary": cell["boundary"],
            }
        )
    recommendations.sort(
        key=lambda item: (
            -item["aggregate_bridge_score"],
            0 if item["status"] == "PRIORITY_GAP" else 1,
            item["foundation"],
            item["carrier"],
            item["obligation"],
        )
    )

    classification_counts = Counter(item["classification"] for item in projections)
    result: dict[str, Any] = {
        "schema_version": "foundational-pair-frontier-analysis-v0",
        "result_id": "FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0",
        "result_kind": "FOUNDATIONAL_NAVIGATION_ANALYSIS",
        "lifecycle": "LITERATURE_SCOPED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "created": "2026-08-11",
        "repository_base_commit": "30ca3c87adb93301794fca6348dec7c50449f231",
        "purpose": "Find products of two cube dimensions that already have an evidence foothold and a nearby assessed open obligation, while keeping unassessed cells and unseeded gaps distinct.",
        "method": {
            "projection_rule": "Fix one key on each of two axes and inspect all six keys on the remaining axis.",
            "seed_strength": "4 * local-result cells + 3 * literature-result cells + 1 * pieces-only cells",
            "open_demand": "4 * priority-gap cells + 2 * pieces-only cells",
            "bridge_score": "If seed_strength is zero, 0; otherwise 2 * min(seed_strength, open_demand) + 2 * pieces-only cells + priority-gap cells.",
            "why_minimum": "The minimum rewards a balance between reusable evidence and named open work; one cannot compensate for the complete absence of the other.",
            "ranking_boundary": "The integer score is a transparent triage heuristic over current classifications. It is not probability, theorem strength, expected scientific value, or evidence that a bridge exists.",
            "not_mapped_rule": "NOT_MAPPED contributes no points and is never converted into a gap or recommendation.",
            "classification_rules": {
                "NEAR_TERM_LOCAL_BRIDGE": "At least one local-result cell and at least one pieces-only or priority-gap cell occur along the scanned axis.",
                "NEAR_TERM_LITERATURE_BRIDGE": "No local-result cell, but at least one literature-result cell and at least one pieces-only or priority-gap cell occur along the scanned axis.",
                "PIECES_ONLY_FRONTIER": "No local or literature result is present, but at least one pieces-only cell supplies a partial foothold.",
                "UNSEEDED_IMPORTANT_GAP": "At least one priority gap is assessed, but the pair has no local, literature, or pieces-only foothold.",
                "NO_FRONTIER": "No assessed open cell occurs along the scanned axis.",
            },
        },
        "summary": {
            "pair_families": 3,
            "projections": len(projections),
            "cells_per_projection": 6,
            "classification_counts": {
                key: classification_counts[key]
                for key in (
                    "NEAR_TERM_LOCAL_BRIDGE",
                    "NEAR_TERM_LITERATURE_BRIDGE",
                    "PIECES_ONLY_FRONTIER",
                    "UNSEEDED_IMPORTANT_GAP",
                    "NO_FRONTIER",
                )
            },
            "ranked_bridge_frontiers": len(ranked),
            "unseeded_important_gaps": len(unseeded),
            "assessed_open_cells": len(recommendations),
        },
        "pair_families": pair_families,
        "projections": projections,
        "ranked_frontier_ids": [item["id"] for item in ranked],
        "unseeded_gap_ids": [item["id"] for item in unseeded],
        "recommended_cells": recommendations,
        "forge_projection": {
            "state": "NOT_REGISTERED",
            "reason": "The current local Forge adoption has no generic importer or generated view for this foundations vocabulary.",
            "requested_capability": "planning/forge-requests/foundations-scope-frontier-importer.json",
            "intended_types": {
                "pair_coordinate": "typed Scope coordinates",
                "assessed_open_cell": "Question plus optional Gate/WorkItem",
                "local_evidence": "Claim plus Certificate reference",
                "literature_evidence": "literature import plus reviewed interpretation",
                "pieces_only": "reviewed QUALIFIES or CROSSWALKS relation",
                "not_mapped": "absence of a node; never an absence claim",
            },
        },
        "provenance": {
            "inputs": [{"path": str(CUBE_PATH.relative_to(ROOT)), "sha256": sha256_file(CUBE_PATH)}],
            "producer": "foundations/analyze_pair_frontiers.py",
        },
        "independent_checker": {
            "path": "foundations/check_pair_frontiers.py",
            "checks": [
                "all 108 pair projections are unique and coordinate-closed",
                "each projection independently recounts six source-cube cells",
                "integer scores and classifications are independently recomputed",
                "ranked and unseeded partitions are exact",
                "recommended open cells are assessed and never NOT_MAPPED",
                "canonical digest",
            ],
            "expected_digest": "",
        },
        "claim_flags": {
            "all_108_pair_projections_computed": True,
            "ranking_is_deterministic": True,
            "ranking_is_scientific_evidence": False,
            "not_mapped_treated_as_gap": False,
            "automatic_forge_registration_complete": False,
            "new_mathematical_theorem": False,
            "new_physical_theorem": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "that a high-scoring pair is easy in absolute time or technical difficulty",
            "that a bridge theorem exists between the evidence and candidate cells",
            "that a low-scoring or unseeded question is scientifically unimportant",
            "that an unmapped cell is absent from the literature",
            "that the current literature review is complete",
            "that pairwise compatibility implies compatibility of all three axes",
            "that any proposed Forge entity has been registered",
            "a new mathematical theorem",
            "a new physical or Lorentzian claim",
        ],
        "human_report": "foundations/reports/pair-frontier-analysis.md",
    }
    result["independent_checker"]["expected_digest"] = canonical_digest(projections, recommendations)
    return result


def clean(text: Any) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def axis_labels(cube: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        axis["id"]: {key["id"]: key["label"] for key in axis["keys"]}
        for axis in cube["axes"]
    }


def fixed_pair_text(item: dict[str, Any], labels: dict[str, dict[str, str]]) -> str:
    return " × ".join(labels[entry["axis"]][entry["key"]] for entry in item["fixed_axes"])


def scanned_values(item: dict[str, Any], labels: dict[str, dict[str, str]], statuses: tuple[str, ...]) -> str:
    field = AXIS_FIELD[item["scan_axis"]]
    records = item["evidence_cells"] + item["candidate_cells"]
    return "; ".join(
        f"{labels[item['scan_axis']][record[field]]} ({STATUS_LABEL[record['status']].lower()})"
        for record in records
        if record["status"] in statuses
    ) or "—"


def render_report(result: dict[str, Any], cube: dict[str, Any]) -> str:
    labels = axis_labels(cube)
    projections = {item["id"]: item for item in result["projections"]}
    ranked = [projections[item] for item in result["ranked_frontier_ids"]]
    unseeded = [projections[item] for item in result["unseeded_gap_ids"]]
    lines = [
        "<!-- Generated by foundations/analyze_pair_frontiers.py; do not edit by hand. -->",
        "# Pair-frontier analysis of the foundations cube",
        "",
        f"**Result:** `{result['result_id']}`",
        "",
        f"**Lifecycle:** `{result['lifecycle']}`",
        "",
        f"**Dependencies:** {', '.join(f'`{tag}`' for tag in result['dependency_tags'])}",
        "",
        "## Outcome",
        "",
        f"The 6 × 6 × 6 cube has **{result['summary']['projections']} distinct products of two dimensions**: 36 mathematical-regime × carrier pairs, 36 mathematical-regime × obligation pairs, and 36 carrier × obligation pairs. Each pair is inspected across the six values of the remaining dimension.",
        "",
        f"The current assessed cube yields **{result['summary']['ranked_bridge_frontiers']} bridgeable pair frontiers**, **{result['summary']['unseeded_important_gaps']} important but unseeded pair gaps**, and **{result['summary']['assessed_open_cells']} assessed open three-axis cells**. Unmapped cells are not counted as gaps.",
        "",
        "The strongest immediate pattern is to reuse a theorem, construction, or literature result already present at one value of the third dimension and test exactly which additional value fails. This turns an enormous foundational question into a bounded comparison or dependency audit.",
        "",
        "## How the score works",
        "",
        "For every fixed pair, the tool counts the six cells along the remaining axis:",
        "",
        "- A local result supplies 4 seed points, a literature result 3, and a pieces-only cell 1.",
        "- A priority gap supplies 4 open-demand points and a pieces-only cell 2.",
        "- The bridge score is `2 × min(seed strength, open demand) + 2 × pieces-only cells + priority-gap cells` when any seed exists. With no seed, it is zero.",
        "- Not-mapped cells contribute nothing. They require classification before scientific prioritization.",
        "",
        "The minimum is the key: a pair ranks well only when evidence and open work occur together. The score is a deterministic triage rule, not a probability of success, a theorem-strength measure, or scientific evidence.",
        "",
        "## Highest-scoring pair frontiers",
        "",
        "| Rank | Fixed product of two dimensions | Scan the third dimension | Score | Existing foothold | Specific assessed openings |",
        "|---:|---|---|---:|---|---|",
    ]
    for rank, item in enumerate(ranked[:15], 1):
        lines.append(
            f"| {rank} | **{clean(fixed_pair_text(item, labels))}** | {AXIS_LABEL[item['scan_axis']]} | {item['bridge_score']} | "
            f"{clean(scanned_values(item, labels, ('LOCAL_RESULT', 'LITERATURE_RESULT', 'PIECES_ONLY')))} | "
            f"{clean(scanned_values(item, labels, ('PIECES_ONLY', 'PRIORITY_GAP')))} |"
        )
    lines += [
        "",
        "A promising row does not say that the open cell follows from the seeded cell. It says that the fixed pair gives a controlled comparison: one can isolate what changes when only the third coordinate changes.",
        "",
        "## Recommended open cells",
        "",
        "The cell score adds the bridge scores of its three containing pairs. It therefore favors a three-axis question that can be approached from more than one already seeded direction.",
        "",
        "| Rank | Mathematical regime | Carrier/analysis | Physical obligation | Current status | Combined pair support | Precise boundary to attack |",
        "|---:|---|---|---|---|---:|---|",
    ]
    for rank, item in enumerate(result["recommended_cells"][:15], 1):
        lines.append(
            f"| {rank} | {clean(labels['FOUNDATION'][item['foundation']])} | {clean(labels['CARRIER'][item['carrier']])} | "
            f"{clean(labels['OBLIGATION'][item['obligation']])} | {STATUS_LABEL[item['status']]} | {item['aggregate_bridge_score']} | {clean(item['boundary'])} |"
        )
    lines += [
        "",
        "## Pairwise overview",
        "",
        "Every table fixes the row and column pair and scans the third axis. A positive integer is the bridge score. `0 — important but unseeded` is deliberately separate from `0 — no assessed bridge`: the former is important, but the present cube offers no evidence foothold from which to call it low-hanging.",
        "",
    ]
    for family in result["pair_families"]:
        left_axis, right_axis = family["fixed_axes"]
        by_fixed = {
            tuple(entry["key"] for entry in item["fixed_axes"]): item
            for item in result["projections"]
            if [entry["axis"] for entry in item["fixed_axes"]] == [left_axis, right_axis]
        }
        left_keys = [key["id"] for key in next(axis for axis in cube["axes"] if axis["id"] == left_axis)["keys"]]
        right_keys = [key["id"] for key in next(axis for axis in cube["axes"] if axis["id"] == right_axis)["keys"]]
        lines += [
            f"### {AXIS_LABEL[left_axis]} × {AXIS_LABEL[right_axis]}",
            "",
            f"Each cell scans all six values of **{AXIS_LABEL[family['scan_axis']].lower()}**.",
            "",
            f"| {AXIS_LABEL[left_axis]} ↓ / {AXIS_LABEL[right_axis]} → | " + " | ".join(labels[right_axis][key] for key in right_keys) + " |",
            "|---|" + "|".join(":---:" for _ in right_keys) + "|",
        ]
        for left_key in left_keys:
            values = []
            for right_key in right_keys:
                item = by_fixed[(left_key, right_key)]
                if item["classification"] == "UNSEEDED_IMPORTANT_GAP":
                    values.append("0 — important but unseeded")
                elif item["bridge_score"]:
                    values.append(f"{item['bridge_score']} — {CLASS_LABEL[item['classification']].lower()}")
                else:
                    values.append("0 — no assessed bridge")
            lines.append(f"| **{clean(labels[left_axis][left_key])}** | " + " | ".join(values) + " |")
        lines.append("")
    lines += [
        "## Important gaps that are not low-hanging yet",
        "",
        "These pairs contain an explicit priority gap but no local result, literature result, or pieces-only foothold along the scanned dimension. Their bridge score is zero by construction; they need a literature or definitions pass before theorem work can be scoped honestly.",
        "",
        "| Fixed product | Scan axis | Priority-gap values | Unmapped values |",
        "|---|---|---|---:|",
    ]
    for item in unseeded:
        lines.append(
            f"| **{clean(fixed_pair_text(item, labels))}** | {AXIS_LABEL[item['scan_axis']]} | "
            f"{clean(scanned_values(item, labels, ('PRIORITY_GAP',)))} | {item['counts']['NOT_MAPPED']} |"
        )
    lines += [
        "",
        "## Forge integration boundary",
        "",
        "The local analyzer is an independent deterministic navigation rail. In a native Science Forge representation, the three keys of a cell should become typed Scope coordinates; an assessed gap should become a Question and optionally a Gate or WorkItem; local evidence should point to a Claim and Certificate; literature evidence should retain its import and interpretation provenance; and a pieces-only judgment should be a reviewed qualification or crosswalk relation.",
        "",
        "No such entities are registered by this result. The missing generic importer and generated pair-frontier view are requested in `planning/forge-requests/foundations-scope-frontier-importer.json`. Most importantly, a not-mapped cell must remain the absence of a node, never an automatically minted absence claim.",
        "",
        "## Boundaries",
        "",
    ]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[str, str]:
    cube = load(CUBE_PATH)
    result = build(cube)
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n", render_report(result, cube)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts are stale")
    args = parser.parse_args(argv)
    result_text, report_text = generated()
    expected = ((RESULT_PATH, result_text), (REPORT_PATH, report_text))
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in expected if not path.is_file() or path.read_text() != text]
        if stale:
            print("stale generated artifacts: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0: generated artifacts current")
        return 0
    for path, text in expected:
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
