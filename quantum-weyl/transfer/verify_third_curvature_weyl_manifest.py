#!/usr/bin/env python3
"""Independent replay of the third-curvature Weyl carrier manifest."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json

try:
    from .third_curvature_weyl_manifest import OUTPUT, ROOT, build, validate
except ImportError:
    from third_curvature_weyl_manifest import OUTPUT, ROOT, build, validate


Permutation = tuple[int, int, int]
S3: tuple[Permutation, ...] = tuple(itertools.permutations(range(3)))


def _compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(3))  # type: ignore[return-value]


def _coset_count(subgroup: tuple[Permutation, ...]) -> int:
    unseen = set(S3)
    count = 0
    while unseen:
        representative = min(unseen)
        unseen.difference_update(_compose(representative, item) for item in subgroup)
        count += 1
    return count


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _polynomial(row: dict[str, dict[str, int]]) -> dict[tuple[int, int, int], Fraction]:
    return {
        tuple(int(item) for item in key.split(",")): _fraction(value)  # type: ignore[misc]
        for key, value in row.items()
    }


def _permute_polynomial(
    polynomial: dict[tuple[int, int, int], Fraction],
    permutation: Permutation,
) -> dict[tuple[int, int, int], Fraction]:
    result: dict[tuple[int, int, int], Fraction] = {}
    for exponents, coefficient in polynomial.items():
        target = tuple(exponents[permutation[index]] for index in range(3))
        result[target] = result.get(target, Fraction()) + coefficient
    return result


def _multiplicities(character: tuple[int, int, int]) -> tuple[int, int, int]:
    identity, transposition, three_cycle = character
    return (
        (identity + 3 * transposition + 2 * three_cycle) // 6,
        (identity - 3 * transposition + 2 * three_cycle) // 6,
        (2 * identity - 2 * three_cycle) // 6,
    )


def verify() -> dict[str, object]:
    stored = json.loads(OUTPUT.read_text())
    rebuilt = build()
    if stored != rebuilt:
        raise ValueError("stored third-curvature Weyl manifest is stale")
    validate(stored)

    identity = (0, 1, 2)
    subgroups = {
        "S3": S3,
        "S2_23": (identity, (0, 2, 1)),
        "S2_12": (identity, (1, 0, 2)),
        "C3": (identity, (1, 2, 0), (2, 0, 1)),
    }
    expected_dimensions = {"I10": 1, "I24": 3, "I25": 3, "I28": 3, "I29": 2}
    for row in stored["permutation_modules"]:
        dimension = _coset_count(subgroups[row["stabilizer"]])
        if dimension != expected_dimensions[row["carrier_id"]]:
            raise ValueError(f"independent label-orbit dimension drifted: {row['carrier_id']}")

    raw_character = stored["raw_module"]["character_by_cycle_type"]
    raw_tuple = (
        raw_character["identity"],
        raw_character["transposition"],
        raw_character["three_cycle"],
    )
    quotient_character = stored["quotient_module"]["character_by_cycle_type"]
    quotient_tuple = (
        quotient_character["identity"],
        quotient_character["transposition"],
        quotient_character["three_cycle"],
    )
    if raw_tuple != (12, 4, 3) or _multiplicities(raw_tuple) != (5, 1, 3):
        raise ValueError("independent raw S3 character replay failed")
    if quotient_tuple != (11, 3, 2) or _multiplicities(quotient_tuple) != (4, 1, 3):
        raise ValueError("independent quotient S3 character replay failed")

    rows = stored["four_dimensional_identity"]["coefficient_polynomials"]
    i10 = _polynomial(rows["I10"])
    i24 = _polynomial(rows["I24"])
    i25 = _polynomial(rows["I25"])
    i28 = _polynomial(rows["I28"])
    for permutation in S3:
        if _permute_polynomial(i10, permutation) != i10:
            raise ValueError("I10 relation coefficient is not fully symmetric")
    swap_23 = (0, 2, 1)
    if _permute_polynomial(i24, swap_23) != i24:
        raise ValueError("I24 relation coefficient violates its stabilizer")
    if _permute_polynomial(i25, swap_23) != i25:
        raise ValueError("I25 relation coefficient violates its stabilizer")
    if i28 != {(0, 0, 0): Fraction(1)}:
        raise ValueError("I28 elimination coefficient drifted")
    if stored["four_dimensional_identity"]["absent_carrier"] != "I29":
        raise ValueError("I29 anchor no longer survives the 4D relation")

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    mutations = []
    for flag in (
        "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE",
        "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED",
        "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["quotient_module"]["generic_label_orbit_dimension"] = 12
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["four_dimensional_identity"]["absent_carrier"] = "I28"
    mutations.append(mutation)
    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("third-curvature Weyl manifest mutation was accepted")

    print("third-curvature Weyl manifest independent replay: PASS")
    return stored


if __name__ == "__main__":
    verify()
