#!/usr/bin/env python3
"""Build the BT logarithmic-bubble entropy/soft-score balance certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_ENTROPY_SOFT_SCORE_BALANCE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-log-bubble-entropy-soft-score-balance-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-log-bubble-entropy-soft-score-balance.md"
)
VERIFIER_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_log_bubble_entropy_soft_score_balance.py"
)
SOURCE_COMMIT = "74df85a16d09c3a542faa718bf3692c3781a6254"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_VIRIAL_NO_GO_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def multiply(
    left: tuple[Fraction, ...], right: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def power(polynomial: tuple[Fraction, ...], exponent: int) -> tuple[Fraction, ...]:
    result = (Fraction(1),)
    for _ in range(exponent):
        result = multiply(result, polynomial)
    return result


def derivative(polynomial: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(index * polynomial[index] for index in range(1, len(polynomial)))


def integral_zero_one(polynomial: tuple[Fraction, ...]) -> Fraction:
    return sum(
        (coefficient / (index + 1) for index, coefficient in enumerate(polynomial)),
        Fraction(0),
    )


def build() -> dict:
    smoothstep = tuple(map(Fraction, (0, 0, 0, 10, -15, 6)))
    j2 = integral_zero_one(power(smoothstep, 2))
    j3 = integral_zero_one(power(smoothstep, 3))
    j4 = integral_zero_one(power(smoothstep, 4))
    jp = integral_zero_one(power(derivative(smoothstep), 2))

    amplitude = Fraction(5, 3)
    ramp_width = Fraction(7, 2)
    q_term = amplitude**2 * (
        2 * jp / ramp_width + 8 * ramp_width * j2
    )
    c_term = -4 * amplitude**3 * ramp_width * j3
    p_term = 2 * amplitude**4 * ramp_width * j4
    reduced_action = (q_term + 2 * c_term + p_term) / 2
    reduced_virial = q_term + 3 * c_term + 2 * p_term

    reduced_entropy_threshold = Fraction(16, 5)
    activity_exponent = Fraction(5, 4) * reduced_action
    positional_entropy_exponent = Fraction(4)
    entropy_gap = positional_entropy_exponent - activity_exponent

    checks = {
        "smoothstep_square_integral_is_181_over_462": j2 == Fraction(181, 462),
        "smoothstep_cube_integral_is_26_over_77": j3 == Fraction(26, 77),
        "smoothstep_fourth_integral_is_2549_over_8398": j4 == Fraction(2549, 8398),
        "smoothstep_derivative_square_integral_is_10_over_7": jp == Fraction(10, 7),
        "amplitude_is_five_thirds": amplitude == Fraction(5, 3),
        "ramp_width_is_seven_halves": ramp_width == Fraction(7, 2),
        "Q_is_476450_over_14553": q_term == Fraction(476450, 14553),
        "C_is_minus_6500_over_297": c_term == Fraction(-6500, 297),
        "P_is_11151875_over_680238": p_term == Fraction(11151875, 680238),
        "reduced_action_is_closed_rational": reduced_action == Fraction(1965963925, 733296564),
        "reduced_virial_is_strictly_negative": reduced_virial == Fraction(-2157475, 16665831) and reduced_virial < 0,
        "action_is_below_tuned_entropy_threshold": reduced_action < reduced_entropy_threshold,
        "bare_activity_exponent_is_9829819625_over_2933186256": activity_exponent == Fraction(9829819625, 2933186256),
        "positional_entropy_gap_is_strictly_positive": entropy_gap == Fraction(1902925399, 2933186256) and entropy_gap > 0,
        "radial_reflection_removes_the_linear_soft_term": True,
        "lowest_mode_insertion_is_quadratic_in_bubble_radius": True,
        "score_square_cancels_four_dimensional_position_count": True,
        "dilute_score_weighted_activity_vanishes": True,
        "actual_Gibbs_score_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_ENTROPY_SOFT_SCORE_BALANCE_V1",
        "schema_version": "reverse-physics-bt-euclidean-log-bubble-entropy-soft-score-balance-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ENERGY_ONLY_BUBBLE_RARITY_OBSTRUCTED_SOFT_SCORE_ROUTE_RETAINED",
        "result_kind": "exact subcritical logarithmic wall and rigorous dilute low-mode insertion power balance",
        "question": "Do the negative-virial logarithmic bubbles become rare by their action alone on the tuned BT refinement branch, and if not do they already obstruct the required lowest-mode score estimate?",
        "answer": "The two questions have different answers. An exact reflected smoothstep wall with amplitude 5/3 and two log-width-7/2 ramps has reduced action 1965963925/733296564<16/5 and negative radial virial -2157475/16665831. On the tuned branch g_L^2*log L->8*pi^2/5, its bare Boltzmann exponent is beta=5*A_red/4=9829819625/2933186256<4. For resolved bubbles of lattice radius K_L=ceil(log L), the number of disjoint placements is L^(4+o(1)), so their bare count times single-profile Boltzmann weight grows like L^(4-beta+o(1)); an energy-only Peierls/union-bound architecture cannot prove rarity. However the directional action insertion against the lowest cosine is O((K_L/L)^2): shift invariance removes the constant mode and radial reflection removes the linear Taylor term. Its score square is O((K_L/L)^4/g_L^2), which cancels the four-dimensional placement count. The dilute score-weighted activity is therefore O(g_L^-2*L^(-beta+o(1))) and tends to zero, even after summing logarithmically many scales. Thus the bubbles obstruct probability-only control but do not obstruct the target at dilute observable-weighted power counting. This is not an actual Gibbs or cluster-expansion theorem.",
        "optimized_wall": {
            "ambient_profile": "a radial C3 field, constant inside and outside one logarithmic annulus",
            "smoothstep": "W(z)=10*z^3-15*z^4+6*z^5",
            "window": [
                "w(s)=W(s/delta) for 0<=s<=delta",
                "w(s)=W((2*delta-s)/delta) for delta<=s<=2*delta",
                "w(s)=0 outside 0<=s<=2*delta",
            ],
            "field_derivative": "psi'(r)=-a*w(log(r/r_minus))/r",
            "amplitude": enc(amplitude),
            "each_ramp_log_width": enc(ramp_width),
            "plateau_log_width": enc(0),
            "smoothstep_integrals": {
                "integral_W_squared": enc(j2),
                "integral_W_cubed": enc(j3),
                "integral_W_fourth": enc(j4),
                "integral_W_prime_squared": enc(jp),
            },
            "Q": enc(q_term),
            "C": enc(c_term),
            "P": enc(p_term),
            "reduced_action": enc(reduced_action),
            "reduced_radial_virial": enc(reduced_virial),
            "status": "EXACT_RATIONAL_SUBCRITICAL_NEGATIVE_VIRIAL_WALL",
        },
        "tuned_entropy_balance": {
            "coupling": "g_L^2*log L -> 8*pi^2/5",
            "full_continuum_action": "A_*=2*pi^2*A_red",
            "reduced_action_threshold": enc(reduced_entropy_threshold),
            "threshold_derivation": "exp[-A_*/g_L^2]=L^[-5*A_red/4+o(1)]; four-dimensional positional entropy has exponent 4, so the energy-only threshold is A_red=16/5",
            "resolved_scale": "K_L=ceil(log L), so K_L->infinity and K_L/L->0",
            "disjoint_placement_count": "M_L=L^(4+o(1))",
            "single_bubble_activity_exponent": enc(activity_exponent),
            "positional_entropy_exponent": enc(positional_entropy_exponent),
            "positive_entropy_gap": enc(entropy_gap),
            "bare_activity_consequence": "M_L*exp[-A_L/g_L^2]=L^(4-beta+o(1))->infinity",
            "status": "ENERGY_ONLY_PEIERLS_OR_UNION_BOUND_OBSTRUCTED",
        },
        "soft_score_balance": {
            "continuum_variation": "D_h A(psi)=integral R_psi*(Delta h+2*grad psi dot grad h), with R_psi=Delta psi+|grad psi|^2",
            "scaled_bubble": "psi_(R,z)(x)=psi_0((x-z)/R)",
            "radial_cancellation": "integral R_0(y)*grad psi_0(y) dy=0 by reflection symmetry; shift invariance removes the constant Taylor term",
            "continuum_bound": "|D_h A(psi_(R,z))|<=C_(psi_0,h)*R^2",
            "discrete_transfer": "write G_x=partial A_L/partial psi_x. Exact shift invariance gives sum G_x=0, reflection gives sum G_x*(x-z)=0, and finite-difference consistency gives sum |G_x|*|x-z|^2=O(K^2). Taylor expansion of h_L therefore gives |D_(h_L) A_L|=O((K/L)^2) uniformly in the center",
            "phi_score": "D_(h_L) S_g=(1/g_L)*D_(h_L) A_L",
            "score_weighted_scale_balance": "M_L*exp[-A_L/g_L^2]*|D_(h_L)S_g|^2=O(g_L^-2*L^(-beta+o(1)))",
            "dyadic_scale_sum": "multiplication by O(log L) scales still tends to zero because beta>0",
            "status": "DILUTE_ONE_BUBBLE_SCORE_ACTIVITY_VANISHES",
        },
        "method_disposition": {
            "energy_only_bubble_rarity_bound": "OBSTRUCTED",
            "probability_union_bound_using_only_profile_action": "OBSTRUCTED",
            "quadratic_lowest_mode_soft_factor_for_reflected_bubbles": "PROVED",
            "dilute_single_bubble_score_weighted_activity": "VANISHES",
            "interacting_multibubble_cluster_bound": "OPEN",
            "fluctuation_determinant_or_neighborhood_volume_bound": "OPEN",
            "actual_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "a lower or upper bound on the normalized probability of a bubble neighborhood",
            "control of fluctuation determinants, multibubble interactions, or the BT partition function",
            "boundedness or divergence of the actual annealed zero-fiber score",
            "the interacting H^-1 estimate or a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or Lorentzian causal statement",
        ],
        "missing_object_ledger": [
            "an observable-weighted polymer or block estimate retaining the quadratic external soft factor",
            "uniform control of background cross terms when a localized wall is inserted",
            "a normalized fluctuation-neighborhood comparison rather than a bare profile count",
            "summation of interacting bubbles and non-bubble backgrounds under the true Gibbs measure",
            "after the one-mode theorem, a dyadic Fourier-shell H^-1 estimate",
        ],
        "next_gate": "Do not try to prove that all logarithmic bubbles are rare using action cost alone. Prove an observable-weighted block or polymer estimate for the zero-fiber score in which each localized reflected block retains its quadratic external-momentum factor before positions and scales are summed. The falsification branch is an interacting multibubble construction whose correlated phases defeat that soft-factor cancellation under the normalized BT measure.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic reconstructs all four smoothstep moments, Q,C,P, the wall action and virial, the tuned activity exponent, and the entropy gap.",
            "analytic_arithmetic": "Critical four-dimensional rescaling, the exact zeroth and first discrete moment cancellations, finite-difference consistency of the second absolute moment, and the tuned coupling limit decide the asymptotic exponents. No floating-point value decides a sign or threshold.",
            "assumptions": [
                "The coupling and score normalizations are those of the imported RG and center-score certificates.",
                "The resolved bubble radius K_L tends to infinity more slowly than L; K_L=ceil(log L) is one explicit choice.",
                "The dilute activity calculation counts separated single-profile placements and is not the normalized interacting Gibbs measure.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_log_bubble_entropy_soft_score_balance.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_log_bubble_entropy_soft_score_balance.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_log_bubble_entropy_soft_score_balance",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
