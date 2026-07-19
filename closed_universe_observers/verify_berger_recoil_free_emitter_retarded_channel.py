#!/usr/bin/env python3
"""Verify the finite free-emitter first-retarded-channel certificate."""

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_recoil_free_emitter_retarded_channel import (
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
        raise SystemExit("free-emitter first-retarded-channel certificate mismatch")
    print("BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
