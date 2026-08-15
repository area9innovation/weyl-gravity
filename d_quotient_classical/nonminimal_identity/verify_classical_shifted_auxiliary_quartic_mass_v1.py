#!/usr/bin/env python3
"""Schema and independent-consumer verifier for the quartic mass export."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator

from check_classical_shifted_auxiliary_quartic_mass_v1 import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
SCHEMA = ROOT / "d_quotient_classical/nonminimal_identity/schema/classical-shifted-auxiliary-quartic-mass-v1.schema.json"


def main() -> int:
    value, schema = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text())
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
