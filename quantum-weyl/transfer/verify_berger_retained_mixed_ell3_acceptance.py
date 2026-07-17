#!/usr/bin/env python3
"""Fast verifier for the persisted retained mixed-ell3 acceptance."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_retained_mixed_ell3_acceptance_certificate import OUTPUT, ROOT, SCHEMA, build


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for path, expected in value["consumer_provenance"]["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"retained ell3 consumer source drifted: {path}")
    if value != build(run_scientific=False):
        raise ValueError("retained ell3 acceptance deterministic replay drifted")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE verifier: PASS")
