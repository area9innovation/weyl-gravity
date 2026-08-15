#!/usr/bin/env python3
"""Validate schema and semantics for formal Møller-coefficient evidence."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from check_strict_386_polarized_formal_moller_coefficients import check


HERE = Path(__file__).resolve().parent
RESULT = HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
SCHEMA = HERE / "schema/strict-386-polarized-formal-moller-coefficients-v1.schema.json"


def verify() -> list[str]:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.path))]
    errors.extend(check(value))
    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1_SCHEMA: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1_SCHEMA: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
