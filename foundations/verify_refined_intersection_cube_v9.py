#!/usr/bin/env python3
"""Verify cube v9, its full surface, and fail-closed boundaries."""
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
from foundations.check_refined_intersection_cube_v9 import check
from foundations.refine_intersection_cube_v9 import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v9.md"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v9.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 cube-v9 schema"]
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent full-Cartesian, preservation, and 175-gap audit")
    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes or text.encode() != report_bytes:
        errors.append("deterministic artifact drift")
    checks.append("deterministic result and report")
    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    checks.append("content-pinned cube-v8 and gap-audit inputs")
    flags = result.get("claim_flags", {})
    for name in ("v8_classified_cells_preserved", "all_576_coordinates_present", "all_576_coordinates_assessed", "zero_not_mapped", "one_hundred_seventy_five_reviewed_gaps", "direct_result_count_unchanged"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("all_obligations_solved", "literature_complete", "literature_absence_established", "empirical_agreement_assessed", "complete_physical_theory_established", "new_lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    for token in ("6 × 6 × 16 = 576", "all 401 previously classified", "51 emitted `NOT_MAPPED`", "124 previously browser-only", "175 reviewed open gaps", "0 not-mapped cells", "not a completed scientific result", "do not license evidence transfer", "new LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("fail-closed reviewed-gap semantics and report boundary")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V9: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
