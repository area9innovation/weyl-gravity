#!/usr/bin/env python3
"""Schema, deterministic-generation and report verifier for cyclic repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from build_strict_minimal_bv_cyclic_sign_reconciliation import generated
from check_strict_minimal_bv_cyclic_sign_reconciliation import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md"
SCHEMA = HERE / "schema/strict-minimal-bv-cyclic-sign-reconciliation-v1.schema.json"


def verify(value: dict[str, Any] | None = None, report: str | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    report = REPORT.read_text() if report is None else report
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(
            json.loads(SCHEMA.read_text()), format_checker=FormatChecker()
        ).iter_errors(value)
    ]
    errors.extend("checker " + item for item in check(value))
    result_bytes, report_bytes = generated()
    candidate = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    if result_bytes != candidate:
        errors.append("deterministic result drift")
    if report_bytes != report.encode():
        errors.append("deterministic report drift")
    for phrase in (
        "540 exact",
        "0\ncyclicity defects",
        "canonical support-local odd pairing",
        "second variation",
        "third variation",
        "Local D",
        "Gate A remains fail closed",
        "Hadamard and QME remain open",
    ):
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify()
    print("STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
