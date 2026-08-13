#!/usr/bin/env python3
"""Apply the certified free ground-state/dynamics interface to cube v5."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V5 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json"
INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v6.md"
EVIDENCE_ID = "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
SOURCE = "CLASSICAL_STANDARD|KREIN_INDEFINITE|PHYSICAL_STATE_SELECTION"
TARGET = "CLASSICAL_STANDARD|KREIN_INDEFINITE|GENERATOR_SPECTRAL_DYNAMICS"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("interface_revision")) for cell in cells],
        "interfaces": interfaces,
    }
    encoded = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def build() -> dict[str, Any]:
    old = load(V5)
    interface_result = load(INTERFACE)
    record = interface_result.get("interface", {})
    if record.get("id") != "SELECTION_TO_DYNAMICS" or record.get("status") != "CERTIFIED" or record.get("relation") != "CONDITIONAL_BRIDGE":
        raise ValueError("interface is not certified")
    expected_source = [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PHYSICAL_STATE_SELECTION"}]
    expected_target = [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "GENERATOR_SPECTRAL_DYNAMICS"}]
    if record.get("source_coordinates") != expected_source or record.get("target_coordinates") != expected_target:
        raise ValueError("interface coordinates")
    prior_interfaces = old.get("certified_interfaces", [])
    if [item.get("id") for item in prior_interfaces] != ["STATE_TO_PROBABILITY"]:
        raise ValueError("v5 interface ledger drift")
    interfaces = [*prior_interfaces, record]

    cells = []
    touched = set()
    for source in old["cells"]:
        cell = dict(source)
        key = coordinate(cell)
        if key in (SOURCE, TARGET):
            touched.add(key)
            if cell["status"] != "LOCAL_RESULT":
                raise ValueError("interface endpoint is not already a local result")
            cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
            cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: "DIRECT_LOCAL"}
            cell["interface_revision"] = {
                "certificate": EVIDENCE_ID,
                "interface_id": "SELECTION_TO_DYNAMICS",
                "relation": "CONDITIONAL_BRIDGE",
                "role": "SOURCE" if key == SOURCE else "TARGET",
                "previous_status": "LOCAL_RESULT",
                "status_change": False,
            }
            if key == SOURCE:
                cell["summary"] = "The explicit free Fock energy has a one-dimensional zero eigenspace, selecting the vacuum uniquely among vector ground states and normal zero-energy density states; the same vacuum is invariant under the generated dynamics."
                cell["boundary"] = "This is free reduced-mode ground-state selection, not selection of an interacting, KMS, Hadamard, BRST-compatible, thermodynamic, or Lorentzian state."
        cells.append(cell)
    if touched != {SOURCE, TARGET}:
        raise ValueError("interface cells missing")

    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    value = {
        "schema_version": "foundational-intersection-cube-v6",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V6",
        "result_kind": "CERTIFIED_INTERFACE_REFINED_NAVIGATION_CUBE",
        "lifecycle": "CROSS_CELL_INTERFACES_CERTIFIED",
        "created": "2026-08-13",
        "repository_base_commit": "9bf95542908bcab56c827795ef209b0f472eded8",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Add the independently certified free ground-state-selection to Krein--Fock dynamics bridge while preserving every v5 coordinate and migration decision.",
        "compatibility": {
            "v0_unchanged": True,
            "v1_unchanged": True,
            "v2_unchanged": True,
            "v3_unchanged": True,
            "v4_unchanged": True,
            "v5_unchanged": True,
            "coordinates_preserved_from_v5": True,
            "migration_fields_preserved_from_v5": True,
            "prior_certified_interfaces_preserved": True,
            "new_certified_interface": EVIDENCE_ID,
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
            "certified_cross_cell_interfaces": len(interfaces),
            "new_interface_source_overlays": 1,
            "new_interface_target_overlays": 1,
            "new_interface_target_promotions": 0,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": interfaces,
        "cells": cells,
        "provenance": {
            "inputs": [
                {"path": str(V5.relative_to(ROOT)), "sha256": sha(V5)},
                {"path": str(INTERFACE.relative_to(ROOT)), "sha256": sha(INTERFACE)},
            ]
        },
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v6.py",
            "checks": ["v5 coordinate and migration preservation", "prior interface preservation", "selection and dynamics evidence overlays", "zero status promotion", "directness-role closure", "status counts", "canonical digest"],
            "expected_digest": digest(cells, interfaces),
        },
        "claim_flags": {
            "v5_preserved": True,
            "two_cross_cell_interfaces_certified": True,
            "free_ground_state_dynamics_interface_added": True,
            "endpoint_evidence_overlaid": True,
            "new_cell_status_promotion_required": False,
            "all_emitted_migrations_reviewed": True,
            "interacting_ground_state_selected": False,
            "all_576_cells_assessed": False,
            "literature_complete": False,
            "empirical_agreement_assessed": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "state-to-dynamics composition outside the certified free reduced-mode Fock system",
            "that stationarity alone uniquely selects a state",
            "an interacting, thermal, Hadamard, BRST-compatible, or thermodynamic state",
            "cross-cell composition for the other five assembly interfaces",
            "causal response, a prediction chain, or empirical agreement",
            "a complete physical theory or Lorentzian completion",
            "literature completeness or coherence of unassessed coordinates",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v6.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    lines = [
        "# Two-interface foundations cube v6",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "**Lifecycle:** `CROSS_CELL_INTERFACES_CERTIFIED`",
        "",
        "## Outcome",
        "",
        "Cube v6 preserves all 452 v5 coordinates, all migration fields, and the",
        "finite-corner state-to-probability bridge. It adds a second certified",
        "`CONDITIONAL_BRIDGE`, from physical state selection to generator/spectral",
        "dynamics on the identical free Krein--Fock carrier.",
        "",
        "Both endpoint cells were already local results, so no coverage grade changes.",
        f"The surface remains at **{counts['LOCAL_RESULT']} local-result**,",
        f"**{counts['LITERATURE_RESULT']} literature-result**,",
        f"**{counts['PIECES_ONLY']} pieces-only**, **{counts['PRIORITY_GAP']} gaps**,",
        f"and **{counts['NOT_MAPPED']} not-mapped** emitted cells. What changes is",
        "object-level composition: the free energy uniquely selects the normal",
        "zero-energy vacuum state and the generated dynamics fixes it.",
        "",
        "## Reproduction",
        "",
        "```text",
        "python3 foundations/refine_intersection_cube_v6.py --check",
        "python3 foundations/check_refined_intersection_cube_v6.py",
        "python3 foundations/verify_refined_intersection_cube_v6.py",
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
            print("FOUNDATIONAL_INTERSECTION_CUBE_V6: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V6: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V6: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
