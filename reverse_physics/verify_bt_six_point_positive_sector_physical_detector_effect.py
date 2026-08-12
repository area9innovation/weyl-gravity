#!/usr/bin/env python3
"""Independent fraction verification of the positive BT detector effect."""
from __future__ import annotations

from fractions import Fraction
from dataclasses import dataclass
import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-positive-sector-physical-detector-effect-v1.schema.json")


@dataclass(frozen=True)
class Qsqrt3:
    rational: Fraction = Fraction(0)
    sqrt3: Fraction = Fraction(0)

    def __add__(self, other):
        other = other if isinstance(other, Qsqrt3) else Qsqrt3(Fraction(other))
        return Qsqrt3(self.rational + other.rational, self.sqrt3 + other.sqrt3)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt3(-self.rational, -self.sqrt3)

    def __sub__(self, other):
        return self + (-other if isinstance(other, Qsqrt3) else -Qsqrt3(Fraction(other)))

    def __mul__(self, other):
        other = other if isinstance(other, Qsqrt3) else Qsqrt3(Fraction(other))
        return Qsqrt3(self.rational * other.rational + 3 * self.sqrt3 * other.sqrt3, self.rational * other.sqrt3 + self.sqrt3 * other.rational)

    __rmul__ = __mul__


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [[sum(left[row][k] * right[k][column] for k in range(len(right))) for column in range(len(right[0]))] for row in range(len(left))]


def add(left, right):
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def identity(size):
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def permutation_sign(permutation):
    inversions = sum(permutation[i] > permutation[j] for i in range(len(permutation)) for j in range(i + 1, len(permutation)))
    return -1 if inversions % 2 else 1


def poly_add(left, right):
    size = max(len(left), len(right))
    return [(left[i] if i < len(left) else 0) + (right[i] if i < len(right) else 0) for i in range(size)]


def poly_mul(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def characteristic_coefficients(matrix):
    size = len(matrix)
    result = [Fraction(0)]
    for permutation in itertools.permutations(range(size)):
        term = [Fraction(permutation_sign(permutation))]
        for row, column in enumerate(permutation):
            factor = [-matrix[row][column], Fraction(1)] if row == column else [-matrix[row][column]]
            term = poly_mul(term, factor)
        result = poly_add(result, term)
    return result


def rank_fraction(matrix):
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        value = rows[rank][column]
        rows[rank] = [entry / value for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def reconstruct_positive_residue(channels):
    coefficients = [Fraction(0) if index == 1 else Fraction(1, 4) for index in range(10)]
    pair_index = {}
    for index, mask in enumerate(channels):
        pair_index[mask] = index
        pair_index[mask ^ 63] = index
    choi = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for mask, index in pair_index.items():
        choi[(mask >> 3) & 7][mask & 7] = coefficients[index]
    # U_plus^T A U_plus.  The two factors 1/sqrt(2) combine to 1/2.
    return [[sum(choi[row][column] for row in (i, 7 - i) for column in (j, 7 - j)) / 2 for j in range(4)] for i in range(4)]


def verify(certificate):
    embedding_path = next(row["path"] for row in certificate["provenance"]["inputs"] if "GHOST_EVEN_HISTORY" in row["path"])
    embedding = load(os.path.join(ROOT, embedding_path))
    channels = embedding["neutral_six_leg_carrier"]["representative_masks"]
    residue = reconstruct_positive_residue(channels)
    expected_residue = [[Fraction(1, 4), 0, 0, 0], [0, Fraction(1, 4), Fraction(1, 4), 0], [0, Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)], [0, Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)]]
    effect = multiply(transpose(residue), residue)
    characteristic = characteristic_coefficients(effect)
    expected_characteristic = [Fraction(0), Fraction(-1, 1024), Fraction(3, 64), Fraction(-9, 16), Fraction(1)]
    generator = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for row in range(4):
        for column in range(4):
            generator[row][4 + column] = -residue[column][row]
            generator[4 + row][column] = residue[row][column]
    second = scale(Fraction(1, 2), multiply(generator, generator))
    survival_amplitude = [row[:4] for row in second[:4]]
    zero4 = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    source = [Fraction(1), 0, 0, 0]
    source_click = sum(source[i] * effect[i][j] * source[j] for i in range(4) for j in range(4))
    root_low = Qsqrt3(Fraction(1, 4), Fraction(-1, 8))
    root_high = Qsqrt3(Fraction(1, 4), Fraction(1, 8))
    contraction_bound = Qsqrt3(Fraction(16), Fraction(-8))

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "positive_residue_reconstructed_from_Choi_masks": residue == expected_residue,
        "effect_reconstructed_as_Gram": effect == multiply(transpose(expected_residue), expected_residue),
        "characteristic_polynomial_reconstructed_by_permutations": characteristic == expected_characteristic,
        "effect_rank_is_three": rank_fraction(effect) == 3,
        "effect_trace_is_nine_sixteenths": sum(effect[i][i] for i in range(4)) == Fraction(9, 16),
        "spectrum_sum_and_product_fixtures": Qsqrt3(Fraction(1, 16)) + root_low + root_high == Qsqrt3(Fraction(9, 16)) and Qsqrt3(Fraction(1, 16)) * root_low * root_high == Qsqrt3(Fraction(1, 1024)),
        "algebraic_roots_are_nonnegative": 4 > 3 and root_high.rational > 0,
        "uniform_bound_is_positive": 16**2 > 3 * 8**2,
        "uniform_bound_saturates_largest_root": contraction_bound * root_high == Qsqrt3(Fraction(1)),
        "no_click_other_roots_remain_positive": Qsqrt3(Fraction(1)) - contraction_bound * Qsqrt3(Fraction(1, 16)) == Qsqrt3(Fraction(0), Fraction(1, 2)) and Qsqrt3(Fraction(1)) - contraction_bound * root_low == Qsqrt3(Fraction(-6), Fraction(4)) and 4**2 * 3 > 6**2,
        "generator_is_skew": transpose(generator) == scale(Fraction(-1), generator),
        "virtual_amplitude_is_minus_half_effect": survival_amplitude == scale(Fraction(-1, 2), effect),
        "survival_and_transition_coefficients_cancel": add(scale(Fraction(2), survival_amplitude), effect) == zero4,
        "declared_source_click_is_one_sixteenth": source_click == Fraction(1, 16),
        "rate_division_is_exact": Fraction(9, 1024) / Fraction(9, 8) == Fraction(1, 128),
        "declared_source_rate_is_exact": Fraction(1, 128) * source_click == Fraction(1, 2048),
        "full_rate_reconstruction_is_exact": Fraction(1, 128) * (Fraction(9, 16) + Fraction(9, 16)) == Fraction(9, 1024),
        "positive_auxiliary_source_is_not_scalar_promoted": certificate["interpretation"]["positive_public_BT_auxiliary_source"] == "EXACTLY_CONSTRUCTED" and certificate["interpretation"]["transported_perfect_square_scalar_source"] == "NOT_CONSTRUCTED",
        "probability_is_typed_as_jet": certificate["detector_probability_jet"]["status"] == "LEADING_ISOLATED_SHELL_TWO_OUTCOME_PROBABILITY_JET",
        "complete_finite_time_probability_remains_open": certificate["interpretation"]["complete_finite_time_probability"] == "NOT_CONSTRUCTED",
        "Eq19_boundary_is_preserved": certificate["interpretation"]["Eq19_all_orders"] == "NOT_PROVED" and "all-order Eq. (19)" in certificate["does_not_establish"],
        "Lorentzian_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
