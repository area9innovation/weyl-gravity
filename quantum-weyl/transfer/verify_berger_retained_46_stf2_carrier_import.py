#!/usr/bin/env python3
"""Independent receipt verifier for the pinned rank-46 carrier import."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_retained_46_stf2_carrier_import import (
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
    validate,
)


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for path, expected in value["consumer_provenance"]["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"rank-46 import consumer source drifted: {path}")
    validate(value)
    if value != build():
        raise ValueError("rank-46 import receipt does not reproduce")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_46_STF2_CARRIER_IMPORT verifier: PASS")
