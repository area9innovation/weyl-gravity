#!/usr/bin/env python3
"""Schema and boundary verifier for the six-row suspended q2 ledger."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_six_row_suspended_q2_ast import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
REPORT = HERE / "REPORT_STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.md"
SCHEMA = HERE / "schema/strict-six-row-suspended-q2-ast-v1.schema.json"
REQUIRED_REPORT_PHRASES = (
    "twelve diagonal quadratic",
    "twenty-two ordered",
    "external Grassmann",
    "q1q2=0",
    "not be substituted",
    "not yet satisfy",
)


def _no_float(value: object, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, float):
        errors.append(f"floating-point value at {path}")
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(_no_float(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_no_float(child, f"{path}[{index}]"))
    return errors


def verify(value: dict[str, object], report: str) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(_no_float(value))
    errors.extend(check(value))
    for phrase in REQUIRED_REPORT_PHRASES:
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, exactness, row coverage, Koszul signs and boundaries pass")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
