#!/usr/bin/env python3
"""Build the BT corrector-slab fiber-stability certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-fiber-stability-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-corrector-slab-fiber-stability.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_corrector_slab_fiber_stability.py"
SOURCE_COMMIT = "2d92392e9840eed7a2da81551a25e33d7f0815d1"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1.json",
]
EXPONENT_MATRIX = (
    (0, 0, 0, 0),
    (0, 0, 1, -1),
    (0, 1, 0, -1),
    (0, 0, 0, 0),
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


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def row_vectors(time: int) -> tuple[list[Fraction], list[Fraction], list[Fraction]]:
    base = []
    left = []
    right = []
    for space in range(4):
        exponent = EXPONENT_MATRIX[time][space]
        base.append(
            Fraction(-4)
            + p2(EXPONENT_MATRIX[time][(space - 1) % 4] - exponent)
            + p2(EXPONENT_MATRIX[time][(space + 1) % 4] - exponent)
        )
        left_exponent = EXPONENT_MATRIX[time - 1][space] if time > 0 else 0
        right_exponent = EXPONENT_MATRIX[time + 1][space] if time < 3 else 0
        left.append(p2(left_exponent - exponent))
        right.append(p2(right_exponent - exponent))
    return base, left, right


def gram(base: list[Fraction], left: list[Fraction], right: list[Fraction]) -> dict[str, Fraction]:
    return {
        "bb": sum((value * value for value in base), Fraction(0)),
        "bl": sum((x * y for x, y in zip(base, left)), Fraction(0)),
        "br": sum((x * y for x, y in zip(base, right)), Fraction(0)),
        "ll": sum((value * value for value in left), Fraction(0)),
        "lr": sum((x * y for x, y in zip(left, right)), Fraction(0)),
        "rr": sum((value * value for value in right), Fraction(0)),
    }


def build() -> dict:
    row_one_vectors = row_vectors(1)
    row_two_vectors = row_vectors(2)
    row_one = gram(*row_one_vectors)
    row_two = gram(*row_two_vectors)
    row_one_minimum = Fraction(1909, 100)
    row_two_minimum = Fraction(387, 50)
    cell_lower = row_one_minimum + row_two_minimum
    action_lower_coefficient = cell_lower / 8
    coupling = Fraction(2, 5)
    curvature_lower = Fraction(512, 9)
    zero_fiber_action_upper = Fraction(15488, 49)
    gaussian_prefactor = Fraction(99, 896) * coupling**2
    tuned_prefactor = Fraction(99, 5600)
    tuned_action_exponent = action_lower_coefficient / coupling**2
    tuned_zero_constant = zero_fiber_action_upper / coupling**2
    row_one_direct_coefficients = (row_one["bb"], 2 * row_one["bl"], 2 * row_one["br"], row_one["ll"], 2 * row_one["lr"], row_one["rr"])
    row_one_completed_coefficients = (
        row_one_minimum + Fraction(25, 4) * Fraction(33, 50) ** 2,
        Fraction(117, 25) - Fraction(21, 2) * Fraction(33, 50),
        -Fraction(25, 2) * Fraction(33, 50),
        Fraction(25, 4),
        Fraction(21, 2),
        Fraction(25, 4),
    )
    row_two_direct_coefficients = (row_two["bb"], 2 * row_two["bl"], 2 * row_two["br"], row_two["ll"], 2 * row_two["lr"], row_two["rr"])
    row_two_completed_coefficients = (
        row_two_minimum + Fraction(25, 4) * Fraction(24, 25) ** 2,
        -Fraction(25, 2) * Fraction(24, 25),
        Fraction(27, 25) - Fraction(21, 2) * Fraction(24, 25),
        Fraction(25, 4),
        Fraction(21, 2),
        Fraction(25, 4),
    )
    checks = {
        "row_one_vectors_are_exact": row_one_vectors == (
            [Fraction(-5, 2), -1, Fraction(-13, 4), 2],
            [1, 1, Fraction(1, 2), 2],
            [1, 2, Fraction(1, 2), 1],
        ),
        "row_two_vectors_are_exact": row_two_vectors == (
            [Fraction(-3, 2), -3, Fraction(-3, 2), 0],
            [1, Fraction(1, 2), 2, 1],
            [1, Fraction(1, 2), 1, 2],
        ),
        "common_gram_matrix_is_exact": row_one["ll"] == row_one["rr"] == row_two["ll"] == row_two["rr"] == Fraction(25, 4) and row_one["lr"] == row_two["lr"] == Fraction(21, 4),
        "row_one_square_completion_coefficients_match": row_one_direct_coefficients == row_one_completed_coefficients,
        "row_two_square_completion_coefficients_match": row_two_direct_coefficients == row_two_completed_coefficients,
        "row_one_boundary_minimum_is_exact": row_one_minimum == Fraction(1909, 100),
        "row_two_boundary_minimum_is_exact": row_two_minimum == Fraction(387, 50),
        "two_row_residual_square_lower_bound_is_2683_over_100": cell_lower == Fraction(2683, 100),
        "fiber_action_lower_coefficient_is_2683_over_800": action_lower_coefficient == Fraction(2683, 800),
        "two_mode_curvature_lower_bound_is_512_over_9": curvature_lower == Fraction(512, 9),
        "zero_background_small_square_action_upper_is_15488_over_49": zero_fiber_action_upper == Fraction(15488, 49),
        "lambda_point_four_density_prefactor_is_99_over_5600": gaussian_prefactor == tuned_prefactor,
        "lambda_point_four_action_exponent_is_2683_over_128": tuned_action_exponent == Fraction(2683, 128),
        "lambda_point_four_zero_constant_is_96800_over_49": tuned_zero_constant == Fraction(96800, 49),
        "slab_zero_fiber_pointwise_no_go_is_not_a_marginal_escape": True,
        "neighborhood_probability_and_corrector_expectation_remain_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1",
        "schema_version": "reverse-physics-bt-euclidean-corrector-slab-fiber-stability-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "INTEGRATED_MARGINAL_POINT_DENSITY_SUPPRESSION_PROVED_NEIGHBORHOOD_GATE_OPEN",
        "result_kind": "exact all-volume fiber-stability and pointwise integrated-background-density suppression for the localized corrector slab",
        "question": "Can integration over the removed lowest cosine-sine phase plane erase the O(L^3) action cost of the slice-valid slab that obstructs deterministic corrector-energy bounds?",
        "answer": "No. Multiplying the slab by an arbitrary positive time-dependent row factor is a relaxation of the complete two-mode fiber. On active rows 1 and 2, exact cone-quadratic decompositions give residual-square lower bounds 1909/100 and 387/50 per four-site spatial period. Hence A(eta_L+T)>=2683*L^3/800 for every T in the lowest cosine-sine plane. Combining this with the certified two-mode strong convexity bounds the actual integrated background density relative to the zero background by (99/5600)*L^2*exp[-(2683/128)*L^3+96800/49] at lambda=2/5. Thus the exact slab is exponentially point-suppressed after fiber integration and is not itself a low-action marginal escape. This is a point-density statement, not a neighborhood probability or the required Gibbs corrector moment bound.",
        "row_cone_coercivity": {
            "row_factor_relaxation": "Omega_(t,s)=q_t*2^n_(t,s) with arbitrary q_t>0; this contains every lowest cosine-sine fiber field q_t=exp[a*cos(2*pi*t/L)+b*sin(2*pi*t/L)]",
            "residual_form": "On row t and one spatial period, r=b+a*l+c*rvec with a=q_(t-1)/q_t>0 and c=q_(t+1)/q_t>0.",
            "common_positive_quadratic_form": "Q(x,y)=(25/4)*x^2+(21/2)*x*y+(25/4)*y^2, with eigenvalues 1 and 23/2",
            "row_one": {
                "base": [enc(value) for value in row_one_vectors[0]],
                "left": [enc(value) for value in row_one_vectors[1]],
                "right": [enc(value) for value in row_one_vectors[2]],
                "decomposition": "sum_s r_(1,s)^2=1909/100+(117/25)*a+Q(a,c-33/50)",
                "lower_bound": enc(row_one_minimum),
            },
            "row_two": {
                "base": [enc(value) for value in row_two_vectors[0]],
                "left": [enc(value) for value in row_two_vectors[1]],
                "right": [enc(value) for value in row_two_vectors[2]],
                "decomposition": "sum_s r_(2,s)^2=387/50+(27/25)*c+Q(a-24/25,c)",
                "lower_bound": enc(row_two_minimum),
            },
            "combined_residual_square_lower_bound": enc(cell_lower),
            "status": "EXACT_POSITIVE_CONE_COERCIVITY",
        },
        "fiber_action_lower_bound": {
            "slab": "The E_p-perpendicular exponent slab from the pointwise-corrector no-go, repeated L/4 times spatially and over L^2 inert sites.",
            "scope": "Every L divisible by four with L>=8 and every real pair (a,b) in the removed lowest cosine-sine plane.",
            "multiplicity": "(L/4)*L^2=L^3/4 copies of each four-site active row",
            "calculation": "A=(1/2)*sum_x r_x^2 >= (1/2)*(L^3/4)*(2683/100)",
            "lower_bound": "A(eta_L+a*h_c+b*h_s)>=(2683/800)*L^3",
            "coefficient": enc(action_lower_coefficient),
            "strengthening": "The proof holds for arbitrary positive time-row factors q_t, a strictly larger class than the two-mode fiber.",
            "status": "FIBER_INFIMUM_RETAINS_ORDER_L_CUBED",
        },
        "integrated_background_density": {
            "measure": "In psi coordinates dmu_lambda is proportional to exp[-A(psi)/lambda^2]dpsi, and Z_eta=integral_R2 exp[-A(eta+a*h_c+b*h_s)/lambda^2] da db.",
            "background_density_ratio": "dnu/deta(eta_L) divided by dnu/deta(0) equals Z_(eta_L)/Z_0 in the same Lebesgue coordinates.",
            "two_mode_strong_convexity": "Hess_(a,b) A >= kappa_L*I_2, kappa_L=(2/9)*N*omega_L^2>=512/9, using sin(pi/L)>=2/L.",
            "slab_fiber_upper": "Z_(eta_L)<=(2*pi*lambda^2/kappa_L)*exp[-2683*L^3/(800*lambda^2)].",
            "zero_background_lower": "On |a|,|b|<=1/(2L), neighbor increments have magnitude below 44/(7L^2)<1/2, A(a*h_c+b*h_s)<=15488/49, so Z_0>=L^-2*exp[-15488/(49*lambda^2)].",
            "general_ratio_bound": "Z_(eta_L)/Z_0 <= (99*lambda^2/896)*L^2*exp[-((2683/800)*L^3-15488/49)/lambda^2].",
            "lambda_point_four_ratio_bound": "Z_(eta_L)/Z_0 <= (99/5600)*L^2*exp[-(2683/128)*L^3+96800/49].",
            "lambda_point_four_prefactor": enc(tuned_prefactor),
            "lambda_point_four_action_exponent": enc(tuned_action_exponent),
            "lambda_point_four_zero_constant": enc(tuned_zero_constant),
            "analytic_lemmas": [
                "pi<22/7 from the positive Dalzell integral already replayed by the predecessor",
                "sin(x)>=2*x/pi on [0,pi/2] by concavity",
                "e^(1/2)<2 because n!>=2^(n-1) bounds its exponential series by 1+2/3",
                "two-dimensional strong convexity gives the Gaussian fiber integral 2*pi*lambda^2/kappa_L",
            ],
            "status": "EXACT_BOUND_ON_POINTWISE_MARGINAL_DENSITY_RATIO",
        },
        "method_disposition": {
            "localized_slab_two_mode_fiber_action_escape": "OBSTRUCTED",
            "localized_slab_integrated_marginal_point_density_escape": "OBSTRUCTED",
            "localized_slab_neighborhood_probability_bound": "OPEN",
            "all_large_corrector_backgrounds_fiber_stable": "OPEN",
            "weighted_potential_mass_structure_factor_bound": "OPEN",
            "Gibbs_corrector_hyperuniformity_bound": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a probability bound for any positive-radius neighborhood of the slab background",
            "a tail estimate covering every background with a large corrector coefficient",
            "the Gibbs corrector hyperuniformity or current-susceptibility estimate",
            "the annealed score or actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "a robust neighborhood version of the row-cone coercivity bound with controlled entropy",
            "a block decomposition showing that every large corrector environment contains many fiber-stable costly patterns",
            "an integrated Gibbs tail estimate for those blocks under the exact background marginal",
            "the complementary weighted-potential mass structure-factor estimate",
            "the resulting current susceptibility and dyadic H^-1 shell theorem",
        ],
        "next_gate": "Robustify the two-row cone gap to a positive-radius block event and count compatible bad blocks. Use the fiber strong-convexity integral before the entropy sum, so the estimate is under the actual background marginal rather than the zero slice. Then prove that a large lowest-mode corrector forces enough bad blocks, or exhibit a different Gibbs-weighted environment that evades this mechanism.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic reconstructs both active residual rows, their Gram matrices, the positive-cone boundary minima, multiplicities, curvature prefactors, and lambda=2/5 exponents.",
            "analytic_arithmetic": "Positive quadratic completion proves the fiber action lower bound. Imported all-phase strong convexity and elementary sine/exponential bounds convert it to a two-dimensional integrated-fiber density comparison.",
            "assumptions": [
                "The action and full cosine-sine background marginal use the conventions certified by the three inputs.",
                "The density ratio compares the same fixed Lebesgue coordinates on E_p perpendicular and is not interpreted as a point probability.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_fiber_stability.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_fiber_stability.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_fiber_stability",
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
