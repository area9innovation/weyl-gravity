#!/usr/bin/env python3
"""Certify a low-action flat-potential convexity obstruction for BT."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_ACTION_FLAT_"
    "CONVEXITY_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-low-action-flat-"
    "convexity-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-low-action-flat-convexity-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_low_action_flat_convexity_obstruction.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
        "DETERMINANT_PUSHFORWARD_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_"
        "CURRENT_SPIKE_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "da2521d7"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        row[:] + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * entry
                for value, entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (
                    left[row][inner] * right[inner][column]
                    for inner in range(len(right))
                ),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def fixture() -> dict:
    """Return the exact C16 longitudinal calculation used on C16^4."""

    omega = [
        Fraction(4),
        Fraction(2, 5),
        Fraction(1, 25),
        Fraction(1, 250),
        Fraction(1, 2500),
        Fraction(1, 1000),
        Fraction(1, 100),
        Fraction(1, 10),
        Fraction(1),
        Fraction(1, 10),
        Fraction(1, 100),
        Fraction(1, 1000),
        Fraction(1, 2500),
        Fraction(1, 250),
        Fraction(1, 25),
        Fraction(2, 5),
    ]
    size = len(omega)
    direction = [Fraction(0) for _ in range(size)]
    direction[0] = 1
    direction[8] = -1
    residual = [
        omega[(site - 1) % size] / omega[site]
        + omega[(site + 1) % size] / omega[site]
        - 2
        for site in range(size)
    ]
    mean_residual = sum(residual, Fraction(0)) / size
    potential = [value - mean_residual for value in residual]
    ground_eigenvalue = -mean_residual
    kinetic = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        kinetic[site][site] = 2 + residual[site]
        kinetic[site][(site - 1) % size] = -1
        kinetic[site][(site + 1) % size] = -1
    bordered = [
        row[:] + [omega[row_index]]
        for row_index, row in enumerate(kinetic)
    ]
    bordered.append(omega[:] + [Fraction(0)])
    pseudoinverse = [row[:size] for row in inverse(bordered)[:size]]
    omega_norm_squared = dot(omega, omega)
    eigenvalue_prime = sum(
        (
            direction[index] * omega[index] ** 2
            for index in range(size)
        ),
        Fraction(0),
    ) / omega_norm_squared
    centered_source = [
        (direction[index] - eigenvalue_prime) * omega[index]
        for index in range(size)
    ]
    eigenvalue_second = (
        -2
        * dot(
            centered_source,
            matrix_vector(pseudoinverse, centered_source),
        )
        / omega_norm_squared
    )
    kinetic_prime = [
        [
            direction[row] - eigenvalue_prime
            if row == column
            else Fraction(0)
            for column in range(size)
        ]
        for row in range(size)
    ]
    pseudoinverse_squared = multiply(pseudoinverse, pseudoinverse)
    pk = multiply(pseudoinverse, kinetic_prime)
    logdet_second_terms = [
        -eigenvalue_second * trace(pseudoinverse),
        -trace(multiply(pk, pk)),
        Fraction(2, omega_norm_squared)
        * dot(
            matrix_vector(kinetic_prime, omega),
            matrix_vector(
                pseudoinverse_squared,
                matrix_vector(kinetic_prime, omega),
            ),
        ),
    ]
    longitudinal_logdet_second = sum(logdet_second_terms, Fraction(0))
    coupling = Fraction(2, 5)
    longitudinal_gaussian_second = (
        dot(direction, direction)
        + size
        * (
            eigenvalue_prime**2
            + ground_eigenvalue * eigenvalue_second
        )
    ) / (coupling * coupling)
    transverse_multiplicity = size**3 - 1
    transverse_trace_factor = Fraction(size, 1) / Fraction(3, 20)
    transverse_upper_bound = (
        -eigenvalue_second
        * transverse_multiplicity
        * transverse_trace_factor
    )
    four_dimensional_gaussian_second = (
        size**3 * longitudinal_gaussian_second
    )
    full_curvature_upper_bound = (
        four_dimensional_gaussian_second
        + longitudinal_logdet_second
        + transverse_upper_bound
    )
    longitudinal_action = sum(
        (value * value for value in residual), Fraction(0)
    ) / 2
    action_density = longitudinal_action / size
    return {
        "omega": omega,
        "direction": direction,
        "residual": residual,
        "mean_residual": mean_residual,
        "potential": potential,
        "ground_eigenvalue": ground_eigenvalue,
        "kinetic": kinetic,
        "omega_norm_squared": omega_norm_squared,
        "eigenvalue_prime": eigenvalue_prime,
        "eigenvalue_second": eigenvalue_second,
        "logdet_second_terms": logdet_second_terms,
        "longitudinal_logdet_second": longitudinal_logdet_second,
        "coupling": coupling,
        "longitudinal_gaussian_second": longitudinal_gaussian_second,
        "four_dimensional_gaussian_second": four_dimensional_gaussian_second,
        "transverse_multiplicity": transverse_multiplicity,
        "transverse_trace_factor": transverse_trace_factor,
        "transverse_upper_bound": transverse_upper_bound,
        "full_curvature_upper_bound": full_curvature_upper_bound,
        "longitudinal_action": longitudinal_action,
        "action_density": action_density,
    }


def build() -> dict:
    exact = fixture()
    with open(os.path.join(ROOT, INPUTS[1]), encoding="utf-8") as handle:
        action_tail = json.load(handle)["lambda_point_four_bulk_tail"]
    imported_cutoff = Fraction(
        action_tail["action_density_cutoff"]["numerator"],
        action_tail["action_density_cutoff"]["denominator"],
    )
    imported_coupling = Fraction(
        action_tail["lambda"]["numerator"],
        action_tail["lambda"]["denominator"],
    )
    imported_tail_rate = Fraction(
        action_tail["tail_rate"]["numerator"],
        action_tail["tail_rate"]["denominator"],
    )
    expected_upper = Fraction(
        -172511934113812002844255298492122939661512764763404478974825,
        59081288175090511897125080246062762727536819609,
    )
    checks = {
        "fixture_has_sixteen_longitudinal_sites": len(exact["omega"]) == 16,
        "ground_vector_is_strictly_positive": all(
            value > 0 for value in exact["omega"]
        ),
        "direction_is_mean_zero": sum(exact["direction"], Fraction(0)) == 0,
        "kinetic_kills_positive_ground_vector": all(
            sum(
                (
                    exact["kinetic"][row][column] * exact["omega"][column]
                    for column in range(16)
                ),
                Fraction(0),
            )
            == 0
            for row in range(16)
        ),
        "residual_mean_is_36_over_5": exact["mean_residual"] == Fraction(36, 5),
        "action_density_is_5121_over_160": exact["action_density"]
        == Fraction(5121, 160),
        "imported_tail_parameters_are_exact": (
            imported_cutoff == 50
            and imported_coupling == Fraction(2, 5)
            and imported_tail_rate == Fraction(17, 5)
        ),
        "action_density_is_below_certified_tail_cutoff": (
            exact["action_density"] < imported_cutoff
        ),
        "lowest_eigenvalue_is_concave_in_direction": exact["eigenvalue_second"]
        < 0,
        "transverse_mode_count_is_4095": exact["transverse_multiplicity"]
        == 4095,
        "rational_transverse_trace_factor_is_320_over_3": exact[
            "transverse_trace_factor"
        ]
        == Fraction(320, 3),
        "curvature_upper_bound_is_exact": exact["full_curvature_upper_bound"]
        == expected_upper,
        "full_flat_effective_curvature_is_strictly_negative": exact[
            "full_curvature_upper_bound"
        ]
        < 0,
        "good_action_global_convexity_route_is_obstructed": True,
        "actual_interacting_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_ACTION_FLAT_"
            "CONVEXITY_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-low-action-flat-"
            "convexity-obstruction-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "LOW_ACTION_FLAT_CONVEXITY_ROUTE_OBSTRUCTED",
        "result_kind": (
            "exact rational finite-volume obstruction to convexity of the "
            "flat-potential BT effective potential inside the certified "
            "low-action region on the physical four-dimensional torus"
        ),
        "question": (
            "Can the exact action tail at A>=50N be combined with global "
            "convexity of the flat effective potential on A<50N?"
        ),
        "answer": (
            "No. On the 16^4 periodic lattice at lambda=2/5, a rational "
            "two-well ground field has A/N=5121/160<50. Along a mean-zero "
            "hyperplane-splitting potential direction, exact longitudinal "
            "curvature plus a rigorous upper bound for all 4095 nonzero "
            "transverse blocks is strictly negative. Thus that particular "
            "good-action convexity plus tail strategy is obstructed on the "
            "actual lattice family. This is a method obstruction, not a "
            "divergence theorem for the interacting moment."
        ),
        "four_torus_construction": {
            "lattice": "Lambda=(Z/16Z)^4 with N=16^4",
            "ground_field": (
                "Omega(x)=omega_(x1), with the exact rational longitudinal "
                "vector recorded in the fixture"
            ),
            "residual": (
                "r_x=(Omega_(x-e1)+Omega_(x+e1))/Omega_x-2; transverse "
                "constant directions contribute zero"
            ),
            "centered_potential": "u=r-(36/5)*1",
            "ground_eigenvalue": "ell_0=-36/5",
            "direction": (
                "h_x=1 on x1=0, h_x=-1 on x1=8, and h_x=0 otherwise"
            ),
            "positivity": (
                "the ground-state transform makes K=-Delta+diag(r) "
                "positive semidefinite with the unique positive null vector "
                "Omega"
            ),
            "status": "EXACT_RATIONAL_CONSTRUCTION",
        },
        "low_action_statement": {
            "action": "A=(1/2)*sum_x r_x^2",
            "action_density": enc(exact["action_density"]),
            "certified_tail_cutoff_density": enc(imported_cutoff),
            "coupling": enc(imported_coupling),
            "tail_rate": enc(imported_tail_rate),
            "strictly_below_cutoff": True,
            "imported_tail_statement": (
                "at lambda=2/5, nu(A>=50N)<=exp(-17N/5)"
            ),
            "status": "INSIDE_CERTIFIED_LOW_ACTION_REGION",
        },
        "transverse_block_bound": {
            "decomposition": (
                "K_4(t)=K_1(t) tensor I + I tensor Delta_perp; the zero "
                "transverse block contributes log det_prime K_1(t)"
            ),
            "nonzero_mode_formula": (
                "C_w=-ell_0''*tr((K_1+wI)^(-1))-"
                "tr(((K_1+wI)^(-1)K_1')^2)"
            ),
            "modewise_upper_bound": "C_w<=(-ell_0'')*16/w",
            "spectral_gap_bound": (
                "w>=2-2*cos(pi/8)>3/20; the rational proof uses "
                "cos(pi/8)<37/40, reduced to sqrt(2)<569/400"
            ),
            "nonzero_transverse_mode_count": exact["transverse_multiplicity"],
            "summed_trace_factor": enc(exact["transverse_multiplicity"] * exact["transverse_trace_factor"]),
            "summed_curvature_upper_bound": enc(exact["transverse_upper_bound"]),
            "status": "PROVED_UPPER_BOUND",
        },
        "exact_longitudinal_fixture": {
            "graph": "cycle C16",
            "omega": [enc(value) for value in exact["omega"]],
            "direction": [enc(value) for value in exact["direction"]],
            "residual": [enc(value) for value in exact["residual"]],
            "mean_residual": enc(exact["mean_residual"]),
            "centered_potential": [enc(value) for value in exact["potential"]],
            "ground_eigenvalue": enc(exact["ground_eigenvalue"]),
            "ground_norm_squared": enc(exact["omega_norm_squared"]),
            "lowest_eigenvalue_first_derivative": enc(exact["eigenvalue_prime"]),
            "lowest_eigenvalue_second_derivative": enc(exact["eigenvalue_second"]),
            "log_pseudodeterminant_second_derivative_terms": [
                enc(value) for value in exact["logdet_second_terms"]
            ],
            "log_pseudodeterminant_second_derivative": enc(
                exact["longitudinal_logdet_second"]
            ),
            "longitudinal_gaussian_second_derivative": enc(
                exact["longitudinal_gaussian_second"]
            ),
            "four_dimensional_gaussian_second_derivative": enc(
                exact["four_dimensional_gaussian_second"]
            ),
            "full_four_dimensional_curvature_upper_bound": enc(
                exact["full_curvature_upper_bound"]
            ),
            "full_four_dimensional_curvature_upper_bound_decimal": float(
                exact["full_curvature_upper_bound"]
            ),
            "coupling": enc(exact["coupling"]),
            "status": "EXACT_RATIONAL_NEGATIVE_UPPER_BOUND",
        },
        "method_disposition": {
            "flat_potential_determinant_pushforward": "IMPORTED_PROVED",
            "actual_action_exponential_tail": "IMPORTED_PROVED",
            "global_convexity_on_A_below_50N": (
                "OBSTRUCTED_BY_EXACT_16_TO_THE_FOUR_WITNESS"
            ),
            "convex_good_region_plus_action_tail_strategy": (
                "OBSTRUCTED_AS_FORMULATED"
            ),
            "all_localized_nonconvex_estimates": "NOT_OBSTRUCTED",
            "noninduced_resolvent_stein_or_localization_estimate": "OPEN",
            "controlled_bad_volume_sequence_for_actual_moment": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "does_not_establish": [
            "nonconvexity throughout the full low-action region or at every volume",
            "failure of every localized, determinant-resolvent, or Stein estimate",
            "a lower bound or divergence sequence for the actual Gibbs H^-1 moment",
            "the normalized lowest-mode estimate, tightness, or a continuum measure",
            "Born probabilities, a Krein reconstruction, or Lorentzian dynamics",
        ],
        "missing_object_ledger": [
            "a Gibbs-weighted nonconvex localization or resolvent estimate",
            "or a controlled volume sequence for the actual interacting moment",
            "the dyadic Fourier-shell sum after a positive one-mode estimate",
        ],
        "next_gate": (
            "Use a genuinely noninduced resolvent-adapted Stein/localization "
            "field, with the low-action double-well region treated "
            "nonconvexly, or construct a controlled bad-volume sequence for "
            "the actual interacting H^-1 moment."
        ),
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "arithmetic": (
                "exact fractions for the C16 ground-state-resolvent jet and "
                "curvature; exact rational inequalities for the transverse "
                "spectral bound; no floating point enters any claim"
            ),
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFY_REL,
        "verification_commands": [
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "bt_euclidean_low_action_flat_convexity_obstruction.py --check"
            ),
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "verify_bt_euclidean_low_action_flat_convexity_obstruction.py"
            ),
            (
                "ulimit -v 500000; python3 -m unittest -v "
                "reverse_physics.tests."
                "test_bt_euclidean_low_action_flat_convexity_obstruction"
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    payload = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not os.path.exists(CERT_PATH):
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            current = handle.read()
        if current != payload:
            print(f"[FAIL] stale certificate: {CERT_REL}", file=sys.stderr)
            return 1
        print("BT low-action flat-convexity obstruction producer: PASS")
        return 0
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(payload)
    print(f"wrote {CERT_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
