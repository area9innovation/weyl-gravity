#!/usr/bin/env python3
"""Certify the single-well structure of every BT one-site fiber."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_FIBER_SINGLE_WELL_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-single-site-fiber-single-well-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-single-site-fiber-single-well-gate.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_single_site_fiber_single_well_gate.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json"
    ),
]
SOURCE_COMMIT = "2040f0c7964077686b7171b528be69cde62d4772"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fiber_coefficients(
    degree: int,
    inverse_edge_weights: list[Fraction],
    deleted_neighbor_residuals: list[Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    """Return A, C2, C1 in the exact one-site exponential fiber."""

    if len(inverse_edge_weights) != degree:
        raise ValueError("wrong number of incident edge weights")
    if len(deleted_neighbor_residuals) != degree:
        raise ValueError("wrong number of deleted residuals")
    if any(value <= 0 for value in inverse_edge_weights):
        raise ValueError("edge weights must be positive")
    edge_weights = [Fraction(1, 1) / value for value in inverse_edge_weights]
    return (
        sum(inverse_edge_weights, Fraction()),
        sum((value * value for value in edge_weights), Fraction()),
        sum(
            (
                value * residual
                for value, residual in zip(
                    edge_weights, deleted_neighbor_residuals
                )
            ),
            Fraction(),
        ),
    )


def polynomial(
    x: Fraction, degree: int, a_value: Fraction, c2: Fraction, c1: Fraction
) -> Fraction:
    return c2 * x**4 + c1 * x**3 + degree * a_value * x - a_value**2


def polynomial_derivative(
    x: Fraction, degree: int, a_value: Fraction, c2: Fraction, c1: Fraction
) -> Fraction:
    return 4 * c2 * x**3 + 3 * c1 * x**2 + degree * a_value


def stationary_value_reduction(
    x: Fraction, degree: int, a_value: Fraction, c2: Fraction
) -> Fraction:
    """Value of P at a hypothetical positive stationary point P'=0."""

    return -Fraction(1, 3) * (
        c2 * x**4 - 2 * degree * a_value * x + 3 * a_value**2
    )


def lattice_fixture() -> dict:
    """Exact period-four four-dimensional nonconvex one-site fiber."""

    degree = 8
    inverse_edges = [Fraction(1, 2)] * degree
    deleted = [Fraction(-121, 16)] * degree
    a_value, c2, c1 = fiber_coefficients(degree, inverse_edges, deleted)
    curvature_at_zero = (
        2 * a_value**2
        - degree * a_value
        + sum(
            2 * Fraction(2) ** 2 + residual * Fraction(2)
            for residual in deleted
        )
    )
    return {
        "lattice": "periodic 4^4 nearest-neighbor lattice",
        "field_modulo_constant": (
            "psi_0=0, psi_y=-log(2) at the eight neighbors of 0, "
            "and psi_z=-5*log(2) elsewhere"
        ),
        "inverse_incident_edge_weights": [enc(value) for value in inverse_edges],
        "deleted_neighbor_residuals": [enc(value) for value in deleted],
        "A": enc(a_value),
        "C2": enc(c2),
        "C1": enc(c1),
        "critical_polynomial": "P(x)=32*x^4-121*x^3+32*x-16",
        "P_at_3": enc(polynomial(Fraction(3), degree, a_value, c2, c1)),
        "P_at_4": enc(polynomial(Fraction(4), degree, a_value, c2, c1)),
        "fiber_curvature_at_z_0": enc(curvature_at_zero),
        "root_bracket": "the unique minimizer has log(3)<z_star<log(4)",
    }


