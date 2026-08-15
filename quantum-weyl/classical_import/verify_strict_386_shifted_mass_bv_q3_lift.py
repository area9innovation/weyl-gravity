#!/usr/bin/env python3
"""Schema and independent-consumer verifier for the auxiliary BV q3 lift."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator

from check_strict_386_shifted_mass_bv_q3_lift import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
SCHEMA = HERE / "schema/strict-386-shifted-mass-bv-q3-lift-v1.schema.json"


def main() -> int:
    value, schema = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text())
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
