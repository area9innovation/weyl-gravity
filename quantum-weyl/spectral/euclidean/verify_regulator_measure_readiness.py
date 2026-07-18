"""Independent verifier for regulator/zero-mode/measure readiness."""

from __future__ import annotations

import json
from jsonschema import Draft202012Validator

from .regulator_measure_readiness import OUTPUT, SCHEMA, build


def verify() -> dict:
    expected = build()
    actual = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(actual)
    if actual != expected:
        raise ValueError("regulator/measure readiness does not reproduce")
    return actual


if __name__ == "__main__":
    verify()
    print("independent regulator/zero-mode/measure readiness verifier: PASS")
