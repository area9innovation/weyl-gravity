#!/usr/bin/env python3
"""Generate cube v2 by applying the explicit v1 migration audit."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V1 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v2.md"

RELATION_TO_STATUS = {
    "EXACT_ONE_TO_ONE": "EXACT_PARENT_TRANSFER",
    "CAPABILITY_QUALIFIED": "CAPABILITY_QUALIFIED",
    "REVIEWED_V1_OVERLAY": "REVIEWED_OVERLAY",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(cell: dict[str, Any]) -> str:
    return "|".join(cell[x] for x in ("foundation", "carrier", "obligation"))


def canonical_digest(cells: list[dict[str, Any]]) -> str:
    payload = [(x["foundation"], x["carrier"], x["obligation"], x["status"], x["migration_status"], x["evidence"], x["migration_evidence"]) for x in cells]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    v1, audit = load(V1), load(AUDIT)
    decisions = {x["coordinate"]: x for x in audit["decisions"]}
    cells = []
    for original in v1["cells"]:
        item = dict(original)
        if original["status"] == "MIGRATION_UNRESOLVED":
            decision = decisions.pop(key(original), None)
            if decision is None:
                raise ValueError("missing audit decision " + key(original))
            item["status"] = decision["resulting_coverage_status"]
            item["evidence"] = []
            item["migration_status"] = decision["decision"]
            item["migration_evidence"] = decision["parent_evidence"]
            item["migration_rationale"] = decision["rationale"]
            item["summary"] = ("Reviewed child gap: " if decision["decision"] == "REVIEWED_CHILD_GAP" else "Reviewed parent-evidence transfer: ") + decision["rationale"]
            item["boundary"] = decision["boundary"]
        else:
            relation = original["migration_relation"]
            if relation not in RELATION_TO_STATUS:
                raise ValueError("unhandled migration relation " + relation)
            item["migration_status"] = RELATION_TO_STATUS[relation]
            item["migration_evidence"] = list(original["evidence"])
            item["migration_rationale"] = {
                "EXACT_ONE_TO_ONE": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
                "CAPABILITY_QUALIFIED": "The explicit v1 evidence-capability registry licenses transfer to this child.",
                "REVIEWED_V1_OVERLAY": "A child-specific v1 review overrides the mechanical migration.",
            }[relation]
        cells.append(item)
    if decisions:
        raise ValueError("unused audit decisions: " + ", ".join(sorted(decisions)))
    counts = Counter(x["status"] for x in cells)
    migrations = Counter(x["migration_status"] for x in cells)
    return {
        "schema_version": "foundational-intersection-cube-v2",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V2",
        "result_kind": "MIGRATION_REVIEWED_FOUNDATIONAL_NAVIGATION_CUBE",
        "lifecycle": "LITERATURE_SCOPED",
        "created": "2026-08-12",
        "repository_base_commit": "24e988693bd9ee6874bedf9de476202c949a2e7e",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "purpose": "Preserve the refined v1 axes while separating scientific coverage from evidence-migration review and clearing all 112 pending migrations.",
        "compatibility": {
            "v0_unchanged": True, "v1_unchanged": True,
            "axes_preserved_from_v1": True, "coordinates_preserved_from_v1": True,
            "migration_audit": audit["result_id"],
            "rule": "Coverage status and migration status are independent. REVIEWED_NO_TRANSFER maps coverage to NOT_MAPPED; REVIEWED_CHILD_GAP maps coverage to PRIORITY_GAP.",
        },
        "axes": v1["axes"],
        "cell_statuses": [
            {"id": "LOCAL_RESULT", "meaning": "A bounded local result directly supports this refined obligation."},
            {"id": "LITERATURE_RESULT", "meaning": "A reviewed source directly treats this refined obligation within its boundary."},
            {"id": "PIECES_ONLY", "meaning": "Relevant ingredients exist but do not compose the refined result."},
            {"id": "PRIORITY_GAP", "meaning": "A child-specific review records a coherent current-programme gap."},
            {"id": "NOT_MAPPED", "meaning": "No coverage classification is made; this is not a literature-absence claim."}
        ],
        "migration_statuses": [
            {"id": "EXACT_PARENT_TRANSFER", "meaning": "The unsplit v0 obligation transfers exactly."},
            {"id": "CAPABILITY_QUALIFIED", "meaning": "An explicit evidence capability supports the split child."},
            {"id": "REVIEWED_OVERLAY", "meaning": "A child-specific v1 overlay supplies the classification."},
            {"id": "REVIEWED_NO_TRANSFER", "meaning": "The named parent evidence was reviewed and does not support the child."},
            {"id": "REVIEWED_CHILD_GAP", "meaning": "An evidence-free broad parent gap was decomposed into this explicit child gap."}
        ],
        "dimensions": {
            "axis_sizes": [6, 6, 16], "cartesian_total": 576,
            "emitted_cells": len(cells), "coverage_classified_cells": len(cells) - counts["NOT_MAPPED"],
            "migration_reviewed_cells": len(cells), "migration_pending_cells": 0,
            "reviewed_no_transfer_cells": migrations["REVIEWED_NO_TRANSFER"],
            "status_counts": dict(sorted(counts.items())), "migration_status_counts": dict(sorted(migrations.items())),
        },
        "cells": cells,
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in (V1, AUDIT)]},
        "independent_checker": {"path": "foundations/check_refined_intersection_cube_v2.py", "checks": ["v1 coordinate preservation", "112 audit decisions applied", "coverage/migration field separation", "zero pending migrations", "status counts", "canonical digest"], "expected_digest": canonical_digest(cells)},
        "claim_flags": {"v0_preserved": True, "v1_preserved": True, "all_v1_migrations_reviewed": True, "coverage_and_migration_separated": True, "all_576_cells_assessed": False, "literature_complete": False, "weakest_base_proved": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "coverage for the 88 reviewed-no-transfer coordinates", "that NOT_MAPPED means no literature exists", "that every Cartesian coordinate is coherent", "a weakest mathematical base", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/refined-intersection-cube-v2.md",
    }


def render(result: dict[str, Any]) -> str:
    d = result["dimensions"]
    lines = [
        "# Migration-reviewed foundations intersection cube v2", "", f"**Result:** `{result['result_id']}`", "",
        "## Outcome", "",
        f"V2 preserves the v1 6 × 6 × 16 axes and all **{d['emitted_cells']}** emitted coordinates. Migration review is complete for those coordinates: **{d['migration_pending_cells']} pending**, including **{d['reviewed_no_transfer_cells']} reviewed no-transfer** cells whose coverage is now explicitly `NOT_MAPPED`.", "",
        f"Coverage is classified in **{d['coverage_classified_cells']}** emitted cells. The other {d['reviewed_no_transfer_cells']} do not inherit their broad parent's evidence and are not called scientific gaps.", "",
        "## Coverage status", "", "| Status | Cells |", "|---|---:|",
    ]
    for status, count in d["status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines += ["", "## Migration status", "", "| Status | Cells | Meaning |", "|---|---:|---|"]
    meanings = {x["id"]: x["meaning"] for x in result["migration_statuses"]}
    for status, count in d["migration_status_counts"].items():
        lines.append(f"| `{status}` | {count} | {meanings[status]} |")
    lines += [
        "", "## Interpretation", "",
        "A reviewed no-transfer decision answers only whether the named v0 parent evidence supports the refined child. It does not answer whether other literature supports the cell. A reviewed child gap is stronger: the formerly broad gap has been stated as a precise missing child object, but it is still a current-corpus programme gap rather than an impossibility result.", "",
        "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v2.py --check", "python3 foundations/check_refined_intersection_cube_v2.py", "python3 foundations/verify_refined_intersection_cube_v2.py", "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    result = build()
    return (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode(), render(result).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    expected = [(OUTPUT, result), (REPORT, report)]
    stale = [str(path.relative_to(ROOT)) for path, content in expected if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_INTERSECTION_CUBE_V2: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V2: generated artifacts current")
        return 0
    for path, content in expected:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V2: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
