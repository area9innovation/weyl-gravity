#!/usr/bin/env python3
"""Validate schema and semantics for the field-equation Green quotient inverse."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_386_field_equation_green_quotient_inverse import check


HERE = Path(__file__).resolve().parent
RESULT = HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
SCHEMA = HERE / "schema/strict-386-field-equation-green-quotient-inverse-v1.schema.json"


def verify() -> list[str]:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.path))]
    errors.extend(check(value))
    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1_SCHEMA: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1_SCHEMA: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
