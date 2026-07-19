#!/usr/bin/env python3
"""Independent replay of the Berger Hadamard regular-morphism boundary."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_hadamard_regular_morphism_boundary import (
    finite_microlocal_replay,
    validate,
)
from .berger_hadamard_regular_morphism_boundary_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-hadamard-regular-morphism-boundary-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    if (
        certificate["finite_microlocal_closure"]["checks"]
        != finite_microlocal_replay()["checks"]
    ):
        raise ValueError("independent finite microlocal replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_REGULAR_GREENHYP_MORPHISM"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("regular-morphism promotion mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER HADAMARD REGULAR-MORPHISM BOUNDARY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
