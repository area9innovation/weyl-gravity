"""Independent verifier for round-S4 conformal-volume locality."""

from __future__ import annotations

import json
from jsonschema import Draft202012Validator

from .round_s4_conformal_volume_locality import OUTPUT, SCHEMA, build


def verify() -> dict:
    expected = build()
    actual = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(actual)
    if actual != expected:
        raise ValueError("conformal-volume locality certificate does not reproduce")
    return actual


if __name__ == "__main__":
    verify()
    print("independent round-S4 conformal-volume locality verifier: PASS")
