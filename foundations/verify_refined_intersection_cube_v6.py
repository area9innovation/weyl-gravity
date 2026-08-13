#!/usr/bin/env python3
"""Verify cube v6 and its two certified interface projections."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_refined_intersection_cube_v6 import check
from foundations.refine_intersection_cube_v6 import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v6.md"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v6.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 cube-v6 schema"]
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent v5-preservation and two-interface audit")
    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes or text.encode() != report_bytes:
        errors.append("deterministic artifact drift")
    checks.append("deterministic result and report")
    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    checks.append("content-pinned v5 and interface inputs")
    flags = result.get("claim_flags", {})
    for name in ("v5_preserved", "two_cross_cell_interfaces_certified", "free_ground_state_dynamics_interface_added", "endpoint_evidence_overlaid"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("new_cell_status_promotion_required", "interacting_ground_state_selected", "empirical_agreement_assessed", "new_lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    checks.append("fail-closed claim boundary")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V6: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
