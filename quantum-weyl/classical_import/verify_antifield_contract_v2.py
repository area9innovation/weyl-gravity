#!/usr/bin/env python3
"""Independent verifier for the executable v2 antifield contract receipt."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .antifield_contract_v2_certificate import (
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
    for path, expected in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"antifield v2 source drifted: {path}")
    if value != build():
        raise ValueError("antifield v2 contract does not reproduce")
    validate(value)
    for flag in (
        "CLASSICAL_ANTIFIELD_EXPORT_IMPORTED",
        "FULL_BV_G2_COMPLETE",
        "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
        "QME_RESTORED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            continue
        raise ValueError(f"antifield v2 overclaim survived: {flag}")
    return value


if __name__ == "__main__":
    verify()
    print("ANTIFIELD EXPORT V2 CONTRACT verifier: PASS")
