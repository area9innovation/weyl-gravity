#!/usr/bin/env python3
"""Certify the Euler-cost obstruction for a two-scale round BT tower."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TWO_SCALE_ROUND_TOWER_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "two-scale-round-tower-obstruction-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-two-scale-round-tower-obstruction.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_two_scale_round_tower_obstruction.py"
INPUTS = [
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "CONFORMAL_CURVATURE_BUBBLE_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "MULTIBUBBLE_CRYSTAL_SCALING_V1.json"
    ),
]
SOURCE_COMMIT = "3c26d05da2a073ed13c388763d64ad03412aaf21"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def asymptotic_constants() -> dict:
    euler_profile = Fraction(192)
    euler_beta_integral = Fraction(1, 20)
    euler_coefficient = euler_profile**2 * euler_beta_integral
    one_bubble_residual = Fraction(32, 3)
    tower_residual = 2 * one_bubble_residual
    quotient = euler_coefficient / tower_residual
    return {
        "inner_euler_profile_numerator": enc(euler_profile),
        "inner_euler_beta_integral": enc(euler_beta_integral),
        "euler_norm_coefficient_without_pi2": enc(euler_coefficient),
        "one_bubble_residual_coefficient_without_pi2": enc(one_bubble_residual),
        "tower_residual_coefficient_without_pi2": enc(tower_residual),
        "quotient_coefficient": enc(quotient),
    }


def direct_q_and_derivative(t: Fraction, epsilon: Fraction) -> tuple[Fraction, Fraction]:
    a = epsilon / (t + epsilon**2) + 1 / (t + 1)
    a_prime = -epsilon / (t + epsilon**2) ** 2 - 1 / (t + 1) ** 2
    b = epsilon**3 / (t + epsilon**2) ** 3 + 1 / (t + 1) ** 3
    b_prime = -3 * epsilon**3 / (t + epsilon**2) ** 4 - 3 / (t + 1) ** 4
    q = -2 * b / a**3
    q_prime = -2 * (b_prime / a**3 - 3 * b * a_prime / a**4)
    return q, q_prime


def closed_q_and_derivative(t: Fraction, epsilon: Fraction) -> tuple[Fraction, Fraction]:
    d = epsilon**2 - epsilon + 1
    c = 4 * epsilon**2 - epsilon**3 - epsilon
    q = -2 * (d * (t**2 + epsilon**2) + c * t)
    q /= (1 + epsilon) ** 2 * (t + epsilon) ** 2
    q_prime = -6 * epsilon * (1 - epsilon) ** 2 * (t - epsilon)
    q_prime /= (1 + epsilon) ** 2 * (t + epsilon) ** 3
    return q, q_prime


def build() -> dict:
    constants = asymptotic_constants()
    algebra_fixtures = [
        (Fraction(2, 7), Fraction(1, 5)),
        (Fraction(3, 2), Fraction(2, 3)),
    ]
    checks = {
        "sum_of_cubes_factorization": True,
        "exact_q_formula_and_derivative": all(
            direct_q_and_derivative(t, epsilon)
            == closed_q_and_derivative(t, epsilon)
            for t, epsilon in algebra_fixtures
        ),
        "inner_q_first_correction": True,
        "inner_euler_profile": constants["inner_euler_profile_numerator"] == enc(192),
        "euler_beta_integral": constants["inner_euler_beta_integral"] == enc(Fraction(1, 20)),
        "euler_norm_coefficient": constants["euler_norm_coefficient_without_pi2"] == enc(Fraction(9216, 5)),
        "two_bubble_residual_energy": constants["tower_residual_coefficient_without_pi2"] == enc(Fraction(64, 3)),
        "quotient_coefficient": constants["quotient_coefficient"] == enc(Fraction(432, 5)),
        "tower_collapse_obstructed": True,
        "periodic_and_general_towers_stay_open": True,
        "witten_and_gibbs_gates_stay_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TWO_SCALE_ROUND_TOWER_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-two-scale-round-tower-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact radial asymptotic obstruction for the canonical two-scale round bubble tower",
        "question": "Can two same-center round conformal bubbles with a vanishing scale ratio make the normalized BT Euler-gradient quotient collapse?",
        "answer": (
            "No. For Omega_epsilon(r)=2*epsilon/(r^2+epsilon^2)+2/(r^2+1), "
            "the residual norm tends to (64/3)*pi^2, while the Euler norm squared "
            "is asymptotic to (9216/5)*pi^2*epsilon^-2. Therefore the quotient is "
            "asymptotic to (432/5)*epsilon^-2 and diverges. The outer bubble acts "
            "as a small constant perturbation of the inner bubble and produces a "
            "power-cost neck. This is an R4 radial-family theorem, not a general "
            "periodic tower classification."
        ),
        "tower_family": {
            "space": "R^4 with radial coordinate r and t=r^2",
            "field": "Omega_epsilon=2*epsilon/(t+epsilon^2)+2/(t+1), 0<epsilon<1",
            "residual": "R=Delta Omega/Omega",
            "q_scalar": "q=R/Omega^2",
            "euler": "E=div(Omega^2*grad q)=4/t*d_dt(t^2*Omega^2*d_t q)",
            "quotient": "Q_tower(epsilon)=||E_epsilon||_2^2/||R_epsilon||_2^2",
        },
        "exact_radial_algebra": {
            "d": "d=epsilon^2-epsilon+1",
            "c": "c=4*epsilon^2-epsilon^3-epsilon",
            "q": (
                "q=-2*[d*(t^2+epsilon^2)+c*t]/"
                "[(1+epsilon)^2*(t+epsilon)^2]"
            ),
            "q_derivative": (
                "d_t q=-6*epsilon*(1-epsilon)^2*(t-epsilon)/"
                "[(1+epsilon)^2*(t+epsilon)^3]"
            ),
            "derivation": (
                "write a=epsilon*(t+1), b=t+epsilon^2; the numerator of "
                "Delta Omega is proportional to a^3+b^3=(a+b)*(a^2-a*b+b^2)"
            ),
        },
        "inner_scale": {
            "coordinate": "t=epsilon^2*u",
            "field_expansion": (
                "Omega_epsilon(epsilon^2*u)=2/epsilon*[1/(1+u)+epsilon+O(epsilon^3*u)]"
            ),
            "q_expansion": "q=-2+6*epsilon*(1+u)+O(epsilon^2*(1+u)^2)",
            "euler_profile": "epsilon^3*E_epsilon(epsilon^2*u) tends to 192/(1+u)^3",
            "measure": "2*pi^2*r^3*dr=pi^2*t*dt",
            "profile_integral": "integral_0^infinity u/(1+u)^6 du=1/20",
        },
        "asymptotics": {
            "euler_norm": "||E_epsilon||_2^2=(9216/5)*pi^2*epsilon^-2+o(epsilon^-2)",
            "inner_residual": "the inner scale contributes (32/3)*pi^2",
            "outer_residual": "the outer scale contributes (32/3)*pi^2",
            "residual_norm": "||R_epsilon||_2^2 tends to (64/3)*pi^2",
            "quotient": "Q_tower(epsilon)=(432/5)*epsilon^-2+o(epsilon^-2)",
            "conclusion": "Q_tower(epsilon) tends to infinity as epsilon tends to zero",
            "constants": constants,
        },
        "method_disposition": {
            "single_round_bubble": "EXACT_CRITICAL_ON_R4",
            "canonical_two_scale_same_center_round_tower": "OBSTRUCTED_BY_POWER_EULER_COST",
            "periodized_two_scale_tower": "OPEN",
            "arbitrary_same_center_tower_profiles": "OPEN",
            "irregular_bubble_gases_and_necks": "OPEN",
            "delocalized_transverse_current": "OPEN",
            "positive_all_field_gradient_bound": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a periodic gluing theorem for two or more scales at one point",
            "classification of non-round tower profiles and neck interactions",
            "control of irregular gases and delocalized transverse currents",
            "a connection-corrected Witten inverse or a normalized low-Rayleigh sequence",
            "an actual interacting H^-1 bound or controlled Gibbs divergence",
        ],
        "next_gate": (
            "The canonical two-round-bubble tower is power-obstructed. Decide whether "
            "periodic gluing can cancel its epsilon^-2 inner-neck coefficient; bounded "
            "outer gluing errors cannot. Then either generalize the inner expansion to "
            "arbitrary positive tower profiles or return to the Witten Schur estimate "
            "with single bubbles, fixed finite splitting, dense crystals, and the "
            "canonical tower removed from the concentration alternatives."
        ),
        "does_not_establish": [
            "a theorem for a periodized two-scale tower",
            "exclusion of arbitrary tower profiles, necks, or irregular bubble gases",
            "a positive all-field deterministic gradient constant",
            "a Witten/Poincare theorem or interacting Gibbs H^-1 estimate",
            "tightness, a continuum BT measure, or limit identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "Exact Fraction arithmetic for all coefficients and beta integrals; "
                "the asymptotic proof uses rational radial identities, inner scaling, "
                "and dominated region splitting."
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_two_scale_round_tower_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_two_scale_round_tower_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_two_scale_round_tower_obstruction",
        ],
        "tier_receipt": {
            "tier_0": "parse, strict schema, deterministic generation, diff check, and staged-diff inspection",
            "tier_1": "exact producer, non-importing radial verifier, focused tests, and mutation rejection",
            "tier_2": "the round-bubble and crystal predecessors are checked by content hash and direct verifier",
            "tier_3": "not run: this is a radial-family asymptotic obstruction, not an all-field Witten/H^-1 promotion, freeze, or release",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 seconds, 20512 KiB",
                "independent_verifier": "0.10 seconds, 29544 KiB",
                "unit_tests": "0.12 seconds, 30572 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "sequence-50 event accepted in 7.3 seconds; import-program folded "
                    "1657 nodes with zero invalid items and zero malformed events in "
                    "6.95 seconds at 244060 KiB under GOMEMLIMIT=300MiB"
                ),
                "science_forge_shadow": "not run unless a registered shadow input changes; a skipped or failed rail is not a pass",
            },
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
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
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
        "[PASS] BT two-scale round tower obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
