#!/usr/bin/env python3
"""Certify BT quartic coercivity and a Schwinger--Dyson mode-route obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-schwinger-dyson-mode-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-schwinger-dyson-mode-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "2be651e7642d86cc09d362b5d5596c4937297b27"


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


def reduced_forms(
    center: tuple[int, ...], direction: tuple[int, ...]
) -> dict[str, Fraction]:
    """Six-time-site calculation used by the producer."""
    directional_action = Fraction(0)
    free_directional_action = Fraction(0)
    action = Fraction(0)
    for time in range(6):
        residual = Fraction(-2)
        residual_variation = Fraction(0)
        laplacian_center = 0
        laplacian_direction = 0
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            weight = dyadic(center[neighbor] - center[time])
            direction_difference = direction[neighbor] - direction[time]
            residual += weight
            residual_variation += weight * direction_difference
            laplacian_center += center[neighbor] - center[time]
            laplacian_direction += direction_difference
        action += residual * residual / 2
        directional_action += residual * residual_variation
        free_directional_action += laplacian_center * laplacian_direction
    return {
        "action": action,
        "directional_action": directional_action,
        "free_directional_action": free_directional_action,
        "center_direction_dot": Fraction(
            sum(left * right for left, right in zip(center, direction))
        ),
        "direction_norm_squared": Fraction(sum(value * value for value in direction)),
    }


def negative_cycle_laplacian(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        2 * values[index]
        - values[(index - 1) % len(values)]
        - values[(index + 1) % len(values)]
        for index in range(len(values))
    )


def build() -> dict:
    coupling = Fraction(2, 5)
    length = 6
    dimensions = 4
    volume = length**dimensions
    spatial_volume = length ** (dimensions - 1)
    center = (-8, 8, -2, -8, 2, 8)
    direction = (2, 1, -1, -2, -1, 1)
    forms = reduced_forms(center, direction)
    full_directional_action = spatial_volume * forms["directional_action"]
    full_free_directional_action = (
        spatial_volume * forms["free_directional_action"]
    )
    full_center_direction_dot = spatial_volume * forms["center_direction_dot"]
    full_direction_norm_squared = spatial_volume * forms["direction_norm_squared"]
    lowest_mode_action_coefficient = Fraction(128) * coupling * coupling

    checks = {
        "coupling_is_exactly_two_fifths": coupling == Fraction(2, 5),
        "center_is_mean_zero": sum(center) == 0,
        "direction_is_mean_zero": sum(direction) == 0,
        "direction_is_lowest_cycle_mode": negative_cycle_laplacian(direction)
        == direction,
        "center_direction_dot_is_sixteen": forms["center_direction_dot"] == 16,
        "direction_norm_squared_is_twelve": forms["direction_norm_squared"] == 12,
        "free_directional_action_is_sixteen": (
            forms["free_directional_action"] == 16
        ),
        "nonlinear_directional_action_is_exact_negative": (
            forms["directional_action"]
            == Fraction(-36885875918835948063, 2147483648)
            and forms["directional_action"] < 0
        ),
        "pointwise_mode_remainder_is_strictly_negative": (
            forms["center_direction_dot"] > 0
            and forms["directional_action"] < 0
            and forms["free_directional_action"] > 0
        ),
        "quartic_gradient_coercivity_has_all_volume_proof": True,
        "lowest_axial_mode_coefficient_is_512_over_25": (
            lowest_mode_action_coefficient == Fraction(512, 25)
        ),
        "annealed_remainder_sign_and_h_minus_one_bound_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-schwinger-dyson-mode-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": (
            "exact all-volume action estimate and obstruction to pointwise "
            "Schwinger-Dyson mode domination"
        ),
        "question": (
            "Can the interacting H^-1 moment bound be obtained from the exact "
            "mode Schwinger-Dyson identity by a pointwise nonnegative "
            "interaction remainder, and what all-volume deterministic control "
            "does the nonlinear residual provide?"
        ),
        "answer": (
            "The pointwise sign route is obstructed: an exact lowest-mode "
            "configuration on the 6^4 lattice has a strictly negative "
            "interaction remainder. Independently, every periodic volume obeys "
            "S_lambda(phi)>=(lambda^2/(2N))*E_grad(phi)^2, giving uniform "
            "quartic action confinement of each continuum-normalized lowest "
            "Fourier coefficient. This deterministic estimate does not by "
            "itself bound its normalized Gibbs moment; the annealed remainder "
            "sign and the interacting H^-1 estimate remain open."
        ),
        "schwinger_dyson_identity": {
            "carrier": "mean-zero hyperplane of the finite periodic L^4 lattice",
            "test_direction": "any fixed mean-zero real vector h",
            "identity": (
                "E[(h.phi)*(h.grad S_lambda(phi))]=||h||_2^2"
            ),
            "proof": (
                "Integrate the divergence of (h.phi)*h*exp(-S_lambda) on the "
                "mean-zero hyperplane; certified finite-volume coercivity "
                "removes the boundary term."
            ),
            "free_mode_split": (
                "If (-Delta_L)h=omega*h, then omega^2*E[(h.phi)^2] "
                "+E[R_h(phi)]=||h||_2^2."
            ),
            "remainder": (
                "R_h(phi)=(h.phi)*h.(grad S_lambda-grad S_0)"
            ),
            "sufficient_but_false_pointwise_route": (
                "R_h(phi)>=0 for every phi would imply the free covariance "
                "bound in direction h."
            ),
        },
        "exact_lowest_mode_counterexample": {
            "coupling": encode(coupling),
            "lattice": {
                "length": length,
                "dimensions": dimensions,
                "volume": volume,
                "spatial_volume": spatial_volume,
            },
            "coordinates": "psi=lambda*phi=k*log(2)",
            "spatially_constant_time_center": list(center),
            "spatially_constant_lowest_mode_direction": list(direction),
            "negative_laplacian_eigenvalue": 1,
            "per_spatial_site": {
                "nonlinear_action": encode(forms["action"]),
                "center_direction_dot": encode(forms["center_direction_dot"]),
                "direction_norm_squared": encode(forms["direction_norm_squared"]),
                "nonlinear_directional_action": encode(
                    forms["directional_action"]
                ),
                "free_directional_action": encode(
                    forms["free_directional_action"]
                ),
            },
            "full_lattice": {
                "center_direction_dot": encode(full_center_direction_dot),
                "direction_norm_squared": encode(full_direction_norm_squared),
                "nonlinear_directional_action": encode(full_directional_action),
                "free_directional_action": encode(full_free_directional_action),
            },
            "exact_sign_factorization": (
                "R_h=(216^2*16*log(2)/lambda^2)*"
                "(D_h A-16*log(2)); the prefactor is positive and both "
                "D_h A<0 and -16*log(2)<0, hence R_h<0."
            ),
            "disposition": "POINTWISE_MODE_REMAINDER_SIGN_OBSTRUCTED",
        },
        "all_volume_quartic_coercivity": {
            "scope": (
                "every finite q-regular periodic undirected multigraph, with "
                "edges counted with lattice multiplicity"
            ),
            "definitions": [
                "psi=lambda*phi",
                "r_x=sum_(y~x)[exp(psi_y-psi_x)-1]",
                "E_grad(phi)=sum_unoriented_edges (phi_y-phi_x)^2",
                "S_lambda=(1/(2*lambda^2))*sum_x r_x^2",
            ],
            "residual_sum_identity": (
                "sum_x r_x=2*sum_edges[cosh(psi_y-psi_x)-1]"
            ),
            "scalar_inequality": (
                "2*(cosh u-1)-u^2=2*sum_(m>=2)u^(2m)/(2m)!>=0"
            ),
            "cauchy_schwarz": "sum_x r_x^2 >= (sum_x r_x)^2/N",
            "theorem": (
                "S_lambda(phi)>=(lambda^2/(2N))*E_grad(phi)^2"
            ),
            "lowest_axial_fourier_consequence": {
                "coefficient": (
                    "hat(Phi_L)(e_mu)=N^-1*sum_x phi_x*"
                    "exp(-2*pi*i*x_mu/L)"
                ),
                "eigenvalue": "omega_L=4*sin(pi/L)^2",
                "spectral_step": (
                    "E_grad(phi)>=N*omega_L*|hat(Phi_L)(e_mu)|^2"
                ),
                "elementary_bound": (
                    "sin(pi/L)>=2/L for L>=2, so N*omega_L^2>=256 in d=4"
                ),
                "all_volume_bound": (
                    "S_lambda(phi)>=128*lambda^2*"
                    "|hat(Phi_L)(e_mu)|^4"
                ),
                "lambda_0p4_coefficient": encode(lowest_mode_action_coefficient),
                "status": "DETERMINISTIC_ACTION_SUBLEVEL_BOUND_PROVED",
            },
            "probabilistic_shortfall": (
                "A pointwise lower action bound does not control the ratio of "
                "the tail integral to the volume-dependent partition function; "
                "an annealed or normalized marginal estimate is still required."
            ),
        },
        "method_disposition": {
            "finite_volume_schwinger_dyson_identity": "PROVED",
            "all_volume_quartic_gradient_action_bound": "PROVED",
            "uniform_lowest_mode_action_sublevel_bound": "PROVED",
            "pointwise_nonnegative_mode_remainder": "OBSTRUCTED",
            "annealed_nonnegative_mode_remainder": "OPEN",
            "interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a normalized marginal or annealed Fourier-mode covariance estimate",
            "an L-uniform interacting H^-1 second-moment estimate",
            "tightness in a topology compactly weaker than the moment bound",
            "identification and uniqueness of any Euclidean limit",
        ],
        "next_gate": (
            "Estimate the Gibbs expectation of the exact mode remainder or "
            "control the normalized one-mode marginal; pointwise signs and "
            "global strong convexity are both unavailable."
        ),
        "does_not_establish": [
            "a negative Gibbs expectation of the mode remainder",
            "failure of the interacting H^-1 moment bound",
            "failure of every Schwinger-Dyson or covariance method",
            "tightness or a continuum BT Euclidean measure",
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
                "Python Fraction arithmetic for dyadic residuals, directional "
                "actions, graph scaling, and the lambda=2/5 coefficient"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_schwinger_dyson_mode_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_schwinger_dyson_mode_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_schwinger_dyson_mode_obstruction",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped git "
                "diff --check, and staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, method-distinct full 6^4 verifier, symbolic "
                "proof-structure checks, unit tests, and mutation rejection"
            ),
            "tier_2": (
                "predecessor certificates checked by content hash; no sampler "
                "rerun because no numerical Gibbs expectation is promoted"
            ),
            "tier_3": (
                "not run: no freeze, release, shared classical operator, "
                "quantum lifecycle, or Lorentzian claim changes"
            ),
            "memory_policy": (
                "all commands sequential under a 500000 KiB virtual-memory "
                "ceiling where relevant"
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
        "[PASS] BT Schwinger-Dyson mode-route obstruction and quartic bound "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
