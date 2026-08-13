#!/usr/bin/env python3
"""Apply the certified finite-corner Born interface to cube v4."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V4 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json"
INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v5.md"
EVIDENCE_ID = "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


SOURCE = "CLASSICAL_STANDARD|ALGEBRAIC_CSTAR|STATE_REPRESENTATION"
TARGET = "CLASSICAL_STANDARD|KREIN_INDEFINITE|PROBABILITY_RULE"


def digest(cells: list[dict[str, Any]]) -> str:
    projection = [
        (coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("interface_revision"))
        for cell in cells
    ]
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old = load(V4)
    interface = load(INTERFACE)
    record = interface.get("interface", {})
    if record.get("status") != "CERTIFIED" or record.get("relation") != "CONDITIONAL_BRIDGE":
        raise ValueError("interface is not certified")
    expected_source = [{"foundation": "CLASSICAL_STANDARD", "carrier": "ALGEBRAIC_CSTAR", "obligation": "STATE_REPRESENTATION"}]
    expected_target = [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PROBABILITY_RULE"}]
    if record.get("source_coordinates") != expected_source or record.get("target_coordinates") != expected_target:
        raise ValueError("interface coordinates")
    cells = []
    touched = set()
    for source in old["cells"]:
        cell = dict(source)
        key = coordinate(cell)
        if key in (SOURCE, TARGET):
            touched.add(key)
            previous = cell["status"]
            if key == TARGET:
                if previous != "PIECES_ONLY":
                    raise ValueError("target prior status")
                cell["status"] = "LOCAL_RESULT"
                cell["summary"] = "A certified conditional bridge evaluates the shared finite-corner state on public Krein process effects and proves exact nonnegative normalized event probabilities under five explicit hypotheses."
                cell["boundary"] = "The promotion is restricted to finite detector corners, finite exhaustive partitions, paired-domain preservation, cross-Krein isometry, and weak ghost orthogonality; it is not an arbitrary-process, thermodynamic, all-order, or empirical Born rule."
            cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
            cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: "DIRECT_LOCAL"}
            cell["interface_revision"] = {
                "certificate": EVIDENCE_ID,
                "interface_id": "STATE_TO_PROBABILITY",
                "relation": "CONDITIONAL_BRIDGE",
                "role": "SOURCE" if key == SOURCE else "TARGET",
                "previous_status": previous,
                "status_change": key == TARGET,
            }
        cells.append(cell)
    if touched != {SOURCE, TARGET}:
        raise ValueError("interface cells missing")
    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    value = {
        "schema_version": "foundational-intersection-cube-v5",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V5",
        "result_kind": "CERTIFIED_INTERFACE_REFINED_NAVIGATION_CUBE",
        "lifecycle": "CROSS_CELL_INTERFACE_CERTIFIED",
        "created": "2026-08-13",
        "repository_base_commit": "64d2a94daf3070e1e422d71d69142161e14c11ff",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Apply one independently certified algebraic-state to Krein-probability conditional bridge while preserving every v4 coordinate and migration decision.",
        "compatibility": {
            "v0_unchanged": True,
            "v1_unchanged": True,
            "v2_unchanged": True,
            "v3_unchanged": True,
            "v4_unchanged": True,
            "coordinates_preserved_from_v4": True,
            "migration_fields_preserved_from_v4": True,
            "certified_interface": EVIDENCE_ID,
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
            "certified_cross_cell_interfaces": 1,
            "interface_source_cells": 1,
            "interface_target_promotions": 1,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": [record],
        "cells": cells,
        "provenance": {
            "inputs": [
                {"path": str(V4.relative_to(ROOT)), "sha256": sha(V4)},
                {"path": str(INTERFACE.relative_to(ROOT)), "sha256": sha(INTERFACE)},
            ]
        },
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v5.py",
            "checks": ["v4 coordinate and migration preservation", "source evidence overlay", "target probability promotion", "directness-role closure", "certified-interface projection", "status counts", "canonical digest"],
            "expected_digest": digest(cells),
        },
        "claim_flags": {
            "v4_preserved": True,
            "one_cross_cell_interface_certified": True,
            "probability_target_promoted": True,
            "all_emitted_migrations_reviewed": True,
            "arbitrary_krein_probability_rule": False,
            "physical_thermodynamic_state_selected": False,
            "all_576_cells_assessed": False,
            "literature_complete": False,
            "empirical_agreement_assessed": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "a probability rule for arbitrary Krein processes",
            "identity of the full algebraic C* and Krein carriers",
            "a physical selection principle for the incoming corner",
            "a thermodynamic, all-order, gravitational, or Lorentzian completion",
            "cross-cell composition for the other six assembly interfaces",
            "empirical agreement or a complete theory",
            "literature completeness or coherence of unassessed coordinates",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v5.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    lines = [
        "# Certified-interface foundations cube v5",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "**Lifecycle:** `CROSS_CELL_INTERFACE_CERTIFIED`",
        "",
        "## Outcome",
        "",
        "Cube v5 preserves all 452 v4 coordinates and every migration field. It adds",
        "one certified `CONDITIONAL_BRIDGE` from the classical-standard algebraic/C*",
        "state-representation cell to the classical-standard Krein/indefinite",
        "probability-rule cell.",
        "",
        "The target moves from `PIECES_ONLY` to `LOCAL_RESULT`, giving",
        f"**{counts['LOCAL_RESULT']} local-result** and **{counts['PIECES_ONLY']} pieces-only**",
        "cells. Coverage remains 371 classified cells because the target was already",
        "classified; what changed is that its ingredients now compose under five named",
        "hypotheses.",
        "",
        "The bridge uses one identical finite-corner state on both sides and exact event",
        "effects. It does not identify the full carriers or license arbitrary Krein",
        "processes.",
        "",
        "## Reproduction",
        "",
        "```text",
        "python3 foundations/refine_intersection_cube_v5.py --check",
        "python3 foundations/check_refined_intersection_cube_v5.py",
        "python3 foundations/verify_refined_intersection_cube_v5.py",
        "```",
        "",
        "## Boundaries",
        "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]],
        "",
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
        if stale:
            print("FOUNDATIONAL_INTERSECTION_CUBE_V5: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V5: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V5: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
