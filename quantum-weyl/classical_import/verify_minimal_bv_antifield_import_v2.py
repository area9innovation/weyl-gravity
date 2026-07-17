"""Independent verifier for the accepted classical antifield V2 import."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .minimal_bv_antifield_import_v2_certificate import (
    EXPORT,
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
            raise ValueError(f"minimal-BV antifield import source drifted: {path}")
    if hashlib.sha256(EXPORT.read_bytes()).hexdigest() != value["dependency_refs"]["classical_export"]["sha256"]:
        raise ValueError("classical minimal-BV antifield export drifted")
    if value != build():
        raise ValueError("minimal-BV antifield import does not reproduce")
    validate(value)
    for flag in (
        "MINIMAL_BV_H04_H14_COMPUTED",
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
        raise ValueError(f"minimal-BV antifield overclaim survived: {flag}")
    return value


if __name__ == "__main__":
    verify()
    print("CLASSICAL MINIMAL-BV ANTIFIELD V2 IMPORT verifier: PASS")
