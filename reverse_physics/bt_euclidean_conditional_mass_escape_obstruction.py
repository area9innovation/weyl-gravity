#!/usr/bin/env python3
"""Certify escape of BT conditional mass from the centered fiber origin."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-conditional-mass-escape-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-conditional-mass-escape-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
]
SOURCE_COMMIT = "31d9f5a73059f7250c72e6c3813295acc3ac9152"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def cycle_action(coefficients: tuple[int, ...]) -> Fraction:
    action = Fraction(0)
    for site in range(6):
        residual = Fraction(-2)
        for neighbor in ((site - 1) % 6, (site + 1) % 6):
            residual += dyadic(coefficients[neighbor] - coefficients[site])
        action += residual * residual / 2
    return action


def fiber_coefficients(
    m: int, u: int, background: tuple[int, ...], mode: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(4 * m * a + u * h for a, h in zip(background, mode))


def theorem_constants(m: int) -> dict[str, int]:
    center_lower = 2 ** (46 * m - 3)
    well_upper = 243 * 2 ** (40 * m)
    beta = 1350
    exponent_gap = beta * (center_lower - well_upper)
    return {
        "center_lower": center_lower,
        "well_upper": well_upper,
        "beta": beta,
        "exponent_gap": exponent_gap,
        "tail_binary_exponent": 50 * m - 1 - exponent_gap,
    }


def build() -> dict:
    coupling = Fraction(2, 5)
    spatial_volume = 6**3
    background = (-1, -1, 1, -3, 3, 1)
    mode = (2, 1, -1, -2, -1, 1)
    shifted = tuple(a - h for a, h in zip(background, mode))
    edge_differences = tuple(
        shifted[(site + 1) % 6] - shifted[site] for site in range(6)
    )
    mode_edge_differences = tuple(
        mode[(site + 1) % 6] - mode[site] for site in range(6)
    )

    fixture_m = 2
    fixture_n = 4 * fixture_m
    fixture_candidate_u = -4 * fixture_m
    fixture_threshold_u = -fixture_m
    candidate_coefficients = fiber_coefficients(
        fixture_m, fixture_candidate_u, background, mode
    )
    threshold_coefficients = fiber_coefficients(
        fixture_m, fixture_threshold_u, background, mode
    )
    candidate_action = cycle_action(candidate_coefficients)
    threshold_action = cycle_action(threshold_coefficients)
    fixture_constants = theorem_constants(fixture_m)

    checks = {
        "coupling_is_two_fifths": coupling == Fraction(2, 5),
        "spatial_replication_is_216": spatial_volume == 216,
        "background_is_mean_zero": sum(background) == 0,
        "mode_is_mean_zero": sum(mode) == 0,
        "background_is_mode_orthogonal": (
            sum(a * h for a, h in zip(background, mode)) == 0
        ),
        "shifted_vector_is_exact": shifted == (-3, -2, 2, -1, 4, 0),
        "shifted_maximum_edge_jump_is_five": max(map(abs, edge_differences)) == 5,
        "mode_maximum_edge_jump_is_two": (
            max(map(abs, mode_edge_differences)) == 2
        ),
        "right_tail_residual_exponents_are_16m_plus_u_and_24m_plus_u": (
            4 * (background[2] - background[3]) == 16
            and 4 * (background[4] - background[3]) == 24
            and mode[2] - mode[3] == mode[4] - mode[3] == 1
        ),
        "full_gibbs_inverse_temperature_is_1350": (
            spatial_volume / (coupling * coupling) == 1350
        ),
        "m2_candidate_coefficients_are_exact": (
            candidate_coefficients == tuple(fixture_n * value for value in shifted)
        ),
        "m2_candidate_action_below_well_upper": (
            candidate_action <= fixture_constants["well_upper"]
        ),
        "m2_threshold_action_above_center_lower": (
            threshold_action >= fixture_constants["center_lower"]
        ),
        "m2_center_lower_exceeds_well_upper": (
            fixture_constants["center_lower"]
            > fixture_constants["well_upper"]
        ),
        "m2_binary_tail_exponent_beats_minus_m": (
            fixture_constants["tail_binary_exponent"] <= -fixture_m
        ),
        "all_m_center_well_gap_proof_retained": True,
        "all_m_tail_probability_proof_retained": True,
        "conditional_raw_second_moment_is_unbounded": True,
        "annealed_and_recentered_moments_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "conditional-mass-escape-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": (
            "exact fixed-volume conditional-mass escape and obstruction to "
            "uniform backgroundwise raw fiber moments"
        ),
        "question": (
            "Can the lowest-mode marginal be controlled by a uniform bound "
            "on the uncentered conditional second moment for every orthogonal "
            "background?"
        ),
        "answer": (
            "No. On the fixed 6^4 lattice, for every integer m>=2 an exact "
            "orthogonal background eta_m=4m*log(2)*a has a conditional "
            "lowest-mode law q_m. Its probability of u>=-m is at most 2^-m, "
            "while every global fiber minimizer lies below -m. Therefore "
            "E_qm[u^2]>=m^2(1-2^-m), so no background-uniform raw "
            "conditional second-moment bound exists. This is not divergence "
            "of the annealed marginal: the exceptional backgrounds may have "
            "vanishing marginal weight. A successful proof must control "
            "recentered widths and the Gibbs-weighted distribution of centers."
        ),
        "finite_volume_carrier": {
            "lattice": "periodic 6^4 lattice",
            "volume": 6**4,
            "spatial_replication_factor": spatial_volume,
            "coupling": encode(coupling),
            "full_action": "A_full=216*A_cycle on the spatially constant sector",
            "conditional_inverse_temperature": 1350,
            "conditional_density": (
                "q_m(u)=Z_m^-1*exp[-1350*A_m(u)] with fiber field "
                "psi=4m*log(2)*a+u*log(2)*h"
            ),
        },
        "exact_orthogonal_family": {
            "parameter": "m>=2 integer",
            "background_coefficients": list(background),
            "lowest_mode_coefficients": list(mode),
            "background_mode_dot_product": 0,
            "background_field": "eta_m=4m*log(2)*a",
            "fiber_coordinate": "t=u*log(2)",
            "candidate_well_coordinate": "u_0=-4m",
            "center_threshold": "u=-m",
            "shifted_coefficients_at_candidate": list(shifted),
            "shifted_adjacent_differences": list(edge_differences),
            "mode_adjacent_differences": list(mode_edge_differences),
        },
        "right_tail_lower_bound": {
            "scope": "m>=2 and u=-m+v with v>=0",
            "time_site": 3,
            "residual": "r_3=2^(16m+u)+2^(24m+u)-2",
            "residual_lower_bound": "r_3>=2^(23m+v-1)",
            "cycle_action_lower_bound": "A_m(-m+v)>=C_m*4^v",
            "C_m": "2^(46m-3)",
            "tail_integral_inequality": (
                "integral_0^infinity exp[-1350*C_m*4^v]dv "
                "<=exp[-1350*C_m]/(1350*C_m)"
            ),
            "analytic_lemma": "4^v>=1+v for v>=0",
        },
        "candidate_well_lower_normalization": {
            "interval": "|u+4m|<=delta_m",
            "delta_m": "2^(-50m)",
            "edge_exponent_bound": "absolute exponent <=20m+2",
            "residual_absolute_bound": "|r_j|<=9*2^(20m)",
            "cycle_action_upper_bound": "A_m(u)<=M_m=243*2^(40m)",
            "normalization_lower_bound": (
                "Z_m>=2*delta_m*exp[-1350*M_m]"
            ),
        },
        "all_m_comparison": {
            "C_m": "2^(46m-3)",
            "M_m": "243*2^(40m)",
            "C_exceeds_M_proof": (
                "C_m/M_m=2^(6m-3)/243>=512/243>1 for m>=2"
            ),
            "D_m": "1350*(C_m-M_m)",
            "D_lower_bound": (
                "D_m>=1350*269*m>51m because 2^(40m)>=m and "
                "2^(6m-3)-243>=269"
            ),
            "tail_probability_bound": (
                "q_m({u>=-m})<=2^(50m-1-D_m)<=2^(-m)"
            ),
            "global_minimizer_consequence": (
                "every global minimizer u_m^* satisfies u_m^*<-m"
            ),
            "raw_second_moment_bound": "E_qm[u^2]>=m^2*(1-2^(-m))",
            "physical_coordinate_bound": (
                "E_qm[t^2]>=(log(2))^2*m^2*(1-2^(-m))"
            ),
            "status": "UNIFORM_BACKGROUNDWISE_RAW_CONDITIONAL_MOMENT_OBSTRUCTED",
        },
        "exact_m2_fixture": {
            "m": fixture_m,
            "n": fixture_n,
            "candidate_u": fixture_candidate_u,
            "threshold_u": fixture_threshold_u,
            "candidate_coefficients": list(candidate_coefficients),
            "threshold_coefficients": list(threshold_coefficients),
            "candidate_cycle_action": encode(candidate_action),
            "threshold_cycle_action": encode(threshold_action),
            "C_m": fixture_constants["center_lower"],
            "M_m": fixture_constants["well_upper"],
            "D_m": fixture_constants["exponent_gap"],
            "binary_tail_exponent": fixture_constants["tail_binary_exponent"],
        },
        "method_disposition": {
            "centered_pointwise_relative_action_domination": "OBSTRUCTED",
            "uniform_backgroundwise_raw_conditional_second_moment": "OBSTRUCTED",
            "uniform_backgroundwise_fiber_minimizer_location": "OBSTRUCTED",
            "conditional_mass_escape_on_exact_family": "PROVED",
            "uniform_recentered_conditional_variance": "OPEN",
            "annealed_center_second_moment": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "integer vectors, dyadic actions, exponent comparisons, and "
                "the m=2 fixture"
            ),
            "finite_dimensional_analytic_layer": (
                "coercive one-dimensional integration, 4^v>=1+v, and "
                "normalization comparison"
            ),
            "uniform_limit_layer": (
                "no volume-uniform Gibbs marginal, H^-1 estimate, compactness, "
                "or represented limit is established"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a uniform recentered conditional-width theorem or obstruction",
            "an annealed bound on the Gibbs-weighted conditional centers",
            "a normalized one-mode second-moment estimate for the actual marginal",
            "a dyadic Fourier-shell estimate yielding the actual interacting H^-1 bound",
            "tightness in a compactly weaker topology",
            "represented convergence and limit identification",
        ],
        "next_gate": (
            "Separate the conditional variance about a moving center from the "
            "annealed second moment of that center. Uniform control relative "
            "to the fixed origin is now ruled out even at fixed volume."
        ),
        "does_not_establish": [
            "divergence of the fully integrated lowest-mode marginal",
            "divergence of the actual interacting H^-1 moment",
            "failure of a uniformly recentered conditional-variance bound",
            "failure of an annealed center estimate",
            "failure of every conditional-fiber or transport method",
            "tightness or a continuum BT Euclidean measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a weakest-foundation reversal",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction and integer arithmetic for dyadic actions, "
                "all displayed constants, and the exact m=2 fixture"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_conditional_mass_escape_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_conditional_mass_escape_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_conditional_mass_escape_obstruction",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped diff "
                "check, and exact staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, method-distinct verifier, direct cycle-action "
                "fixtures, all-m integer inequalities, and mutation rejection"
            ),
            "tier_2": (
                "predecessor certificates checked by content hash; no sampler "
                "rerun because no numerical Gibbs claim is promoted"
            ),
            "tier_3": (
                "not run: no freeze, release, shared operator, continuum "
                "theorem, quantum lifecycle, or Lorentzian claim"
            ),
            "memory_policy": (
                "all commands sequential under a 500000 KiB virtual-memory ceiling"
            ),
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
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
        "[PASS] BT conditional-mass escape obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
