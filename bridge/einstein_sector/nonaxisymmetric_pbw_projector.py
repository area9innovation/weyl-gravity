"""Exact equatorial projector for nonaxisymmetric ell=2 quadratic sources.

The product PBW payload stores coefficient jets at ``theta=pi/2``.  This
module couples two standard normalized spherical-harmonic carriers with an
exact Clebsch--Gordan tensor and extracts the unique reduced output
multiplicity from equatorial output jets.  It deliberately does not evaluate
the background coefficient profiles away from the equator.
"""
from __future__ import annotations

import json
from functools import lru_cache
from math import factorial
from pathlib import Path
from typing import Sequence

import sympy as sp
from sympy.functions.special.spherical_harmonics import Ynm
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
THETA, PHI = sp.symbols("theta phi", real=True)
EQUATOR = {THETA: sp.pi / 2, PHI: 0}

AXIAL_ROWS = frozenset((8, 9, 11, 12, 16, 17))
POLAR_ROWS = frozenset((6, 7, 10, 18, 19))
OUTPUT_ROWS = {
    "axial": ((22, 23), (25, 26), (30,), (31,)),
    "polar": ((20,), (21,), (24,), (32, 33)),
}


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def multinomial(total: int, coefficient: int, first: int) -> int:
    second = total - coefficient - first
    return factorial(total) // (
        factorial(coefficient) * factorial(first) * factorial(second)
    )


@lru_cache(maxsize=1)
def payload() -> tuple[list[dict[int, sp.Expr]], list[dict[str, object]]]:
    content = json.loads(Q2.read_text())["content"]
    profiles: list[dict[int, sp.Expr]] = []
    for profile in content["coefficient_profiles"]:
        values: dict[int, sp.Expr] = {}
        for item in profile["coefficient_jets"]:
            word = item["word"]
            if any(axis != 2 for axis in word):
                raise AssertionError(f"non-theta coefficient jet: {word}")
            values[len(word)] = sp.Rational(item["coefficient"])
        profiles.append(values)
    terms = [
        term
        for term in content["terms"]
        if 20 <= int(term["output_row"]) <= 33
        and 6 <= int(term["inputs"][0]["row"]) <= 19
        and 6 <= int(term["inputs"][1]["row"]) <= 19
    ]
    return profiles, terms


@lru_cache(maxsize=None)
def harmonic(ell: int, magnetic: int) -> sp.Expr:
    return sp.simplify(sp.expand_func(Ynm(ell, magnetic, THETA, PHI)))


@lru_cache(maxsize=None)
def axial_covector_component(ell: int, magnetic: int, axis: int) -> sp.Expr:
    value = harmonic(ell, magnetic)
    if axis == 2:
        return sp.diff(value, PHI) / sp.sin(THETA)
    if axis == 3:
        return -sp.sin(THETA) * sp.diff(value, THETA)
    raise ValueError(axis)


@lru_cache(maxsize=None)
def axial_contravariant_component(ell: int, magnetic: int, axis: int) -> sp.Expr:
    value = harmonic(ell, magnetic)
    if axis == 2:
        return sp.diff(value, PHI) / sp.sin(THETA)
    if axis == 3:
        return -sp.diff(value, THETA) / sp.sin(THETA)
    raise ValueError(axis)


def supported_rows(parity: str) -> frozenset[int]:
    return AXIAL_ROWS if parity == "axial" else POLAR_ROWS


def component(
    parity: str,
    row: int,
    magnetic: int,
    amplitudes: Sequence[sp.Expr],
) -> sp.Expr:
    y_value = harmonic(2, magnetic)
    if parity == "axial":
        h_time, h_space, q_time, q_space = amplitudes
        return {
            8: h_time * axial_covector_component(2, magnetic, 2),
            9: h_time * axial_covector_component(2, magnetic, 3),
            11: h_space * axial_covector_component(2, magnetic, 2),
            12: h_space * axial_covector_component(2, magnetic, 3),
            16: q_time * y_value,
            17: q_space * y_value,
        }.get(row, sp.S.Zero)
    if parity == "polar":
        a_time, mixed, a_space, maxwell = amplitudes
        return {
            6: a_time * y_value,
            7: mixed * y_value,
            10: a_space * y_value,
            18: maxwell * axial_covector_component(2, magnetic, 2),
            19: maxwell * axial_covector_component(2, magnetic, 3),
        }.get(row, sp.S.Zero)
    raise ValueError(parity)


