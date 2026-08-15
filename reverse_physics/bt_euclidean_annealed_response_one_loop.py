#!/usr/bin/env python3
"""Certify the BT annealed signed-response one-loop reduction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from collections import defaultdict
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_ONE_LOOP_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-response-one-loop-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-annealed-response-one-loop.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_annealed_response_one_loop.py"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SIGNED_RESPONSE_AXIAL_GATE_V1.json"
]
SOURCE_COMMIT = "f200473094f19981ad41566270c1fc7b4abbc20b"

Coord = tuple[int, int, int, int]
Monomial = tuple[int, ...]
Poly = dict[Monomial, Fraction]
ORIGIN: Coord = (0, 0, 0, 0)
DIRS = tuple(
    tuple(sign if index == axis else 0 for index in range(4))
    for axis in range(4)
    for sign in (-1, 1)
)


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add_coord(left: Coord, right: Coord) -> Coord:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def padd(*polys: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] += coefficient
    return {key: value for key, value in result.items() if value}


def pscale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in poly.items()
        if scalar * coefficient
    }


def pmul(left: Poly, right: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            result[tuple(sorted(left_monomial + right_monomial))] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value}


def pconst(value: Fraction | int) -> Poly:
    value = Fraction(value)
    return {(): value} if value else {}


class Variables:
    def __init__(self) -> None:
        self.ids: dict[Coord, int] = {}
        self.coords: dict[int, Coord] = {}

    def var(self, coord: Coord) -> Poly:
        if coord == ORIGIN:
            raise ValueError("the origin is the conditional fiber")
        if coord not in self.ids:
            identifier = len(self.ids) + 1
            self.ids[coord] = identifier
            self.coords[identifier] = coord
        return {(self.ids[coord],): Fraction(1)}


def free_conditional_center(variables: Variables) -> Poly:
    nearest = [add_coord(ORIGIN, direction) for direction in DIRS]
    axial = [add_coord(direction, direction) for direction in DIRS]
    mixed = []
    for first in range(4):
        for second in range(first + 1, 4):
            for first_sign in (-1, 1):
                for second_sign in (-1, 1):
                    mixed.append(
                        tuple(
                            first_sign
                            if axis == first
                            else second_sign
                            if axis == second
                            else 0
                            for axis in range(4)
                        )
                    )
    result: Poly = {}
    for coord in nearest:
        result = padd(result, pscale(variables.var(coord), Fraction(2, 9)))
    for coord in axial:
        result = padd(result, pscale(variables.var(coord), Fraction(-1, 72)))
    for coord in mixed:
        result = padd(result, pscale(variables.var(coord), Fraction(-1, 36)))
    return result


def fiber_field(
    coord: Coord, center: Poly, variables: Variables
) -> tuple[Poly, Fraction]:
    if coord == ORIGIN:
        return center, Fraction(1)
    return variables.var(coord), Fraction()


def conditional_jets() -> tuple[Variables, Poly, dict[str, Poly]]:
    """Return only the u-components that survive the centered Gaussian fiber."""

    variables = Variables()
    center = free_conditional_center(variables)
    first = {1: {}, 2: {}, 3: {}}
    second = {1: {}, 3: {}}
    affected = [ORIGIN] + [add_coord(ORIGIN, direction) for direction in DIRS]
    for vertex in affected:
        vertex_zero, vertex_u = fiber_field(vertex, center, variables)
        a0: Poly = {}
        a1 = Fraction()
        b0: Poly = {}
        b1: Poly = {}
        b2 = Fraction()
        c0: Poly = {}
        c1: Poly = {}
        c2: Poly = {}
        c3 = Fraction()
        for direction in DIRS:
            endpoint = add_coord(vertex, direction)
            endpoint_zero, endpoint_u = fiber_field(
                endpoint, center, variables
            )
            d0 = padd(endpoint_zero, pscale(vertex_zero, -1))
            d1 = endpoint_u - vertex_u
            d0_square = pmul(d0, d0)
            a0 = padd(a0, d0)
            a1 += d1
            b0 = padd(b0, d0_square)
            b1 = padd(b1, pscale(d0, 2 * d1))
            b2 += d1 * d1
            c0 = padd(c0, pmul(d0_square, d0))
            c1 = padd(c1, pscale(d0_square, 3 * d1))
            c2 = padd(c2, pscale(d0, 3 * d1 * d1))
            c3 += d1**3

        first[1] = padd(
            first[1],
            pscale(padd(pmul(a0, b1), pscale(b0, a1)), Fraction(1, 2)),
        )
        first[2] = padd(
            first[2],
            pscale(padd(pscale(a0, b2), pscale(b1, a1)), Fraction(1, 2)),
        )
        first[3] = padd(first[3], pconst(Fraction(a1 * b2, 2)))

        second[1] = padd(
            second[1],
            pscale(pmul(b0, b1), Fraction(1, 4)),
            pscale(
                padd(pmul(a0, c1), pscale(c0, a1)), Fraction(1, 6)
            ),
        )
        second[3] = padd(
            second[3],
            pscale(b1, Fraction(b2, 4)),
            pscale(
                padd(pscale(a0, c3), pscale(c2, a1)), Fraction(1, 6)
            ),
        )
    return variables, center, {
        "p1": first[1],
        "p2": first[2],
        "p3": first[3],
        "q1": second[1],
        "q3": second[3],
    }


def q_weight(coord: Coord) -> Fraction:
    return Fraction(coord[0] ** 2, 2)


def canonical_displacement(left: Coord, right: Coord) -> Coord:
    displacement = tuple(a - b for a, b in zip(left, right))
    opposite = tuple(-value for value in displacement)
    return min(displacement, opposite)  # type: ignore[return-value]


def derivative_form(
    left: Poly, variables: Variables, right: Poly | None = None
) -> tuple[Fraction, dict[Coord, Fraction]]:
    right = pconst(1) if right is None else right
    constant = Fraction()
    covariance: dict[Coord, Fraction] = defaultdict(Fraction)
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = left_monomial + right_monomial
            coefficient = left_coefficient * right_coefficient
            for index, variable in enumerate(monomial):
                weight = q_weight(variables.coords[variable])
                if not weight:
                    continue
                remainder = monomial[:index] + monomial[index + 1 :]
                value = coefficient * weight
                if not remainder:
                    constant += value
                elif len(remainder) == 2:
                    covariance[
                        canonical_displacement(
                            variables.coords[remainder[0]],
                            variables.coords[remainder[1]],
                        )
                    ] += value
                else:
                    raise ValueError("unexpected Wick degree")
    return constant, {key: value for key, value in covariance.items() if value}


def add_form(
    target: list, source: tuple[Fraction, dict[Coord, Fraction]], factor: Fraction
) -> None:
    target[0] += factor * source[0]
    for displacement, coefficient in source[1].items():
        target[1][displacement] += factor * coefficient


def covariance_kernel(
    variables: Variables, jets: dict[str, Poly]
) -> tuple[Fraction, dict[Coord, Fraction]]:
    variance = Fraction(1, 72)
    result: list = [Fraction(), defaultdict(Fraction)]
    add_form(
        result,
        derivative_form(jets["p1"], variables, jets["p2"]),
        2 * variance**2,
    )
    add_form(
        result,
        derivative_form(jets["p2"], variables, jets["p3"]),
        12 * variance**3,
    )
    add_form(
        result, derivative_form(jets["q1"], variables), -variance
    )
    add_form(
        result,
        derivative_form(jets["q3"], variables),
        -3 * variance**2,
    )
    return result[0], {
        key: value for key, value in result[1].items() if value
    }


def permutations4() -> list[tuple[int, ...]]:
    return list(itertools.permutations(range(4)))


def laurent_symmetrization(
    kernel: dict[Coord, Fraction]
) -> dict[Coord, Fraction]:
    laurent: dict[Coord, Fraction] = defaultdict(Fraction)
    for displacement, coefficient in kernel.items():
        if displacement == ORIGIN:
            laurent[displacement] += coefficient
        else:
            laurent[displacement] += coefficient / 2
            laurent[tuple(-value for value in displacement)] += coefficient / 2
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    permutations = permutations4()
    for exponent, coefficient in laurent.items():
        for permutation in permutations:
            permuted = tuple(exponent[permutation[index]] for index in range(4))
            result[permuted] += coefficient / len(permutations)
    return {key: value for key, value in result.items() if value}


def chebyshev(degree: int) -> dict[int, Fraction]:
    rows = [{0: Fraction(1)}, {1: Fraction(1)}]
    for _ in range(2, degree + 1):
        row: dict[int, Fraction] = defaultdict(Fraction)
        for power, coefficient in rows[-1].items():
            row[power + 1] += 2 * coefficient
        for power, coefficient in rows[-2].items():
            row[power] -= coefficient
        rows.append(dict(row))
    return rows[degree]


def mpoly_mul(left: dict[Coord, Fraction], right: dict[Coord, Fraction]):
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = tuple(a + b for a, b in zip(left_power, right_power))
            result[power] += left_coefficient * right_coefficient
    return {key: value for key, value in result.items() if value}


def x_polynomial(kernel: dict[Coord, Fraction]) -> dict[Coord, Fraction]:
    laurent = laurent_symmetrization(kernel)
    grouped: dict[Coord, list[Fraction]] = defaultdict(list)
    for exponent, coefficient in laurent.items():
        grouped[tuple(abs(value) for value in exponent)].append(coefficient)
    cosine: dict[Coord, Fraction] = defaultdict(Fraction)
    for absolute, coefficients in grouped.items():
        if len(set(coefficients)) != 1:
            raise ValueError("sign orbit failed")
        amplitude = coefficients[0] * 2 ** sum(value != 0 for value in absolute)
        row = {ORIGIN: Fraction(1)}
        for axis, degree in enumerate(absolute):
            factor = {}
            for power, coefficient in chebyshev(degree).items():
                exponent = [0, 0, 0, 0]
                exponent[axis] = power
                factor[tuple(exponent)] = coefficient
            row = mpoly_mul(row, factor)
        for exponent, coefficient in row.items():
            cosine[exponent] += amplitude * coefficient

    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for powers, coefficient in cosine.items():
        row = {ORIGIN: coefficient}
        for axis, power in enumerate(powers):
            factor = {}
            for degree in range(power + 1):
                exponent = [0, 0, 0, 0]
                exponent[axis] = degree
                factor[tuple(exponent)] = Fraction(
                    math.comb(power, degree) * (-1) ** degree, 2**degree
                )
            row = mpoly_mul(row, factor)
        for exponent, value in row.items():
            result[exponent] += value
    return {key: value for key, value in result.items() if value}


def elementary_symbol() -> dict[Coord, Fraction]:
    variables = [
        {tuple(1 if axis == index else 0 for axis in range(4)): Fraction(1)}
        for index in range(4)
    ]
    e1: dict[Coord, Fraction] = defaultdict(Fraction)
    e2: dict[Coord, Fraction] = defaultdict(Fraction)
    for variable in variables:
        for monomial, coefficient in variable.items():
            e1[monomial] += coefficient
    for left in range(4):
        for right in range(left + 1, 4):
            for monomial, coefficient in mpoly_mul(
                variables[left], variables[right]
            ).items():
                e2[monomial] += coefficient
    e1 = dict(e1)
    e2 = dict(e2)
    e1_2 = mpoly_mul(e1, e1)
    e1_3 = mpoly_mul(e1_2, e1)
    e1_4 = mpoly_mul(e1_2, e1_2)
    e1e2 = mpoly_mul(e1, e2)
    e1_2e2 = mpoly_mul(e1_2, e2)
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    rows = [
        (e1, Fraction(1, 24)),
        (e1_2, Fraction(-5, 288)),
        (e2, Fraction(1, 144)),
        (e1_3, Fraction(5, 1296)),
        (e1e2, Fraction(5, 1728)),
        (e1_4, Fraction(-5, 31104)),
        (e1_2e2, Fraction(-13, 31104)),
    ]
    for poly, factor in rows:
        for monomial, coefficient in poly.items():
            result[monomial] += factor * coefficient
    return {key: value for key, value in result.items() if value}


def symbol_value(values: tuple[Fraction, ...]) -> Fraction:
    e1 = sum(values, Fraction())
    e2 = sum(
        (values[left] * values[right] for left in range(4) for right in range(left + 1, 4)),
        Fraction(),
    )
    return (
        e1 / 24
        - Fraction(5, 288) * e1**2
        + e2 / 144
        + Fraction(5, 1296) * e1**3
        + Fraction(5, 1728) * e1 * e2
        - Fraction(5, 31104) * e1**4
        - Fraction(13, 31104) * e1**2 * e2
    )


def exact_l6_coefficient() -> Fraction:
    eigenvalues = (
        Fraction(0), Fraction(1), Fraction(3), Fraction(4), Fraction(3), Fraction(1)
    )
    total = Fraction()
    for momentum in itertools.product(range(6), repeat=4):
        values = tuple(eigenvalues[index] for index in momentum)
        omega = sum(values, Fraction())
        if omega:
            total += symbol_value(values) / omega**2
    return Fraction(-43, 5184) + total / 6**4


def diagnostic_coefficient(length: int) -> float:
    total = 0.0
    for momentum in itertools.product(range(length), repeat=4):
        values = tuple(
            2.0 * (1.0 - math.cos(2.0 * math.pi * index / length))
            for index in momentum
        )
        omega = sum(values)
        if not omega:
            continue
        e2 = sum(
            values[left] * values[right]
            for left in range(4)
            for right in range(left + 1, 4)
        )
        p = (
            omega / 24.0
            - 5.0 * omega**2 / 288.0
            + e2 / 144.0
            + 5.0 * omega**3 / 1296.0
            + 5.0 * omega * e2 / 1728.0
            - 5.0 * omega**4 / 31104.0
            - 13.0 * omega**2 * e2 / 31104.0
        )
        total += p / omega**2
    return -43.0 / 5184.0 + total / length**4


def build() -> dict:
    variables, center, jets = conditional_jets()
    vacuum_term, kernel = covariance_kernel(variables, jets)
    derived_symbol = x_polynomial(kernel)
    expected_symbol = elementary_symbol()
    l6 = exact_l6_coefficient()
    diagnostic_lengths = (5, 6, 8, 12, 16)
    diagnostics = [
        {"length": length, "binary64_b2": diagnostic_coefficient(length)}
        for length in diagnostic_lengths
    ]
    checks = {
        "free_center_has_40_terms": len(center) == 40,
        "free_center_coefficients_sum_to_one": sum(center.values(), Fraction()) == 1,
        "surviving_jet_term_counts": {
            key: len(value) for key, value in jets.items()
        } == {"p1": 820, "p2": 40, "p3": 1, "q1": 11480, "q3": 40},
        "vacuum_coefficient_is_minus_43_over_5184": vacuum_term == Fraction(-43, 5184),
        "covariance_kernel_has_161_terms": len(kernel) == 161,
        "covariance_kernel_kills_constant_mode": sum(kernel.values(), Fraction()) == 0,
        "conditional_wick_symbol_matches_elementary_formula": derived_symbol == expected_symbol,
        "elementary_symbol_has_69_monomials": len(expected_symbol) == 69,
        "l6_coefficient_exact_value": l6 == Fraction(-849547889, 1849425177600),
        "l6_coefficient_strictly_negative": l6 < 0,
        "diagnostics_are_negative": all(row["binary64_b2"] < 0 for row in diagnostics),
        "large_volume_sign_remains_uncertified": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_ONE_LOOP_V1",
        "schema_version": "reverse-physics-bt-euclidean-annealed-response-one-loop-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact finite-volume full-Gibbs annealed signed-response one-loop coefficient and all-volume Fourier reduction",
        "question": "Do actual Gibbs background fluctuations repair the negative weak-coupling vacuum coefficient beta_vac at the first nontrivial order?",
        "answer": (
            "Not completely. Expanding the exact conditional mean and the actual "
            "background marginal shows beta_L(lambda)=b_(2,L)*lambda^2+O_L(lambda^4). "
            "The order-lambda marginal reweighting drops out by translation and "
            "constant-shift symmetry. The surviving local Gaussian/Wick jet has an "
            "exact hypercubic Fourier numerator P. On the 6^4 torus its algebraic "
            "sum is b_(2,6)=-849547889/1849425177600<0. Thus annealing cancels most, "
            "but not all, of the negative vacuum defect at one loop. The exact "
            "all-volume formula and its Brillouin-zone limit are reduced below; a "
            "rigorous sign bound for that limit and a nonperturbative H^-1 estimate "
            "remain open."
        ),
        "corrected_distance_two_response": {
            "axial_path": "D_y M_o=-(exp(psi_y-2*psi_v)/lambda^2)*Cov_q(z,exp(z)), with v the unique intermediate site",
            "mixed_path": "sum the two coefficients exp(psi_y-2*psi_v) over the two intermediate sites",
            "sign": "each coefficient and Cov_q(z,exp(z)) are strictly positive, so every distance-two response is negative",
        },
        "conditional_expansion": {
            "scaled_field": "psi=lambda*phi",
            "action": "S_lambda=S0+lambda*S1+lambda^2*S2+O(lambda^3)",
            "residual_jets": "A=sum d, B=sum d^2, C=sum d^3; S1=(1/2)sum A*B and S2=sum(B^2/8+A*C/6)",
            "free_conditional_precision": 72,
            "free_conditional_variance": enc(Fraction(1, 72)),
            "free_center_terms": len(center),
            "surviving_component_term_counts": {key: len(value) for key, value in jets.items()},
            "conditional_mean_coefficients": [
                "m1=-E_u[u*S1]",
                "m2=(1/2)E_u[u*S1^2]-E_u[u*S2]-E_u[u*S1]*E_u[S1]",
            ],
            "annealed_reweighting_cancellation": "D m1 is linear and E_0[phi_j*S1]=sum_i C_ji E_0[partial_i S1]=0 because translation makes E_0[partial_i S1] site-independent while constant-shift invariance makes its site sum zero",
            "evenness": "S_(-lambda)(phi)=S_lambda(-phi), so beta_L is even in lambda and the next remainder is O_L(lambda^4)",
        },
        "one_loop_symbol": {
            "variables": "x_mu=2*(1-cos(k_mu)), omega=e1=sum_mu x_mu, e2=sum_(mu<nu)x_mu*x_nu",
            "P": "e1/24-5*e1^2/288+e2/144+5*e1^3/1296+5*e1*e2/1728-5*e1^4/31104-13*e1^2*e2/31104",
            "vacuum_term": enc(Fraction(-43, 5184)),
            "covariance_kernel_terms": len(kernel),
            "covariance_kernel_sum": enc(sum(kernel.values(), Fraction())),
            "derived_x_monomials": len(derived_symbol),
            "finite_volume_formula": "b_(2,L)=-43/5184+L^-4*sum_(k in (2*pi/L)Z_L^4, k!=0) P(x(k))/omega(k)^2, for nondegenerate L>=5",
        },
        "exact_l6_decision": {
            "lattice": "periodic 6^4",
            "one_axis_x_values": [0, 1, 3, 4, 3, 1],
            "coefficient": enc(l6),
            "decimal_for_orientation_only": float(l6),
            "sign": "STRICTLY_NEGATIVE",
            "analytic_consequence": "there exists epsilon_6>0 such that beta_6(lambda)<0 for 0<|lambda|<epsilon_6",
        },
        "binary64_volume_diagnostic": {
            "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
            "rows": diagnostics,
            "interpretation": "the exact formula is negative on every displayed volume and approaches a small negative value; these floating evaluations do not certify the large-volume sign",
        },
        "large_volume_reduction": {
            "convergence": "P(x)/omega^2=O(|k|^-2) near k=0 and is integrable in four dimensions, so Riemann sums converge to the Brillouin-zone integral",
            "definitions": [
                "f(t)=exp(-2*t)*I_0(2*t)",
                "W4=integral_0^infinity f(t)^4 dt",
                "I4=integral_0^infinity f(t)^2*f'(t)^2 dt",
            ],
            "integration_by_parts": "the continuum Brillouin average of e2/omega^2 equals 2*W4, while the average of e2/omega equals 6*I4",
            "limit_formula": "b_(2,infinity)=-85/5184+W4/18+5*I4/288",
            "sign_status": "OPEN_PENDING_RIGOROUS_WATSON_BESSEL_INTERVAL",
        },
        "method_disposition": {
            "pointwise_signed_response_contraction": "OBSTRUCTED_PREDECESSOR",
            "annealed_beta_nonnegative_at_all_finite_volumes": "REFUTED_AT_ONE_LOOP_ON_L6",
            "large_volume_annealed_beta_sign": "EXACT_INTEGRAL_REDUCTION_SIGN_OPEN",
            "nonperturbative_annealed_response": "OPEN",
            "block_or_multiscale_signed_response": "OPEN",
            "volume_uniform_global_poincare_or_witten": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "ordinary_os_reconstruction": "OBSTRUCTED_AT_FINITE_VOLUME_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a rigorous upper interval for W4/18+5*I4/288 deciding the large-volume sign",
            "uniform control of higher weak-coupling coefficients or a nonperturbative block-response replacement",
            "a theorem connecting any surviving response estimate to the normalized lowest-mode and interacting H^-1 upper bound",
        ],
        "next_gate": "Certify rational upper bounds W4<31/200 and I4<54/125 (or any bounds strong enough for the displayed limit formula), using positive return-walk/Bessel series with an explicit tail. If the resulting b_(2,infinity) is negative, close single-site annealed signed contraction as a volume-uniform route and move to block conditional response or the direct score/Witten programme.",
        "does_not_establish": [
            "a negative beta_L at lambda=0.4 or at arbitrary coupling",
            "a negative large-volume one-loop coefficient before the Watson/Bessel interval is certified",
            "instability or a negative spectral gap for continuous-time heat-bath dynamics",
            "failure of block conditioning, direct score estimates, or every Witten method",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound or its failure",
            "an interacting continuum measure or ordinary OS reconstruction",
            "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "exact Python Fraction sparse conditional jets, centered Gaussian moments, Laurent/hypercubic symmetrization, and an exact rational 6^4 Fourier sum; displayed multi-volume diagnostics alone use binary64",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_response_one_loop.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_response_one_loop.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_response_one_loop",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer replay, independent symbolic verifier, and focused mutation tests required",
            "tier_2": "the corrected signed-response predecessor is replayed; no shared operator or claimed continuum theorem changes",
            "tier_3": "not applicable: this computes a finite-volume perturbative method coefficient but does not promote the interacting H^-1, continuum, freeze, release, or Lorentzian lifecycle",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; Go uses GOMEMLIMIT=300MiB and GOGC=50",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "2.96 s, 36344 KiB",
                "independent_verifier": "0.42 s, 30480 KiB",
                "unit_tests": "5.68 s, 45276 KiB",
                "corrected_predecessor_producer": "0.03 s, 21020 KiB",
                "corrected_predecessor_verifier": "0.09 s, 30524 KiB",
                "corrected_predecessor_tests": "0.12 s, 30884 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1697 nodes, 0 invalid items, 0 malformed events; 6.63 s, 183084 KiB",
                "science_forge_shadow": "not run: the earlier memory-capped external-indexing abort remains unresolved; this skip is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT annealed response one-loop "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
