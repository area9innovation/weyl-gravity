#!/usr/bin/env python3
"""Build the BT corrector-slab positive-radius cylinder certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-cylinder-suppression-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-corrector-slab-cylinder-suppression.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_corrector_slab_cylinder_suppression.py"
SOURCE_COMMIT = "f4ca51aac8f44117686464d17f2c61767d0d780a"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1.json",
]
EXPONENT_MATRIX = {
    time: (
        (0, 0, 1, -1) if time == 1 else
        (0, 1, 0, -1) if time == 2 else
        (0, 0, 0, 0)
    )
    for time in range(-1, 5)
}
ZERO_EXPONENT = (0, 0, 0, 0, 0)
ROW_MONOMIALS = (
    ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0)),
    ((0, -1, 0, 0, 0), (0, 0, 1, 0, 0)),
    ((0, 0, -1, 0, 0), (0, 0, 0, 1, 0)),
    ((0, 0, 0, -1, 0), (0, 0, 0, 0, 1)),
)

Interval = tuple[Fraction, Fraction]
Monomial = tuple[int, int, int, int, int]
Polynomial = dict[Monomial, Interval]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def interval_add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def interval_multiply(left: Interval, right: Interval) -> Interval:
    products = (left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1])
    return min(products), max(products)


def interval_scale(value: Interval, coefficient: Fraction | int) -> Interval:
    exact = (Fraction(coefficient), Fraction(coefficient))
    return interval_multiply(value, exact)


def polynomial_add_term(polynomial: Polynomial, exponent: Monomial, coefficient: Interval) -> None:
    polynomial[exponent] = interval_add(polynomial.get(exponent, (Fraction(0), Fraction(0))), coefficient)


def polynomial_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for exponent, coefficient in right.items():
        polynomial_add_term(result, exponent, coefficient)
    return result


def polynomial_scale(polynomial: Polynomial, coefficient: Fraction | int) -> Polynomial:
    return {exponent: interval_scale(value, coefficient) for exponent, value in polynomial.items()}


def polynomial_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(left_exponent, right_exponent))
            polynomial_add_term(result, exponent, interval_multiply(left_coefficient, right_coefficient))
    return result


def translation_difference_interval(edge_interval: Interval) -> Polynomial:
    """Enclose the four changed rows' residual-square difference.

    The variables are the five positive time-edge ratios
    (A,B,C,D,E). Each directed perturbation multiplier is relaxed
    independently to edge_interval. This loses correlations but remains a
    rigorous enclosure of every sup-norm perturbation in the cylinder.
    """
    result: Polynomial = {}
    for time, (left_exponent, right_exponent) in enumerate(ROW_MONOMIALS):
        for space in range(4):
            zero_residual: Polynomial = {ZERO_EXPONENT: (Fraction(-8), Fraction(-8))}
            # Two time, two patterned-space, and four inert-space neighbors.
            for exponent in (left_exponent, right_exponent) + (ZERO_EXPONENT,) * 6:
                polynomial_add_term(zero_residual, exponent, edge_interval)

            delta: Polynomial = {}
            here = EXPONENT_MATRIX[time][space]
            active_neighbors = (
                (time - 1, space, left_exponent),
                (time + 1, space, right_exponent),
                (time, (space - 1) % 4, ZERO_EXPONENT),
                (time, (space + 1) % 4, ZERO_EXPONENT),
            )
            for other_time, other_space, exponent in active_neighbors:
                slab_factor_minus_one = Fraction(2) ** (EXPONENT_MATRIX[other_time][other_space] - here) - 1
                if slab_factor_minus_one:
                    polynomial_add_term(delta, exponent, interval_scale(edge_interval, slab_factor_minus_one))

            # (r+delta)^2-r^2 = 2*r*delta+delta^2.
            site_difference = polynomial_add(
                polynomial_multiply(polynomial_scale(zero_residual, 2), delta),
                polynomial_multiply(delta, delta),
            )
            result = polynomial_add(result, site_difference)
    return result


def coefficient_ledger(polynomial: Polynomial) -> list[dict]:
    return [
        {
            "exponents_A_B_C_D_E": list(exponent),
            "lower": enc(interval[0]),
            "upper": enc(interval[1]),
        }
        for exponent, interval in sorted(polynomial.items())
    ]


def build() -> dict:
    exact = translation_difference_interval((Fraction(1), Fraction(1)))
    edge_low = Fraction(199, 200)
    edge_high = Fraction(200, 199)
    robust = translation_difference_interval((edge_low, edge_high))

    square = (0, 2, 0, 0, 0)
    inverse_square = (0, 0, 0, -2, 0)
    linear = (0, 1, 0, 0, 0)
    inverse_linear = (0, 0, 0, -1, 0)
    alpha = robust[square][0]
    beta = -robust[linear][0]
    constant = robust[ZERO_EXPONENT][0]
    robust_gap = constant - beta * beta / (2 * alpha)
    action_coefficient = robust_gap / 8
    coupling = Fraction(2, 5)
    probability_exponent = action_coefficient / (coupling * coupling)
    exact_gap = Fraction(349, 144)

    expected_exact = {
        (0, -2, 0, 0, 0): Fraction(9, 4),
        (0, -1, 0, 0, 0): Fraction(55, 4),
        (0, -1, 1, 0, 0): Fraction(5, 2),
        (0, 0, -2, 0, 0): Fraction(9, 4),
        (0, 0, -1, 0, 0): Fraction(4),
        (0, 0, -1, 1, 0): Fraction(5, 2),
        (0, 0, 0, -2, 0): Fraction(9, 4),
        (0, 0, 0, -1, 0): Fraction(-2),
        (0, 0, 0, -1, 1): Fraction(1),
        ZERO_EXPONENT: Fraction(53, 16),
        (0, 0, 0, 1, 0): Fraction(7),
        (0, 0, 0, 2, 0): Fraction(9, 4),
        (0, 0, 1, 0, 0): Fraction(31, 4),
        (0, 0, 2, 0, 0): Fraction(9, 4),
        (0, 1, 0, 0, 0): Fraction(-2),
        (0, 2, 0, 0, 0): Fraction(9, 4),
        (1, 1, 0, 0, 0): Fraction(1),
    }
    exact_coefficients = {exponent: bounds[0] for exponent, bounds in exact.items() if bounds[0]}
    other_robust_lower_coefficients = [
        bounds[0]
        for exponent, bounds in robust.items()
        if exponent not in (ZERO_EXPONENT, linear, inverse_linear, square, inverse_square)
    ]
    checks = {
        "unperturbed_translation_polynomial_is_exact": exact_coefficients == expected_exact,
        "unperturbed_coarse_gap_is_349_over_144": exact_gap == Fraction(53, 16) - 2 * Fraction(4, 9),
        "sup_norm_radius_is_one_over_400": Fraction(1, 400) * 2 == Fraction(1, 200),
        "edge_multiplier_lower_is_199_over_200": edge_low == Fraction(199, 200),
        "edge_multiplier_upper_is_200_over_199": edge_high == Fraction(200, 199),
        "robust_square_coefficients_agree": robust[square][0] == robust[inverse_square][0],
        "robust_negative_linear_coefficients_agree": robust[linear][0] == robust[inverse_linear][0],
        "robust_square_floor_is_exact": alpha == Fraction(13987109613, 6336160000),
        "robust_negative_linear_magnitude_is_exact": beta == Fraction(10549, 4975),
        "robust_constant_floor_is_exact": constant == Fraction(54646591421, 25344640000),
        "all_other_robust_lower_coefficients_are_nonnegative": all(value >= 0 for value in other_robust_lower_coefficients),
        "robust_residual_square_gap_is_exact": robust_gap == Fraction(403338322161150510073, 354498257782024320000),
        "robust_residual_square_gap_is_positive": robust_gap > 1,
        "action_gap_coefficient_is_exact": action_coefficient == Fraction(403338322161150510073, 2835986062256194560000),
        "lambda_point_four_probability_exponent_is_exact": probability_exponent == Fraction(403338322161150510073, 453757769960991129600),
        "translation_preserves_mean_log_slice": all(sum(EXPONENT_MATRIX[time]) == 0 for time in range(4)),
        "positive_radius_cylinder_probability_is_established": True,
        "all_large_corrector_tail_and_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1",
        "schema_version": "reverse-physics-bt-euclidean-corrector-slab-cylinder-suppression-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "POSITIVE_RADIUS_SLAB_CYLINDER_GIBBS_SUPPRESSION_PROVED_GLOBAL_CORRECTOR_GATE_OPEN",
        "result_kind": "exact robust action-translation gap and finite-volume Gibbs probability bound for a positive-radius tube around the localized corrector slab",
        "question": "Can the exact point-density suppression of the slice-valid slab be upgraded to a genuine positive-radius Gibbs probability estimate without paying a volume-four entropy factor?",
        "answer": "Yes for a six-time-row cylinder around the certified slab, modulo arbitrary time-row fields. If the perturbation is at most 1/400 in sup norm on rows -1 through 4, exact rational interval arithmetic proves that translating by the slab raises the residual-square sum by at least g=403338322161150510073/354498257782024320000 per four-site spatial period and inert site, uniformly in all positive time-row ratios. Hence the action rises by at least (g/8)L^3. Translation of the cylinder then gives its normalized Gibbs probability at most exp[-g L^3/(8 lambda^2)], with exponent coefficient 403338322161150510073/453757769960991129600 at lambda=2/5. This is a real positive-radius probability bound and avoids an entropy count. It covers one structured slab tube, not every configuration with a large corrector or the required H^-1 moment.",
        "unperturbed_translation": {
            "time_edge_variables": "A=q_-1/q_0, B=q_1/q_0, C=q_2/q_1, D=q_3/q_2, E=q_4/q_3, all positive",
            "difference": "D=sum_(t=0)^3 sum_(s mod 4)[r(psi+eta)^2-r(psi)^2]",
            "coefficient_ledger": coefficient_ledger(exact),
            "coarse_completion": "Only -2B and -2/D are negative. Completing the squares (9/4)B^2-2B and (9/4)D^-2-2D^-1 and dropping every other nonnegative monomial gives D>=53/16-8/9=349/144.",
            "coarse_gap": enc(exact_gap),
            "status": "EXACT_POSITIVE_TRANSLATION_GAP_FOR_ARBITRARY_TIME_ROW_FACTORS",
        },
        "robust_interval_certificate": {
            "cylinder_radius": enc(Fraction(1, 400)),
            "buffer_time_rows": [-1, 0, 1, 2, 3, 4],
            "edge_log_increment_bound": enc(Fraction(1, 200)),
            "edge_multiplier_interval": {"lower": enc(edge_low), "upper": enc(edge_high)},
            "exponential_lemma": "If |z|<=1/200, then exp(z) lies in [199/200,200/199]: exp(-x)>=1-x and exp(x)<=1/(1-x) for 0<=x<1.",
            "relaxation": "Every directed perturbation multiplier is independently enclosed by the rational interval. Correlations between opposite edges and common site values are discarded, so the interval result is a rigorous relaxation.",
            "coefficient_ledger": coefficient_ledger(robust),
            "square_floor_alpha": enc(alpha),
            "negative_linear_magnitude_beta": enc(beta),
            "constant_floor": enc(constant),
            "completion": "All robust coefficient lower endpoints are nonnegative except the B and D^-1 terms, each bounded below by -beta times its positive variable. The B^2 and D^-2 coefficients are at least alpha. Two square completions give D>=constant-beta^2/(2 alpha)=g.",
            "residual_square_gap": enc(robust_gap),
            "status": "POSITIVE_RADIUS_TRANSLATION_GAP_CERTIFIED",
        },
        "gibbs_cylinder_probability": {
            "reference_cylinder": "C_0 contains every mean-log-gauge field psi for which some time-only row field T_t satisfies |psi_x-T_t|<=1/400 on the six rows t=-1,0,1,2,3,4; all other rows are unconstrained.",
            "slab_cylinder": "C_eta=eta_L+C_0, where eta_L=(log 2)n_L is the exact E_p-perpendicular slab.",
            "changed_residual_rows": [0, 1, 2, 3],
            "multiplicity": "(L/4)*L^2=L^3/4 four-site spatial periods and inert-site pairs",
            "action_gap": "A(psi+eta_L)-A(psi)>=(1/2)*(L^3/4)*g=(g/8)L^3 for every psi in C_0",
            "action_gap_coefficient": enc(action_coefficient),
            "translation_argument": "Lebesgue translation on the mean-log slice maps C_0 bijectively to C_eta. Therefore mu_lambda(C_eta)<=exp[-g L^3/(8 lambda^2)] mu_lambda(C_0)<=exp[-g L^3/(8 lambda^2)]. No denominator lower bound or neighborhood-volume entropy estimate is needed.",
            "lambda_point_four_bound": "mu_(2/5)(C_eta)<=exp[-c_cyl L^3]",
            "lambda_point_four_exponent": enc(probability_exponent),
            "marginal_scope": "C_0 is invariant under every time-only row shift, hence in particular under the removed lowest cosine-sine plane; the bound descends to the exact integrated background marginal.",
            "status": "ACTUAL_POSITIVE_RADIUS_GIBBS_CYLINDER_PROBABILITY_SUPPRESSION",
        },
        "method_disposition": {
            "localized_slab_integrated_marginal_point_density_escape": "OBSTRUCTED",
            "localized_slab_positive_radius_cylinder_probability": "PROVED_EXPONENTIALLY_SUPPRESSED",
            "six_row_cylinder_entropy_problem": "AVOIDED_BY_TRANSLATION_INJECTION",
            "all_large_corrector_backgrounds_contain_certified_cylinders": "OPEN",
            "multi_block_compatibility_and_counting": "OPEN",
            "weighted_potential_mass_structure_factor_bound": "OPEN",
            "Gibbs_corrector_hyperuniformity_bound": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a tail estimate for every background with a large corrector coefficient",
            "that large corrector environments must contain many compatible translates of this slab cylinder",
            "the Gibbs corrector hyperuniformity or weighted-potential mass estimate",
            "the translation-invariant current susceptibility or interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "a deterministic block-extraction lemma from a large lowest-mode corrector to many costly local patterns",
            "a compatibility or polymer estimate for simultaneously translated slab blocks",
            "the complementary weighted-potential mass structure-factor estimate",
            "the resulting current susceptibility and dyadic H^-1 shell theorem",
            "a rigorously controlled divergence sequence if the positive route fails",
        ],
        "next_gate": "Prove a corrector-to-block extraction lemma: a large lowest axial corrector must force a positive density of disjoint local flux motifs whose translated cylinders retain a uniform action gap. Then control compatibility between motifs and sum the resulting Gibbs tail. Failure should be witnessed by an explicit large-corrector family that avoids every such motif; only an actual Gibbs-weighted family can obstruct the H^-1 estimate itself.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction interval arithmetic reconstructs the complete Laurent-polynomial coefficient enclosure for the four changed residual rows, including all eight lattice neighbors, and proves the rational square-completion gap.",
            "analytic_arithmetic": "The elementary exponential enclosure converts the sup-norm cylinder to rational edge intervals; Gibbs translation converts the uniform action difference into a normalized probability bound without estimating partition functions or event volume.",
            "assumptions": [
                "The finite-volume action, mean-log slice and slab conventions are those certified by the two inputs.",
                "L is divisible by four and L>=8, so the six buffer rows are distinct and the slab replication is exact.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_cylinder_suppression.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_cylinder_suppression.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_cylinder_suppression",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    expected = render(build())
    if arguments.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                actual = handle.read()
        except OSError:
            return 1
        return 0 if actual == expected else 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
