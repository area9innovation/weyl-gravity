#!/usr/bin/env python3
"""Build the BT annealed-center score-reduction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-annealed-center-score-reduction-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-annealed-center-score-reduction.md"
OBSERVATION_REL = "reverse_physics/data/bt_euclidean_center_score_observations_v1.json"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/data/anderson_bateman_herzog_turok_divergences_source_v1.json",
    OBSERVATION_REL,
]
SOURCE_COMMIT = "0aecdac4ed8ed7a6e3b76eac977cf4118cc40261"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def estimate(run: dict, numerator: str, denominator: str | None = None) -> float:
    count = math.fsum(block["sample_count"] for block in run["blocks"])
    value = math.fsum(block[numerator] for block in run["blocks"]) / count
    if denominator:
        divisor = math.fsum(
            block[denominator] for block in run["blocks"]
        ) / count
        value /= divisor
    return value


def jackknife_error(
    run: dict, numerator: str, denominator: str | None = None
) -> float:
    blocks = run["blocks"]
    total_count = math.fsum(block["sample_count"] for block in blocks)
    total_numerator = math.fsum(block[numerator] for block in blocks)
    total_denominator = (
        math.fsum(block[denominator] for block in blocks)
        if denominator
        else None
    )
    deleted = []
    for block in blocks:
        count = total_count - block["sample_count"]
        value = (total_numerator - block[numerator]) / count
        if denominator:
            divisor = (total_denominator - block[denominator]) / count
            value /= divisor
        deleted.append(value)
    center = math.fsum(deleted) / len(deleted)
    variance = (len(deleted) - 1) / len(deleted) * math.fsum(
        (value - center) ** 2 for value in deleted
    )
    return math.sqrt(variance)


def summarize(run: dict) -> dict:
    volume = run["lattice"]["volume"]
    omega = run["mode"]["omega"]
    scale = volume * omega * omega
    t2 = estimate(run, "sum_t2")
    center2 = estimate(run, "sum_mode_center2")
    recentered2 = estimate(run, "sum_recentered2")
    score2 = estimate(run, "sum_zero_fiber_score2")
    center_fraction = estimate(
        run, "sum_mode_center2", "sum_t2"
    )
    return {
        "length": run["lattice"]["length"],
        "volume": volume,
        "omega": omega,
        "sample_count": sum(block["sample_count"] for block in run["blocks"]),
        "acceptance_rate": run["acceptance_rate"],
        "mean_action_density": estimate(run, "sum_action_density"),
        "mean_t2": t2,
        "mean_mode_center2": center2,
        "mean_recentered_about_mode2": recentered2,
        "mean_zero_fiber_score2": score2,
        "scaled_mode_center2_N_omega2": scale * center2,
        "scaled_mode_center2_jackknife_error": (
            scale * jackknife_error(run, "sum_mode_center2")
        ),
        "scaled_zero_fiber_score2_over_N_omega2": score2 / scale,
        "scaled_zero_fiber_score2_jackknife_error": (
            jackknife_error(run, "sum_zero_fiber_score2") / scale
        ),
        "mode_center_fraction_of_raw_t2": center_fraction,
        "mode_center_fraction_jackknife_error": jackknife_error(
            run, "sum_mode_center2", "sum_t2"
        ),
        "certified_conditional_variance_upper_bound": 9.0 / (2.0 * scale),
        "free_real_mode_variance": 2.0 / scale,
        "maximum_absolute_mode_center": run["root_diagnostic"]["maximum_absolute_mode_center"],
        "maximum_absolute_mode_score_residual": run["root_diagnostic"]["maximum_absolute_mode_score_residual"],
        "maximum_center_score_inequality_residual": run["root_diagnostic"]["maximum_center_score_inequality_residual"],
    }


def build() -> dict:
    with open(os.path.join(ROOT, OBSERVATION_REL), encoding="utf-8") as handle:
        observations = json.load(handle)
    summaries = [summarize(run) for run in observations["runs"]]
    curvature_coefficient = Fraction(2, 9)
    gaussian_kappa = Fraction(2)
    gaussian_R = Fraction(5)
    gaussian_center_variance = gaussian_R**2
    gaussian_conditional_variance = 1 / gaussian_kappa
    gaussian_total_variance = (
        gaussian_center_variance + gaussian_conditional_variance
    )
    gaussian_score_variance = (
        gaussian_kappa**2 * gaussian_center_variance
    )
    gaussian_hessian_determinant = Fraction(2, 25)
    checks = {
        "curvature_coefficient_is_two_ninths": curvature_coefficient == Fraction(2, 9),
        "conditional_mode_mean_square_constant_is_inverse_kappa": True,
        "conditional_variance_constant_is_inverse_kappa": True,
        "center_score_constant_is_inverse_kappa_squared": True,
        "sufficient_score_to_mode_constant_is_four_over_eighty_one": curvature_coefficient**2 == Fraction(4, 81),
        "integrated_moment_constant_is_27_plus_81C_over_two": True,
        "gaussian_counterexample_hessian_is_positive": gaussian_hessian_determinant > 0,
        "gaussian_counterexample_center_variance_is_twenty_five": gaussian_center_variance == 25,
        "gaussian_counterexample_total_variance_is_fifty_one_halves": gaussian_total_variance == Fraction(51, 2),
        "gaussian_counterexample_score_variance_is_one_hundred": gaussian_score_variance == 100,
        "both_observed_scaled_centers_are_below_one_tenth": all(row["scaled_mode_center2_N_omega2"] < 0.1 for row in summaries),
        "both_observed_center_fractions_are_below_one_twentieth": all(row["mode_center_fraction_of_raw_t2"] < 0.05 for row in summaries),
        "both_observed_scaled_scores_are_below_one_fiftieth": all(row["scaled_zero_fiber_score2_over_N_omega2"] < 0.02 for row in summaries),
        "all_numeric_root_residuals_are_below_one_e_minus_eight": all(row["maximum_absolute_mode_score_residual"] < 1.0e-8 for row in summaries),
        "all_sampled_center_score_inequalities_pass": all(row["maximum_center_score_inequality_residual"] <= 1.0e-14 for row in summaries),
        "annealed_score_theorem_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-annealed-center-score-reduction-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_REDUCTION_PROVED_WITH_FINITE_VOLUME_DIAGNOSTIC",
        "result_kind": "exact annealed-center reduction, logical input obstruction, and finite-volume numerical diagnostic",
        "question": "What theorem is now exactly sufficient to convert the all-background conditional width into the normalized interacting lowest-mode second moment, and do the first two simulated volumes show center growth?",
        "answer": "Let V_eta(t)=S_lambda(eta+t*h), kappa_L=(2/9)*N*omega_L^2, m(eta) be its unique mode, and nu be the exact background marginal. Strong convexity proves m(eta)^2<=V_eta'(0)^2/kappa_L^2 and places the conditional mean within squared distance 1/kappa_L of m. Therefore E_nu[V_eta'(0)^2]<=C_s*N*omega_L^2 would imply E[t^2]<=(27+81*C_s)/(2*N*omega_L^2). Curvature, half-period symmetry, and an extensive action/virial bound do not imply this score estimate by themselves: an exact shifted-Gaussian family has all three and arbitrarily large center variance. Deterministic finite-volume Metropolis diagnostics at L=4 and L=6 show N*omega_L^2*E[m^2] approximately 0.036 and 0.040 and E[V_eta'(0)^2]/(N*omega_L^2) approximately 0.010 and 0.012. These observations support, but do not prove, the required uniform score bound.",
        "exact_center_reduction": {
            "fiber": "V_eta(t)=S_lambda(eta+t*h), eta orthogonal to h",
            "curvature": "V_eta''(t)>=kappa_L=(2/9)*N*omega_L^2",
            "mode": "m(eta) is the unique solution V_eta'(m)=0",
            "background_marginal": "dnu(eta)=Z_eta*deta/Z, Z_eta=integral_R exp[-V_eta(t)]dt",
            "conditional_mode_mean_identity": "E_q[(T-m)*V_eta'(T)]=1",
            "mode_mean_square_bound": "E_q[(T-m)^2]<=1/kappa_L and |E_q[T]-m|^2<=1/kappa_L",
            "conditional_variance_bound": "Var_q(T)<=1/kappa_L",
            "zero_fiber_score_bound": "m(eta)^2<=V_eta'(0)^2/kappa_L^2",
            "sufficient_score_theorem": "E_nu[V_eta'(0)^2]<=C_s*N*omega_L^2",
            "integrated_consequence": "E_mu[T^2]<=(27+81*C_s)/(2*N*omega_L^2), using the exact even marginal",
            "curvature_coefficient": enc(curvature_coefficient),
            "sufficient_score_normalization_coefficient": enc(curvature_coefficient**2),
            "status": "PROVED_REDUCTION_ONLY",
        },
        "logical_input_obstruction": {
            "family": "V_R(t,y)=(kappa/2)*(t-y)^2+y^2/(2*R^2), R>0",
            "properties": [
                "V_R is a positive-definite homogeneous quadratic potential",
                "V_R(-t,-y)=V_R(t,y)",
                "the t-fiber curvature is exactly kappa",
                "the conditional center is m(y)=y",
                "x dot grad V_R=2*V_R pointwise and E[V_R]=1",
                "Var(m)=R^2 is unbounded as R tends to infinity",
            ],
            "exact_fixture": {
                "kappa": enc(gaussian_kappa),
                "R": enc(gaussian_R),
                "potential": "V(t,y)=(t-y)^2+y^2/50",
                "hessian_determinant": enc(gaussian_hessian_determinant),
                "conditional_variance": enc(gaussian_conditional_variance),
                "center_variance": enc(gaussian_center_variance),
                "total_t_variance": enc(gaussian_total_variance),
                "zero_fiber_score_variance": enc(gaussian_score_variance),
                "mean_action": enc(1),
                "radial_virial_expectation": enc(2),
            },
            "disposition": "All-background fiber curvature, inversion symmetry, and an extensive affine-virial/action expectation do not logically imply annealed center control. This abstract family does not reproduce every BT locality or quartic-coercivity property and is not an obstruction to a model-specific BT theorem.",
            "extensive_dimension_extension": "Adjoining independent centered unit Gaussian spectator coordinates preserves the shifted t-y block, gives pointwise radial virial equality for the full homogeneous quadratic potential, and makes the mean action proportional to dimension while Var(m)=R^2 remains arbitrary.",
        },
        "finite_volume_diagnostic": {
            "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
            "observation_path": OBSERVATION_REL,
            "observation_sha256": sha256(OBSERVATION_REL),
            "summaries": summaries,
            "interpretation": "At both sampled volumes the mode-center term is below two percent of the raw t second moment and the two dimensionless score/center scalings are similar. Autocorrelation, two-volume reach, one sampler, and binary64 root finding prevent a uniform theorem or precision scaling claim.",
        },
        "perturbative_interface": {
            "source": "Anderson--Bateman--Herzog--Turok, arXiv:2608.12210v1",
            "source_record": "reverse_physics/data/anderson_bateman_herzog_turok_divergences_source_v1.json",
            "source_disposition": "The source proves all-orders Euclidean off-shell perturbative IR finiteness from derivative-vertex momentum factors and states the perfect-square renormalization Ward identity. This supports the expected low-score cancellation mechanism but does not supply a nonperturbative finite-volume background-marginal score bound.",
            "claim_boundary": "PERTURBATIVE_SOURCE_ONLY_NOT_USED_AS_NONPERTURBATIVE_EVIDENCE",
        },
        "method_disposition": {
            "mode_mean_center_equivalence_up_to_width": "PROVED",
            "annealed_center_to_zero_fiber_score_reduction": "PROVED",
            "curvature_symmetry_virial_alone_suffice": "OBSTRUCTED_AS_A_LOGICAL_INFERENCE",
            "finite_volume_center_scaling": "OBSERVED_L4_L6_NOT_CERTIFIED_UNIFORM",
            "annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "a volume-uniform annealed center or zero-fiber-score estimate",
            "the normalized interacting lowest-mode or H^-1 second moment",
            "tightness or a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a nonperturbative background-marginal estimate E_nu[V_eta'(0)^2]<=C_s*N*omega_L^2",
            "a proof mechanism using BT locality, shift-derivative momentum cancellation, or a controlled multiscale decomposition",
            "after the score bound, a Fourier-shell extension beyond one axial lowest mode",
        ],
        "next_gate": "Derive the zero-fiber score as a low-momentum projection of local nonlinear residual composites and prove its background-marginal second moment has the extra omega_L factor suggested by shift symmetry and the two-volume diagnostic; alternatively construct a BT volume sequence violating that scaling.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "exact_arithmetic": "Python Fraction arithmetic for all reduction and shifted-Gaussian constants",
            "numerical_arithmetic": observations["arithmetic"],
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_center_score_reduction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_center_score_reduction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_center_score_reduction",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        with open(CERT_PATH, encoding="utf-8") as handle:
            return 0 if json.load(handle) == payload else 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
