"""Independent verifier for the generic typed-biwave theorem import."""

from __future__ import annotations

import json
from jsonschema import Draft202012Validator

from .typed_biwave_volterra_theorem_import import OUTPUT, SCHEMA, build


def verify() -> dict:
    expected = build()
    actual = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(actual)
    if actual != expected:
        raise ValueError("typed-biwave theorem import does not reproduce")
    return actual


if __name__ == "__main__":
    verify()
    print("independent typed-biwave theorem import verifier: PASS")
