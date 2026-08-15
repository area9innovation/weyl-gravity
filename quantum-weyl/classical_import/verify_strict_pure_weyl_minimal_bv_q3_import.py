#!/usr/bin/env python3
"""Schema and boundary verifier for the strict minimal-BV q3 import."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_pure_weyl_minimal_bv_q3_import import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.md"
SCHEMA = HERE / "schema/strict-pure-weyl-minimal-bv-q3-import-v1.schema.json"
REQUIRED_REPORT_PHRASES = (
    "authoritative classical minimal master action",
    "square-free algebra",
    "41 stored terms",
    "implementation regressions, not the proof",
    "does **not** yet claim the arity-three identity",
    "386-row stabilization",
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


def verify(value: dict[str, object], report: str, *, replay_exact: bool = True) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(no_float(value))
    errors.extend(check(value, replay_exact=replay_exact))
    for phrase in REQUIRED_REPORT_PHRASES:
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    if "LORENTZIAN-CAUSAL" in value.get("dependency_tags", []):
        errors.append("local q3 import promoted to LORENTZIAN-CAUSAL")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, exactness, authority chain and report boundaries pass")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
