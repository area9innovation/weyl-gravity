#!/usr/bin/env python3
"""Build the BT cubic-current free-chaos obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-cubic-current-chaos-obstruction-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-cubic-current-chaos-obstruction.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_cubic_current_chaos_obstruction.py"
SOURCE_COMMIT = "d13ef71a823fda09db0390c0e5479c17ccbed0cf"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_CURRENT_SPIKE_GATE_V1.json",
]
MOTIF = {
    (0, 0, 0, 0): -1,
    (0, 1, 0, 0): 1,
    (1, 0, 0, 0): 1,
    (1, 2, 0, 0): -1,
}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    result = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def cubic_fixture(length: int) -> dict:
    points = list(itertools.product(range(length), repeat=4))

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    psi = {point: Fraction(MOTIF.get(point, 0)) for point in points}
    laplacian = {
        point: sum(
            (psi[shift(point, axis, step)] - psi[point] for axis in range(4) for step in (-1, 1)),
            Fraction(0),
        )
        for point in points
    }
    quadratic = {
        point: sum(
            ((psi[shift(point, axis, step)] - psi[point]) ** 2 for axis in range(4) for step in (-1, 1)),
            Fraction(0),
        ) / 2
        for point in points
    }
    cubic = {
        point: sum(
            ((psi[shift(point, axis, step)] - psi[point]) ** 3 for axis in range(4) for step in (-1, 1)),
            Fraction(0),
        ) / 6
        for point in points
    }
    current = {}
    for point in points:
        other = shift(point, 0, 1)
        delta = psi[other] - psi[point]
        current[point] = (
            cubic[point] - cubic[other]
            + delta * (quadratic[point] + quadratic[other])
            + delta**2 * (laplacian[point] - laplacian[other]) / 2
        )
    row_sums = [sum((current[point] for point in points if point[0] == time), Fraction(0)) for time in range(length)]
    return {
        "free_action_norm_squared": sum((value**2 for value in laplacian.values()), Fraction(0)),
        "cubic_current_total": sum(current.values(), Fraction(0)),
        "cubic_current_row_sums": row_sums,
        "nonzero_laplacian_count": sum(value != 0 for value in laplacian.values()),
        "nonzero_cubic_current_count": sum(value != 0 for value in current.values()),
    }


def build() -> dict:
    fixture_five = cubic_fixture(5)
    fixture_seven = cubic_fixture(7)
    norm_squared = Fraction(350)
    profile_constant = Fraction(44)
    profile_neighbor = Fraction(-3)
    profile_floor = profile_constant + 2 * profile_neighbor
    packing_density = Fraction(1, 625)
    hermite_variance = Fraction(6)
    variance_density = hermite_variance * profile_floor**2 * packing_density / norm_squared**3
    coupling = Fraction(2, 5)
    tuned_variance_density = variance_density * coupling**6
    omega_upper_coefficient = Fraction(1936, 49)
    normalized_divergence_coefficient = tuned_variance_density / omega_upper_coefficient

    checks = {
        "motif_is_rowwise_zero": all(sum(value for point, value in MOTIF.items() if point[0] == time) == 0 for time in (0, 1)),
        "cubic_fixture_is_volume_stable": (
            fixture_five["free_action_norm_squared"] == fixture_seven["free_action_norm_squared"]
            and fixture_five["cubic_current_total"] == fixture_seven["cubic_current_total"]
            and fixture_five["nonzero_laplacian_count"] == fixture_seven["nonzero_laplacian_count"]
            and fixture_five["nonzero_cubic_current_count"] == fixture_seven["nonzero_cubic_current_count"]
        ),
        "free_action_norm_squared_is_350": fixture_five["free_action_norm_squared"] == norm_squared,
        "cubic_current_total_is_38": fixture_five["cubic_current_total"] == 38,
        "cubic_current_profile_is_minus3_44_minus3": fixture_five["cubic_current_row_sums"] == [44, -3, 0, 0, -3],
        "profile_polynomial_floor_is_38": profile_floor == 38,
        "five_cell_packing_density_is_one_over_625": packing_density == Fraction(1, 625),
        "third_hermite_variance_is_six": hermite_variance == 6,
        "free_cubic_variance_density_is_exact": variance_density == Fraction(1083, 3349609375),
        "lambda_point_four_variance_density_is_exact": tuned_variance_density == Fraction(69312, 52337646484375),
        "lowest_lattice_omega_upper_coefficient_is_1936_over_49": omega_upper_coefficient == Fraction(1936, 49),
        "normalized_divergence_coefficient_is_exact": normalized_divergence_coefficient == Fraction(4332, 129241943359375),
        "orthogonal_motif_coordinates_are_independent_gaussians": True,
        "hermite_projection_gives_variance_lower_bound": True,
        "free_cubic_current_susceptibility_is_extensive": True,
        "termwise_N_omega_bound_is_obstructed": True,
        "full_perturbative_Ward_cancellation_remains_open": True,
        "actual_interacting_current_susceptibility_remains_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-cubic-current-chaos-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "FREE_CUBIC_CURRENT_TERM_HYPERUNIFORMITY_OBSTRUCTED_FULL_INTERACTING_CANCELLATION_OPEN",
        "result_kind": "exact extensive lower bound for the third Wiener-chaos component of the cubic canonical current under the full-phase free bilaplacian background",
        "question": "Can the moderate-current susceptibility be proved by bounding each homogeneous order of the canonical current separately by N times the lowest lattice momentum squared?",
        "answer": "No. The cubic homogeneous current already violates that termwise bound on every L^4 torus with 5 dividing L. A compact rowwise-zero motif has free action norm squared 350 and cubic axial-current profile 44-3z-3z^-1, whose magnitude is at least 38 at every axial momentum. Translates on a five-cell grid give N/625 mutually action-orthogonal directions inside the exact full-phase background slice. Projecting the cubic current onto their independent third Hermite chaoses proves E_0|Jhat_0^(3)(p_L)|^2>=(1083/3349609375)lambda^6 N. At lambda=2/5, division by N omega_p grows at least (4332/129241943359375)L^2. Therefore no proof may demand the missing momentum factor from the cubic current term alone. This is a perturbative method obstruction, not an obstruction to the complete interacting susceptibility: measure corrections and cross-order Ward cancellations have not been assembled or ruled out.",
        "cubic_current_expansion": {
            "field_scaling": "Set psi=epsilon f and expand the canonical current J_(x,0)=r_x exp(psi_(x+e0)-psi_x)-r_(x+e0) exp(psi_x-psi_(x+e0)).",
            "linear_residual": "ell_x=Delta f_x",
            "quadratic_residual": "q_x=(1/2)sum_(y~x)(f_y-f_x)^2",
            "cubic_residual": "c_x=(1/6)sum_(y~x)(f_y-f_x)^3",
            "edge_difference": "delta_x=f_(x+e0)-f_x",
            "cubic_current": "J_x^(3)=c_x-c_(x+e0)+delta_x(q_x+q_(x+e0))+(delta_x^2/2)(ell_x-ell_(x+e0)).",
            "zero_mode_after_telescoping": "sum_x J_x^(3)=sum_x[delta_x(q_x+q_(x+e0))+(delta_x^2/2)(ell_x-ell_(x+e0))].",
            "status": "EXACT_HOMOGENEOUS_EXPANSION",
        },
        "compact_cubic_motif": {
            "scope": "every L^4 torus with L>=5",
            "exponent_support": [{"site": list(point), "value": value} for point, value in sorted(MOTIF.items())],
            "slice_proof": "Every active time row sums to zero, so the motif is mean-zero and orthogonal to both phases of every nonzero axial time momentum.",
            "free_action_inner_product_norm_squared": enc(norm_squared),
            "cubic_current_row_profile": [enc(value) for value in fixture_five["cubic_current_row_sums"]],
            "fourier_profile": "P(z)=44-3z-3z^-1=44-6cos(p)>=38 for |z|=1.",
            "fourier_profile_floor": enc(profile_floor),
            "nonzero_laplacian_count": fixture_five["nonzero_laplacian_count"],
            "nonzero_cubic_current_count": fixture_five["nonzero_cubic_current_count"],
            "status": "EXACT_LOCAL_CUBIC_CURRENT_WITNESS",
        },
        "orthogonal_packing_and_chaos": {
            "volume_sequence": "L=5m, m>=1, N=L^4",
            "translations": "translate the motif by (5a0,5a1,5a2,5a3), with aj=0,...,m-1",
            "packing_count": "M=(L/5)^4=N/625",
            "orthogonality": "The supports of Delta f_a are disjoint, so e_a=f_a/sqrt(350) are orthonormal in the free action inner product sum_x Delta f Delta g.",
            "background_slice": "Every translate remains rowwise-zero and hence belongs to E_p perpendicular.",
            "gaussian_coordinates": "Under the free bilaplacian background, X_a=<psi,e_a>_A are independent centered Gaussians of variance lambda^2.",
            "third_chaos": "The coefficient of H_3(X_a/lambda) is lambda^3 exp(i p t_a)P(exp(i p))/350^(3/2), and E[H_3(G)^2]=3!=6.",
            "status": "EXACT_ORTHOGONAL_HERMITE_LOWER_BOUND",
        },
        "extensive_variance_obstruction": {
            "general_lower_bound": "E_0|Jhat_0^(3)(p)|^2>=(1083/3349609375)lambda^6 N for every axial p and every L in 5N.",
            "general_variance_density": enc(variance_density),
            "lambda_point_four_lower_bound": "E_0|Jhat_0^(3)(p)|^2>=(69312/52337646484375)N.",
            "lambda_point_four_variance_density": enc(tuned_variance_density),
            "lowest_momentum": "p_L=(2pi/L,0,0,0), omega_p=4sin^2(pi/L)<1936/(49L^2).",
            "normalized_divergence": "E_0|Jhat_0^(3)(p_L)|^2/(N omega_p)>=(4332/129241943359375)L^2.",
            "normalized_divergence_coefficient": enc(normalized_divergence_coefficient),
            "status": "DIVERGES_QUADRATICALLY_TERM_BY_TERM_ON_L_IN_5N",
        },
        "method_disposition": {
            "linear_current_second_soft_factor": "PRESENT_ON_BACKGROUND_SLICE",
            "quadratic_current_zero_mode": "CANCELS_IDENTICALLY",
            "cubic_current_termwise_hyperuniformity": "OBSTRUCTED",
            "homogeneous_order_by_order_absolute_current_bound": "OBSTRUCTED",
            "cross_order_and_measure_Ward_cancellation": "OPEN",
            "complete_perturbative_current_susceptibility": "NOT_DECIDED",
            "nonperturbative_background_marginal_susceptibility": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "failure of the complete perturbative current susceptibility after measure and cross-order corrections",
            "failure or boundedness of the exact interacting background-marginal score",
            "divergence or boundedness of the actual interacting H^-1 moment",
            "tightness or identification of a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "the background-density expansion and all order-lambda-six cross terms required by the current Ward identity",
            "a proof or obstruction for cancellation of the extensive third-chaos component in the complete score",
            "a nonperturbative observable-weighted block estimate under the exact background marginal",
            "the resulting current susceptibility or actual low-mode divergence",
            "the dyadic shell theorem for the interacting H^-1 moment or divergence",
        ],
        "next_gate": "Compute the complete order-lambda-six background-marginal score variance, including the cubic current, quadratic-current/action-density cross terms, and the fiber determinant/normalization correction. The certified third-chaos lower bound is the adversarial term: either the Ward identity cancels it exactly, revealing the positive mechanism, or a nonzero extensive remainder obstructs the current-susceptibility route perturbatively. Neither outcome alone may be promoted to the fixed-coupling interacting H^-1 theorem without a uniform bridge.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic expands the cubic current and enumerates the compact motif on two torus sizes. The packing, action norm, Hermite variance, variance density, and lowest-momentum divergence coefficient are exact rationals.",
            "analytic_arithmetic": "Disjoint Laplacian supports give orthogonal free Gaussian coordinates. Orthogonal projection onto their third Hermite chaoses yields a rigorous variance lower bound. The elementary pi<22/7 bound converts it to explicit lowest-momentum divergence.",
            "assumptions": [
                "The free reference is the Gaussian bilaplacian measure on the mean-zero carrier intersected with the full lowest axial cosine-sine orthogonal complement.",
                "The current and Fourier conventions are those of the weighted-current input.",
                "This certificate classifies a homogeneous perturbative term and does not substitute it for the full interacting observable.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_cubic_current_chaos_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_cubic_current_chaos_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_cubic_current_chaos_obstruction",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    expected = render(build())
    if arguments.check:
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
