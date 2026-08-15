#!/usr/bin/env python3
"""Schema and independent-consumer verifier for the hh/hv cotangent lift."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator

from check_strict_386_hh_hv_auxiliary_cotangent_lift import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
SCHEMA = ROOT / "quantum-weyl/classical_import/schema/strict-386-hh-hv-auxiliary-cotangent-lift-v1.schema.json"


def main() -> int:
    value, schema = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text())
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1_SCHEMA_AND_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
