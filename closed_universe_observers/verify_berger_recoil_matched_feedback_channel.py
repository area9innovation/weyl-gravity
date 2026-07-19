#!/usr/bin/env python3
"""Verify the detector-matched absolute-g3 feedback certificate."""

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_recoil_matched_feedback_channel import (
    CERTIFICATE,
    SCHEMA,
    build,
)


def main() -> int:
    actual = json.loads(CERTIFICATE.read_text())
    expected = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(actual)
    if actual != expected:
        raise SystemExit("matched absolute-g3 feedback certificate mismatch")
    print("BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
