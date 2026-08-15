#!/usr/bin/env python3
"""Schema, exactness and prose-boundary verifier for the q3 preflight."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_386_stabilized_q3_lift_preflight import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.md"
SCHEMA = HERE / "schema/strict-386-stabilized-q3-lift-preflight-v1.schema.json"
PHRASES = (
    "same orthogonal direct sum",
    "16** potentially nonzero block",
    "72** minimal typed channels",
    "modulo horizontal boundary",
    "not an authoritative nonminimal",
    "does not yet authorize the lambda-squared q2/q3/Green response",
)


def floats(value: object, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, float):
        errors.append("float at " + path)
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(floats(child, path + "." + str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(floats(child, f"{path}[{index}]"))
    return errors


def verify(value: dict[str, object], report: str) -> list[str]:
    errors = ["schema: " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend(floats(value))
    errors.extend(check(value))
    for phrase in PHRASES:
        if phrase not in report:
            errors.append("report phrase: " + phrase)
    return errors


def main() -> int:
    errors = verify(json.loads(RESULT.read_text()), REPORT.read_text())
    print("STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for item in errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
