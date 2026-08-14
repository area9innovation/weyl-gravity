#!/usr/bin/env python3
"""Verify cube v10 schema, deterministic outputs, provenance, and boundaries."""
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
from foundations.check_refined_intersection_cube_v10 import check
from foundations.refine_intersection_cube_v10 import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v10.md"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v10.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 cube-v10 schema"]
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent 570-cell preservation and six-decision projection")
    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes or text.encode() != report_bytes:
        errors.append("deterministic artifact drift")
    checks.append("deterministic result and report")
    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    checks.append("content-pinned cube-v9 and import inputs")
    for token in ("changes exactly six", "Five receive direct local", "remains `PRIORITY_GAP`", "conditional bridges remain open", "new LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("fail-closed finite/continuum/carrier report boundary")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V10: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
