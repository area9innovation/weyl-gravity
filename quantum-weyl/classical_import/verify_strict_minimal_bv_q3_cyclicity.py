#!/usr/bin/env python3
"""Schema and boundary verifier for minimal-BV q3 cyclicity."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator
from check_strict_minimal_bv_q3_cyclicity import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.md"
SCHEMA = HERE / "schema/strict-minimal-bv-q3-cyclicity-v1.schema.json"
PHRASES = ("D^4 S_W", "symmetric in all four", "modulo horizontal boundary", "does not claim pointwise equality", "386-row cyclic", "no full-carrier promotion")


def no_float(value: object, path: str = "$") -> list[str]:
    if isinstance(value, float):
        return [f"floating-point value at {path}"]
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in no_float(child, f"{path}.{key}")]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in no_float(child, f"{path}[{index}]")]
    return []


def verify(value: dict[str, object], report: str) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(no_float(value))
    errors.extend(check(value))
    errors.extend(f"report missing boundary phrase: {phrase}" for phrase in PHRASES if phrase not in report)
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_MINIMAL_BV_Q3_CYCLICITY_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print(f"  - {error}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