@lru_cache(maxsize=None)
def _angular_derivative(
    parity: str,
    row: int,
    magnetic: int,
    theta_order: int,
    phi_order: int,
) -> sp.Expr:
    unit = component(parity, row, magnetic, (1, 1, 1, 1))
    if unit == 0:
        return sp.S.Zero
    return canonical(
        sp.diff(unit, THETA, theta_order, PHI, phi_order).subs(EQUATOR)
    )


def mode_derivative(
    parity: str,
    row: int,
    word: tuple[int, ...],
    magnetic: int,
    momentum: sp.Expr,
    frequency: sp.Expr,
    amplitudes: Sequence[sp.Expr],
    extra_theta: int = 0,
) -> sp.Expr:
    row_to_amplitude = {
        "axial": {8: 0, 9: 0, 11: 1, 12: 1, 16: 2, 17: 3},
        "polar": {6: 0, 7: 1, 10: 2, 18: 3, 19: 3},
    }[parity]
    if row not in row_to_amplitude:
        return sp.S.Zero
    angular = _angular_derivative(
        parity,
        row,
        magnetic,
        word.count(2) + extra_theta,
        word.count(3),
    )
    return (
        amplitudes[row_to_amplitude[row]]
        * (-sp.I * frequency) ** word.count(0)
        * (sp.I * momentum) ** word.count(1)
        * angular
    )


def _term_roles(
    first_parity: str,
    second_parity: str,
    left_row: int,
    right_row: int,
) -> tuple[int, int] | None:
    first_rows, second_rows = supported_rows(first_parity), supported_rows(second_parity)
    if left_row in first_rows and right_row in second_rows:
        return 0, 1
    if first_parity != second_parity and left_row in second_rows and right_row in first_rows:
        return 1, 0
    return None


def coupled_output_jet(
    first_parity: str,
    second_parity: str,
    first_amplitudes: Sequence[sp.Expr],
    second_amplitudes: Sequence[sp.Expr],
    first_momentum: sp.Expr,
    first_frequency: sp.Expr,
    second_momentum: sp.Expr,
    second_frequency: sp.Expr,
    output_ell: int,
    output_magnetic: int,
    output_row: int,
    theta_order: int,
) -> sp.Expr:
    profiles, terms = payload()
    role_data = (
        (first_parity, first_amplitudes, first_momentum, first_frequency),
        (second_parity, second_amplitudes, second_momentum, second_frequency),
    )
    result = sp.S.Zero
    for first_magnetic in range(-2, 3):
        second_magnetic = output_magnetic - first_magnetic
        if not -2 <= second_magnetic <= 2:
            continue
        coupling = clebsch_gordan(
            2,
            2,
            output_ell,
            first_magnetic,
            second_magnetic,
            output_magnetic,
        )
        if coupling == 0:
            continue
        for term in terms:
            if int(term["output_row"]) != output_row:
                continue
            left, right = term["inputs"]
            left_row, right_row = int(left["row"]), int(right["row"])
            roles = _term_roles(first_parity, second_parity, left_row, right_row)
            if roles is None:
                continue
            magnetic_numbers = (first_magnetic, second_magnetic)
            profile = profiles[int(term["coefficient_profile"])]
            for coefficient_order in range(theta_order + 1):
                coefficient = profile.get(coefficient_order, sp.S.Zero)
                if coefficient == 0:
                    continue
                for left_extra in range(theta_order - coefficient_order + 1):
                    right_extra = theta_order - coefficient_order - left_extra
                    left_role, right_role = roles
                    left_data, right_data = role_data[left_role], role_data[right_role]
                    result += (
                        coupling
                        * multinomial(theta_order, coefficient_order, left_extra)
                        * coefficient
                        * mode_derivative(
                            left_data[0], left_row, tuple(left["word"]),
                            magnetic_numbers[left_role], left_data[2], left_data[3],
                            left_data[1], left_extra,
                        )
                        * mode_derivative(
                            right_data[0], right_row, tuple(right["word"]),
                            magnetic_numbers[right_role], right_data[2], right_data[3],
                            right_data[1], right_extra,
                        )
                    )
    return canonical(result)


