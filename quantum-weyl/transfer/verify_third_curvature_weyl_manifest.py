#!/usr/bin/env python3
"""Independent replay of the third-curvature Weyl carrier manifest."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json

from sympy import Matrix, Rational

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


def _transverse_tracefree_basis(momentum: Matrix) -> list[Matrix]:
    """Return five exact rational TT tensors at a nonzero 4-momentum."""
    transverse = Matrix([list(momentum)]).nullspace()
    orthogonal: list[Matrix] = []
    for vector in transverse:
        reduced = vector
        for previous in orthogonal:
            reduced -= previous * (previous.dot(reduced) / previous.dot(previous))
        orthogonal.append(reduced)
    projectors = [vector * vector.T / vector.dot(vector) for vector in orthogonal]
    return [
        projectors[0] - projectors[1],
        projectors[0] - projectors[2],
        orthogonal[0] * orthogonal[1].T + orthogonal[1] * orthogonal[0].T,
        orthogonal[0] * orthogonal[2].T + orthogonal[2] * orthogonal[0].T,
        orthogonal[1] * orthogonal[2].T + orthogonal[2] * orthogonal[1].T,
    ]


def _carrier_value(
    carrier: str,
    momenta: list[Matrix],
    tensors: list[Matrix],
    labels: Permutation,
):
    k1, k2, k3 = [momenta[index] for index in labels]
    first, second, third = [tensors[index] for index in labels]
    if carrier == "I10":
        return (first * second * third).trace()
    if carrier == "I24":
        return -(k2.T * first * k3)[0] * (second * third).trace()
    if carrier == "I25":
        return -((second * k3).T * first * (third * k2))[0]
    if carrier == "I28":
        return (k1.T * third * k2)[0] * (k3.T * first * second * k3)[0]
    if carrier == "I29":
        return -(
            (k2.T * first * k2)[0]
            * (k3.T * second * k3)[0]
            * (k1.T * third * k1)[0]
        )
    raise ValueError(f"unknown carrier: {carrier}")


def _scalar_flat_fixture_replay() -> None:
    """Replay the effective I29 symmetry and the sole A.35 null row."""
    momenta = [Matrix([1, 2, 0, 1]), Matrix([0, 1, 3, 0])]
    momenta.append(-momenta[0] - momenta[1])
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    columns = [
        ("I10", (0, 1, 2)),
        *(('I24', labels) for labels in ((0, 1, 2), (1, 0, 2), (2, 0, 1))),
        *(('I25', labels) for labels in ((0, 1, 2), (1, 0, 2), (2, 0, 1))),
        *(('I28', labels) for labels in ((0, 1, 2), (0, 2, 1), (1, 2, 0))),
        ("I29", (0, 1, 2)),
    ]
    evaluations = []
    reversal_differences = []
    for choices in itertools.product(range(5), repeat=3):
        tensors = [bases[index][choices[index]] for index in range(3)]
        evaluations.append(
            [
                _carrier_value(carrier, momenta, tensors, labels)
                for carrier, labels in columns
            ]
        )
        reversal_differences.append(
            _carrier_value("I29", momenta, tensors, (0, 2, 1))
            - _carrier_value("I29", momenta, tensors, (0, 1, 2))
        )
    matrix = Matrix(evaluations)
    if any(reversal_differences):
        raise ValueError("independent scalar-flat I29 reversal identity failed")
    if matrix.shape != (125, 11) or matrix.rank() != 10 or len(matrix.nullspace()) != 1:
        raise ValueError("independent scalar-flat carrier rank drifted")

    x1, x2, x3 = [momentum.dot(momentum) for momentum in momenta]
    a35 = Matrix(
        [
            3
            * -Rational(1, 12)
            * (x1**2 + x2**2 + x3**2 - 2 * x1 * x2 - 2 * x2 * x3 - 2 * x1 * x3),
            x1 / 2,
            x2 / 2,
            x3 / 2,
            -Rational(1, 2) * (x1 - x2 - x3),
            -Rational(1, 2) * (x2 - x1 - x3),
            -Rational(1, 2) * (x3 - x1 - x2),
            1,
            1,
            1,
            0,
        ]
    )
    if matrix * a35 != Matrix.zeros(125, 1):
        raise ValueError("independent A.35 carrier relation failed")
    null = matrix.nullspace()[0]
    pivot = next(index for index, value in enumerate(a35) if value)
    if null != a35 * (null[pivot] / a35[pivot]):
        raise ValueError("unexpected second scalar-flat carrier relation")


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
    expected_dimensions = {"I10": 1, "I24": 3, "I25": 3, "I28": 3, "I29": 1}
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
    if raw_tuple != (11, 5, 2) or _multiplicities(raw_tuple) != (5, 0, 3):
        raise ValueError("independent raw S3 character replay failed")
    if quotient_tuple != (10, 4, 1) or _multiplicities(quotient_tuple) != (4, 0, 3):
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
    enhancement = stored["scalar_flat_symmetry_enhancement"]
    if (
        enhancement["source_generic_stabilizer"] != "C3"
        or enhancement["effective_scalar_flat_K_stabilizer"] != "S3"
    ):
        raise ValueError("scalar-flat I29 symmetry enhancement drifted")
    _scalar_flat_fixture_replay()

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
    mutation["quotient_module"]["generic_label_orbit_dimension"] = 11
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
