#!/usr/bin/env python3
"""Schema plus independent verification for strict nonlinear Green compatibility."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_m2_q2_q3_typed_green_compatibility import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
SCHEMA = HERE / "schema/strict-m2-q2-q3-typed-green-compatibility-v1.schema.json"


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
