#!/usr/bin/env python3
"""Independent verifier for the BT conformal-curvature bubble gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "CONFORMAL_CURVATURE_BUBBLE_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-conformal-curvature-bubble-gate-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def radial_laplacian(
    first_derivative: Fraction,
    second_derivative: Fraction,
    t: Fraction,
    rho: Fraction,
) -> Fraction:
    """Laplacian of f(t), t=1+|x|^2/rho^2, in four dimensions."""
    return (
        4 * (t - 1) * second_derivative + 8 * first_derivative
    ) / rho**2


def reconstruct_floor_point(
    rho: Fraction, floor: Fraction, t: Fraction
) -> dict[str, Fraction]:
    """Reconstruct R, q and E directly from radial differentiation."""
    epsilon = floor * rho
    omega = floor + 1 / (rho * t)
    omega_prime = -1 / (rho * t**2)
    omega_second = 2 / (rho * t**3)
    delta_omega = radial_laplacian(omega_prime, omega_second, t, rho)
    residual = delta_omega / omega

    q = residual / omega**2
    q_prime = 24 * epsilon / (1 + epsilon * t) ** 4
    q_second = -96 * epsilon**2 / (1 + epsilon * t) ** 5
    weight = omega**2
    weight_prime = 2 * omega * omega_prime
    divergence = (
        4 * (t - 1) * weight * q_second
        + (8 * weight + 4 * (t - 1) * weight_prime) * q_prime
    ) / rho**2
    return {
        "epsilon": epsilon,
        "omega": omega,
        "delta_omega": delta_omega,
        "residual": residual,
        "q": q,
        "euler_gradient": divergence,
    }


def reconstruct_round_bubble(rho: Fraction, t: Fraction) -> dict[str, Fraction]:
    omega = 2 / (rho * t)
    first = -2 / (rho * t**2)
    second = 4 / (rho * t**3)
    delta = radial_laplacian(first, second, t, rho)
    residual = delta / omega
    scalar = -6 * residual / omega**2
    return {
        "omega": omega,
        "delta": delta,
        "minus_two_omega_cubed": -2 * omega**3,
        "residual": residual,
        "minus_two_omega_squared": -2 * omega**2,
        "scalar": scalar,
    }


def beta_tail_independent(moment: int) -> Fraction:
    """Integrate t^(1-moment)-t^(-moment) term by term."""
    return Fraction(1, moment - 2) - Fraction(1, moment - 1)


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    recorded = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["provenance_hashes_current"] = len(recorded) == 2 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )

    round_rows = [
        reconstruct_round_bubble(Fraction(2), Fraction(3)),
        reconstruct_round_bubble(Fraction(5, 3), Fraction(7, 2)),
    ]
    checks["round_bubble_radial_calculus"] = all(
        row["delta"] == row["minus_two_omega_cubed"]
        and row["residual"] == row["minus_two_omega_squared"]
        and row["scalar"] == 12
        for row in round_rows
    )
    checks["round_bubble_norm_and_action"] = (
        64 * beta_tail_independent(4) == Fraction(32, 3)
        and 32 * beta_tail_independent(4) == Fraction(16, 3)
        and certificate["round_four_sphere_bubble"]["action"]
        == "A[Omega_rho]=(16/3)*pi^2, independent of rho"
    )

    fixture = certificate["positive_floor_bubble"]["exact_point_fixture"]
    rebuilt = reconstruct_floor_point(
        decode(fixture["rho"]),
        decode(fixture["floor_a"]),
        decode(fixture["t_equals_1_plus_radius_squared_over_rho_squared"]),
    )
    checks["floor_fixture_reconstructed"] = (
        rebuilt["epsilon"] == decode(fixture["epsilon_equals_a_rho"])
        and rebuilt["omega"] == decode(fixture["omega"])
        and rebuilt["residual"] == decode(fixture["residual_R"])
        and rebuilt["q"]
        == decode(fixture["weighted_scalar_q_equals_R_over_omega_squared"])
        and rebuilt["euler_gradient"] == decode(fixture["euler_gradient_E"])
    )
    second_fixture = reconstruct_floor_point(
        Fraction(3, 2), Fraction(2, 5), Fraction(7, 3)
    )
    epsilon = Fraction(3, 5)
    t = Fraction(7, 3)
    rho = Fraction(3, 2)
    closed_e = (
        192
        * epsilon
        * (1 + 2 * epsilon * t - epsilon * t**2)
        / (rho**4 * t**3 * (1 + epsilon * t) ** 3)
    )
    checks["floor_formula_second_point"] = (
        second_fixture["residual"]
        == -8 / (rho**2 * t**2 * (1 + epsilon * t))
        and second_fixture["q"] == -8 / (1 + epsilon * t) ** 3
        and second_fixture["euler_gradient"] == closed_e
    )

    residual_limit = 64 * beta_tail_independent(4)
    gradient_scaled_limit = 192**2 * beta_tail_independent(6)
    quotient = gradient_scaled_limit / residual_limit
    checks["independent_asymptotic_constants"] = (
        residual_limit == Fraction(32, 3)
        and gradient_scaled_limit == Fraction(9216, 5)
        and quotient == Fraction(864, 5)
        and quotient / 16 == Fraction(54, 5)
    )
    checks["asymptotic_limit_bound_recorded"] = (
        "bounded by 16/t^3"
        in certificate["positive_floor_bubble"]["limit_justification"]
        and "(8/3)*epsilon^2"
        in certificate["positive_floor_bubble"]["limit_justification"]
    )
    identity = certificate["four_dimensional_conformal_identity"]
    checks["conformal_identity_chain"] = (
        identity["scalar_curvature"]
        == "Scal_g=-6*Omega^(-3)*Delta Omega=-6*Omega^(-2)*R"
        and identity["volume_form"] == "dvol_g=Omega^4 dx"
        and identity["identity"]
        == "integral Scal_g^2 dvol_g=36*integral R^2 dx=72*A"
        and "not the Weyl-tensor-squared" in identity["interpretation"]
    )
    gate = certificate["torus_scaling_gate"]
    checks["periodic_gate_fail_closed"] = (
        gate["status"] == "OPEN"
        and gate["formal_normalized_ratio"] == "54/(5*pi^4)"
        and "not a certified torus quotient" in gate["decisive_caveat"]
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["continuum_conformal_curvature_identification"] == "PROVED"
        and disposition["noncompact_exact_critical_bubble"] == "PROVED"
        and disposition["periodic_torus_normalized_low_gradient_sequence"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["continuum_reconstruction"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a periodic finite-volume critical point or normalized low-gradient sequence",
        "failure of a positive volume-uniform torus gradient constant",
        "a Poincare inequality or Witten one-form coercivity theorem or obstruction",
        "an interacting residual, field, or H^-1 Gibbs moment estimate",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    receipt = certificate["tier_receipt"]
    checks["receipt_boundaries"] = (
        receipt["elapsed_seconds"]
        == {
            "producer_check": "0.05",
            "independent_verifier": "0.14",
            "unit_tests": "0.17",
        }
        and "REFUSED" in receipt["repository_audits"]["planning_conformance"]
        and "NOT PASSED"
        in receipt["repository_audits"]["science_forge_shadow"]
    )
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
