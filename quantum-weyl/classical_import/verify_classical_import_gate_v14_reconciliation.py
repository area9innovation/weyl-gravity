#!/usr/bin/env python3
"""Schema and independent verifier for Gate-A V14."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator

from check_classical_import_gate_v14_reconciliation import check


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
SCHEMA = ROOT / "quantum-weyl/classical_import/schema/classical-import-gate-v14-reconciliation-v1.schema.json"


def main() -> int:
    value, schema = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text())
    errors = ["schema: " + error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("CLASSICAL_IMPORT_GATE_V14_RECONCILIATION_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
