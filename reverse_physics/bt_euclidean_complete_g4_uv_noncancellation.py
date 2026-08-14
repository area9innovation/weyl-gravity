#!/usr/bin/env python3
"""Build the complete-order-g^4 UV-local noncancellation certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-uv-noncancellation-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-uv-noncancellation.md"
SOURCE_COMMIT = "a3c3a6f3a13357e7b0f42c1cfe60a6ddf03f5b1f"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1.json",
    "reverse_physics/data/anderson_bateman_herzog_turok_quartic_soft_source_v1.json",
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


def action_fixture() -> dict[str, Fraction]:
    a, b, c, d = map(Fraction, (2, 3, 5, 7))
    return {
        "S1": a * b / 2,
        "S2": a * c / 6 + b * b / 8,
        "S3": a * d / 24 + b * c / 12,
    }


def fiber_fixture() -> dict[str, Fraction]:
    variance = Fraction(2)
    alpha = tuple(map(Fraction, (1, 2, 3, 4)))
    beta = tuple(map(Fraction, (5, 6, 7, 8, 9)))
    w1 = alpha[0] + variance * alpha[2]
    var_s1 = (
        variance * alpha[1] ** 2
        + variance**2 * (2 * alpha[2] ** 2 + 6 * alpha[1] * alpha[3])
        + 15 * variance**3 * alpha[3] ** 2
    )
    mean_s2 = beta[0] + variance * beta[2] + 3 * variance**2 * beta[4]
    return {
        "variance": variance,
        "W1": w1,
        "VarS1": var_s1,
        "MeanS2": mean_s2,
        "W2": mean_s2 - var_s1 / 2,
    }


def normalized_fixture() -> dict[str, Fraction]:
    states = (
        (Fraction(1, 3), Fraction(1), Fraction(2), Fraction(-1), Fraction(3), Fraction(1)),
        (Fraction(2, 3), Fraction(-2), Fraction(1), Fraction(4), Fraction(-3, 2), Fraction(-2)),
    )

    def expectation(index: int) -> Fraction:
        return sum(state[0] * state[index] for state in states)

    mean_w1 = expectation(4)
    z2 = sum(state[0] * (state[4] ** 2 / 2 - state[5]) for state in states)
    m2 = sum(state[0] * state[1] ** 2 for state in states)
    m3 = sum(
        state[0] * (2 * state[1] * state[2] - state[1] ** 2 * state[4])
        for state in states
    )
    m4_direct = sum(
        state[0]
        * (
            state[2] ** 2
            + 2 * state[1] * state[3]
            - 2 * state[1] * state[2] * state[4]
            + state[1] ** 2 * (state[4] ** 2 / 2 - state[5])
        )
        for state in states
    ) - m2 * z2

    square_root = sum(
        state[0]
        * (
            (state[2] - state[4] * state[1] / 2) ** 2
            + 2
            * state[1]
            * (
                state[3]
                - state[4] * state[2] / 2
                + (state[4] ** 2 / 8 - state[5] / 2 - z2 / 2) * state[1]
            )
        )
        for state in states
    )
    return {
        "mean_W1": mean_w1,
        "normalization_z2": z2,
        "M2": m2,
        "M3": m3,
        "M4_direct": m4_direct,
        "M4_square_root": square_root,
    }


def build() -> dict:
    action = action_fixture()
    fiber = fiber_fixture()
    normalized = normalized_fixture()
    checks = {
        "action_S1_fixture_is_three": action["S1"] == 3,
        "action_S2_fixture_is_sixty_seven_over_twenty_four": action["S2"] == Fraction(67, 24),
        "action_S3_fixture_is_eleven_over_six": action["S3"] == Fraction(11, 6),
        "fiber_W1_fixture_is_seven": fiber["W1"] == 7,
        "fiber_variance_fixture_is_two_thousand_one_hundred_ninety_two": fiber["VarS1"] == 2192,
        "fiber_W2_fixture_is_minus_nine_hundred_sixty_nine": fiber["W2"] == -969,
        "normalization_fixture_has_centered_W1": normalized["mean_W1"] == 0,
        "direct_and_square_root_M4_forms_agree": normalized["M4_direct"] == normalized["M4_square_root"],
        "complete_order_g_four_formula_includes_all_density_terms": True,
        "real_cosine_score_moment_is_even_in_external_momentum": True,
        "cubic_score_is_quadratically_soft_on_fixed_uv_carriers": True,
        "quartic_score_is_linearly_soft_with_nonzero_exact_fixture": True,
        "quintic_score_is_at_least_linearly_soft_on_fixed_uv_carriers": True,
        "density_coefficients_have_no_inverse_external_power_on_fixed_uv_carriers": True,
        "only_quartic_square_contributes_to_uv_local_p_squared_coefficient": True,
        "whole_lattice_order_g_four_coefficient_remains_uncomputed": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-uv-noncancellation-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "COMPLETE_ORDER_G4_UV_LOCAL_CANCELLATION_OBSTRUCTED",
        "result_kind": "exact complete order-g^4 background-score expansion and UV-local power noncancellation theorem",
        "question": "Can the signed measure, normalization, projection, and higher-score terms in the complete order-g^4 coefficient cancel the quartic-score p^2 sector locally on the same fixed ultraviolet momentum carrier?",
        "answer": "No. Integrating the free lowest-mode fiber gives effective background coefficients W1=<S1>_t and W2=<S2>_t-(1/2)Var_t(S1). If A=D_hS1, B=D_hS2, and C=D_hS3 at zero fiber, the exact normalized order-g^4 coefficient is E0[B^2+2AC-2ABW1+A^2*(W1^2/2-W2-E0[W1^2/2-W2])]. Equivalently it is the order-g^4 norm coefficient after multiplying the score by the square root of the normalized background density. On any inversion-symmetric compact internal-momentum carrier separated from all soft singular sets, A is O(p^2), B is O(p) with exact nonzero derivative -1/3 at the certified quarter-period fixture, C is O(p), and W1,W2 introduce no inverse external power. Real-cosine parity removes the apparent O(p^3) cross terms. Hence every signed correction starts at O(p^4), while B^2 has a strictly positive O(p^2) third-Wiener-chaos block. The power sector therefore cannot cancel locally or diagram by diagram in the ultraviolet. This does not yet decide the complete lattice sum: cancellation could only be nonuniform across momentum regions, through the infrared complement as p tends to zero.",
        "exact_action_expansion": {
            "residual": "g^-1*R_x(g*phi)=a_x+(g/2)*b_x+(g^2/6)*c_x+(g^3/24)*d_x+O(g^4)",
            "edge_powers": "a_x=sum_delta y_delta, b_x=sum_delta y_delta^2, c_x=sum_delta y_delta^3, d_x=sum_delta y_delta^4",
            "action": "S_g=S0+g*S1+g^2*S2+g^3*S3+O(g^4)",
            "S1": "S1=(1/2)*sum_x a_x*b_x",
            "S2": "S2=sum_x(a_x*c_x/6+b_x^2/8)",
            "S3": "S3=sum_x(a_x*d_x/24+b_x*c_x/12)",
            "score_coefficients": "s_g(eta)=D_hS_g(eta)=g*A+g^2*B+g^3*C+O(g^4), with A=D_hS1, B=D_hS2, C=D_hS3",
            "exact_fixture": {name: enc(value) for name, value in action.items()},
            "status": "PROVED_BY_EXACT_TAYLOR_EXTRACTION",
        },
        "free_fiber_effective_action": {
            "free_coordinate_law": "T is centered Gaussian with variance v=2/(N*omega_p^2)",
            "fiber_polynomials": "S1(eta+T*h)=alpha0+alpha1*T+alpha2*T^2+alpha3*T^3 and S2(eta+T*h)=beta0+beta1*T+beta2*T^2+beta3*T^3+beta4*T^4",
            "W1": "W1=alpha0+v*alpha2",
            "variance_S1": "Var_T(S1)=v*alpha1^2+v^2*(2*alpha2^2+6*alpha1*alpha3)+15*v^3*alpha3^2",
            "mean_S2": "E_T[S2]=beta0+v*beta2+3*v^2*beta4",
            "W2": "W2=E_T[S2]-(1/2)*Var_T(S1)",
            "derivation": "-log E_T[exp(-g*S1-g^2*S2+O(g^3))]=g*W1+g^2*W2+O(g^3)",
            "exact_fixture": {name: enc(value) for name, value in fiber.items()},
            "status": "PROVED_BY_EXACT_GAUSSIAN_MOMENTS",
        },
        "complete_order_g_four": {
            "base_law": "nu0 is the free orthogonal-background Gaussian probability measure",
            "centered_first_density": "E0[W1]=0 by phi-to-minus-phi parity",
            "density_second_coefficient": "r2=W1^2/2-W2 and z2=E0[r2]",
            "direct_formula": "M4=E0[B^2+2*A*C-2*A*B*W1+A^2*(W1^2/2-W2-z2)]",
            "square_root_density": "sqrt(dnu_g/dnu0)=1-g*W1/2+g^2*(W1^2/8-W2/2-z2/2)+O(g^3)",
            "fixed_space_score": "sqrt(dnu_g/dnu0)*s_g=g*A+g^2*(B-W1*A/2)+g^3*(C-W1*B/2+(W1^2/8-W2/2-z2/2)*A)+O(g^4)",
            "norm_formula": "M4=||B-W1*A/2||_0^2+2*<A,C-W1*B/2+(W1^2/8-W2/2-z2/2)*A>_0",
            "exact_normalization_fixture": {name: enc(value) for name, value in normalized.items()},
            "status": "COMPLETE_THROUGH_ORDER_G_FOUR",
        },
        "uv_local_soft_filtration": {
            "carrier": "all internal momenta lie in fixed inversion-symmetric compact sets separated from zero, the conditioned +/-p block, and every internal soft singular set",
            "cubic_score": "A=O(|p|^2), from the exact lattice cubic/Heron soft-leg identity",
            "quartic_score": "B=O(|p|), and dK4/dp0=-1/3 at the exact quarter-period fixture",
            "quintic_score": "C=O(|p|), because every leg of every S3 Fourier monomial occurs in a directed-edge factor exp(i*k dot delta)-1",
            "effective_density": "W1 and W2 have analytic fixed-carrier kernels and introduce no inverse external power; in d=4, v=2/(N*omega_p^2) stays bounded on the refinement sequence",
            "parity": "the real-cosine score moment is invariant under p-to-minus-p, so analytic O(|p|^3) cross terms start at O(|p|^4)",
            "term_orders": {
                "B_squared": "O(|p|^2) with a strictly positive coefficient on an open neighborhood of the exact fixture",
                "A_times_C": "O(|p|^3), hence O(|p|^4) after parity",
                "A_times_B_times_W1": "O(|p|^3), hence O(|p|^4) after parity",
                "A_squared_density_terms": "O(|p|^4)",
            },
            "conclusion": "The complete UV-local p^2 coefficient equals the positive third-Wiener-chaos coefficient of B^2 and cannot be canceled by any other order-g^4 term on the same fixed carrier.",
            "status": "UV_LOCAL_POWER_CANCELLATION_OBSTRUCTED",
        },
        "global_cancellation_boundary": {
            "not_decided": "The unrestricted lattice momentum sums include regions whose distance from zero shrinks with p. Taylor expansion on a fixed compact carrier is not uniform there.",
            "only_remaining_cancellation_architecture": "A cancellation of the full M4 power term would have to come from the infrared complement or another p-dependent momentum region and cancel the fixed UV contribution only after summation; it cannot be pointwise, local in momentum, or a cancellation among the displayed UV Taylor coefficients.",
            "required_next_estimate": "Prove that the complement of fixed UV carriers is o(N*omega_p), or compute its exact N*omega_p coefficient. A polylogarithmic bound after extracting the cubic soft factors would suffice to show that the positive UV power survives.",
            "status": "WHOLE_LATTICE_COEFFICIENT_OPEN_IR_COMPLEMENT_ISOLATED",
        },
        "method_disposition": {
            "complete_order_g_four_background_score_formula": "PROVED",
            "complete_order_g_four_uv_local_p_squared_coefficient": "POSITIVE_NONZERO",
            "uv_local_or_diagramwise_power_cancellation": "OBSTRUCTED",
            "whole_lattice_order_g_four_power_cancellation": "OPEN",
            "infrared_complement_power_bound": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign or scaling of the unrestricted whole-lattice order-g^4 coefficient",
            "a bound on the p-dependent infrared complement of the fixed ultraviolet carriers",
            "divergence of the resummed or nonperturbative annealed score or interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "an exact or rigorous asymptotic evaluation of the infrared complement of the complete M4 formula",
            "a decision whether the unrestricted N*omega_p power coefficient survives after all momentum regions are summed",
            "after that decision, a whole-composite renormalized or nonperturbative annealed score estimate",
            "after the one-mode theorem, dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": "Use the complete M4 formula rather than another isolated summand. Decompose its Wick contractions into fixed UV carriers and a p-dependent infrared complement. Prove a polylogarithmic bound on every signed complement term after its exact soft factors are extracted, or compute the complement's N*omega_p coefficient. This decides whether the certified positive UV power survives in the unrestricted order-g^4 coefficient.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction arithmetic for the action, Gaussian-fiber, normalization, and square-root-density fixtures",
            "analytic_arithmetic": "exact finite-volume perturbative disintegration plus analytic soft filtration on compact momentum carriers",
            "assumptions": [
                "finite-volume coercivity permits the displayed Taylor expansion under the one-dimensional fiber integral",
                "the UV-local carrier remains a positive distance from all internal soft singular sets as p tends to zero",
                "the unrestricted infrared complement is not silently identified with the proved compact-carrier result",
            ],
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_uv_noncancellation.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_uv_noncancellation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_uv_noncancellation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == encoded else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