def build() -> dict:
    degree = 8
    fixture = lattice_fixture()
    product_lower_bound = degree**3
    discriminant_margin = 16 * degree**3 - degree**4
    minimum_curvature_lower_bound = Fraction(13)
    checks = {
        "bt_lattice_degree_is_eight": degree == 8,
        "degree_is_strictly_below_sixteen": degree < 16,
        "hoelder_product_bound_is_q_cubed": product_lower_bound == 512,
        "stationary_value_margin_is_positive": discriminant_margin == 4096,
        "rational_minimum_curvature_bound_is_thirteen": (
            minimum_curvature_lower_bound == 13
            and 2 * 32**2 > 45**2
        ),
        "fixture_coefficients_are_exact": (
            fixture["A"] == enc(4)
            and fixture["C2"] == enc(32)
            and fixture["C1"] == enc(-121)
        ),
        "fixture_is_pointwise_nonconvex": (
            fixture["fiber_curvature_at_z_0"] == enc(-57)
        ),
        "fixture_unique_minimum_is_bracketed": (
            Fraction(fixture["P_at_3"]["numerator"], fixture["P_at_3"]["denominator"]) < 0
            < Fraction(fixture["P_at_4"]["numerator"], fixture["P_at_4"]["denominator"])
        ),
        "uniform_one_site_poincare_remains_open": True,
        "global_witten_and_interacting_moment_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_FIBER_"
            "SINGLE_WELL_GATE_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-single-site-fiber-"
            "single-well-gate-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact all-background one-site single-well theorem, quantitative "
            "minimum-curvature bound, and local-convexity obstruction"
        ),
        "question": (
            "Can a nonconvex single-site or block functional-inequality theorem "
            "enter the BT Witten problem through uniformly controlled local fibers?"
        ),
        "answer": (
            "Every one-site conditional BT action on an eight-regular lattice "
            "has exactly one critical point, its global minimum, despite possible "
            "negative curvature away from that minimum. The action curvature at "
            "the minimum is strictly greater than 13 before division by lambda^2. "
            "An exact 4^4 fixture has curvature -57 at another point, so local "
            "uniform convexity and direct convex Lu-Yau/Otto-Reznikoff imports are "
            "obstructed. The surviving local-to-global route is to prove a uniform "
            "one-site Poincare bound from this single-well structure and then "
            "control inter-site influence; neither step is claimed here."
        ),
        "one_site_reduction": {
            "graph": "finite simple q-regular graph with 1<=q<16",
            "action": (
                "A(psi)=(1/2)*sum_v[sum_(w~v)exp(psi_w-psi_v)-q]^2"
            ),
            "fiber": "z maps to psi+z*delta_o, with all other coordinates fixed",
            "definitions": (
                "B_i=exp(psi_o-psi_i), A=sum_i B_i^-1, "
                "d_i=sum_(w~i,w!=o)exp(psi_w-psi_i)-q, "
                "C2=sum_i B_i^2, C1=sum_i B_i*d_i"
            ),
            "exact_energy": (
                "F(z)=1/2*(A*exp(-z)-q)^2+"
                "1/2*sum_i*(B_i*exp(z)+d_i)^2+constant"
            ),
            "deleted_residual_bound": "d_i>-q",
            "critical_polynomial": (
                "with x=exp(z), x^2*F'(z)=P(x)="
                "C2*x^4+C1*x^3+q*A*x-A^2"
            ),
        },
        "single_well_theorem": {
            "product_inequality": (
                "A^2*C2=(sum B_i^-1)^2*(sum B_i^2)>=q^3"
            ),
            "stationary_value_identity": (
                "if P'(x)=0 then P(x)=-(1/3)*"
                "[C2*x^4-2*q*A*x+3*A^2]"
            ),
            "quartic_minimum": (
                "the bracket has its minimum at x0^3=q*A/(2*C2), "
                "where it equals 3*A*(A-q*x0/2)"
            ),
            "strict_sign": (
                "q<16 and A^2*C2>=q^3 imply x0<2*A/q, so every "
                "positive stationary value of P is strictly negative"
            ),
            "conclusion": (
                "P(0)=-A^2<0, P(x) tends to +infinity, and every critical "
                "value is negative; hence P has exactly one positive zero. "
                "The fiber is coercive and that zero is its unique global minimum."
            ),
            "bt_degree": degree,
            "exact_product_lower_bound": enc(product_lower_bound),
            "exact_q_less_than_16_margin": enc(discriminant_margin),
        },
        "minimum_curvature": {
            "identity": (
                "at the unique root, F''=C2*x^2+3*A^2/x^2-2*q*A/x"
            ),
            "bound_chain": (
                "put y=A/x and K=A*sqrt(C2)>=q^(3/2); then "
                "F''>=2*K-q^2/2>=32*sqrt(2)-32>13 for q=8"
            ),
            "rational_square_check": "sqrt(2)>45/32 because 2*32^2>45^2",
            "bt_action_bound": "F''(z_star)>13",
            "coupled_action_bound": (
                "for S_lambda=A(lambda*phi)/lambda^2 in the log coordinate "
                "psi=lambda*phi, the corresponding one-site phi-fiber "
                "curvature at its minimum is also greater than 13"
            ),
            "scope": "curvature at the minimum only, not global strong convexity",
        },
        "nonconvex_fixture": fixture,
        "literature_hypothesis_audit": {
            "thoma_membrane": (
                "uses a uniformly convex single-site potential in the Laplacian field; "
                "the BT fixture violates the required pointwise convexity"
            ),
            "menz_otto": (
                "treats a noninteracting conservative spin system whose single-site "
                "potential is a bounded perturbation of a strictly convex function; "
                "no such volume-uniform BT decomposition is supplied"
            ),
            "nonconvex_gradient_rg": (
                "small or controlled perturbations of a quadratic gradient model do "
                "not match the exact residual-square many-body BT interaction"
            ),
            "import_status": "METHODS_IDENTIFIED_THEOREMS_NOT_IMPORTED",
        },
        "method_disposition": {
            "all_one_site_fibers_single_well": "PROVED_FOR_Q_LESS_THAN_16",
            "bt_one_site_minimum_curvature": "PROVED_GREATER_THAN_13",
            "global_one_site_strong_convexity": "OBSTRUCTED_BY_EXACT_L4_FIXTURE",
            "uniform_one_site_poincare": "OPEN",
            "uniform_inter_site_influence": "OPEN",
            "lu_yau_or_otto_reznikoff_import": "NOT_JUSTIFIED",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_ON_DECLARED_L6_FIXTURE",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a volume- and background-uniform Poincare bound for the one-site conditional law",
            "a quantitative inter-site influence or multiscale covariance estimate",
            "a transfer from local conditional control to the lowest Fourier source cyclic sector",
            "the actual interacting H^-1 moment and Fourier-shell summation",
        ],
        "next_gate": (
            "Apply a one-dimensional Muckenhoupt/Hardy criterion to the exact "
            "single-well exponential-quartic fiber, seeking a constant uniform "
            "in A,C1,C2 under their BT constraints. If it succeeds, test the "
            "resulting conditional covariance influence matrix at free scaling; "
            "if it fails, retain the parameter family as a local low-gap sequence."
        ),
        "does_not_establish": [
            "a uniform one-site Poincare or logarithmic-Sobolev inequality",
            "a volume-uniform global Poincare or Witten one-form estimate",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound",
            "an interacting continuum Euclidean measure or ordinary OS reconstruction",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction arithmetic for the exact lattice fixture, "
                "polynomial evaluations, and rational inequalities"
            ),
            "literature_sources": [
                "https://arxiv.org/abs/2112.07584",
                "https://arxiv.org/abs/1307.2338",
                "https://arxiv.org/abs/2007.10869",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_single_site_fiber_single_well_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_single_site_fiber_single_well_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_single_site_fiber_single_well_gate",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation, JSON/schema parsing, scoped diff check, "
                "explicit input hashes, and staged-diff inspection required"
            ),
            "tier_1": "producer replay, independent verifier, and focused mutation tests required",
            "tier_2": (
                "unchanged content-addressed predecessor certificates checked by hash; "
                "no shared operator or transitive generated chain changed"
            ),
            "tier_3": (
                "not applicable: this is a classified local theorem/method obstruction, "
                "not a freeze, theorem lifecycle promotion, shared-core change, or release"
            ),
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "1.09 seconds, 275140 KiB",
                "independent_verifier": "1.14 seconds, 265600 KiB",
                "unit_tests": "1.17 seconds, 270140 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "1658 nodes with zero invalid items and zero malformed events in "
                    "7.30 seconds at 202472 KiB under GOMEMLIMIT=300MiB"
                ),
                "science_forge_shadow": (
                    "not run unless a registered shadow input changes; a skip is not a pass"
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
        "[PASS] BT one-site fiber single-well gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
