#!/usr/bin/env python3
"""Independent verifier for the retained-36 projector-obstruction import."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_retained_36_branch_projector_obstruction_import import (
    LOCAL_SCHEMA,
    OUTPUT,
    ROOT,
    build,
)


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(LOCAL_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for path, expected in value["consumer_provenance"]["source_manifest"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"branch-projector obstruction consumer source drifted: {path}")
    if value != build():
        raise ValueError("branch-projector obstruction import does not reproduce")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER RETAINED-36 BRANCH PROJECTOR OBSTRUCTION IMPORT verifier: PASS")
