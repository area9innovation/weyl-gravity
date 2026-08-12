#!/usr/bin/env python3
"""Independent checker for the migration-reviewed cube v2."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
V1 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
AUDIT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(cells: list[dict[str, Any]]) -> str:
    payload = [(x.get("foundation"), x.get("carrier"), x.get("obligation"), x.get("status"), x.get("migration_status"), x.get("evidence"), x.get("migration_evidence")) for x in cells]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if result is None else result
    v1, audit = load(V1), load(AUDIT)
    errors: list[str] = []
    cells = result.get("cells", [])
    v1_by = {(x["foundation"], x["carrier"], x["obligation"]): x for x in v1["cells"]}
    by = {(x.get("foundation"), x.get("carrier"), x.get("obligation")): x for x in cells}
    if len(cells) != 452 or len(by) != 452 or set(by) != set(v1_by):
        errors.append("v1 coordinate preservation")
    decisions = {x["coordinate"]: x for x in audit["decisions"]}
    applied = 0
    for coordinate, cell in by.items():
        original = v1_by.get(coordinate, {})
        if original.get("status") == "MIGRATION_UNRESOLVED":
            audit_key = "|".join(coordinate)
            decision = decisions.get(audit_key, {})
            applied += 1
            if cell.get("status") != decision.get("resulting_coverage_status") or cell.get("migration_status") != decision.get("decision") or cell.get("evidence") != [] or cell.get("evidence_roles") != {} or cell.get("migration_evidence") != decision.get("parent_evidence"):
                errors.append("audit application " + audit_key)
        else:
            for field in ("foundation", "carrier", "obligation", "status", "evidence", "evidence_roles", "parent_obligation", "migration_relation", "summary", "boundary"):
                if cell.get(field) != original.get(field):
                    errors.append("nonpending preservation " + "|".join(coordinate))
                    break
        if not cell.get("migration_status") or not isinstance(cell.get("migration_evidence"), list) or not cell.get("migration_rationale"):
            errors.append("migration fields " + "|".join(coordinate))
    if applied != 112:
        errors.append("112 decisions applied")
    statuses = Counter(x.get("status") for x in cells)
    migrations = Counter(x.get("migration_status") for x in cells)
    expected_statuses = {"LITERATURE_RESULT": 90, "LOCAL_RESULT": 85, "NOT_MAPPED": 88, "PIECES_ONLY": 158, "PRIORITY_GAP": 31}
    expected_migrations = {"CAPABILITY_QUALIFIED": 257, "EXACT_PARENT_TRANSFER": 72, "REVIEWED_CHILD_GAP": 24, "REVIEWED_NO_TRANSFER": 88, "REVIEWED_OVERLAY": 11}
    dimensions = result.get("dimensions", {})
    if dict(sorted(statuses.items())) != expected_statuses or dimensions.get("status_counts") != expected_statuses:
        errors.append("coverage counts")
    if dict(sorted(migrations.items())) != expected_migrations or dimensions.get("migration_status_counts") != expected_migrations:
        errors.append("migration counts")
    if dimensions.get("migration_pending_cells") != 0 or dimensions.get("migration_reviewed_cells") != 452 or dimensions.get("coverage_classified_cells") != 364:
        errors.append("review dimensions")
    role_counts = Counter(role for x in cells for role in (x.get("evidence_roles") or {}).values())
    dual_direct = sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set((x.get("evidence_roles") or {}).values()) for x in cells)
    if dimensions.get("evidence_role_counts") != dict(sorted(role_counts.items())) or dimensions.get("dual_direct_cells") != dual_direct:
        errors.append("evidence-role counts")
    if any(sorted(x.get("evidence_roles") or {}) != sorted(x.get("evidence") or []) for x in cells):
        errors.append("evidence-role closure")
    calculated = digest(cells)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "cells": len(cells), "audit_decisions_applied": applied, "coverage_classified": dimensions.get("coverage_classified_cells"), "reviewed_no_transfer": migrations["REVIEWED_NO_TRANSFER"], "reviewed_child_gap": migrations["REVIEWED_CHILD_GAP"], "migration_pending": dimensions.get("migration_pending_cells"), "role_counts": dict(sorted(role_counts.items())), "dual_direct_cells": dual_direct}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
