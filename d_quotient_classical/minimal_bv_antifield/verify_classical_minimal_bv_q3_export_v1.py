#!/usr/bin/env python3
"""Schema, exactness and prose-boundary verifier for the classical q3 export."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_classical_minimal_bv_q3_export_v1 import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/minimal_bv_antifield"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-minimal-bv-q3-export-v1.md"
SCHEMA = HERE / "schema/classical-minimal-bv-q3-export-v1.schema.json"
REQUIRED_REPORT_PHRASES = (
    "authoritative pure-Weyl minimal master action",
    "Exactly one row",
    "not a reconstruction of a second BV complex",
    "does not",
    "386-row",
)


def no_float(value: object, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, float):
        errors.append(f"floating-point value at {path}")
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(no_float(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(no_float(child, f"{path}[{index}]"))
    return errors


def verify(value: dict[str, object], report: str) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(no_float(value))
    errors.extend(check(value))
    for phrase in REQUIRED_REPORT_PHRASES:
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, exactness, authority and fail-closed prose boundaries pass")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
