#!/usr/bin/env python3
"""Verify the finite positive-energy preparation coefficient certificate."""

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_recoil_positive_energy_preparation_coefficients import (
    CERTIFICATE,
    SCHEMA,
    build,
)


def main() -> int:
    expected = build()
    actual = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(actual)
    if actual != expected:
        raise SystemExit("positive-energy preparation coefficient certificate mismatch")
    print("BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
