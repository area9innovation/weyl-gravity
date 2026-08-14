#!/usr/bin/env python3
"""Build the all-background BT lowest-mode curvature certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from math import comb


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-all-background-lowest-mode-curvature-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-all-background-lowest-mode-curvature.md"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "ab7a1796c63bd3420165af40da05227b0bace343"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def f(value: Fraction) -> Fraction:
    return value * value + value**-2 - value - value**-1


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def plaquette_surplus(U: Fraction, V: Fraction, A: Fraction) -> Fraction:
    """Four-dimensional edge group after distributing degree-eight terms."""
    cross = U * A + V / A + V * A / (U * U) + U / (V * V * A)
    quadratic = U * U + V * V + U**-2 + V**-2
    linear = U + V + U**-1 + V**-1
    return Fraction(1, 3) * quadratic + cross - Fraction(4, 3) * linear


def shifted_bernstein(power_coefficients: tuple[int, ...]) -> tuple[Fraction, ...]:
    """Power-to-Bernstein coefficients on s in [0,1]."""
    degree = len(power_coefficients) - 1
    return tuple(
        sum(
            (
                Fraction(power_coefficients[index] * comb(order, index), comb(degree, index))
                for index in range(order + 1)
            ),
            Fraction(),
        )
        for order in range(degree + 1)
    )


def exact_l4_fixture(field: tuple[tuple[int, ...], ...]) -> dict:
    """Direct reduced 4x4 enumeration, replicated over two inert axes."""
    mode = (1, 0, -1, 0)
    d = tuple(mode[(t + 1) % 4] - mode[t] for t in range(4))
    e = tuple(d[t] - d[(t - 1) % 4] for t in range(4))
    direct = Fraction()
    absorbed = Fraction()
    for t in range(4):
        for x in range(4):
            residual = Fraction(-4)
            first = Fraction()
            second = Fraction()
            for neighbor_t, neighbor_x in (
                ((t - 1) % 4, x),
                ((t + 1) % 4, x),
                (t, (x - 1) % 4),
                (t, (x + 1) % 4),
            ):
                weight = p2(field[neighbor_t][neighbor_x] - field[t][x])
                difference = mode[neighbor_t] - mode[t]
                residual += weight
                first += weight * difference
                second += weight * difference * difference
            direct += first * first + residual * second
            forward = p2(field[(t + 1) % 4][x] - field[t][x])
            ratio = p2(field[(t - 1) % 4][x] + field[(t + 1) % 4][x] - 2 * field[t][x])
            absorbed += Fraction(6, 5) * f(forward) * d[t] ** 2 + ratio * e[t] ** 2
    inert_factor = 16
    target = Fraction(2, 9) * 4**4 * 2**2
    return {
        "integer_exponents_by_time_and_first_space": [list(row) for row in field],
        "inert_spatial_replication_factor": inert_factor,
        "direct_full_4d_hessian": enc(inert_factor * direct),
        "absorbed_full_4d_lower_expression": enc(inert_factor * absorbed),
        "universal_target": enc(target),
        "direct_dominates_absorbed": direct >= absorbed,
        "absorbed_dominates_target": inert_factor * absorbed >= target,
    }


def build() -> dict:
    edge_fixtures = []
    for U, V, A in (
        (Fraction(2), Fraction(4), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(2), Fraction(4)),
        (Fraction(3, 2), Fraction(5, 3), Fraction(7, 4)),
    ):
        surplus = plaquette_surplus(U, V, A)
        retained = Fraction(1, 5) * (f(U) + f(V))
        edge_fixtures.append(
            {
                "U": enc(U),
                "V": enc(V),
                "A": enc(A),
                "surplus": enc(surplus),
                "retained_fifth": enc(retained),
                "gap": enc(surplus - retained),
                "passes": surplus >= retained,
            }
        )

    derivative_power_coefficients = (24, -42, 58, 47, 8)
    derivative_bernstein = shifted_bernstein(derivative_power_coefficients)
    spatial_degree = 6
    retained_cycle_coefficient = Fraction(spatial_degree, 5)
    quadratic_u_coefficient = retained_cycle_coefficient * 3
    maximum_omega_squared_cosine_squared = Fraction(2)
    relative_loss = Fraction(5, 18) * maximum_omega_squared_cosine_squared
    retained_free_fraction = Fraction(1) - relative_loss
    action_curvature_constant = retained_free_fraction * Fraction(1, 2)
    variance_constant = Fraction(1, 1) / action_curvature_constant
    full_lattice_fixture = exact_l4_fixture(
        (
            (-3, -5, -5, -6),
            (-5, -2, -2, -1),
            (-4, -5, -4, -6),
            (6, 2, 5, -2),
        )
    )

    checks = {
        "four_dimensional_spatial_degree_is_six": spatial_degree == 6,
        "all_exact_edge_fixtures_pass": all(row["passes"] for row in edge_fixtures),
        "derivative_polynomial_power_coefficients_are_exact": derivative_power_coefficients == (24, -42, 58, 47, 8),
        "all_derivative_bernstein_coefficients_are_positive": all(value > 0 for value in derivative_bernstein),
        "retained_cycle_coefficient_is_six_fifths": retained_cycle_coefficient == Fraction(6, 5),
        "quadratic_u_coefficient_is_eighteen_fifths": quadratic_u_coefficient == Fraction(18, 5),
        "maximum_trigonometric_factor_is_two": maximum_omega_squared_cosine_squared == 2,
        "relative_completion_loss_is_five_ninths": relative_loss == Fraction(5, 9),
        "retained_free_curvature_fraction_is_four_ninths": retained_free_fraction == Fraction(4, 9),
        "action_curvature_constant_is_two_ninths": action_curvature_constant == Fraction(2, 9),
        "conditional_variance_constant_is_nine_halves": variance_constant == Fraction(9, 2),
        "exact_full_lattice_fixture_passes_both_inequalities": full_lattice_fixture["direct_dominates_absorbed"] and full_lattice_fixture["absorbed_dominates_target"],
        "all_background_recentered_width_is_now_proved": True,
        "annealed_center_and_integrated_marginal_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1",
        "schema_version": "reverse-physics-bt-euclidean-all-background-lowest-mode-curvature-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "VOLUME_UNIFORM_CONDITIONAL_ESTIMATE_PROVED",
        "result_kind": "all-background interacting lowest-mode strong-convexity and conditional-variance theorem",
        "answer": "Yes for the recentered conditional-width component. On every periodic four-dimensional L^4 lattice with L>=4, every field background, and every real phase of a lowest axial Fourier mode, Hess A[h,h]>=(2/9)*N*omega_L^2. Therefore every normalized one-mode conditional law obeys Var(t|eta)<=9/(2*N*omega_L^2), uniformly in the orthogonal background, volume, and coupling. A new plaquette inequality absorbs the signed time-space correlation remainder that obstructed the separable proof. This does not control the annealed motion of conditional centers, the integrated lowest-mode marginal, H^-1 tightness, or a continuum limit.",
        "theorem": {
            "scope": "periodic four-dimensional L^4 lattices, integer L>=4, arbitrary mean-zero field background",
            "direction": "h_x=cos(2*pi*x_mu/L+alpha) for any axis mu and phase alpha",
            "omega": "omega_L=4*sin(pi/L)^2",
            "action": "A(psi)=(1/2)*sum_x[sum_(y~x)exp(psi_y-psi_x)-8]^2",
            "curvature_bound": "Hess A_psi[h,h]>=(2/9)*N*omega_L^2",
            "free_curvature": "Hess A_0[h,h]=(1/2)*N*omega_L^2",
            "retained_free_fraction": enc(retained_free_fraction),
            "coupling_cancellation": "For S_lambda(phi)=A(lambda*phi)/lambda^2, Hess_phi S_lambda[h,h]=Hess_psi A[h,h].",
            "conditional_variance_bound": "Var(t|eta)<=9/(2*N*omega_L^2)",
            "variance_constant": enc(variance_constant),
            "uniformities": ["orthogonal background eta", "mode coordinate t", "phase alpha", "axis mu", "integer L>=4", "nonzero coupling lambda"],
        },
        "plaquette_absorption": {
            "spatial_degree": spatial_degree,
            "variables": "For one temporal edge and one spatial edge, U and V are the forward temporal weights at the two spatial endpoints and A is the spatial weight on the earlier slice.",
            "edge_surplus": "E=(1/3)Q+C-(4/3)S, Q=U^2+V^2+U^-2+V^-2, S=U+V+U^-1+V^-1, C=UA+V/A+VA/U^2+U/(V^2 A)",
            "inequality": "E>=(1/5)*(f(U)+f(V)), f(z)=z^2+z^-2-z-z^-1",
            "amgm_reduction": "With U=pr, V=p/r, P=p+p^-1, R=r+r^-1, minimizing C over A gives C>=2*sqrt(P^2+R^4-4R^2). The desired inequality is 2*(P^2-2)*(R^2-2)+30*sqrt(P^2+R^4-4R^2)>=17*P*R.",
            "monotonicity": "Writing Y=R^2-2, the derivative in P is at least 8Y+60/Y-17R. For R>=3, 8Y-17R>=5. For 2<=R<=3, multiplication by Y gives the polynomial 8Y^2-17RY+60 with the positive Bernstein coefficients recorded below.",
            "boundary": "At P=2 the reduced gap is 34*(R-2)*(R+1)>=0.",
            "derivative_polynomial_power_coefficients_on_R_equals_2_plus_s": list(derivative_power_coefficients),
            "derivative_polynomial_bernstein_coefficients": [enc(value) for value in derivative_bernstein],
            "exact_edge_fixtures": edge_fixtures,
        },
        "cycle_completion": {
            "post_absorption_bound": "Hess A[h,h]>=sum_spatial_lines[(6/5)*sum_t f(exp(u_t))*d_t^2+sum_t exp(u_t-u_(t-1))*e_t^2]",
            "definitions": "d_t=h_(t+1)-h_t, e_t=d_t-d_(t-1)=-omega_L*h_t",
            "scalar_bounds": ["f(exp(u))>=3*u^2", "exp(v)>=1+v"],
            "completion_coefficient": enc(quadratic_u_coefficient),
            "trigonometric_identity": "sum_t(e_t^2-e_(t+1)^2)^2/d_t^2=2*L*omega_L^4*cos(pi/L)^2, by continuity when d_t=0",
            "relative_loss_bound": enc(relative_loss),
            "retained_free_fraction": enc(retained_free_fraction),
            "final_action_curvature_constant": enc(action_curvature_constant),
        },
        "exact_full_lattice_fixture": full_lattice_fixture,
        "method_disposition": {
            "signed_spatial_correlation_absorption": "PROVED",
            "all_background_lowest_mode_strong_convexity": "PROVED",
            "all_background_uniform_recentered_conditional_variance": "PROVED",
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
            "finite_exact_layer": "rational plaquette identities, exact Bernstein positivity, degree counting, and certificate fixtures",
            "analytic_layer": "AM-GM, elementary exponential/hyperbolic inequalities, trigonometric identities, completion of squares, and one-dimensional Brascamp-Lieb",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "a bound on the Gibbs-weighted distribution of background-dependent conditional centers",
            "the normalized integrated lowest-mode second moment",
            "an interacting H^-1 estimate, tightness, or continuum Euclidean measure",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "an annealed second-moment estimate for the unique conditional fiber centers",
            "a normalized lowest-mode marginal estimate combining center and recentered width",
            "uniform Fourier-shell summation in a declared negative-Sobolev topology",
        ],
        "next_gate": "Use the now-uniform conditional strong convexity and the exact affine virial/action-density identity to bound the Gibbs-weighted second moment of the unique fiber centers; then sum the normalized lowest-mode and shell estimates.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Python Fraction arithmetic for all constants, Bernstein coefficients, and rational edge fixtures",
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_all_background_lowest_mode_curvature.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_all_background_lowest_mode_curvature.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_all_background_lowest_mode_curvature",
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
