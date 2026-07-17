#!/usr/bin/env python3
"""Independent verifier for the Berger branch-carrier architecture preflight."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_branch_carrier_architecture_preflight import (
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
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"architecture-preflight source drifted: {path}")
    validate(value)
    if value != build():
        raise ValueError("architecture-preflight certificate does not reproduce")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER BRANCH-CARRIER ARCHITECTURE PREFLIGHT verifier: PASS")
