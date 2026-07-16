#!/usr/bin/env python3
"""Independent verifier for stationary companion decomposability."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_companion_stationary_decomposability import (
    stationary_orientation_replay,
    validate,
)
from .berger_companion_stationary_decomposability_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-companion-stationary-decomposability-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    if stationary_orientation_replay() != certificate["orientation_exclusion"][
        "sector_replay"
    ]:
        raise ValueError("independent stationary orientation replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_COMPANION_HADAMARD_STATE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("Hadamard-state mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER COMPANION STATIONARY DECOMPOSABILITY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
