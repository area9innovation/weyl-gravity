#!/usr/bin/env python3
"""Apply the exact finite-BRST twenty-cell classification to cube v7."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V7 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json"
CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v8.md"
EVIDENCE_ID = "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {"cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision")) for cell in cells], "interfaces": interfaces}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, closure = load(V7), load(CLOSURE)
    if closure.get("result_id") != EVIDENCE_ID or closure.get("lifecycle") != "RESIDUAL_TRANSFERRED":
        raise ValueError("closure identity/lifecycle")
    decisions = {"|".join(item["coordinate"].values()): item for item in closure["promotions"]}
    if len(decisions) != 20:
        raise ValueError("twenty unique decisions")
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
            cell["classification_revision"] = {"certificate": EVIDENCE_ID, "previous_status": "NOT_MAPPED", "new_status": decision["new_status"], "evidence_role": decision["evidence_role"], "status_change": True}
        cells.append(cell)
    if touched != set(decisions):
        raise ValueError("closure coordinates absent from cube")
    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    interfaces = old["certified_interfaces"]
    value = {
        "schema_version": "foundational-intersection-cube-v8",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V8",
        "result_kind": "LOCAL_CERTIFICATE_REFINED_NAVIGATION_CUBE",
        "lifecycle": "TWENTY_EMPTY_CELLS_CLASSIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "d617eab947813e48afebdd1ed2462012e955360e",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Classify exactly twenty cube-v7 NOT_MAPPED coordinates with an independently checked finite BRST certificate while preserving all coordinates, migrations, and interfaces.",
        "compatibility": {**{f"v{index}_unchanged": True for index in range(8)}, "coordinates_preserved_from_v7": True, "migration_fields_preserved_from_v7": True, "certified_interfaces_preserved_from_v7": True, "new_local_certificate": EVIDENCE_ID},
        "axes": old["axes"],
        "cell_statuses": old["cell_statuses"],
        "migration_statuses": old["migration_statuses"],
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            "axis_sizes": [6, 6, 16], "cartesian_total": 576, "emitted_cells": 452,
            "coverage_classified_cells": 452 - counts["NOT_MAPPED"], "migration_reviewed_cells": 452, "migration_pending_cells": 0,
            "reviewed_no_transfer_cells": migrations["REVIEWED_NO_TRANSFER"],
            "reviewed_no_transfer_unmapped_cells": sum(cell["migration_status"] == "REVIEWED_NO_TRANSFER" and cell["status"] == "NOT_MAPPED" for cell in cells),
            "reviewed_no_transfer_classified_cells": sum(cell["migration_status"] == "REVIEWED_NO_TRANSFER" and cell["status"] != "NOT_MAPPED" for cell in cells),
            "certified_cross_cell_interfaces": len(interfaces), "newly_classified_cells": 20, "new_local_result_cells": 17, "new_pieces_only_cells": 3,
            "status_counts": dict(sorted(counts.items())), "migration_status_counts": dict(sorted(migrations.items())), "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells)
        },
        "certified_interfaces": interfaces,
        "cells": cells,
        "provenance": {"inputs": [{"path": str(V7.relative_to(ROOT)), "sha256": sha(V7)}, {"path": str(CLOSURE.relative_to(ROOT)), "sha256": sha(CLOSURE)}]},
        "independent_checker": {"path": "foundations/check_refined_intersection_cube_v8.py", "checks": ["v7 coordinate and migration preservation", "exact twenty-cell prior emptiness", "seventeen local and three pieces-only promotions", "interface preservation", "lifecycle order", "directness-role closure", "status counts", "canonical digest"], "expected_digest": digest(cells, interfaces)},
        "claim_flags": {
            "v7_preserved": True, "twenty_previously_unmapped_cells_classified": True, "seventeen_local_results_added": True, "three_pieces_only_results_added": True,
            "classify_restore_transfer_order_preserved": True, "all_emitted_migrations_reviewed": True,
            "continuum_renormalized_products_constructed": False, "weyl_qme_restored": False, "weyl_residual_transfer_completed": False,
            "all_576_cells_assessed": False, "literature_complete": False, "empirical_agreement_assessed": False, "new_lorentzian_claim": False
        },
        "does_not_establish": [
            "that the finite toy BRST complex is the Weyl BV complex", "Weyl counterterm or anomaly classification", "a continuum renormalized product", "an all-loop or Lorentzian QME",
            "transfer to the Weyl residual complex", "equivalence of general carrier categories", "coverage of 124 un-emitted Cartesian coordinates", "literature completeness or a weakest base",
            "empirical agreement or a complete physical theory", "a new LORENTZIAN-CAUSAL conclusion"
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v8.md"
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    lines = [
        "# Twenty-cell foundations cube v8", "", f"**Result:** `{value['result_id']}`", "", "**Lifecycle:** `TWENTY_EMPTY_CELLS_CLASSIFIED`", "", "## Outcome", "",
        "Cube v8 preserves all 452 cube-v7 coordinates, migration decisions, and both certified cross-cell interfaces. It changes exactly twenty prior `NOT_MAPPED` cells: seventeen become `LOCAL_RESULT` and three regulated-product cells become `PIECES_ONLY`.", "",
        f"The emitted surface now contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**. Classified coverage rises to **{value['dimensions']['coverage_classified_cells']} of 452 emitted cells**.", "",
        "The certificate respects the quantum programme's order inside its named finite toy model: exact `H^0` and `H^1` classify counterterms and anomalies; an exact counterterm then restores the one-loop differential QME; only the restored correction is projected to residual cohomology. None of these scoped statements is promoted to the Weyl metric BV complex.", "",
        "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v8.py --check", "python3 foundations/check_refined_intersection_cube_v8.py", "python3 foundations/verify_refined_intersection_cube_v8.py", "```", "", "## Boundaries", "", *["- This does not establish " + item + "." for item in value["does_not_establish"]], ""
    ]
    return "\n".join(lines)


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
        print("FOUNDATIONAL_INTERSECTION_CUBE_V8: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V8: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
