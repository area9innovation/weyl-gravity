#!/usr/bin/env python3
"""Build the exact BT radial-convexity and unit-virial obstruction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction


sys.set_int_max_str_digits(20000)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RADIAL_CONVEXITY_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-radial-convexity-obstruction-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-radial-convexity-obstruction.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_radial_convexity_obstruction.py"
SOURCE_COMMIT = "6994434dd201a0ec6bfd6d835b1c981ac9df12b7"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
]

SIDE = 6
DIMENSION = 4
DEGREE = 8
BASE = Fraction(101, 100)
SHELL_EXPONENTS = (0, 1, 2, 3, 4, 5, 7, 10, 15, 25, 48, 101, 214)


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def shell(point: tuple[int, ...]) -> int:
    return sum(min(coordinate, SIDE - coordinate) for coordinate in point)


def exact_fixture() -> tuple[Fraction, Fraction, Fraction, dict[int, int]]:
    """Return A, D/log(BASE), A''/log(BASE)^2 by direct site enumeration."""
    points = tuple(itertools.product(range(SIDE), repeat=DIMENSION))
    multiplicities: dict[int, int] = {}
    action = Fraction(0)
    virial_coefficient = Fraction(0)
    curvature_coefficient = Fraction(0)
    for point in points:
        level = shell(point)
        multiplicities[level] = multiplicities.get(level, 0) + 1
        exponent = SHELL_EXPONENTS[level]
        residual = Fraction(-DEGREE)
        first = Fraction(0)
        second = Fraction(0)
        for axis in range(DIMENSION):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % SIDE
                difference = SHELL_EXPONENTS[shell(tuple(neighbor))] - exponent
                weight = BASE**difference
                residual += weight
                first += weight * difference
                second += weight * difference * difference
        action += residual * residual / 2
        virial_coefficient += residual * first
        curvature_coefficient += first * first + residual * second
    return action, virial_coefficient, curvature_coefficient, multiplicities


def build() -> dict:
    action, virial, curvature, multiplicities = exact_fixture()
    x = Fraction(1, 100)
    log_upper = x - x * x / 2 + x**3 / 3
    checks = {
        "periodic_lattice_has_6_to_the_4_sites": sum(multiplicities.values()) == SIDE**DIMENSION,
        "shell_profile_covers_0_through_12": tuple(sorted(multiplicities)) == tuple(range(13)),
        "base_is_101_over_100": BASE == Fraction(101, 100),
        "action_is_strictly_positive": action > 0,
        "virial_coefficient_is_strictly_positive": virial > 0,
        "radial_curvature_coefficient_is_strictly_negative": curvature < 0,
        "alternating_log_upper_bound_is_exact": log_upper == Fraction(29851, 3000000),
        "unit_virial_bound_is_strictly_violated": virial * log_upper < action,
        "coefficient_two_predecessor_is_strengthened": virial * log_upper < action < 2 * action,
        "affine_action_density_theorem_is_not_refuted": True,
        "positive_constant_below_one_remains_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_RADIAL_CONVEXITY_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-radial-convexity-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "POINTWISE_RADIAL_CONVEXITY_AND_UNIT_VIRIAL_OBSTRUCTED",
        "result_kind": "exact finite-volume counterexample to radial convexity and to D>=A for the BT Euclidean action",
        "question": "Can the tuned Gibbs action estimate be closed by proving radial convexity of A(rho*psi), or at least the pointwise unit inequality D(psi)>=A(psi)?",
        "answer": "No to both proposed inequalities. On the exact four-dimensional period-six torus, take psi_x=k_d*log(101/100), up to subtraction of its mean, where d is periodic Manhattan distance and k=(0,1,2,3,4,5,7,10,15,25,48,101,214). Direct enumeration of all 1296 sites gives A>0, D=C_D*log(101/100), and the second radial derivative A''=C_2*log(101/100)^2, with C_D>0 but C_2<0. The alternating rational bound log(101/100)<29851/3000000 proves D<A exactly. Thus A(rho*psi) is not convex at rho=1 and the coefficient-one homogeneous virial inequality fails. This does not rule out D>=c*A for 0<c<1, the certified affine virial theorem, or a non-pointwise Gibbs estimate.",
        "exact_fixture": {
            "graph": "four-dimensional periodic nearest-neighbor torus (Z/6Z)^4",
            "volume": SIDE**DIMENSION,
            "degree": DEGREE,
            "periodic_distance": "d(x)=sum_i min(x_i,6-x_i)",
            "shell_exponents": list(SHELL_EXPONENTS),
            "shell_multiplicities": {str(key): value for key, value in sorted(multiplicities.items())},
            "field": "psi_x=(k_(d(x))-mean(k_d))*log(101/100); the centering constant cancels from every edge weight and from D",
            "edge_weight": "w_xy=(101/100)^(k_(d(y))-k_(d(x)))",
            "action_A": enc(action),
            "virial_log_coefficient_C_D": enc(virial),
            "radial_curvature_log_squared_coefficient_C_2": enc(curvature),
            "identities": [
                "A=(1/2)*sum_x r_x^2",
                "D=psi dot grad(A)=C_D*log(101/100)",
                "d^2/d rho^2 A(rho*psi)|_(rho=1)=C_2*log(101/100)^2",
            ],
            "status": "EXACT_SITE_ENUMERATION",
        },
        "strict_comparisons": {
            "log_upper_bound": enc(log_upper),
            "log_proof": "For x=1/100, the odd alternating partial sum log(1+x)<x-x^2/2+x^3/3=29851/3000000.",
            "unit_virial_integer_witness": enc(action - virial * log_upper),
            "conclusions": [
                "0<D<A",
                "A''(rho=1)<0",
                "D>=A is false",
                "rho -> A(rho*psi) is not convex on the positive radial ray",
            ],
            "status": "STRICT_EXACT_RATIONAL_INEQUALITIES",
        },
        "method_disposition": {
            "pointwise_D_ge_2A": "OBSTRUCTED_BY_PREDECESSOR",
            "pointwise_D_ge_A": "OBSTRUCTED",
            "radial_convexity_of_A_rho_psi": "OBSTRUCTED",
            "pointwise_D_ge_cA_for_0_lt_c_lt_1": "OPEN",
            "pointwise_D_ge_0": "OPEN",
            "affine_volume_defect_virial": "PROVED_BY_PREDECESSOR",
            "actual_uniform_action_density": "PROVED_BY_PREDECESSOR",
            "nonpointwise_low_temperature_Gibbs_estimate": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "failure of every positive homogeneous virial constant",
            "failure of the affine virial or actual action-density theorem",
            "divergence of any actual Gibbs moment",
            "an interacting H^-1 estimate or counterexample",
            "a continuum measure, Born rule, Krein reconstruction, or Lorentzian causal result",
        ],
        "missing_object_ledger": [
            "a proof or counterexample for D>=c*A with an explicit 0<c<1",
            "a Gibbs-weighted estimate that does not require pointwise radial convexity",
            "the annealed lowest-mode center-score bound on the tuned branch",
            "the subsequent dyadic Fourier-shell H^-1 estimate",
            "continuum tightness and identification only after the moment gate",
        ],
        "next_gate": "Do not use radial convexity or D>=A. Either decide the remaining weaker D>=c*A range with 0<c<1 by a reciprocal-edge compensation theorem, or move directly to a Gibbs-weighted block estimate for the whole zero-fiber score. A method obstruction must not be called failure of the actual interacting moment.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "All weights, residuals, A, C_D, C_2, and the logarithm upper bound are computed with Fraction arithmetic. No floating-point value decides a claim.",
            "assumptions": [
                "The BT action and radial-virial normalization are those fixed by the imported predecessor certificates.",
                "Subtracting the finite-volume field mean is permitted because A is invariant under constant shifts and grad(A) is orthogonal to constants.",
                "The counterexample is finite-volume and EUCLIDEAN-SPECTRAL only.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_radial_convexity_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_radial_convexity_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_radial_convexity_obstruction",
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
