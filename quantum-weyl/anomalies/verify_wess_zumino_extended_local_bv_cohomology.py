#!/usr/bin/env python3
"""Independent verifier for the extended WZ local-BV theorem."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json

from jsonschema import Draft202012Validator

try:
    from .wess_zumino_extended_local_bv_cohomology import OUTPUT, SCHEMA, build, validate
except ImportError:
    from wess_zumino_extended_local_bv_cohomology import OUTPUT, SCHEMA, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _rank(matrix: list[list[dict[str, int]]]) -> int:
    rows = [[_fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [value - factor * pivot for value, pivot in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("extended WZ local-BV theorem does not reproduce")
    left = value["local_algebra"]["left_inverse_matrix"]
    right = value["local_algebra"]["right_inverse_matrix"]
    size = len(left)
    identity = [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]
    if (
        [[_fraction(x) for x in row] for row in left] != identity
        or [[_fraction(x) for x in row] for row in right] != identity
        or _rank(value["H04"]["even_dh_boundary_matrix"]) != 1
        or _rank(value["H04"]["positive_afn_boundary_matrix"]) != 0
        or _rank(value["H14"]["boundary_matrix"]) != 4
        or value["one_loop_QME"]["strict_breaking_coordinates"]
        != value["one_loop_QME"]["boundary_image_coordinates"]
    ):
        raise ValueError("independent extended cohomology matrix replay failed")
    mutant = deepcopy(value)
    mutant["H04"]["even_classes"].remove("R(g_hat)^2")
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("missing dressed R-squared class was accepted")
    mutant = deepcopy(value)
    mutant["lifecycle"]["residual_transfer"] = "AUTHORIZED"
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("residual transfer over-promotion was accepted")
    return value


if __name__ == "__main__":
    verify()
    print("WZ extended local-BV cohomology independent verification: PASS")
