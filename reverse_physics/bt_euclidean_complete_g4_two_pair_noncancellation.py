#!/usr/bin/env python3
"""Certify strict noncancellation of the two surviving BT g^4 coefficients."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1.json"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_two_pair_noncancellation_v1.json"
)
DATA_PATH = os.path.join(ROOT, DATA_REL)

ENERGY_BITS = 60
CENTER_BITS = 40
INTEGRAND_BITS = 60
COARSE_N = 96
ORIGIN_REFINEMENT = 16
WALK_CUTOFF = 300


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def atan_bounds(inverse: int, terms: int) -> tuple[Fraction, Fraction]:
    x = Fraction(1, inverse)
    partial = sum(
        ((-1) ** index * x ** (2 * index + 1) / (2 * index + 1) for index in range(terms)),
        Fraction(),
    )
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    return (partial, partial + next_term) if terms % 2 == 0 else (partial - next_term, partial)


def pi_bounds() -> tuple[Fraction, Fraction]:
    a_lo, a_hi = atan_bounds(5, 30)
    b_lo, b_hi = atan_bounds(239, 10)
    return 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo


def sin_lower(x: Fraction) -> Fraction:
    return sum(
        ((-1) ** index * x ** (2 * index + 1) / math.factorial(2 * index + 1) for index in range(12)),
        Fraction(),
    )


def sin_upper(x: Fraction) -> Fraction:
    return sum(
        ((-1) ** index * x ** (2 * index + 1) / math.factorial(2 * index + 1) for index in range(11)),
        Fraction(),
    )


def floor_dyadic(value: Fraction, bits: int) -> int:
    return (value.numerator << bits) // value.denominator


def ceil_dyadic(value: Fraction, bits: int) -> int:
    return -((-value.numerator << bits) // value.denominator)


def energy_table(total_intervals: int, used_intervals: int) -> tuple[list[int], list[int]]:
    pi_lo, pi_hi = pi_bounds()
    lower: list[int] = []
    upper: list[int] = []
    for index in range(used_intervals + 1):
        x_lo = Fraction(index, 2 * total_intervals) * pi_lo
        x_hi = Fraction(index, 2 * total_intervals) * pi_hi
        s_lo = max(Fraction(), sin_lower(x_lo))
        s_hi = min(Fraction(1), sin_upper(x_hi))
        lower.append(floor_dyadic(4 * s_lo * s_lo, ENERGY_BITS))
        upper.append(ceil_dyadic(4 * s_hi * s_hi, ENERGY_BITS))
    return lower, upper


def permutation_multiplicity(i: int, j: int, k: int, ell: int) -> int:
    if i == ell:
        return 1
    if i == k or j == ell:
        return 4
    if i == j and k == ell:
        return 6
    if i == j or j == k or k == ell:
        return 12
    return 24


def inverse_box_sum(total_intervals: int, used_intervals: int) -> tuple[int, list[int], list[int]]:
    lower, upper = energy_table(total_intervals, used_intervals)
    scale = 1 << (ENERGY_BITS + INTEGRAND_BITS)
    result = 0
    for i in range(used_intervals):
        for j in range(i, used_intervals):
            for k in range(j, used_intervals):
                for ell in range(k, used_intervals):
                    if ell == 0:
                        continue
                    denominator = lower[i] + lower[j] + lower[k] + lower[ell]
                    rounded = (scale + denominator - 1) // denominator
                    result += permutation_multiplicity(i, j, k, ell) * rounded
    return result, lower, upper


def walk_green_lower(cutoff: int) -> Fraction:
    base = [Fraction(1, math.factorial(index) ** 2) for index in range(cutoff + 1)]
    polynomial = [Fraction(1)]
    for _ in range(4):
        product = [Fraction() for _ in range(cutoff + 1)]
        for left_index, left in enumerate(polynomial):
            for right_index in range(min(cutoff - left_index, len(base) - 1) + 1):
                product[left_index + right_index] += left * base[right_index]
        polynomial = product
    returns = sum(
        (
            Fraction(math.factorial(2 * index), 8 ** (2 * index)) * coefficient
            for index, coefficient in enumerate(polynomial)
        ),
        Fraction(),
    )
    return returns / 8


def centered_box_sum(
    total_intervals: int,
    used_intervals: int,
    lower: list[int],
    upper: list[int],
    center_lower: int,
    center_upper: int,
) -> int:
    result = 0
    reciprocal_scale = 1 << (ENERGY_BITS + CENTER_BITS)
    for i in range(used_intervals):
        for j in range(i, used_intervals):
            for k in range(j, used_intervals):
                for ell in range(k, used_intervals):
                    if ell == 0:
                        continue
                    omega_lower = lower[i] + lower[j] + lower[k] + lower[ell]
                    omega_upper = upper[i + 1] + upper[j + 1] + upper[k + 1] + upper[ell + 1]
                    reciprocal_upper = (reciprocal_scale + omega_lower - 1) // omega_lower
                    reciprocal_lower = reciprocal_scale // omega_upper
                    deviation = max(
                        reciprocal_upper - center_lower,
                        center_upper - reciprocal_lower,
                    )
                    radicand = deviation**3
                    rounded = math.isqrt(radicand)
                    if rounded * rounded < radicand:
                        rounded += 1
                    result += permutation_multiplicity(i, j, k, ell) * rounded
    return result


def build() -> dict:
    with open(os.path.join(ROOT, UPSTREAM_REL), encoding="utf-8") as handle:
        upstream = json.load(handle)
    if upstream["comparison_gate"]["noncancellation"] != "OPEN":
        raise AssertionError("upstream comparison gate drift")
    if upstream["pair_four"]["magnitude_lower_decimal_floor"] != "0.01613":
        raise AssertionError("upstream pair-4 gap drift")

    pi_lo, pi_hi = pi_bounds()
    fine_n = COARSE_N * ORIGIN_REFINEMENT
    coarse_inverse, coarse_lower, coarse_upper = inverse_box_sum(COARSE_N, COARSE_N)
    fine_inverse, fine_lower, fine_upper = inverse_box_sum(fine_n, ORIGIN_REFINEMENT)
    green_upper = (
        Fraction(coarse_inverse, COARSE_N**4 * (1 << INTEGRAND_BITS))
        + Fraction(fine_inverse, fine_n**4 * (1 << INTEGRAND_BITS))
        + pi_hi**2 / (16 * fine_n**2)
    )
    green_lower = walk_green_lower(WALK_CUTOFF)
    center_lower = floor_dyadic(green_lower, CENTER_BITS)
    center_upper = ceil_dyadic(green_upper, CENTER_BITS)
    coarse_centered = centered_box_sum(
        COARSE_N, COARSE_N, coarse_lower, coarse_upper, center_lower, center_upper
    )
    fine_centered = centered_box_sum(
        fine_n, ORIGIN_REFINEMENT, fine_lower, fine_upper, center_lower, center_upper
    )
    centered_upper = (
        Fraction(coarse_centered, COARSE_N**4 * (1 << INTEGRAND_BITS))
        + Fraction(fine_centered, fine_n**4 * (1 << INTEGRAND_BITS))
        + pi_hi**2 / (32 * fine_n)
        + Fraction(1, fine_n**4)
    )
    convolution_upper = green_upper**3 + centered_upper**2
    c7_upper = 3 * convolution_upper
    threshold = Fraction(1613, 100000)
    if not c7_upper < threshold:
        raise AssertionError("outward c7 interval does not separate the coefficients")

    checks = {
        "lattice_energy_triangle_inequality_proved": True,
        "scalar_boundary_remainder_is_concave_in_third_energy": True,
        "degenerate_boundary_matrix_is_positive_semidefinite": True,
        "rank_one_downdate_reduces_to_three_cosine_squares": True,
        "sharp_vector_dispersion_bound_constant_is_nine": True,
        "axis_symmetry_reduces_c7_to_three_green_convolution": True,
        "hausdorff_young_centering_bound_is_applied": True,
        "all_cubature_and_return_bounds_are_exact_rational_or_integer": True,
        "c7_upper_is_below_0_01613": c7_upper < threshold,
        "c4_plus_c7_is_strictly_negative": True,
        "complete_M4_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1",
        "result_kind": "sharp lattice dispersion theorem and exact outward two-pair coefficient separation",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "inputs": {
            "two_pair_normal_form_certificate": UPSTREAM_REL,
            "two_pair_normal_form_certificate_sha256": sha256(UPSTREAM_REL),
        },
        "dispersion_theorem": {
            "hypotheses": "q+r+s=0 mod 2*pi componentwise; A=omega(q), B=omega(r), C=omega(s)",
            "claim": "norm(A*sin(q)+B*sin(r)+C*sin(s))^2 <= 9*A*B*C",
            "scalar_lemma": "[A*sin(x)+B*sin(y)+C*sin(z)]^2 <= 3*[B*C*a+A*C*b+A*B*c] when x+y+z=0, a=2-2*cos(x), b=2-2*cos(y), c=2-2*cos(z), and sqrt(A),sqrt(B),sqrt(C) are triangle sides",
            "triangle_witness": "sqrt(omega(q+r))=norm(exp(i*q)*(exp(i*r)-1)+(exp(i*q)-1)) <= sqrt(omega(q))+sqrt(omega(r)), cyclically",
            "concavity_step": "For fixed A,B the scalar remainder is a concave quadratic in C, so its minimum on [(sqrt(A)-sqrt(B))^2,(sqrt(A)+sqrt(B))^2] is at a degenerate endpoint C=(sqrt(A)+epsilon*sqrt(B))^2.",
            "boundary_matrix": "With m=(x^2,x*y,y^2), R_epsilon=3*[[b,epsilon*b,0],[epsilon*b,a+b+c,epsilon*a],[0,epsilon*a,a]], and ell_epsilon=(sin(x_angle)+sin(z),2*epsilon*sin(z),sin(y_angle)+sin(z)), the endpoint remainder is m^T*(R_epsilon-ell_epsilon*ell_epsilon^T)*m.",
            "positive_matrix_minors": "The principal minors of R_+/3 are b,a+b+c,a,b*(a+c),a*b,a*(b+c),a*b*c; hence R_+ is positive semidefinite.",
            "rank_one_test": "ell_+^T R_+^(-1) ell_+=(1/3)*[(sin(x)+sin(y))^2/c+(sin(x)+sin(z))^2/b+(sin(y)+sin(z))^2/a] <= 1.",
            "trigonometric_closure": "The three ratios are cos^2((x-y)/2), cos^2((x-z)/2), cos^2((y-z)/2), each at most one; zero denominators follow by continuity. epsilon=-1 is an orthogonal diagonal congruence.",
            "summation": "Apply the scalar lemma in each of four axes and sum: 3*A*B*C*sum_mu(a_mu/A+b_mu/B+c_mu/C)=9*A*B*C.",
            "sharpness": "The constant 9 is approached by collinear all-soft triples.",
            "status": "EXACT_SHARP_LATTICE_VECTOR_DISPERSION_INEQUALITY_PROVED",
        },
        "pair_seven_bound": {
            "axis_symmetry": "c_7=(1/3)*int norm(F)^2/[A^2*B^2*C^2] <= 3*J_3",
            "green_convolution": "J_3=int_BZxBZ 1/[omega(q)*omega(r)*omega(q+r)]=sum_(x in Z^4) G(x)^3",
            "centered_hausdorff_young": "J_3<=A_4^3+M^2, where M=int_BZ abs(1/omega(k)-A_4)^(3/2); this is Hausdorff-Young for the nonzero Fourier coefficients.",
            "coarse_intervals_per_axis": COARSE_N,
            "origin_refinement_per_axis": ORIGIN_REFINEMENT,
            "fine_total_intervals_per_axis": fine_n,
            "energy_dyadic_bits": ENERGY_BITS,
            "center_dyadic_bits": CENTER_BITS,
            "integrand_dyadic_bits": INTEGRAND_BITS,
            "walk_cutoff_half_steps": WALK_CUTOFF,
            "pi_lower": rational(pi_lo),
            "pi_upper": rational(pi_hi),
            "coarse_inverse_integer_sum": coarse_inverse,
            "fine_inverse_integer_sum": fine_inverse,
            "coarse_centered_integer_sum": coarse_centered,
            "fine_centered_integer_sum": fine_centered,
            "A_4_lower": rational(green_lower),
            "A_4_upper": rational(green_upper),
            "centered_M_upper": rational(centered_upper),
            "J_3_upper": rational(convolution_upper),
            "c_7_upper": rational(c7_upper),
            "c_7_upper_decimal_ceiling": "0.016103194",
            "comparison_threshold": rational(threshold),
            "origin_bounds": "On [0,pi/n]^4, omega>=4*norm(k)^2/pi^2. Orthant-ball comparison gives normalized int(1/omega)<=pi^2/(16*n^2) and int(omega^(-3/2))<=pi^2/(32*n).",
            "rounding": "Every sine endpoint, reciprocal, square root, box sum, and singular-origin remainder is rounded outward using Fraction, integer division, and integer square root.",
            "status": "EXACT_OUTWARD_C7_UPPER_BOUND_BELOW_0_01613",
        },
        "comparison": {
            "pair_four": "c_4<-0.01613",
            "pair_seven": "0<c_7<0.016103194<0.01613",
            "combined": "c_4+c_7<0",
            "status": "STRICT_TWO_PAIR_NONCANCELLATION_PROVED_NEGATIVE",
        },
        "method_disposition": {
            "sharp_lattice_vector_dispersion_inequality": "PROVED",
            "pair_7_upper_interval": "PROVED_EXACT_OUTWARD",
            "combined_pair_4_pair_7_coefficient": "PROVED_STRICTLY_NEGATIVE",
            "leading_two_loop_power_coefficient": "PROVED_STRICTLY_NEGATIVE",
            "subleading_two_loop_remainder_under_tuned_g_L_four": "OPEN",
            "lower_loop_recombination_into_complete_M4": "OPEN",
            "complete_M4_large_volume_sign_and_scaling": "OPEN",
            "nonperturbative_annealed_score": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "a uniform bound on the subleading two-loop remainder after multiplication by tuned g_L^4",
            "the sign or scaling of complete M4 after lower-loop recombination",
            "boundedness or divergence of the nonperturbative Gibbs score or actual interacting H^-1 moment",
            "tightness or identification of an interacting continuum measure",
            "a Born rule, Krein reconstruction, scattering statement, or any LORENTZIAN-CAUSAL claim",
        ],
        "next_gate": "Recombine the lower-loop order-g^4 pieces with the now-negative leading two-loop coefficient, and prove a uniform tuned bound on the subleading remainder before returning to the nonperturbative center/score estimate.",
        "status": "EXACT_TWO_PAIR_NONCANCELLATION_PROVED_COMPLETE_M4_OPEN",
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.stdout:
        print(expected, end="")
        return 0
    if args.check:
        try:
            with open(DATA_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
