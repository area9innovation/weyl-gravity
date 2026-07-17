#!/usr/bin/env python3
"""Independent verifier for zero-frequency ledger readiness."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .berger_zero_frequency_ledger_readiness import DEPENDENCIES, validate
from .berger_zero_frequency_ledger_readiness_certificate import HERE, OUTPUT, build_certificate


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-zero-frequency-ledger-readiness-v1.schema.json").read_text()
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if certificate != build_certificate():
        raise ValueError("zero-frequency readiness certificate does not reproduce")
    for name, path in DEPENDENCIES.items():
        if certificate["dependency_refs"][name]["sha256"] != hashlib.sha256(
            path.read_bytes()
        ).hexdigest():
            raise ValueError(f"zero-frequency dependency drifted: {name}")
    for key in (
        "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
        "BERGER_26_ROW_BRST_HADAMARD",
        "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"zero-frequency overclaim accepted: {key}")
    return certificate


def main() -> int:
    verify()
    print("BERGER ZERO-FREQUENCY readiness independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
