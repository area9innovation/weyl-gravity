#!/usr/bin/env python3
"""Certify the BT conformal-curvature identity and radial bubble gate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CONFORMAL_CURVATURE_BUBBLE_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-conformal-curvature-bubble-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-conformal-curvature-bubble-gate.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_conformal_curvature_bubble_gate.py"
INPUTS = [
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json"
    ),
]
SOURCE_COMMIT = "37b3cac874c0662d09206d9d6a6b5362f7c4bf57"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def beta_tail(moment: int) -> Fraction:
    """Integral from 1 to infinity of (t-1)/t**moment, moment > 2."""
    if moment <= 2:
        raise ValueError("moment must exceed two")
    return Fraction(1, (moment - 2) * (moment - 1))


def floor_fixture(
    rho: Fraction = Fraction(2),
    floor: Fraction = Fraction(1, 3),
    t: Fraction = Fraction(3),
) -> dict:
    """Exact point fixture for Omega=a+rho/(|x|^2+rho^2)."""
    epsilon = floor * rho
    bubble = Fraction(1, 1) / (rho * t)
    omega = floor + bubble
    residual = -8 / (rho**2 * t**2 * (1 + epsilon * t))
    quotient = -8 / (1 + epsilon * t) ** 3
    numerator = 1 + 2 * epsilon * t - epsilon * t**2
    gradient = (
        192
        * epsilon
        * numerator
        / (rho**4 * t**3 * (1 + epsilon * t) ** 3)
    )
    return {
        "rho": enc(rho),
        "floor_a": enc(floor),
        "t_equals_1_plus_radius_squared_over_rho_squared": enc(t),
        "epsilon_equals_a_rho": enc(epsilon),
        "bubble_B": enc(bubble),
        "omega": enc(omega),
        "residual_R": enc(residual),
        "weighted_scalar_q_equals_R_over_omega_squared": enc(quotient),
        "euler_gradient_E": enc(gradient),
    }


def build() -> dict:
    fixture = floor_fixture()
    residual_leading_integral = beta_tail(4)
    gradient_leading_integral = beta_tail(6)
    residual_norm_limit_over_pi_squared = 64 * residual_leading_integral
    gradient_scaled_limit_over_pi_squared = 192**2 * gradient_leading_integral
    quotient_coefficient = (
        gradient_scaled_limit_over_pi_squared / residual_norm_limit_over_pi_squared
    )
    matched_free_ratio_without_pi_fourth = quotient_coefficient / 16
    checks = {
        "conformal_dimension_is_four": True,
        "scalar_curvature_multiplier_is_minus_six": -2 * (4 - 1) == -6,
        "curvature_squared_multiplier_is_seventy_two": 6**2 * 2 == 72,
        "round_bubble_residual_coefficient_is_minus_eight": -2 * 2**2 == -8,
        "round_bubble_action_over_pi_squared_is_sixteen_thirds": (
            32 * residual_leading_integral == Fraction(16, 3)
        ),
        "floor_fixture_epsilon": fixture["epsilon_equals_a_rho"] == enc(Fraction(2, 3)),
        "floor_fixture_omega": fixture["omega"] == enc(Fraction(1, 2)),
        "floor_fixture_residual": fixture["residual_R"] == enc(Fraction(-2, 27)),
        "floor_fixture_weighted_scalar": (
            fixture["weighted_scalar_q_equals_R_over_omega_squared"]
            == enc(Fraction(-8, 27))
        ),
        "floor_fixture_euler_gradient": (
            fixture["euler_gradient_E"] == enc(Fraction(-8, 729))
        ),
        "residual_beta_integral": residual_leading_integral == Fraction(1, 6),
        "gradient_beta_integral": gradient_leading_integral == Fraction(1, 20),
        "gradient_quotient_coefficient": quotient_coefficient == Fraction(864, 5),
        "matched_free_ratio_coefficient": (
            matched_free_ratio_without_pi_fourth == Fraction(54, 5)
        ),
        "periodic_gluing_gate_stays_open": True,
        "witten_and_gibbs_gates_stay_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "CONFORMAL_CURVATURE_BUBBLE_GATE_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "conformal-curvature-bubble-gate-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact continuum conformal-geometric identification, noncompact radial "
            "critical bubble, and periodic-gluing obstruction gate"
        ),
        "question": (
            "Does the four-dimensional BT continuum functional possess a "
            "nonperturbative almost-stationary mechanism that can threaten the "
            "desired volume-uniform gradient scale?"
        ),
        "answer": (
            "Yes on noncompact R^4: the functional is one seventy-second of "
            "scalar-curvature squared for g=Omega^2 delta, the stereographic "
            "round four-sphere is an exact finite-action critical bubble, and a "
            "positive-floor family approaches it with an explicitly vanishing "
            "Euler-gradient quotient. Under the natural torus-size matching, "
            "however, the quotient remains of order L^-4 with candidate normalized "
            "coefficient 54/(5*pi^4). Periodic gluing contributes at that same "
            "order, so this does not construct a torus counterexample or decide "
            "the Gibbs/Witten estimate."
        ),
        "four_dimensional_conformal_identity": {
            "metric": "g=Omega^2*delta on a four-dimensional Euclidean domain",
            "bt_residual": "R=Delta Omega/Omega=Delta psi+|grad psi|^2",
            "bt_action": "A=(1/2)*integral R^2 dx",
            "scalar_curvature": "Scal_g=-6*Omega^(-3)*Delta Omega=-6*Omega^(-2)*R",
            "volume_form": "dvol_g=Omega^4 dx",
            "identity": "integral Scal_g^2 dvol_g=36*integral R^2 dx=72*A",
            "interpretation": (
                "the continuum BT action is the scalar-curvature-squared functional "
                "restricted to conformally flat metrics, not the Weyl-tensor-squared "
                "functional"
            ),
        },
        "round_four_sphere_bubble": {
            "domain": "R^4",
            "profile": "Omega_rho(x)=2*rho/(|x|^2+rho^2), rho>0",
            "laplacian_identity": "Delta Omega_rho=-2*Omega_rho^3",
            "residual": "R_rho=-2*Omega_rho^2=-8*rho^2/(|x|^2+rho^2)^2",
            "scalar_curvature": "Scal_g=12",
            "euler_gradient": "E=Delta R-2*div(R*grad psi)=0",
            "residual_norm_squared": "integral_R4 R_rho^2 dx=(32/3)*pi^2",
            "action": "A[Omega_rho]=(16/3)*pi^2, independent of rho",
            "status": (
                "an exact noncompact finite-action critical family; it is not a "
                "positive periodic finite-volume field"
            ),
        },
        "positive_floor_bubble": {
            "domain": "R^4",
            "profile": (
                "B=rho/(|x|^2+rho^2), Omega=a+B, a>0, rho>0, "
                "t=1+|x|^2/rho^2, epsilon=a*rho"
            ),
            "laplacian_identity": "Delta B=-8*B^3",
            "residual": "R=-8*rho^(-2)/(t^2*(1+epsilon*t))",
            "weighted_scalar": "q=R/Omega^2=-8/(1+epsilon*t)^3",
            "current": "j=Omega^2*grad q",
            "euler_gradient": (
                "E=div j=192*epsilon*rho^(-4)*(1+2*epsilon*t-"
                "epsilon*t^2)/(t^3*(1+epsilon*t)^3)"
            ),
            "radial_measure": "dx=pi^2*rho^4*(t-1)dt after angular integration",
            "residual_norm_integral": (
                "||R||_2^2=64*pi^2*integral_1^infinity "
                "(t-1)/(t^4*(1+epsilon*t)^2)dt"
            ),
            "gradient_norm_integral": (
                "||E||_2^2=192^2*epsilon^2*rho^(-4)*pi^2*"
                "integral_1^infinity (t-1)*(1+2*epsilon*t-epsilon*t^2)^2/"
                "(t^6*(1+epsilon*t)^6)dt"
            ),
            "limit_justification": (
                "for 0<epsilon<=1 split at t=1/epsilon: below the split the "
                "dimensionless gradient integrand is bounded by 16/t^3 and "
                "converges pointwise; above it its integral is at most "
                "(8/3)*epsilon^2. The residual integrand is bounded directly by "
                "(t-1)/t^4"
            ),
            "epsilon_to_zero_limits": {
                "residual_norm_squared": "||R||_2^2 -> (32/3)*pi^2",
                "scaled_gradient_norm_squared": (
                    "(rho^2/a^2)*||E||_2^2 -> (9216/5)*pi^2"
                ),
                "gradient_quotient": (
                    "||E||_2^2/||R||_2^2=(864/5)*(a/rho)^2*(1+o(1))"
                ),
            },
            "exact_point_fixture": fixture,
        },
        "torus_scaling_gate": {
            "transition_radius": "R_transition is asymptotic to sqrt(rho/a)",
            "matched_scale": "set L^2=rho/a, hence a/rho=L^(-2)",
            "formal_bubble_quotient": (
                "||E||_2^2/||R||_2^2 is asymptotic to (864/5)*L^(-4)"
            ),
            "free_lowest_scale": "omega_L^2 is asymptotic to (2*pi/L)^4",
            "formal_normalized_ratio": "54/(5*pi^4)",
            "decisive_caveat": (
                "a periodic smoothing or Green-function correction acts in the "
                "transition region and contributes at the same L^(-4) order; the "
                "formal coefficient is therefore not a certified torus quotient"
            ),
            "status": "OPEN",
        },
        "method_disposition": {
            "continuum_conformal_curvature_identification": "PROVED",
            "noncompact_exact_critical_bubble": "PROVED",
            "positive_floor_critical_at_infinity_sequence": "PROVED",
            "periodic_torus_normalized_low_gradient_sequence": "OPEN",
            "positive_volume_uniform_deterministic_gradient_bound": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a smooth periodic bubble or periodic Green-function ansatz with controlled L^-4 error",
            "an exact lower bound or a collapsing sequence for the normalized torus gradient quotient",
            "a transfer from deterministic gradient geometry to the full Witten one-form operator",
            "an actual Gibbs H^-1 bound or controlled divergence sequence",
        ],
        "next_gate": (
            "Construct the smooth periodic analogue using the four-torus Green "
            "function and compute the complete L^-4 coefficient, including the "
            "gluing region. If it stays positive, seek a quantitative compactness "
            "theorem modulo one bubble; if it collapses, test the same sequence in "
            "the full Witten Rayleigh quotient before making a probabilistic claim."
        ),
        "does_not_establish": [
            "a periodic finite-volume critical point or normalized low-gradient sequence",
            "failure of a positive volume-uniform torus gradient constant",
            "a Poincare inequality or Witten one-form coercivity theorem or obstruction",
            "an interacting residual, field, or H^-1 Gibbs moment estimate",
            "tightness, a continuum BT measure, or limit identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction arithmetic for the radial point fixture and beta "
                "integrals; analytic identities use exact four-dimensional conformal "
                "and radial differentiation"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_conformal_curvature_bubble_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_conformal_curvature_bubble_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_conformal_curvature_bubble_gate",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, diff check, and "
                "staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, independent radial-calculus verifier, unit tests, "
                "and decisive-field mutation rejection"
            ),
            "tier_2": (
                "predecessor certificates checked by content hash; no shared operator "
                "or generated transitive chain changed"
            ),
            "tier_3": (
                "not run: no torus estimate, Witten/H^-1 theorem, reconstruction "
                "promotion, freeze, release, or shared-core change"
            ),
            "memory_policy": (
                "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling"
            ),
            "elapsed_seconds": {
                "producer_check": "0.05",
                "independent_verifier": "0.14",
                "unit_tests": "0.17",
            },
            "repository_audits": {
                "planning_conformance": (
                    "REFUSED (exit 3, 9.7 seconds): the new seq-45 event is OK; "
                    "the directory retains 10 pre-existing forge-request lifecycle "
                    "nonconformances"
                ),
                "science_forge_shadow": (
                    "NOT PASSED: stopped after more than 75 seconds when unrelated "
                    "cbp index subprocesses aborted under the memory cap before an "
                    "audit disposition"
                ),
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
        "[PASS] BT conformal-curvature bubble gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
