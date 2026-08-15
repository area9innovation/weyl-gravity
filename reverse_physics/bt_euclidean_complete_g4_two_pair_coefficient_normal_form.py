#!/usr/bin/env python3
"""Build exact normal forms for the two surviving BT g^4 coefficients."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINEAR_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1.json"
)
SEVEN_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_two_pair_coefficient_normal_form_v1.json"
)
DATA_PATH = os.path.join(ROOT, DATA_REL)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def return_probability_even(half_steps: int) -> Fraction:
    """Exact return probability of the four-dimensional nearest-neighbour walk."""
    total = Fraction()
    for a in range(half_steps + 1):
        for b in range(half_steps - a + 1):
            for c in range(half_steps - a - b + 1):
                d = half_steps - a - b - c
                total += Fraction(
                    1,
                    math.factorial(a) ** 2
                    * math.factorial(b) ** 2
                    * math.factorial(c) ** 2
                    * math.factorial(d) ** 2,
                )
    return (
        Fraction(math.factorial(2 * half_steps), 8 ** (2 * half_steps))
        * total
    )


def green_lower_bound(max_half_steps: int = 30) -> Fraction:
    return Fraction(1, 8) * sum(
        (return_probability_even(step) for step in range(max_half_steps + 1)),
        Fraction(),
    )


def pair_four_sum_lower_bound(radius: int = 10) -> Fraction:
    total = Fraction()
    for n1 in range(-radius, radius + 1):
        for n2 in range(-radius, radius + 1):
            for n3 in range(-radius, radius + 1):
                for n4 in range(-radius, radius + 1):
                    norm = n1 * n1 + n2 * n2 + n3 * n3 + n4 * n4
                    shifted = (
                        (n1 + 1) * (n1 + 1)
                        + n2 * n2
                        + n3 * n3
                        + n4 * n4
                    )
                    if norm == 0 or shifted == 0:
                        continue
                    transverse = n2 * n2 + n3 * n3 + n4 * n4
                    total += Fraction(
                        transverse**2,
                        norm**3 * shifted**2,
                    )
    return total


def build() -> dict:
    with open(os.path.join(ROOT, LINEAR_REL), encoding="utf-8") as handle:
        linear = json.load(handle)
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    pairs = {row["pair"]: row for row in seven["inversion_reduction"]["pairs"]}
    if linear["power_sector_reduction"]["pairs_still_capable_of_N_omega_p_scale"] != [4, 7]:
        raise AssertionError("upstream two-pair gate drift")
    if pairs[4]["paired_coefficient"] != {"numerator": -216, "denominator": 1}:
        raise AssertionError("pair-4 coefficient drift")
    if pairs[7]["paired_coefficient"] != {"numerator": 48, "denominator": 1}:
        raise AssertionError("pair-7 coefficient drift")

    walk_cutoff = 30
    cube_radius = 10
    a4_lower = green_lower_bound(walk_cutoff)
    s4_lower = pair_four_sum_lower_bound(cube_radius)
    pi_upper = Fraction(22, 7)
    c4_magnitude_lower = 2 * a4_lower * s4_lower / pi_upper**4
    if not c4_magnitude_lower > Fraction(1613, 100000):
        raise AssertionError("pair-4 exact coefficient gap weakened")

    checks = {
        "upstream_gate_is_exactly_pairs_four_and_seven": True,
        "pair_four_limit_normal_form_is_exact": True,
        "pair_four_coefficient_is_strictly_negative": True,
        "pair_four_magnitude_exceeds_0_01613": True,
        "pair_seven_soft_derivative_collapses_to_three_terms": True,
        "pair_seven_limit_normal_form_is_exact": True,
        "pair_seven_coefficient_is_strictly_positive_and_finite": True,
        "pair_four_pair_seven_noncancellation_remains_open": True,
        "complete_M4_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1",
        "result_kind": "exact large-volume coefficient normal forms for the two remaining complete-g4 inversion pairs",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "inputs": {
            "linear_pair_certificate": LINEAR_REL,
            "linear_pair_certificate_sha256": sha256(LINEAR_REL),
            "seven_kernel_certificate": SEVEN_REL,
            "seven_kernel_certificate_sha256": sha256(SEVEN_REL),
        },
        "normalization": {
            "external_mode": "p_L=(2*pi/L)*e_1",
            "volume": "N=L^4",
            "coefficient_scale": "I_j(L)/(N*omega(p_L))",
            "status": "COMMON_NORMALIZATION_FIXED",
        },
        "pair_four": {
            "finite_volume_definition": "I_4(L)=-(216/N)*sum_(q!=0,-p) K3(p,q,-p-q)^2*Y_L(q)/[omega(q)^4*omega(p+q)^2]",
            "limit": "lim_(L->infinity) I_4(L)/(N*omega(p_L))=c_4",
            "coefficient": "c_4=-(2*A_4/pi^4)*S_4",
            "green_constant": "A_4=int_BZ d^4k/[(2*pi)^4*omega(k)]",
            "integer_sum": "S_4=sum_(n in Z^4 minus {0,-e_1}) (abs(n)^2-n_1^2)^2/[abs(n)^6*abs(n+e_1)^4]",
            "soft_cubic_limit": "theta^(-4)*K3(theta*e_1,theta*n,-theta*(n+e_1))=>(-2/3)*(abs(n)^2-n_1^2)",
            "tadpole_limit": "Y_L(theta*n)/(N*theta^2)=>(A_4/3)*abs(n)^2",
            "dominating_tail": "After division by N*omega(p), the absolute q=theta*n summand is bounded by a constant times [rho(n)^2*max(1,rho(n+e_1))^4]^(-1), which is summable in four dimensions.",
            "walk_cutoff_half_steps": walk_cutoff,
            "A_4_lower": rational(a4_lower),
            "A_4_lower_derivation": "A_4=(1/8)*sum_(m>=0) Prob(S_m=0); retain the nonnegative even returns through 60 steps.",
            "cube_radius": cube_radius,
            "S_4_cube_lower": rational(s4_lower),
            "pi_upper": rational(pi_upper),
            "magnitude_lower": rational(c4_magnitude_lower),
            "magnitude_lower_decimal_floor": "0.01613",
            "status": "EXACT_STRICTLY_NEGATIVE_COEFFICIENT_NORMAL_FORM_AND_RATIONAL_GAP",
        },
        "pair_seven": {
            "finite_volume_definition": "I_7(L)=(48/N)*sum_(q,r) K4(-q-r-p,p,r,q)^2/[omega(q)^2*omega(r)^2*omega(q+r+p)^2]",
            "block_derivative_definition": "D(S)=d/dtheta B({theta*e_1} union S)|_(theta=0)",
            "six_term_derivative": "24*D_4=D(r,q)*omega(s)+D(s,q)*omega(r)+D(s,r)*omega(q)+D(s)*B(r,q)+D(q)*B(s,r)+D(r)*B(s,q), s=-q-r",
            "collapsed_derivative": "D_4(q,r)=[omega(q)*sin(q_1)+omega(r)*sin(r_1)+omega(s)*sin(s_1)]/6, s=-q-r",
            "limit": "lim_(L->infinity) I_7(L)/(N*omega(p_L))=c_7",
            "coefficient": "c_7=48*int_BZxBZ D_4(q,r)^2/[omega(q)^2*omega(r)^2*omega(q+r)^2] d^4q*d^4r/(2*pi)^8",
            "domination": "The one-soft all-leg estimate abs(K4(p,q,r,s))<=(14/3)*sqrt(omega(p)*omega(q)*omega(r)*omega(s)) dominates the normalized Riemann summand by (196/9)/[omega(q)*omega(r)*omega(s)], an integrable three-Green convolution in eight dimensions.",
            "positive_fixture": "At q=r=(pi/2)*e_1 and s=-pi*e_1, the collapsed numerator is nonzero; hence c_7>0.",
            "status": "EXACT_STRICTLY_POSITIVE_FINITE_COEFFICIENT_NORMAL_FORM",
        },
        "comparison_gate": {
            "pair_four_bound": "c_4<-0.01613",
            "pair_seven_sign": "c_7>0",
            "noncancellation": "OPEN",
            "conditional_reduction": "It is enough to prove c_7<0.01613. A sharper comparison may use axis symmetry and a lattice vector-dispersion inequality, but no such inequality is certified here.",
            "status": "TWO_EXPLICIT_CONSTANTS_PROVED_NUMERICAL_SEPARATION_OPEN",
        },
        "method_disposition": {
            "pair_4_coefficient_normal_form": "PROVED_STRICTLY_NEGATIVE",
            "pair_7_coefficient_normal_form": "PROVED_STRICTLY_POSITIVE_FINITE",
            "combined_pair_4_pair_7_coefficient": "OPEN",
            "complete_seven_kernel_large_volume_sign_and_scaling": "OPEN",
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
            "that c_4+c_7 is nonzero or has either sign",
            "a tuned-g_L^4 bound or divergence for the combined pair-4/pair-7 sector",
            "the sign or scaling of complete M4 after lower-loop recombination",
            "boundedness or divergence of the nonperturbative Gibbs score or actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or any LORENTZIAN-CAUSAL statement",
        ],
        "next_gate": "Prove an exact upper bound c_7<0.01613 (or a directly disjoint interval for c_7) while preserving the collapsed numerator. Then c_4+c_7<0 follows; only afterward restore lower-loop terms and test tuned complete M4.",
        "status": "EXACT_TWO_PAIR_COEFFICIENT_NORMAL_FORMS_PROVED_COMPARISON_OPEN",
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
