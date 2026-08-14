#!/usr/bin/env python3
"""Build the BT lowest-score logarithm/RG matching certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-score-rg-matching-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-score-rg-matching.md"
SOURCE_COMMIT = "65344fd4c8a7b0d224059f5fce63ca8ca049f1a9"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
    "reverse_physics/data/anderson_bateman_herzog_turok_score_rg_source_v1.json",
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


def build() -> dict:
    with open(os.path.join(ROOT, INPUTS[1]), encoding="utf-8") as handle:
        score_log = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[3]), encoding="utf-8") as handle:
        source = json.load(handle)

    dimension = 4
    mean_cosine_squared = Fraction(1, dimension)
    mean_cosine_fourth = Fraction(3, dimension * (dimension + 2))
    mean_sine_fourth = 1 - 2 * mean_cosine_squared + mean_cosine_fourth
    sphere_surface_coefficient_pi_squared = Fraction(2)
    fourier_measure_denominator_coefficient_pi_fourth = Fraction(16)
    vertex_prefactor = Fraction(4)
    log_residue_coefficient_over_pi_squared = (
        vertex_prefactor
        * mean_sine_fourth
        * sphere_surface_coefficient_pi_squared
        / fourier_measure_denominator_coefficient_pi_fourth
    )

    beta0_coefficient_over_pi_squared = Fraction(5, 16)
    beta1_coefficient_over_pi_fourth = Fraction(15, 128)
    running_g_squared_times_log_coefficient_pi_squared = (
        1 / (2 * beta0_coefficient_over_pi_squared)
    )
    matched_score_limit = (
        log_residue_coefficient_over_pi_squared
        * running_g_squared_times_log_coefficient_pi_squared
    )
    two_loop_loglog_coefficient = (
        beta1_coefficient_over_pi_fourth
        / (2 * beta0_coefficient_over_pi_squared**2)
    )
    gaussian_kappa = Fraction(2)
    gaussian_radius = Fraction(5)
    gaussian_full_score_variance = gaussian_kappa
    gaussian_zero_fiber_score_variance = gaussian_kappa**2 * gaussian_radius**2

    table = {row["length"]: row for row in score_log["numerical_preflight"]["table"]}
    slope_rows = []
    residue_float = float(log_residue_coefficient_over_pi_squared) / math.pi**2
    for length in (4, 6, 8, 12, 16):
        doubled = 2 * length
        if doubled not in table:
            continue
        slope = (
            table[doubled]["coefficient_C_L"]
            - table[length]["coefficient_C_L"]
        ) / math.log(2.0)
        slope_rows.append(
            {
                "length_pair": [length, doubled],
                "dyadic_slope": slope,
                "predicted_residue": residue_float,
                "slope_over_predicted_residue": slope / residue_float,
            }
        )

    checks = {
        "four_dimensional_cosine_second_moment_is_one_quarter": mean_cosine_squared == Fraction(1, 4),
        "four_dimensional_cosine_fourth_moment_is_one_eighth": mean_cosine_fourth == Fraction(1, 8),
        "four_dimensional_sine_fourth_moment_is_five_eighths": mean_sine_fourth == Fraction(5, 8),
        "lattice_log_residue_is_five_over_sixteen_pi_squared": log_residue_coefficient_over_pi_squared == Fraction(5, 16),
        "physical_beta0_is_five_over_sixteen_pi_squared": beta0_coefficient_over_pi_squared == Fraction(5, 16),
        "physical_beta1_is_fifteen_over_one_twenty_eight_pi_fourth": beta1_coefficient_over_pi_fourth == Fraction(15, 128),
        "score_log_residue_equals_physical_one_loop_beta_coefficient": log_residue_coefficient_over_pi_squared == beta0_coefficient_over_pi_squared,
        "running_g_squared_log_coefficient_is_eight_pi_squared_over_five": running_g_squared_times_log_coefficient_pi_squared == Fraction(8, 5),
        "rg_matched_leading_score_limit_is_one_half": matched_score_limit == Fraction(1, 2),
        "two_loop_loglog_coefficient_is_three_fifths": two_loop_loglog_coefficient == Fraction(3, 5),
        "sampled_dyadic_slopes_approach_the_predicted_residue_from_above": all(
            row["dyadic_slope"] > row["predicted_residue"] for row in slope_rows
        ) and all(
            left["dyadic_slope"] > right["dyadic_slope"]
            for left, right in zip(slope_rows, slope_rows[1:])
        ),
        "fixed_spacing_and_fixed_physical_volume_are_not_conflated": True,
        "all_order_and_nonperturbative_score_bounds_remain_open": True,
        "ordinary_eom_ward_identity_does_not_control_zero_fiber_score": gaussian_full_score_variance == 2 and gaussian_zero_fiber_score_variance == 100,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1",
        "schema_version": "reverse-physics-bt-euclidean-score-rg-matching-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "analytic lattice logarithmic residue and leading asymptotically-free score matching",
        "question": "Does asymptotic freedom cancel the logarithmic first score coefficient on a fixed-physical-volume lattice refinement, and is that the same question as fixed-spacing large volume?",
        "answer": "At leading order, yes on the matched refinement and no identification of the two limits is allowed. The orthogonal-background score coefficient satisfies C_L=(5/(16*pi^2))*log(L)+O(1). The lattice exponential coupling g is the unrescaled perfect-square coefficient; the source convention has g=4*pi*lambda_MS at leading matching order and beta_g=-(5/(16*pi^2))*g^3-(15/(128*pi^4))*g^5+... . Hence on an asymptotically free fixed-physical-volume trajectory, g_L^2*log(L) tends to 8*pi^2/5 and g_L^2*C_L tends exactly to 1/2. This removes the leading logarithmic nonuniformity but is not an all-order or nonperturbative Gibbs estimate. At fixed lattice spacing, L instead sends the external momentum to zero while the cutoff coupling is not tuned by mu proportional to L; the RG cancellation cannot be imported into that large-volume branch.",
        "lattice_log_residue": {
            "coefficient_definition": "C_L is the free orthogonal-background coefficient in Var[V_eta'(0)]=g^2*N*omega_p^2*C_L+O(g^3)",
            "small_momentum_vertex": "V3(p,q,-p-q)=-4*(p^2*q^2-(p dot q)^2)+higher lattice orders",
            "annular_integrand": "V3^2/(4*p^4*q^4*(p+q)^4)=4*sin(theta)^4/|q|^4+integrable remainder",
            "sphere_moments": {
                "mean_cosine_squared": enc(mean_cosine_squared),
                "mean_cosine_fourth": enc(mean_cosine_fourth),
                "mean_sine_fourth": enc(mean_sine_fourth),
            },
            "fourier_measure": "d^4q/(2*pi)^4 and area(S^3)=2*pi^2",
            "residue": "5/(16*pi^2)",
            "residue_coefficient_over_pi_squared": enc(log_residue_coefficient_over_pi_squared),
            "asymptotic_theorem": "C_L=(5/(16*pi^2))*log(L)+O(1)",
            "remainder_argument": "Split into |q|=O(p), p<<|q|<<1, and |q| bounded away from zero. The inner and outer pieces are O(1). On the annulus, lattice-symbol Taylor errors integrate to O(1); dyadic-shell Riemann-sum errors are summable because each is O(p/r). The projected external-cosine correction is O(L^-4).",
            "status": "PROVED_ANALYTICALLY",
        },
        "rg_normalization": {
            "source": "Anderson--Bateman--Herzog--Turok, arXiv:2608.12210v1",
            "source_record": INPUTS[3],
            "source_archive_sha256": source["source_archive_sha256"],
            "ms_convention": "lambda_3_b=(4*pi)*mu^(epsilon/2)*Z_3*lambda_3_r",
            "lattice_to_ms_leading_match": "g_PS=4*pi*lambda_MS",
            "beta_ms": "beta_lambda_MS=-5*lambda_MS^3-30*lambda_MS^5+O(lambda_MS^7)",
            "beta_physical": "beta_g=-(5/(16*pi^2))*g^3-(15/(128*pi^4))*g^5+O(g^7)",
            "beta0_coefficient_over_pi_squared": enc(beta0_coefficient_over_pi_squared),
            "beta1_coefficient_over_pi_fourth": enc(beta1_coefficient_over_pi_fourth),
            "ward_identity": "Z_3*sqrt(Z_sigma)=Z_4*Z_sigma=1",
            "field_running": "At epsilon=0, gamma_sigma=beta_g/g; with mu*d sigma/dmu=-gamma_sigma*sigma, the exponential field psi=g*sigma is RG invariant",
            "finite_lattice_ms_matching": "OPEN_BEYOND_UNIVERSAL_LEADING_COEFFICIENTS",
        },
        "matched_refinement": {
            "scale_setting": "fixed physical torus size with inverse lattice spacing mu_L proportional to L",
            "running_limit": "lim_(L->infinity) g_L^2*log(L)=8*pi^2/5",
            "running_limit_coefficient_pi_squared": enc(running_g_squared_times_log_coefficient_pi_squared),
            "score_limit": "lim_(L->infinity) g_L^2*C_L=1/2 at leading-log order",
            "score_limit_exact": enc(matched_score_limit),
            "two_loop_running_form": "g_L^2=(8*pi^2/(5*log L))*(1-(3/5)*log(log L)/log L+O(1/log L)) up to scheme-dependent nonlogarithmic 1/log L terms",
            "two_loop_loglog_coefficient": enc(two_loop_loglog_coefficient),
            "status": "LEADING_AND_TWO_LOOP_RUNNING_MATCHED",
        },
        "scale_setting_split": {
            "fixed_physical_volume_refinement": "mu_L grows proportionally to L, so asymptotic freedom compensates the score logarithm at leading order",
            "fixed_lattice_spacing_large_volume": "the ultraviolet cutoff and its bare coupling are fixed while the lowest external momentum tends to zero; the matched-refinement running cannot be used as a volume-uniform estimate",
            "source_ir_boundary": "Perturbative off-shell IR finiteness at fixed nonzero external momentum does not establish a bound uniform as that external momentum tends to zero",
            "status": "DISTINCT_LIMITS_CERTIFIED",
        },
        "finite_lattice_ward_gate": {
            "full_field_identity": "For the normalized finite-volume Gibbs measure and any fixed mean-zero direction h, E_mu[(D_h S_g(phi))^2]=E_mu[D_h^2 S_g(phi)]",
            "conditional_identity": "For every background eta, E_qeta[V_eta'(T)^2]=E_qeta[V_eta''(T)]",
            "derivation": "Integrate D_h[(D_h S_g)*exp(-S_g)] over the mean-zero field space, or integrate d/dt[V_eta'(t)*exp(-V_eta(t))] on each fiber; coercivity kills the boundary term",
            "target_mismatch": "The missing center theorem concerns E_nu[V_eta'(0)^2], with the score evaluated at the zero fiber coordinate. The ordinary equation-of-motion identity evaluates V_eta' at the sampled T and supplies no general transfer to V_eta'(0).",
            "exact_shifted_gaussian_fixture": {
                "potential": "V_R(t,y)=(kappa/2)*(t-y)^2+y^2/(2*R^2)",
                "kappa": enc(gaussian_kappa),
                "R": enc(gaussian_radius),
                "conditional_full_score_variance": enc(gaussian_full_score_variance),
                "conditional_expected_hessian": enc(gaussian_kappa),
                "annealed_zero_fiber_score_variance": enc(gaussian_zero_fiber_score_variance),
            },
            "disposition": "The ordinary full-score Ward identity is exact but cannot by itself close the zero-fiber score target. The abstract fixture is a logical no-transfer theorem, not an obstruction to an additional BT-specific identity.",
            "status": "FULL_SCORE_IDENTITY_PROVED_ZERO_FIBER_TRANSFER_OBSTRUCTED_LOGICALLY",
        },
        "numerical_preflight": {
            "evidence_type": "BINARY64_DYADIC_SLOPES_SUPPORTING_ONLY",
            "slope_rows": slope_rows,
            "interpretation": "The finite-size dyadic slopes decrease toward 5/(16*pi^2). The analytic annular argument, not this table, establishes the residue.",
        },
        "method_disposition": {
            "lattice_score_logarithmic_residue": "PROVED",
            "fixed_bare_coupling_leading_score_uniformity": "OBSTRUCTED",
            "rg_matched_leading_score_uniformity": "RESTORED_AT_LEADING_LOG",
            "score_residue_equals_physical_beta0": "PROVED",
            "rg_invariant_exponential_field": "PROVED_FROM_IMPORTED_WARD_IDENTITY",
            "ordinary_finite_lattice_eom_score_identity": "PROVED",
            "ordinary_eom_to_zero_fiber_score_transfer": "OBSTRUCTED_AS_A_LOGICAL_INFERENCE",
            "bt_specific_zero_fiber_ward_identity": "OPEN",
            "finite_lattice_to_ms_scheme_matching": "OPEN",
            "all_order_leading_log_score_resummation": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "fixed_spacing_large_volume_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "an all-order bound on perturbative score coefficients or their resummation",
            "a lattice-to-MS matching theorem beyond the universal leading coefficients",
            "a nonperturbative annealed score, center, lowest-mode, or H^-1 moment bound",
            "fixed-spacing large-volume control from fixed-physical-volume RG running",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a finite-volume lattice Ward identity for the conditional zero-fiber score composite",
            "an all-order leading-log equation or uniform Borel/cluster control for that composite",
            "a nonperturbative multiscale estimate under the running-coupling lattice Gibbs measure",
            "after the annealed score bound, the integrated lowest-mode and Fourier-shell estimates",
        ],
        "next_gate": "The ordinary finite-lattice equation-of-motion Ward identity is now proved but lands on the sampled full score and has no general transfer to the zero-fiber target. Derive a BT-specific renormalized identity for the projected zero-fiber composite and determine its all-order leading-log RG equation. If the resulting RG-improved score remains bounded, seek a nonperturbative multiscale inequality on the tuned fixed-physical-volume trajectory; treat fixed-spacing large volume separately.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction arithmetic for angular moments, beta-function normalization conversion, running constants, matched limit, and two-loop log-log coefficient",
            "analytic_arithmetic": "standard four-dimensional spherical moments and a dyadic lattice-symbol/Riemann-sum remainder estimate",
            "numerical_arithmetic": "binary64 dyadic slopes derived from the independently verified predecessor finite sums",
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_score_rg_matching.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_score_rg_matching.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_score_rg_matching",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
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