def output_basis(output_parity: str, output_row: int, ell: int, magnetic: int) -> sp.Expr:
    if output_parity == "polar" and output_row in (20, 21, 24):
        return harmonic(ell, magnetic)
    if output_parity == "polar" and output_row in (32, 33):
        return axial_contravariant_component(ell, magnetic, output_row - 30)
    if output_parity == "axial" and output_row in (22, 23, 25, 26):
        return axial_contravariant_component(ell, magnetic, 2 if output_row in (22, 25) else 3)
    if output_parity == "axial" and output_row in (30, 31):
        return harmonic(ell, magnetic)
    raise ValueError((output_parity, output_row))


def reduced_source(
    first_parity: str,
    second_parity: str,
    first_amplitudes: Sequence[sp.Expr],
    second_amplitudes: Sequence[sp.Expr],
    first_momentum: sp.Expr,
    first_frequency: sp.Expr,
    second_momentum: sp.Expr,
    second_frequency: sp.Expr,
    output_ell: int,
    output_magnetic: int | None = None,
    max_jet_order: int = 4,
) -> sp.Matrix:
    output_parity = (
        "polar" if (first_parity == second_parity) == (output_ell % 2 == 0)
        else "axial"
    )
    # Equivalent readable parity rule: same parity gives polar even/axial odd;
    # cross parity gives axial even/polar odd.
    if first_parity == second_parity:
        output_parity = "polar" if output_ell % 2 == 0 else "axial"
    else:
        output_parity = "axial" if output_ell % 2 == 0 else "polar"
    magnetic = output_ell if output_magnetic is None else output_magnetic
    coefficients: list[sp.Expr] = []
    for row_group in OUTPUT_ROWS[output_parity]:
        ratios: list[sp.Expr] = []
        for row in row_group:
            basis = output_basis(output_parity, row, output_ell, magnetic)
            for order in range(max_jet_order + 1):
                denominator = canonical(sp.diff(basis, THETA, order).subs(EQUATOR))
                if denominator == 0:
                    continue
                numerator = coupled_output_jet(
                    first_parity, second_parity,
                    first_amplitudes, second_amplitudes,
                    first_momentum, first_frequency,
                    second_momentum, second_frequency,
                    output_ell, magnetic, row, order,
                )
                ratios.append(canonical(numerator / denominator))
        if not ratios:
            raise AssertionError((output_parity, output_ell, magnetic, row_group))
        if any(canonical(value - ratios[0]) != 0 for value in ratios[1:]):
            raise AssertionError(
                f"output did not separate on L={output_ell}, M={magnetic}, rows={row_group}: {ratios}"
            )
        coefficients.append(ratios[0])
    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    weights = (
        (eigenvalue / 2, eigenvalue / 2, sp.Rational(1, 2), sp.Rational(1, 2))
        if output_parity == "axial"
        else (2, 2, 2, 2 * eigenvalue)
    )
    return sp.Matrix(
        [canonical(weight * value) for weight, value in zip(weights, coefficients, strict=True)]
    )


def axisymmetric_conversion(output_ell: int) -> sp.Expr:
    """Convert a normalized coupled coefficient to the P_2 x P_2 -> P_L one."""

    input_scale = sp.sqrt(4 * sp.pi / 5)
    output_scale = sp.sqrt(4 * sp.pi / (2 * output_ell + 1))
    return canonical(
        input_scale**2
        * clebsch_gordan(2, 2, output_ell, 0, 0, 0)
        / output_scale
    )
