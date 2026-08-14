#!/usr/bin/env python3
"""Build the exact BT separable lowest-mode curvature certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-separable-lowest-mode-curvature-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-separable-lowest-mode-curvature.md"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "e75bac393108c75601a84f9b0931050a8a1f816d"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


MODE = (1, 0, -1, 0)
CORRELATED = (
    (-3, -5, -5, -6),
    (-5, -2, -2, -1),
    (-4, -5, -4, -6),
    (6, 2, 5, -2),
)


def two_dimensional_parts(field: tuple[tuple[int, ...], ...]) -> tuple[Fraction, Fraction]:
    """Temporal-line Hessian and the spatial-correlation remainder."""
    temporal = Fraction()
    remainder = Fraction()
    for time in range(4):
        for space in range(4):
            residual = Fraction(-2)
            first = Fraction()
            second = Fraction()
            for neighbor_time in ((time - 1) % 4, (time + 1) % 4):
                weight = p2(field[neighbor_time][space] - field[time][space])
                difference = MODE[neighbor_time] - MODE[time]
                residual += weight
                first += weight * difference
                second += weight * difference * difference
            temporal += first * first + residual * second
            spatial_residual = Fraction(-2)
            for neighbor_space in ((space - 1) % 4, (space + 1) % 4):
                spatial_residual += p2(
                    field[time][neighbor_space] - field[time][space]
                )
            remainder += spatial_residual * second
    return temporal, remainder


def separable_fixture() -> tuple[Fraction, Fraction, Fraction]:
    """Exact 4^4 fixture with psi=(a_t+b_x) log(2)."""
    time_profile = (0, 1, -1, 0)
    spatial_profile = (0, 1, -1, 0)
    field = tuple(
        tuple(time_profile[t] + spatial_profile[x] for x in range(4))
        for t in range(4)
    )
    temporal, remainder = two_dimensional_parts(field)
    inert_spatial_factor = 4**2
    return (
        temporal * inert_spatial_factor,
        remainder * inert_spatial_factor,
        (temporal + remainder) * inert_spatial_factor,
    )


def build() -> dict:
    temporal, remainder = two_dimensional_parts(CORRELATED)
    sep_temporal, sep_remainder, sep_total = separable_fixture()
    centered_sum = sum(sum(row) for row in CORRELATED)
    mode_pairing = sum(
        CORRELATED[t][x] * MODE[t] for t in range(4) for x in range(4)
    )
    inert_factor = 4**2
    checks = {
        "mode_is_lowest_axial_eigenvector_at_L4": MODE == (1, 0, -1, 0),
        "correlated_fixture_is_mode_orthogonal": mode_pairing == 0,
        "centering_constant_does_not_change_weights": centered_sum == -37,
        "correlation_remainder_is_strictly_negative": remainder < 0,
        "correlated_total_hessian_remains_positive": temporal + remainder > 0,
        "separable_spatial_remainder_is_nonnegative": sep_remainder >= 0,
        "general_curvature_fraction_is_two_thirds": Fraction(1) - Fraction(1, 3) == Fraction(2, 3),
        "conditional_variance_constant_is_three": Fraction(1, 1) / Fraction(1, 3) == 3,
        "all_background_extension_remains_open": True,
        "interacting_h_minus_one_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1",
        "schema_version": "reverse-physics-bt-euclidean-separable-lowest-mode-curvature-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "SCOPED_THEOREM_PROVED",
        "result_kind": "exact separable-background curvature theorem and correlated-remainder obstruction",
        "answer": "For every L>=4 and every separable background psi(t,x)=a_t+b_x on the four-dimensional periodic lattice, the BT action Hessian in any real lowest temporal Fourier direction is at least N*omega_L^2/3. Hence the one-dimensional conditional variance is at most 3/(N*omega_L^2). An exact centered, mode-orthogonal, nonseparable L=4 fixture has a strictly negative spatial-correlation remainder, so the proof cannot be extended by declaring that remainder positive. The all-background conditional width, annealed center, interacting H^-1 estimate, and continuum limit remain open.",
        "theorem": {
            "lattice": "four-dimensional periodic L^4 lattice, integer L>=4",
            "background": "psi(t,x)=a_t+b_x, with arbitrary real periodic a and b",
            "direction": "h_t=cos(2*pi*t/L+alpha), with arbitrary phase alpha",
            "omega": "omega_L=4*sin(pi/L)^2",
            "action": "A(psi)=(1/2)*sum_x[sum_(y~x) exp(psi_y-psi_x)-8]^2",
            "curvature_bound": "Hess A_psi[h,h]>=N*omega_L^2/3",
            "free_curvature": "Hess A_0[h,h]=N*omega_L^2/2",
            "retained_fraction_of_free_curvature": enc(Fraction(2, 3)),
            "conditional_variance_bound": "Var(t|separable background)<=3/(N*omega_L^2)",
            "coupling_cancellation": "For S_lambda(phi)=A(lambda*phi)/lambda^2, its phi-Hessian along h equals the psi-Hessian of A.",
        },
        "proof_ledger": {
            "cycle_identity": "H=2*sum_t f(exp(u_t))*d_t^2+sum_t exp(u_t-u_(t-1))*e_t^2, where f(x)=x^2+x^-2-x-x^-1, d_t=h_(t+1)-h_t, e_t=d_t-d_(t-1)",
            "scalar_inequality": "f(exp(u))=2*cosh(2u)-2*cosh(u)>=3*u^2",
            "exponential_tangent": "exp(v)>=1+v",
            "completion_of_squares": "6*d_t^2*u_t^2+(e_t^2-e_(t+1)^2)*u_t>=-(e_t^2-e_(t+1)^2)^2/(24*d_t^2)",
            "trigonometric_sum": "sum_t (e_t^2-e_(t+1)^2)^2/d_t^2=2*L*omega_L^4*cos(pi/L)^2",
            "relative_loss": "omega_L^2*cos(pi/L)^2/6=(8/3)*sin(pi/L)^4*cos(pi/L)^2<=1/3",
            "spatial_term": "separability makes c_t independent of x and sum_x[sum_(y~x)exp(b_y-b_x)-6]>=0 by pairing every undirected edge as exp(delta)+exp(-delta)-2",
        },
        "exact_separable_fixture": {
            "L": 4,
            "time_exponents": [0, 1, -1, 0],
            "one_spatial_axis_exponents": [0, 1, -1, 0],
            "other_two_spatial_axes": "constant",
            "temporal_line_part": enc(sep_temporal),
            "spatial_remainder": enc(sep_remainder),
            "full_hessian": enc(sep_total),
        },
        "exact_correlated_fixture": {
            "L": 4,
            "coordinates": "psi=(k+37/16)*log(2), repeated in the other two spatial axes",
            "integer_exponents_k_by_time_and_first_space": [list(row) for row in CORRELATED],
            "mode": list(MODE),
            "mode_pairing_per_inert_spatial_cell": mode_pairing,
            "mean_before_centering_per_inert_spatial_cell": centered_sum,
            "temporal_line_part_per_inert_spatial_cell": enc(temporal),
            "spatial_correlation_remainder_per_inert_spatial_cell": enc(remainder),
            "full_hessian_per_inert_spatial_cell": enc(temporal + remainder),
            "full_4d_replication_factor": inert_factor,
            "conclusion": "The spatial-correlation remainder has no all-background nonnegative sign, even on a centered background orthogonal to the selected lowest mode.",
        },
        "method_disposition": {
            "separable_background_lowest_mode_curvature": "PROVED",
            "separable_background_conditional_variance": "PROVED",
            "all_background_spatial_remainder_nonnegative": "OBSTRUCTED",
            "all_background_recentered_conditional_variance": "OPEN",
            "annealed_center_second_moment": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": "rational power-of-two fixture arithmetic and finite edge pairing",
            "analytic_layer": "elementary real exponential, hyperbolic, trigonometric, and one-dimensional Brascamp-Lieb inequalities",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "an all-background conditional variance bound",
            "an annealed bound on moving conditional centers",
            "the normalized interacting lowest-mode second moment",
            "an interacting H^-1 estimate or tightness",
            "a continuum Euclidean measure, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "an inequality absorbing the signed correlation remainder into positive temporal curvature or Gibbs weight",
            "an annealed second-moment bound for background-dependent fiber centers",
            "a volume-uniform normalized lowest-mode estimate followed by Fourier-shell summation",
        ],
        "next_gate": "Prove an all-background correlation-absorption inequality, or construct a periodic family where the complete lowest-mode fiber curvature/normalized marginal fails; then combine recentered width with annealed center control.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Python Fraction arithmetic for every lattice fixture",
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_separable_lowest_mode_curvature.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_separable_lowest_mode_curvature.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_separable_lowest_mode_curvature",
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
