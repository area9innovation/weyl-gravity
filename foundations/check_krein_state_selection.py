#!/usr/bin/env python3
"""Independent exact checker for the Krein state/selection separation."""
from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json"


def mat_vec(matrix: tuple[tuple[int, int], tuple[int, int]], vector: tuple[int, int]) -> tuple[int, int]:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def transpose(matrix: tuple[tuple[int, int], tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    return ((matrix[0][0], matrix[1][0]), (matrix[0][1], matrix[1][1]))


def multiply(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return tuple(
        tuple(sum(left[row][middle] * right[middle][column] for middle in range(2)) for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def hilbert(vector: tuple[int, int], other: tuple[int, int]) -> int:
    return vector[0] * other[0] + vector[1] * other[1]


def krein(vector: tuple[int, int], other: tuple[int, int]) -> int:
    return vector[0] * other[0] - vector[1] * other[1]


def omega(sign: int, vector: tuple[int, int], matrix: tuple[tuple[int, int], tuple[int, int]]) -> int:
    return sign * krein(vector, mat_vec(matrix, vector))


def fraction_payload(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def finite_digest() -> tuple[str, int]:
    positive = (1, 0)
    negative = (0, 1)
    rows = []
    for entries in product(range(-2, 3), repeat=4):
        matrix = ((entries[0], entries[1]), (entries[2], entries[3]))
        square = multiply(transpose(matrix), matrix)
        positive_value = omega(1, positive, square)
        negative_value = omega(-1, negative, square)
        positive_norm = hilbert(mat_vec(matrix, positive), mat_vec(matrix, positive))
        negative_norm = hilbert(mat_vec(matrix, negative), mat_vec(matrix, negative))
        rows.append([*entries, positive_value, positive_norm, negative_value, negative_norm])
    payload = json.dumps(rows, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest(), len(rows)


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if result is None else result
    errors: list[str] = []
    positive = (1, 0)
    negative = (0, 1)
    identity = ((1, 0), (0, 1))
    positive_projection = ((1, 0), (0, 0))

    if krein(positive, positive) != 1 or krein(negative, negative) != -1:
        errors.append("Krein signature control")
    if omega(1, positive, identity) != 1 or omega(-1, negative, identity) != 1:
        errors.append("state normalization")
    if (omega(1, positive, positive_projection), omega(-1, negative, positive_projection)) != (1, 0):
        errors.append("state nonuniqueness witness")

    digest, matrix_count = finite_digest()
    if digest != result.get("independent_checker", {}).get("expected_finite_digest"):
        errors.append("finite positivity digest")
    if matrix_count != result.get("finite_exact_witness", {}).get("integer_matrix_count"):
        errors.append("finite matrix count")

    controls = result.get("finite_exact_witness", {}).get("permutation_controls", [])
    expected_controls = [
        {
            "sector_size_each_sign": size,
            "total_dimension": 2 * size,
            "uniform_coordinate_weight": fraction_payload(Fraction(1, 2 * size)),
            "fixed_two_coordinate_mass": fraction_payload(Fraction(1, size)),
        }
        for size in range(1, 13)
    ]
    if controls != expected_controls:
        errors.append("permutation truncation controls")
    if any(
        Fraction(item["uniform_coordinate_weight"]["numerator"], item["uniform_coordinate_weight"]["denominator"])
        <= 0
        for item in controls
    ):
        errors.append("nonpositive finite invariant weight")
    if controls and controls[-1]["uniform_coordinate_weight"] != {"numerator": 1, "denominator": 24}:
        errors.append("cutoff-12 invariant weight")

    promotions = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation"), item.get("new_status"))
        for item in result.get("cube_promotions", [])
    }
    expected_promotions = {
        ("CLASSICAL_STANDARD", "KREIN_INDEFINITE", "STATES_PROBABILITY", "LOCAL_RESULT"),
        ("WEAK_CHOICE_ZF", "KREIN_INDEFINITE", "STATES_PROBABILITY", "LOCAL_RESULT"),
        ("CLASSICAL_STANDARD", "ALGEBRAIC_CSTAR", "STATES_PROBABILITY", "LOCAL_RESULT"),
    }
    if promotions != expected_promotions:
        errors.append("cube promotion set")

    return errors, {
        "passed": not errors,
        "arithmetic": "exact integers and rational numbers only",
        "integer_matrices_checked": matrix_count,
        "positive_state_normalized": omega(1, positive, identity) == 1,
        "negative_state_sign_normalized": omega(-1, negative, identity) == 1,
        "states_distinguished_by_positive_projection": [
            omega(1, positive, positive_projection),
            omega(-1, negative, positive_projection),
        ],
        "permutation_cutoffs_checked": len(expected_controls),
        "finite_positivity_digest": digest,
    }


def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1: " + ("PASS" if not errors else "FAIL"))
    print(json.dumps({"errors": errors, **summary}, indent=2, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
