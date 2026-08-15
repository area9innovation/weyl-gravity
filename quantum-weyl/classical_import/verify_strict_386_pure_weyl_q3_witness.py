#!/usr/bin/env python3
"""Schema and boundary verifier for the strict pure-Weyl q3 witness."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
SCHEMA = HERE / "schema/strict-386-pure-weyl-q3-witness-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_386_PURE_WEYL_Q3_WITNESS_V1.md"


def verify(value: dict | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)]
    report = REPORT.read_text() if REPORT.is_file() else ""
    for token in ("-75760/9", "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP", "not yet as a full authoritative import"):
        if token not in report:
            errors.append("report boundary token absent: " + token)
    return errors


def main() -> int:
    errors = verify()
    print("STRICT_386_PURE_WEYL_Q3_WITNESS_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("- " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
