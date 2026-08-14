#!/usr/bin/env python3
"""Project the certified BT Euclidean finite-lattice import into cube v10."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V9 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json"
IMPORT = FOUNDATIONS / "results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v10.md"
EVIDENCE_ID = "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(coordinate: dict[str, str]) -> str:
    return "|".join(coordinate[name] for name in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], cross_interfaces: list[dict[str, Any]], carrier_interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [
            (
                key(cell), cell["status"], cell["evidence"], cell["evidence_roles"],
                cell["migration_status"], cell.get("classification_revision"),
                cell.get("interface_revision"), cell.get("bt_euclidean_revision"),
            )
            for cell in cells
        ],
        "cross_interfaces": cross_interfaces,
        "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, imported = load(V9), load(IMPORT)
    if imported.get("result_id") != EVIDENCE_ID or imported.get("lifecycle") != "CLASSIFIED":
        raise ValueError("import identity/lifecycle")
    decisions = {key(item["coordinate"]): item for item in imported["capability_decisions"]}
    if len(decisions) != 6:
        raise ValueError("six unique decisions required")
    cells = json.loads(json.dumps(old["cells"]))
    previous = {key(cell): cell["status"] for cell in cells}
    for cell in cells:
        decision = decisions.get(key(cell))
        if decision is None:
            continue
        prior_status = cell["status"]
        if decision["status_change"] != (prior_status != decision["new_status"]):
            raise ValueError("status-change declaration " + key(cell))
        cell["status"] = decision["new_status"]
        cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
        cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: decision["evidence_role"]}
        cell["summary"] = decision["finding"]
        cell["boundary"] = decision["boundary"]
        cell["bt_euclidean_revision"] = {
            "certificate": EVIDENCE_ID,
            "previous_status": prior_status,
            "new_status": decision["new_status"],
            "evidence_role": decision["evidence_role"],
            "status_change": decision["status_change"],
        }

    expected_previous = {
        "KINEMATICS_OBSERVABLES": "LITERATURE_RESULT",
        "STATE_EXISTENCE": "REVIEWED_GAP",
        "STATE_REPRESENTATION": "REVIEWED_GAP",
        "PROBABILITY_RULE": "REVIEWED_GAP",
        "INTERACTION_CONSTRUCTION": "LITERATURE_RESULT",
        "RECONSTRUCTION_LIMITS": "PRIORITY_GAP",
    }
    for obligation, status in expected_previous.items():
        coordinate_key = key({"foundation": "FINITE_DISCRETE", "carrier": "SMOOTH_DISTRIBUTIONAL", "obligation": obligation})
        if previous.get(coordinate_key) != status:
            raise ValueError("unexpected v9 source status " + obligation)

    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    for status in ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"):
        counts.setdefault(status, 0)
    cross_interfaces = old["certified_interfaces"]
    carrier_interfaces = [imported["carrier_interface"]]
    value = {
        "schema_version": "foundational-intersection-cube-v10",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V10",
        "result_kind": "FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_EUCLIDEAN_LATTICE_IMPORT",
        "lifecycle": "EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE",
        "created": "2026-08-14",
        "repository_base_commit": "be5b23b72ea73f6b5dd099e9a3bd3126e6778922",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "purpose": "Preserve the complete cube-v9 surface while importing the certified finite Euclidean BT capabilities, numerical-reproduction boundary, and scoped Euclidean/Krein carrier non-identity.",
        "compatibility": {
            **old["compatibility"],
            "v9_full_surface_preserved": True,
            "v9_cells_preserved_except_six_declared_import_decisions": True,
            "v9_cross_cell_interfaces_preserved": True,
            "bt_euclidean_import": EVIDENCE_ID,
        },
        "axes": old["axes"],
        "cell_statuses": old["cell_statuses"],
        "migration_statuses": old["migration_statuses"],
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            **old["dimensions"],
            "certified_cross_cell_interfaces": len(cross_interfaces),
            "certified_carrier_interfaces": len(carrier_interfaces),
            "bt_euclidean_imported_cells": 6,
            "bt_euclidean_direct_cells": 5,
            "bt_euclidean_supporting_cells": 1,
            "bt_euclidean_status_promotions": 5,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": cross_interfaces,
        "certified_carrier_interfaces": carrier_interfaces,
        "cells": cells,
        "provenance": {"inputs": [
            {"path": str(V9.relative_to(ROOT)), "sha256": sha(V9)},
            {"path": str(IMPORT.relative_to(ROOT)), "sha256": sha(IMPORT)},
        ]},
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v10.py",
            "checks": [
                "exact 576-cell surface", "570 cube-v9 cells unchanged",
                "five direct local imports and one supporting-only reconstruction record",
                "status and evidence-role closure", "two cross-cell interfaces preserved",
                "one scoped carrier interface added", "canonical digest",
            ],
            "expected_digest": digest(cells, cross_interfaces, carrier_interfaces),
        },
        "claim_flags": {
            "v9_surface_preserved": True,
            "all_576_coordinates_assessed": True,
            "five_finite_euclidean_capabilities_imported": True,
            "reconstruction_priority_gap_preserved": True,
            "coarse_numerical_reproduction_separated": True,
            "all_obligations_solved": False,
            "literature_complete": False,
            "continuum_reconstruction_established": False,
            "empirical_agreement_assessed": False,
            "complete_physical_theory_established": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "that the five finite Euclidean capabilities form a continuum theory",
            "that zero-mode fixing is physical-state selection",
            "that a positive Euclidean Gibbs measure is a Born rule or reflection-positive quantum theory",
            "that coarse sampler reproduction is empirical validation",
            "a controlled continuum or infinite-volume limit",
            "an analytic-continuation map to the BT Krein carrier",
            "that the scoped carrier incompatibility forbids every conditional bridge",
            "that all 576 coordinates are jointly realizable",
            "a complete Weyl theory or quantum completion",
            "a new LORENTZIAN-CAUSAL conclusion",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v10.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    return "\n".join([
        "# Foundations cube v10: BT Euclidean lattice import", "",
        f"**Result:** `{value['result_id']}`", "",
        "## Outcome", "",
        "Cube v10 preserves the complete 576-coordinate cube-v9 surface and changes exactly six declared coordinates in `FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL`. Five receive direct local evidence: kinematics/observables, state existence, state representation, a Euclidean probability rule, and interaction construction.", "",
        "`RECONSTRUCTION_LIMITS` receives supporting evidence but remains `PRIORITY_GAP`. The finite object and coarse L=4/L=6 independent-sampler preflight do not supply a topology, uniform estimate, continuum limit, reflection positivity, Lorentzian transfer, or operational observable map.", "",
        f"The surface now contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.", "",
        "The existing two cross-cell interfaces are preserved. A separate scoped carrier interface records that the positive Euclidean lattice measure and all-real two-field BT/Krein path integral are incompatible with identification as the same full nonperturbative carrier; conditional bridges remain open.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/refine_intersection_cube_v10.py --check",
        "python3 foundations/check_refined_intersection_cube_v10.py",
        "python3 foundations/verify_refined_intersection_cube_v10.py",
        "python3 -m unittest foundations.tests.test_refined_intersection_cube_v10",
        "```", "", "## Boundaries", "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_INTERSECTION_CUBE_V10: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V10: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
