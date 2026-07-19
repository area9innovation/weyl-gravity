#!/usr/bin/env python3
"""Verify the partition-refined leading-response rank-two certificate."""

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_recoil_partitioned_leading_response_rank_two import (
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
        raise SystemExit("partitioned leading-response rank-two certificate mismatch")
    print("BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
