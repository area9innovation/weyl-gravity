#!/usr/bin/env python3
"""Generate cube v3 by applying the normally-hyperbolic research atlas."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V2 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
ATLAS = FOUNDATIONS / "results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v3.md"


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text())
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def coordinate(cell: dict[str, Any]) -> str: return "|".join(cell[x] for x in ("foundation", "carrier", "obligation"))
def digest(cells: list[dict[str, Any]]) -> str:
    payload = [(coordinate(x), x["status"], x["evidence"], x["migration_status"], x.get("research_revision")) for x in cells]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    v2, atlas = load(V2), load(ATLAS)
    actions = {x["coordinate"]: x for x in atlas["cell_actions"]}
    overlays = {x["coordinate"]: x for x in atlas["evidence_overlays"]}
    cells = []
    for source in v2["cells"]:
        cell = dict(source)
        key = coordinate(cell)
        action, overlay = actions.pop(key, None), overlays.pop(key, None)
        if action:
            if cell["status"] != action["old"]: raise ValueError("old status mismatch " + key)
            cell["status"] = action["new"]
            cell["evidence"] = list(dict.fromkeys([*cell["evidence"], *action["evidence"]]))
            cell["summary"] = action["basis"]
            cell["boundary"] = "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims."
            cell["research_revision"] = {"atlas": atlas["result_id"], "kind": "STATUS_CHANGE", "previous_status": action["old"]}
            # New atlas evidence carries no per-obligation directness review, so it
            # stays UNREVIEWED rather than inheriting the cell's grade.
            cell["evidence_roles"] = {**{e: "UNREVIEWED" for e in cell["evidence"]}, **cell["evidence_roles"]}
        elif overlay:
            cell["evidence"] = list(dict.fromkeys([*cell["evidence"], *overlay["evidence"]]))
            cell["summary"] = cell["summary"] + " New atlas evidence: " + overlay["basis"]
            cell["research_revision"] = {"atlas": atlas["result_id"], "kind": "EVIDENCE_OVERLAY", "previous_status": cell["status"]}
            # New atlas evidence carries no per-obligation directness review, so it
            # stays UNREVIEWED rather than inheriting the cell's grade.
            cell["evidence_roles"] = {**{e: "UNREVIEWED" for e in cell["evidence"]}, **cell["evidence_roles"]}
        cells.append(cell)
    if actions or overlays: raise ValueError("unused atlas coordinates")
    counts, migrations = Counter(x["status"] for x in cells), Counter(x["migration_status"] for x in cells)
    reviewed_no_transfer_unmapped = sum(x["migration_status"] == "REVIEWED_NO_TRANSFER" and x["status"] == "NOT_MAPPED" for x in cells)
    return {
        "schema_version": "foundational-intersection-cube-v3", "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V3",
        "result_kind": "RESEARCH_REFINED_FOUNDATIONAL_NAVIGATION_CUBE", "lifecycle": "LITERATURE_SCOPED", "created": "2026-08-12",
        "repository_base_commit": "1ec0ae4b25c0cb53859263613a8dc6a56fb85709", "dependency_tags": v2["dependency_tags"],
        "purpose": "Apply the bounded normally-hyperbolic factor atlas while retaining the complete v2 migration history.",
        "compatibility": {"v0_unchanged": True, "v1_unchanged": True, "v2_unchanged": True, "axes_preserved_from_v2": True, "coordinates_preserved_from_v2": True, "migration_fields_preserved_from_v2": True, "research_atlas": atlas["result_id"], "rule": "New child-specific evidence may classify a cell even when the old parent evidence had a REVIEWED_NO_TRANSFER decision; the migration decision remains historical and unchanged."},
        "axes": v2["axes"], "cell_statuses": v2["cell_statuses"], "migration_statuses": v2["migration_statuses"],
        "evidence_role_vocabulary": v2["evidence_role_vocabulary"], "evidence_role_rule": v2["evidence_role_rule"],
        "dimensions": {"axis_sizes": [6, 6, 16], "cartesian_total": 576, "emitted_cells": len(cells), "coverage_classified_cells": len(cells) - counts["NOT_MAPPED"], "migration_reviewed_cells": len(cells), "migration_pending_cells": 0, "reviewed_no_transfer_cells": migrations["REVIEWED_NO_TRANSFER"], "reviewed_no_transfer_unmapped_cells": reviewed_no_transfer_unmapped, "research_status_changes": len(atlas["cell_actions"]), "research_evidence_overlays": len(atlas["evidence_overlays"]), "status_counts": dict(sorted(counts.items())), "migration_status_counts": dict(sorted(migrations.items())), "evidence_role_counts": dict(sorted(Counter(role for x in cells for role in x["evidence_roles"].values()).items())), "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(x["evidence_roles"].values()) for x in cells)},
        "cells": cells,
        "provenance": {"inputs": [{"path": str(x.relative_to(ROOT)), "sha256": sha(x)} for x in (V2, ATLAS)]},
        "independent_checker": {"path": "foundations/check_refined_intersection_cube_v3.py", "checks": ["v2 coordinate and migration preservation", "nine status changes", "five evidence overlays", "evidence closure", "status counts", "canonical digest"], "expected_digest": digest(cells)},
        "claim_flags": {"v2_preserved": True, "atlas_actions_applied": True, "all_emitted_migrations_reviewed": True, "all_576_cells_assessed": False, "literature_complete": False, "weakest_base_proved": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "coverage for the 81 still-unmapped reviewed-no-transfer coordinates", "that NOT_MAPPED means no literature exists", "a weakest mathematical base", "a reverse-mathematical classification of hyperbolic PDE", "a choice-free Green theorem", "a continuum limit from finite graphs", "a new Lorentzian-causal Weyl result"],
        "human_report": "foundations/reports/refined-intersection-cube-v3.md",
    }


def render(result: dict[str, Any]) -> str:
    d = result["dimensions"]
    lines = ["# Research-refined foundations intersection cube v3", "", f"**Result:** `{result['result_id']}`", "", "## Outcome", "", f"The normally-hyperbolic atlas changes **{d['research_status_changes']}** coverage classifications and adds **{d['research_evidence_overlays']}** evidence overlays without changing any v2 coordinate or migration decision. Coverage rises from 364 to **{d['coverage_classified_cells']}** of 452 emitted cells.", "", f"All 88 `REVIEWED_NO_TRANSFER` decisions remain as historical statements about the old parent evidence. New child-specific evidence now covers seven of those cells, leaving **{d['reviewed_no_transfer_unmapped_cells']}** still `NOT_MAPPED`.", "", "## Coverage status", "", "| Status | Cells |", "|---|---:|"]
    lines += [f"| `{k}` | {v} |" for k, v in d["status_counts"].items()]
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v3.py --check", "python3 foundations/check_refined_intersection_cube_v3.py", "python3 foundations/verify_refined_intersection_cube_v3.py", "```", "", "## Boundaries", ""]
    lines += ["- This does not establish " + x + "." for x in result["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated():
    result = build(); return (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode(), render(result).encode()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    values = generated(); outputs = ((OUTPUT, values[0]), (REPORT, values[1])); stale = [str(p.relative_to(ROOT)) for p, v in outputs if not p.is_file() or p.read_bytes() != v]
    if args.check:
        if stale: print("FOUNDATIONAL_INTERSECTION_CUBE_V3: stale: " + ", ".join(stale)); return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V3: generated artifacts current"); return 0
    for path, value in outputs: path.write_bytes(value)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V3: wrote result and report"); return 0


if __name__ == "__main__": raise SystemExit(main())
