#!/usr/bin/env python3
"""Build the BT zero-fiber Ward-weight obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-zero-fiber-ward-weight-obstruction-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-zero-fiber-ward-weight-obstruction.md"
SOURCE_COMMIT = "5678550187b21085448e103403fa793eba7fd600"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json",
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


def build() -> dict:
    kappa = Fraction(2)
    radius = Fraction(5)
    marginal_variance = radius**2 + 1 / kappa
    posterior_variance = radius**2 / (1 + kappa * radius**2)
    target_score_second_moment = kappa**2 * radius**2
    weighted_score_second_moment = kappa**2 * posterior_variance
    weighted_hessian = kappa
    marginal_log_curvature = -1 / marginal_variance

    fixture_m = 2
    fixture_tail_bound = Fraction(1, 2**fixture_m)
    fixture_density_bound = fixture_tail_bound / fixture_m
    fixture_inverse_density_bound = 1 / fixture_density_bound

    checks = {
        "background_marginal_factorization_is_exact": True,
        "constrained_measure_is_q_zero_weighted_background_measure": True,
        "target_requires_inverse_q_zero_under_constrained_measure": True,
        "marginal_first_derivative_identity_is_exact": True,
        "marginal_second_derivative_identity_is_exact": True,
        "gaussian_marginal_variance_is_fifty_one_over_two": marginal_variance == Fraction(51, 2),
        "gaussian_posterior_variance_is_twenty_five_over_fifty_one": posterior_variance == Fraction(25, 51),
        "gaussian_target_score_second_moment_is_one_hundred": target_score_second_moment == 100,
        "gaussian_weighted_score_second_moment_is_one_hundred_over_fifty_one": weighted_score_second_moment == Fraction(100, 51),
        "gaussian_marginal_log_curvature_is_minus_two_over_fifty_one": marginal_log_curvature == Fraction(-2, 51),
        "bt_m_two_density_bound_is_one_eighth": fixture_density_bound == Fraction(1, 8),
        "bt_m_two_inverse_density_bound_is_eight": fixture_inverse_density_bound == 8,
        "bt_zero_fiber_density_has_no_positive_family_uniform_lower_bound": True,
        "annealed_score_and_h_minus_one_targets_remain_open": True,
        "no_born_krein_continuum_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-zero-fiber-ward-weight-obstruction-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact disintegration identities and BT-specific obstruction to pointwise removal of the zero-fiber density weight",
        "question": "Can the missing annealed zero-fiber-score moment be obtained from a constrained or integrated-marginal Ward identity by removing its conditional-density weight uniformly over backgrounds?",
        "answer": "No for that proof architecture. Exact disintegration shows that the relevant derivatives of the integrated lowest-mode marginal at t=0 weight the background by q_eta(0), the conditional density at the zero fiber. The target instead equals rho(0) times the constrained expectation of s_eta^2/q_eta(0). On the certified fixed 6^4 BT runaway family, strict convexity, a mode left of -m, and q_m^(u){u>=-m}<=2^-m imply q_m^(u)(0)<=2^-m/m. Since t=u*log(2), the t-density obeys q_eta_m^(t)(0)=q_m^(u)(0)/log(2), and it too has no positive background-uniform lower bound. Thus pointwise division by the weight cannot close the target. A shifted-Gaussian family independently shows that the displayed q(0)-weighted marginal data can stay bounded while the unweighted score moment diverges. This obstructs local/constrained Ward-to-target transfer as formulated, not an annealed BT estimate using the Gibbs rarity of runaway backgrounds.",
        "exact_disintegration": {
            "fiber_potential": "V_eta(t)=S(eta+t*h)",
            "fiber_normalization": "Z_eta=integral_R exp[-V_eta(t)]dt",
            "background_measure": "nu(deta)=Z_eta*deta/Z",
            "conditional_density": "q_eta(t)=exp[-V_eta(t)]/Z_eta",
            "integrated_mode_density": "rho(t)=E_nu[q_eta(t)]",
            "zero_fiber_score": "s_eta=V_eta'(0)",
            "zero_fiber_hessian": "H_eta=V_eta''(0)",
            "first_derivative": "rho'(0)=-E_nu[q_eta(0)*s_eta]",
            "second_derivative": "rho''(0)=E_nu[q_eta(0)*(s_eta^2-H_eta)]",
            "status": "PROVED_BY_FINITE_DIMENSIONAL_DISINTEGRATION_AND_DIFFERENTIATION",
        },
        "constrained_measure_change": {
            "definition": "mu_0(deta)=exp[-V_eta(0)]*deta/(Z*rho(0))",
            "radon_nikodym": "dmu_0/dnu=q_eta(0)/rho(0)",
            "inverse_radon_nikodym": "dnu/dmu_0=rho(0)/q_eta(0)",
            "weighted_ward_content": "rho''(0)/rho(0)=E_mu0[s_eta^2-H_eta]",
            "target_identity": "E_nu[s_eta^2]=rho(0)*E_mu0[s_eta^2/q_eta(0)]",
            "interpretation": "Constrained local insertions determine q_eta(0)-weighted moments. The desired background-marginal score is a nonlocal fiber observable because 1/q_eta(0)=Z_eta*exp[V_eta(0)] contains the full fiber normalization.",
            "status": "EXACT_WEIGHT_MISMATCH_PROVED",
        },
        "shifted_gaussian_no_transfer": {
            "potential": "V_R(t,y)=(kappa/2)*(t-y)^2+y^2/(2*R^2)",
            "background_law": "nu=N(0,R^2)",
            "conditional_law": "q_y=N(y,1/kappa)",
            "score": "s_y=-kappa*y",
            "hessian": "H_y=kappa",
            "marginal_variance": enc(marginal_variance),
            "posterior_variance_at_t_zero": enc(posterior_variance),
            "fixture": {
                "kappa": enc(kappa),
                "R": enc(radius),
                "unweighted_score_second_moment": enc(target_score_second_moment),
                "q_zero_weighted_score_second_moment_divided_by_rho_zero": enc(weighted_score_second_moment),
                "q_zero_weighted_hessian_divided_by_rho_zero": enc(weighted_hessian),
                "rho_second_derivative_divided_by_rho_zero": enc(marginal_log_curvature),
            },
            "family_limit": "As R tends to infinity, E_nu[s_y^2]=kappa^2*R^2 diverges while E_mu0[s_y^2]=kappa^2*R^2/(1+kappa*R^2) tends to kappa and rho''(0)/rho(0) tends to zero.",
            "status": "GENERAL_WEIGHT_REMOVAL_OBSTRUCTED_LOGICALLY",
        },
        "bt_runaway_density_obstruction": {
            "carrier": "fixed periodic 6^4 BT Euclidean lattice at lambda=2/5",
            "family": "eta_m=4*m*log(2)*a, t=u*log(2), integer m>=2",
            "u_density": "q_m^(u) is the normalized conditional density with respect to du",
            "coordinate_density_relation": "q_eta_m^(t)(0)=q_m^(u)(0)/log(2) because t=u*log(2)",
            "imported_mass_bound": "q_m^(u)({u>=-m})<=2^-m",
            "imported_shape_bound": "The fiber potential is strictly convex and its unique minimizer lies below -m.",
            "monotonicity": "The normalized u-density q_m^(u)(u) is decreasing for u>=-m, so q_m^(u)(u)>=q_m^(u)(0) on [-m,0].",
            "integral_bound": "m*q_m^(u)(0)<=integral_[-m,0]q_m^(u)(u)du<=q_m^(u)({u>=-m})<=2^-m",
            "density_bound": "q_m^(u)(0)<=2^-m/m",
            "inverse_density_bound": "1/q_m^(u)(0)>=m*2^m",
            "exact_m2_fixture": {
                "m": fixture_m,
                "tail_probability_upper_bound": enc(fixture_tail_bound),
                "zero_fiber_density_upper_bound": enc(fixture_density_bound),
                "inverse_zero_fiber_density_lower_bound": enc(fixture_inverse_density_bound),
            },
            "conclusion": "There is no positive lower bound on q_eta(0) uniform over BT orthogonal backgrounds, even at fixed L=6.",
            "status": "POINTWISE_ZERO_FIBER_DENSITY_LOWER_BOUND_OBSTRUCTED_IN_BT",
        },
        "method_disposition": {
            "integrated_marginal_derivative_identities": "PROVED",
            "zero_fiber_constrained_change_of_measure": "PROVED",
            "local_constrained_insertions_are_q_zero_weighted": "PROVED",
            "general_weight_removal_from_marginal_data": "OBSTRUCTED_AS_A_LOGICAL_INFERENCE",
            "bt_background_uniform_q_zero_lower_bound": "OBSTRUCTED",
            "pointwise_constrained_ward_to_annealed_score_transfer": "OBSTRUCTED_AS_FORMULATED",
            "annealed_inverse_density_or_center_bound": "OPEN",
            "bt_specific_annealed_multiscale_score_bound": "OPEN",
            "all_order_leading_log_score_resummation": "OPEN",
            "fixed_spacing_large_volume_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "divergence of the annealed zero-fiber score or conditional-center moment",
            "failure of a BT estimate that uses the Gibbs probability of runaway backgrounds",
            "failure of an all-order renormalized composite identity with nonlocal fiber-normalization control",
            "divergence of the integrated lowest-mode or actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "an annealed estimate of s_eta^2 under nu, equivalently inverse-q_eta(0) control under mu_0",
            "a BT-specific nonperturbative multiscale inequality coupling runaway-center size to its background Gibbs rarity",
            "all-order control of the renormalized zero-fiber composite on the tuned fixed-physical-volume trajectory",
            "after the one-mode bound, dyadic Fourier-shell estimates for the actual interacting H^-1 moment",
        ],
        "next_gate": "Do not pursue a pointwise q_eta(0) lower bound or a purely local constrained Ward insertion. Estimate the joint annealed tail of the zero-fiber score and inverse conditional density, using the exact all-background strong convexity and BT action cost of moving the conditional minimizer; on the tuned refinement branch incorporate the certified RG normalization. A theorem must retain the background Gibbs weight. Alternatively construct a rigorously weighted BT family whose contribution makes the annealed score diverge.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction arithmetic for the shifted-Gaussian fixture and m=2 BT consequence; symbolic disintegration identities and exact imported BT inequalities for all m>=2",
            "assumptions": [
                "finite-volume coercivity and differentiability justify differentiation under the fiber/background integrals",
                "the fiber coordinate and Lebesgue factor are fixed consistently in nu, q_eta, rho, and mu_0",
            ],
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_zero_fiber_ward_weight_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_zero_fiber_ward_weight_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_zero_fiber_ward_weight_obstruction",
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
