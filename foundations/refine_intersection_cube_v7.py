#!/usr/bin/env python3
"""Apply the exact finite-operator ten-cell classification to cube v6."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V6 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json"
CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v7.md"
EVIDENCE_ID = "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision")) for cell in cells],
        "interfaces": interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, closure = load(V6), load(CLOSURE)
    if closure.get("result_id") != EVIDENCE_ID or closure.get("lifecycle") != "SUFFICIENCY_PROVED":
        raise ValueError("closure identity")
    decisions = {"|".join(item["coordinate"].values()): item for item in closure["promotions"]}
    if len(decisions) != 10:
        raise ValueError("ten unique decisions")
    cells, touched = [], set()
    for source in old["cells"]:
        cell = dict(source)
        key = coordinate(cell)
        if key in decisions:
            decision = decisions[key]
            if cell["status"] != "NOT_MAPPED" or decision["prior_status"] != "NOT_MAPPED":
                raise ValueError("nonempty prior coordinate " + key)
            touched.add(key)
            cell["status"] = decision["new_status"]
            cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
            cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: decision["evidence_role"]}
            cell["summary"] = decision["finding"]
            cell["boundary"] = decision["boundary"]
            cell["classification_revision"] = {
                "certificate": EVIDENCE_ID,
                "previous_status": "NOT_MAPPED",
                "new_status": decision["new_status"],
                "evidence_role": decision["evidence_role"],
                "status_change": True,
            }
        cells.append(cell)
    if touched != set(decisions):
        raise ValueError("closure coordinates absent from cube")

    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    interfaces = old["certified_interfaces"]
    value = {
        "schema_version": "foundational-intersection-cube-v7",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V7",
        "result_kind": "LOCAL_CERTIFICATE_REFINED_NAVIGATION_CUBE",
        "lifecycle": "TEN_EMPTY_CELLS_CLASSIFIED",
        "created": "2026-08-13",
        "repository_base_commit": "64e0e9460b659b43eb10583aa9d95fb27f2b5589",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Classify ten emitted NOT_MAPPED coordinates with an independently checked finite-operator certificate while preserving every cube-v6 migration and interface decision.",
        "compatibility": {
            **{f"v{index}_unchanged": True for index in range(7)},
            "coordinates_preserved_from_v6": True,
            "migration_fields_preserved_from_v6": True,
            "certified_interfaces_preserved_from_v6": True,
            "new_local_certificate": EVIDENCE_ID,
        },
        "axes": old["axes"],
        "cell_statuses": old["cell_statuses"],
        "migration_statuses": old["migration_statuses"],
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            "axis_sizes": [6, 6, 16],
            "cartesian_total": 576,
            "emitted_cells": 452,
            "coverage_classified_cells": 452 - counts["NOT_MAPPED"],
            "migration_reviewed_cells": 452,
            "migration_pending_cells": 0,
            "reviewed_no_transfer_cells": migrations["REVIEWED_NO_TRANSFER"],
            "reviewed_no_transfer_unmapped_cells": sum(cell["migration_status"] == "REVIEWED_NO_TRANSFER" and cell["status"] == "NOT_MAPPED" for cell in cells),
            "reviewed_no_transfer_classified_cells": sum(cell["migration_status"] == "REVIEWED_NO_TRANSFER" and cell["status"] != "NOT_MAPPED" for cell in cells),
            "certified_cross_cell_interfaces": len(interfaces),
            "newly_classified_cells": 10,
            "new_local_result_cells": 9,
            "new_pieces_only_cells": 1,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": interfaces,
        "cells": cells,
        "provenance": {"inputs": [{"path": str(V6.relative_to(ROOT)), "sha256": sha(V6)}, {"path": str(CLOSURE.relative_to(ROOT)), "sha256": sha(CLOSURE)}]},
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v7.py",
            "checks": ["v6 coordinate and migration preservation", "exact ten-cell prior emptiness", "nine local and one pieces-only promotion", "interface preservation", "directness-role closure", "status counts", "canonical digest"],
            "expected_digest": digest(cells, interfaces),
        },
        "claim_flags": {
            "v6_preserved": True,
            "ten_previously_unmapped_cells_classified": True,
            "nine_local_results_added": True,
            "one_pieces_only_result_added": True,
            "all_emitted_migrations_reviewed": True,
            "continuum_renormalized_products_constructed": False,
            "general_carrier_equivalence_established": False,
            "all_576_cells_assessed": False,
            "literature_complete": False,
            "empirical_agreement_assessed": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "equivalence of finite, Hilbert, and Krein carrier categories",
            "a continuum interaction or thermodynamic limit",
            "continuum renormalized products from finite Pauli-product closure",
            "Weyl-gravity counterterm or anomaly classification",
            "QME restoration or residual transfer",
            "a general Krein probability rule",
            "coverage of the 124 un-emitted Cartesian coordinates",
            "literature completeness, empirical agreement, or a complete physical theory",
            "a new LORENTZIAN-CAUSAL conclusion",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v7.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    lines = [
        "# Ten-cell foundations cube v7", "", f"**Result:** `{value['result_id']}`", "", "**Lifecycle:** `TEN_EMPTY_CELLS_CLASSIFIED`", "", "## Outcome", "",
        "Cube v7 preserves all 452 cube-v6 coordinates, all migration decisions, and both certified cross-cell interfaces. It changes exactly ten prior `NOT_MAPPED` coordinates: nine become `LOCAL_RESULT`, while finite regulated-product closure becomes `PIECES_ONLY` rather than being mislabeled as continuum renormalization.", "",
        f"The emitted surface now contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**. Classified coverage rises to **{value['dimensions']['coverage_classified_cells']} of 452 emitted cells**.", "",
        "The ten decisions are object-level finite constructions. The same labelled matrices can be read as exact arrays, bounded operators on the named `C^4`, and—with the explicit fundamental symmetry—as a named finite Krein realization. This does not identify those carrier categories in general.", "",
        "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v7.py --check", "python3 foundations/check_refined_intersection_cube_v7.py", "python3 foundations/verify_refined_intersection_cube_v7.py", "```", "", "## Boundaries", "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
    ]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = ((OUTPUT, generated()[0]), (REPORT, generated()[1]))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_INTERSECTION_CUBE_V7: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V7: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
