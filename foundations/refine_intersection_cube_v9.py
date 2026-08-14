#!/usr/bin/env python3
"""Apply the full-surface gap audit and emit all 576 cube coordinates."""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V8 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v9.md"
EVIDENCE_ID = "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def coordinate_dict(key: str) -> dict[str, str]:
    foundation, carrier, obligation = key.split("|")
    return {"foundation": foundation, "carrier": carrier, "obligation": obligation}


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [
            (
                coordinate(cell), cell["status"], cell["evidence"],
                cell["evidence_roles"], cell["migration_status"],
                cell.get("classification_revision"), cell.get("interface_revision"),
            )
            for cell in cells
        ],
        "interfaces": interfaces,
    }
    encoded = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def build() -> dict[str, Any]:
    old, audit = load(V8), load(AUDIT)
    if audit.get("result_id") != EVIDENCE_ID or audit.get("lifecycle") != "CLASSIFIED":
        raise ValueError("audit identity/lifecycle")
    decisions = {"|".join(item["coordinate"].values()): item for item in audit["decisions"]}
    if len(decisions) != 175:
        raise ValueError("175 unique decisions required")
    prior = {coordinate(cell): cell for cell in old["cells"]}
    foundation_ids = [item["id"] for item in old["axes"][0]["keys"]]
    carrier_ids = [item["id"] for item in old["axes"][1]["keys"]]
    obligation_ids = [item["id"] for item in old["axes"][2]["keys"]]
    surface = ["|".join(parts) for parts in product(foundation_ids, carrier_ids, obligation_ids)]
    if len(surface) != 576 or len(set(surface)) != 576:
        raise ValueError("axis Cartesian product")
    if set(decisions) != {key for key in surface if key not in prior or prior[key]["status"] == "NOT_MAPPED"}:
        raise ValueError("audit must exactly cover the prior unassessed surface")

    cells: list[dict[str, Any]] = []
    for key in surface:
        decision = decisions.get(key)
        if key in prior:
            cell = dict(prior[key])
            if decision is not None:
                if cell["status"] != "NOT_MAPPED" or decision["prior_surface_state"] != "EMITTED_NOT_MAPPED":
                    raise ValueError("invalid emitted-gap decision " + key)
                cell["status"] = "REVIEWED_GAP"
                cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
                cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: "SUPPORTING"}
                cell["summary"] = decision["finding"]
                cell["boundary"] = decision["boundary"]
                cell["classification_revision"] = {
                    "certificate": EVIDENCE_ID,
                    "previous_status": "NOT_MAPPED",
                    "new_status": "REVIEWED_GAP",
                    "evidence_role": "SUPPORTING",
                    "status_change": True,
                }
        else:
            if decision is None or decision["prior_surface_state"] != "SYNTHETIC_NOT_EMITTED":
                raise ValueError("missing synthetic decision " + key)
            cell = {
                **coordinate_dict(key),
                "status": "REVIEWED_GAP",
                "evidence": [EVIDENCE_ID],
                "evidence_roles": {EVIDENCE_ID: "SUPPORTING"},
                "parent_obligation": None,
                "migration_relation": "DIRECT_FULL_SURFACE_ASSESSMENT",
                "migration_status": "DIRECT_COORDINATE_REVIEW",
                "migration_evidence": [EVIDENCE_ID],
                "migration_rationale": "This coordinate was not inherited from a broad parent; the full-surface audit formulates and assesses it directly.",
                "summary": decision["finding"],
                "boundary": decision["boundary"],
                "classification_revision": {
                    "certificate": EVIDENCE_ID,
                    "previous_status": "NOT_EMITTED",
                    "new_status": "REVIEWED_GAP",
                    "evidence_role": "SUPPORTING",
                    "status_change": True,
                },
            }
        cells.append(cell)

    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    for status in ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"):
        counts.setdefault(status, 0)
    statuses = [*old["cell_statuses"], {
        "id": "REVIEWED_GAP",
        "meaning": "An explicitly formulated and reviewed open question with no direct result; it is not a priority, absence, or no-go claim.",
    }]
    migrations_vocab = [*old["migration_statuses"], {
        "id": "DIRECT_COORDINATE_REVIEW",
        "meaning": "A previously un-emitted Cartesian coordinate was formulated and assessed directly; no parent transfer is implied.",
    }]
    interfaces = old["certified_interfaces"]
    value = {
        "schema_version": "foundational-intersection-cube-v9",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V9",
        "result_kind": "FULL_CARTESIAN_ASSESSMENT_CUBE",
        "lifecycle": "FULL_CARTESIAN_SURFACE_ASSESSED",
        "created": "2026-08-14",
        "repository_base_commit": "3b4c7dfa3506baeef447ba97038f5f6f9f807a75",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Emit and assess all 576 foundation-carrier-obligation coordinates while preserving all prior results, pieces, priorities, migrations, and certified interfaces.",
        "compatibility": {
            **{f"v{index}_unchanged": True for index in range(9)},
            "v8_classified_cells_unchanged": True,
            "v8_migration_fields_preserved": True,
            "certified_interfaces_preserved_from_v8": True,
            "full_surface_gap_audit": EVIDENCE_ID,
        },
        "axes": old["axes"],
        "cell_statuses": statuses,
        "migration_statuses": migrations_vocab,
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            "axis_sizes": [6, 6, 16],
            "cartesian_total": 576,
            "emitted_cells": 576,
            "coverage_classified_cells": 576,
            "migration_reviewed_cells": 576,
            "migration_pending_cells": 0,
            "reviewed_no_transfer_cells": migrations["REVIEWED_NO_TRANSFER"],
            "reviewed_no_transfer_unmapped_cells": 0,
            "reviewed_no_transfer_classified_cells": migrations["REVIEWED_NO_TRANSFER"],
            "direct_coordinate_review_cells": migrations["DIRECT_COORDINATE_REVIEW"],
            "certified_cross_cell_interfaces": len(interfaces),
            "newly_classified_cells": 175,
            "new_reviewed_gap_cells": 175,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": interfaces,
        "cells": cells,
        "provenance": {"inputs": [
            {"path": str(V8.relative_to(ROOT)), "sha256": sha(V8)},
            {"path": str(AUDIT.relative_to(ROOT)), "sha256": sha(AUDIT)},
        ]},
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v9.py",
            "checks": [
                "exact 6x6x16 Cartesian surface", "401 cube-v8 classified cells unchanged",
                "51 emitted gaps revised", "124 previously un-emitted coordinates added",
                "zero NOT_MAPPED", "migration and evidence-role closure", "interface preservation", "canonical digest",
            ],
            "expected_digest": digest(cells, interfaces),
        },
        "claim_flags": {
            "v8_classified_cells_preserved": True,
            "all_576_coordinates_present": True,
            "all_576_coordinates_assessed": True,
            "zero_not_mapped": True,
            "one_hundred_seventy_five_reviewed_gaps": True,
            "direct_result_count_unchanged": True,
            "all_obligations_solved": False,
            "literature_complete": False,
            "literature_absence_established": False,
            "empirical_agreement_assessed": False,
            "complete_physical_theory_established": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "a result for any REVIEWED_GAP coordinate", "that a reviewed gap is a programme priority",
            "literature completeness or absence", "that all 576 coordinates are jointly realizable",
            "evidence transfer from a one-axis neighbor", "impossibility, independence, inconsistency, or a no-go theorem",
            "a weakest foundation or equivalence of carrier categories", "a continuum limit or empirical equivalence",
            "a complete Weyl theory or quantum completion", "a new LORENTZIAN-CAUSAL conclusion",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v9.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    return "\n".join([
        "# Full-surface foundations cube v9", "", f"**Result:** `{value['result_id']}`", "",
        "**Lifecycle:** `FULL_CARTESIAN_SURFACE_ASSESSED`", "", "## Outcome", "",
        "Cube v9 emits the exact **6 × 6 × 16 = 576** Cartesian surface and records an assessment for every coordinate. It preserves all 401 previously classified cube-v8 cells, revises the 51 emitted `NOT_MAPPED` cells, and adds the 124 previously browser-only complements.", "",
        f"The surface contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed open gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.", "",
        "`REVIEWED_GAP` is a complete assessment state, not a completed scientific result. Each such cell has a coherent research question and a typed missing certificate, but no direct local or literature result. The 30 `PRIORITY_GAP` cells remain the selected programme priorities.", "",
        "The 124 new coordinates use `DIRECT_COORDINATE_REVIEW`: they were assessed directly rather than inherited from a broad parent. Already classified one-axis neighbors remain navigation only and do not license evidence transfer.", "",
        "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v9.py --check", "python3 foundations/check_refined_intersection_cube_v9.py", "python3 foundations/verify_refined_intersection_cube_v9.py", "python3 -m unittest foundations.tests.test_refined_intersection_cube_v9", "```", "",
        "## Boundaries", "", *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
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
        print("FOUNDATIONAL_INTERSECTION_CUBE_V9: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V9: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
