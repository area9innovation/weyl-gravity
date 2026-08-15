#!/usr/bin/env python3
"""Schema and boundary verifier for the minimal-BV arity-three identity."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_minimal_bv_arity_three_identity import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.md"
SCHEMA = HERE / "schema/strict-minimal-bv-arity-three-identity-v1.schema.json"
REQUIRED_REPORT_PHRASES = (
    "72 nonempty channels",
    "212 composable paths",
    "first three Taylor coefficients",
    "implementation regressions",
    "does **not** promote the 386-row candidate",
    "Quartic q3 cyclicity",
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


def verify(value: dict[str, object], report: str, *, replay: bool = True) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(no_float(value))
    errors.extend(check(value, replay=replay))
    for phrase in REQUIRED_REPORT_PHRASES:
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    if "LORENTZIAN-CAUSAL" in value.get("dependency_tags", []):
        errors.append("local arity-three result promoted to LORENTZIAN-CAUSAL")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, exactness, exhaustive replay and lifecycle boundaries pass")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
