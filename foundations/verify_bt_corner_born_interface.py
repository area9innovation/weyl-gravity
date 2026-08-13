#!/usr/bin/env python3
"""Verify the certified finite-corner state-to-probability interface."""
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

from foundations.build_bt_corner_born_interface import generated
from foundations.check_bt_corner_born_interface import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
REPORT = ROOT / "foundations/reports/bt-corner-born-interface.md"
SCHEMA = ROOT / "foundations/schema/foundational-bt-corner-born-interface-v1.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 interface schema"]
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent exact shared-object and probability audit")
    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if text.encode() != report_bytes:
        errors.append("deterministic report drift")
    checks.append("deterministic result and report")
    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    checks.append("content-pinned source certificates")
    for token in ("CONDITIONAL_BRIDGE", "same state", "STATE_REPRESENTATION", "PROBABILITY_RULE", "9/25", "16/25", "five explicit hypotheses", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("human-readable claim and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
