#!/usr/bin/env python3
"""Schema plus independent verification of the strict BRST Hadamard pair."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_386_brst_hadamard_two_point import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/lorentzian"
RESULT = HERE / "certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json"
SCHEMA = HERE / "schema/strict-386-brst-hadamard-two-point-v1.schema.json"


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("STRICT_386_BRST_HADAMARD_TWO_POINT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
