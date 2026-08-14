#!/usr/bin/env python3
"""Independent full-Cartesian and preservation checker for cube v9."""
from __future__ import annotations

from collections import Counter
from itertools import product
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json"
V8 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json"
AUDIT = ROOT / "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
EVIDENCE_ID = "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(coordinate(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision")) for cell in cells],
        "interfaces": interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    old, audit = load(V8), load(AUDIT)
    errors: list[str] = []
    cells = result.get("cells", [])
    current = {coordinate(cell): cell for cell in cells}
    prior = {coordinate(cell): cell for cell in old["cells"]}
    decisions = {"|".join(item["coordinate"].values()): item for item in audit["decisions"]}
    axis_ids = [[item["id"] for item in axis["keys"]] for axis in old["axes"]]
    surface = {"|".join(parts) for parts in product(*axis_ids)}
    complement = {key for key in surface if key not in prior or prior[key]["status"] == "NOT_MAPPED"}
    if len(cells) != 576 or len(current) != 576 or set(current) != surface:
        errors.append("exact 6x6x16 Cartesian surface")
    if len(decisions) != 175 or set(decisions) != complement:
        errors.append("exact 175-coordinate audit complement")

    revised_emitted = 0
    added = 0
    for key in surface & set(current):
        cell = current[key]
        source = prior.get(key)
        decision = decisions.get(key)
        if source is not None and source["status"] != "NOT_MAPPED":
            if cell != source:
                errors.append("prior classified cell drift " + key)
                break
            continue
        if decision is None:
            errors.append("unreviewed complement " + key)
            break
        expected_prior = "NOT_MAPPED" if source is not None else "NOT_EMITTED"
        revision = cell.get("classification_revision", {})
        expected_revision = {"certificate": EVIDENCE_ID, "previous_status": expected_prior, "new_status": "REVIEWED_GAP", "evidence_role": "SUPPORTING", "status_change": True}
        if cell.get("status") != "REVIEWED_GAP" or revision != expected_revision:
            errors.append("reviewed-gap projection " + key)
            break
        if cell.get("evidence_roles", {}).get(EVIDENCE_ID) != "SUPPORTING" or EVIDENCE_ID not in cell.get("evidence", []):
            errors.append("reviewed-gap evidence " + key)
            break
        if cell.get("summary") != decision.get("finding") or cell.get("boundary") != decision.get("boundary"):
            errors.append("reviewed-gap text " + key)
            break
        if source is not None:
            revised_emitted += 1
            for field in ("migration_status", "migration_evidence", "migration_rationale", "migration_relation", "parent_obligation"):
                if cell.get(field) != source.get(field):
                    errors.append("emitted migration drift " + key)
                    break
        else:
            added += 1
            if cell.get("migration_status") != "DIRECT_COORDINATE_REVIEW" or cell.get("parent_obligation") is not None or cell.get("migration_evidence") != [EVIDENCE_ID]:
                errors.append("direct coordinate review " + key)
                break

    for key, cell in current.items():
        roles = cell.get("evidence_roles", {})
        if sorted(roles) != sorted(cell.get("evidence", [])):
            errors.append("evidence role closure " + key)
            break
        direct = set(roles.values()) & {"DIRECT_LOCAL", "DIRECT_LITERATURE"}
        if direct and cell.get("status") not in {"LOCAL_RESULT", "LITERATURE_RESULT"}:
            errors.append("directness role/status agreement " + key)
            break

    if result.get("certified_interfaces") != old.get("certified_interfaces"):
        errors.append("certified interface preservation")
    counts_counter = Counter(cell.get("status") for cell in cells)
    counts = {status: counts_counter.get(status, 0) for status in ("LITERATURE_RESULT", "LOCAL_RESULT", "NOT_MAPPED", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP")}
    expected_counts = {"LITERATURE_RESULT": 93, "LOCAL_RESULT": 115, "NOT_MAPPED": 0, "PIECES_ONLY": 163, "PRIORITY_GAP": 30, "REVIEWED_GAP": 175}
    dimensions = result.get("dimensions", {})
    if counts != expected_counts or dimensions.get("status_counts") != dict(sorted(expected_counts.items())):
        errors.append("status counts")
    expected_dimensions = {
        "cartesian_total": 576, "emitted_cells": 576, "coverage_classified_cells": 576,
        "migration_reviewed_cells": 576, "migration_pending_cells": 0,
        "reviewed_no_transfer_cells": 88, "reviewed_no_transfer_unmapped_cells": 0,
        "reviewed_no_transfer_classified_cells": 88, "direct_coordinate_review_cells": 124,
        "newly_classified_cells": 175, "new_reviewed_gap_cells": 175,
        "certified_cross_cell_interfaces": 2,
    }
    for name, expected in expected_dimensions.items():
        if dimensions.get(name) != expected:
            errors.append("dimension " + name)
    if revised_emitted != 51:
        errors.append("51 emitted revisions")
    if added != 124:
        errors.append("124 direct additions")
    calculated = digest(cells, result.get("certified_interfaces", []))
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {
        "digest": calculated, "cells": len(cells), "revised_emitted": revised_emitted,
        "added": added, "not_mapped": counts.get("NOT_MAPPED"), "status_counts": counts,
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
