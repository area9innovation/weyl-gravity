#!/usr/bin/env python3
"""Independent verifier for the split-field branch-projection contract."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_residual_ell3_branch_projection_readiness_v2 import (
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
)


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for path, expected in value["provenance"]["source_manifest"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"split-field readiness source drifted: {path}")
    if value != build():
        raise ValueError("split-field readiness certificate does not reproduce")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2 verifier: PASS")
