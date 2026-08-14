#!/usr/bin/env python3
"""Independent verifier for the all-background BT lowest-mode theorem."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json")
SCHEMA_PATH = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-all-background-lowest-mode-curvature-v1.schema.json")


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_surplus(U: Fraction, V: Fraction, A: Fraction) -> Fraction:
    values = (U, V, U**-1, V**-1)
    cross = U * A + V / A + V * A / U**2 + U / (V**2 * A)
    return Fraction(1, 3) * sum((z * z for z in values), Fraction()) + cross - Fraction(4, 3) * sum(values, Fraction())


def independent_f(value: Fraction) -> Fraction:
    return value**2 + value**-2 - value - value**-1


def polynomial_product(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    output = [0] * (len(left) + len(right) - 1)
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            output[left_degree + right_degree] += left_coefficient * right_coefficient
    return tuple(output)


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def independent_l4(field: tuple[tuple[int, ...], ...]) -> tuple[Fraction, Fraction]:
    mode = (1, 0, -1, 0)
    d = tuple(mode[(t + 1) % 4] - mode[t] for t in range(4))
    e = tuple(d[t] - d[(t - 1) % 4] for t in range(4))
    direct = Fraction()
    absorbed = Fraction()
    for t in range(4):
        for x in range(4):
            weights = []
            differences = []
            for neighbor_t, neighbor_x in (((t - 1) % 4, x), ((t + 1) % 4, x), (t, (x - 1) % 4), (t, (x + 1) % 4)):
                weights.append(p2(field[neighbor_t][neighbor_x] - field[t][x]))
                differences.append(mode[neighbor_t] - mode[t])
            first = sum((w * delta for w, delta in zip(weights, differences)), Fraction())
            second = sum((w * delta * delta for w, delta in zip(weights, differences)), Fraction())
            direct += first * first + (sum(weights, Fraction(-4))) * second
            U = p2(field[(t + 1) % 4][x] - field[t][x])
            ratio = p2(field[(t - 1) % 4][x] + field[(t + 1) % 4][x] - 2 * field[t][x])
            absorbed += Fraction(6, 5) * independent_f(U) * d[t] ** 2 + ratio * e[t] ** 2
    return 16 * direct, 16 * absorbed


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False

        plaquette = data["plaquette_absorption"]
        for row in plaquette["exact_edge_fixtures"]:
            U, V, A = (decode(row[name]) for name in ("U", "V", "A"))
            surplus = independent_surplus(U, V, A)
            retained = Fraction(1, 5) * (independent_f(U) + independent_f(V))
            if decode(row["surplus"]) != surplus or decode(row["retained_fifth"]) != retained:
                return False
            if decode(row["gap"]) != surplus - retained or surplus < retained:
                return False

        if plaquette["spatial_degree"] != 6:
            return False
        power = tuple(plaquette["derivative_polynomial_power_coefficients_on_R_equals_2_plus_s"])
        R = (2, 1)
        R_squared = polynomial_product(R, R)
        Y = (R_squared[0] - 2, *R_squared[1:])
        Y_squared = polynomial_product(Y, Y)
        RY = polynomial_product(R, Y)
        independently_derived_power = tuple(
            8 * Y_squared[index]
            - 17 * (RY[index] if index < len(RY) else 0)
            + (60 if index == 0 else 0)
            for index in range(len(Y_squared))
        )
        if power != independently_derived_power or power != (24, -42, 58, 47, 8):
            return False
        degree = len(power) - 1
        bernstein = tuple(
            sum((Fraction(power[i] * comb(k, i), comb(degree, i)) for i in range(k + 1)), Fraction())
            for k in range(degree + 1)
        )
        if bernstein != tuple(decode(value) for value in plaquette["derivative_polynomial_bernstein_coefficients"]):
            return False
        if bernstein != (Fraction(24), Fraction(27, 2), Fraction(38, 3), Fraction(133, 4), Fraction(95)):
            return False

        theorem = data["theorem"]
        if decode(theorem["retained_free_fraction"]) != Fraction(4, 9):
            return False
        if decode(theorem["variance_constant"]) != Fraction(9, 2):
            return False
        cycle = data["cycle_completion"]
        if decode(cycle["completion_coefficient"]) != Fraction(18, 5):
            return False
        if decode(cycle["relative_loss_bound"]) != Fraction(5, 9):
            return False
        if decode(cycle["retained_free_fraction"]) != Fraction(4, 9):
            return False
        if decode(cycle["final_action_curvature_constant"]) != Fraction(2, 9):
            return False
        fixture = data["exact_full_lattice_fixture"]
        field = tuple(tuple(row) for row in fixture["integer_exponents_by_time_and_first_space"])
        direct, absorbed = independent_l4(field)
        if decode(fixture["direct_full_4d_hessian"]) != direct:
            return False
        if decode(fixture["absorbed_full_4d_lower_expression"]) != absorbed:
            return False
        if not direct >= absorbed >= decode(fixture["universal_target"]):
            return False
        disposition = data["method_disposition"]
        if disposition["all_background_uniform_recentered_conditional_variance"] != "PROVED":
            return False
        if disposition["annealed_center_second_moment"] != "OPEN":
            return False
        if disposition["actual_interacting_h_minus_one_second_moment"] != "OPEN":
            return False
        if data["foundational_dependency_cut"]["weakest_base_or_reversal"] != "NOT_ESTABLISHED":
            return False
        if not all(data["checks"].values()):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
