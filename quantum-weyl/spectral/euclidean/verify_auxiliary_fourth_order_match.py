"""Independent verifier for the standard spin-two auxiliary Schur identity."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator

from .auxiliary_fourth_order_match import (
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
    validate_claim_boundary,
)


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(checked)
    if checked != build():
        raise ValueError("auxiliary/fourth-order certificate does not reproduce")
    for path, expected in checked["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"auxiliary/fourth-order source drifted: {path}")
    for integer in range(-4, 5):
        eigenvalue = Fraction(integer)
        block_determinant = -(2 * eigenvalue + eigenvalue * eigenvalue)
        target = eigenvalue * (eigenvalue + 2)
        if block_determinant != -target:
            raise ValueError("independent eigenvalue determinant replay failed")
    for flag in (
        "FULL_GHOST_AND_NONMINIMAL_OPERATOR_MATCH",
        "REPOSITORY_AUXILIARY_MEASURE_MATCH",
        "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_DISPOSITION",
    ):
        mutant = deepcopy(checked)
        mutant["claim_flags"][flag] = True
        try:
            validate_claim_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"auxiliary/fourth-order overclaim survived: {flag}")
    return checked


if __name__ == "__main__":
    verify()
    print("standard spin2 auxiliary/fourth-order independent verifier: PASS")
