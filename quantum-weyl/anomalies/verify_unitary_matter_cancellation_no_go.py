#!/usr/bin/env python3
"""Independent verifier for the unitary-matter cancellation no-go."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json

from jsonschema import Draft202012Validator

try:
    from .unitary_matter_cancellation_no_go import OUTPUT, SCHEMA, SPECIES, build, validate
except ImportError:
    from unitary_matter_cancellation_no_go import OUTPUT, SCHEMA, SPECIES, build, validate


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("matter cancellation certificate does not reproduce")
    if any(c <= 0 or e >= 0 for c, e in SPECIES.values()):
        raise ValueError("matter cone is not standard-sign")
    for witness_index, coordinate in ((0, 0), (1, 1)):
        witness = value["separating_witnesses"][witness_index]
        sign = 1 if coordinate == 0 else -1
        if Fraction(**{
            "numerator": witness["gravity_value"]["numerator"],
            "denominator": witness["gravity_value"]["denominator"],
        }) <= 0:
            raise ValueError("gravity separation failed")
        if any(sign * vector[coordinate] <= 0 for vector in SPECIES.values()):
            raise ValueError("matter separation failed")
    mutant = deepcopy(value)
    mutant["classification"]["solution_set"] = "NONEMPTY"
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("nonempty-solution mutation was accepted")
    return value


if __name__ == "__main__":
    verify()
    print("unitary conformal matter cancellation no-go independent verification: PASS")
