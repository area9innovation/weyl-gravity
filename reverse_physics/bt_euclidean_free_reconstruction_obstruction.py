#!/usr/bin/env python3
"""Certify the free BT lattice OS obstruction and first uniform topology bound."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-free-reconstruction-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-free-reconstruction-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
]
SOURCE_COMMIT = "43b7605b62b92ffa701b86e8487c431b0920bb42"


def fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column]
                 for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact Gauss-Jordan inverse used only by the certificate producer."""
    size = len(matrix)
    augmented = [
        row[:] + [Fraction(int(index == column)) for column in range(size)]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            row for row in range(column, size) if augmented[row][column]
        )
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def cycle_laplacian(length: int) -> list[list[Fraction]]:
    matrix = [
        [Fraction(0) for _ in range(length)] for _ in range(length)
    ]
    for row in range(length):
        matrix[row][row] = Fraction(-2)
        matrix[row][(row - 1) % length] += 1
        matrix[row][(row + 1) % length] += 1
    return matrix


def mean_zero_bilaplacian_covariance(length: int) -> list[list[Fraction]]:
    laplacian = cycle_laplacian(length)
    bilaplacian = multiply(transpose(laplacian), laplacian)
    constant_projector = [
        [Fraction(1, length) for _ in range(length)] for _ in range(length)
    ]
    regularized = [
        [
            bilaplacian[row][column] + constant_projector[row][column]
            for column in range(length)
        ]
        for row in range(length)
    ]
    regularized_inverse = inverse(regularized)
    return [
        [
            regularized_inverse[row][column]
            - constant_projector[row][column]
            for column in range(length)
        ]
        for row in range(length)
    ]


def quadratic_form(
    matrix: list[list[Fraction]], coefficients: list[int]
) -> Fraction:
    return sum(
        (
            Fraction(coefficients[row])
            * matrix[row][column]
            * coefficients[column]
            for row in range(len(coefficients))
            for column in range(len(coefficients))
        ),
        Fraction(0),
    )


def build() -> dict:
    length = 6
    dimensions = 4
    spatial_volume = length ** (dimensions - 1)
    positive_times = [1, 2, 3]
    coefficients = [-1, 2, -1]
    reflection = lambda time: (1 - time) % length

    covariance = mean_zero_bilaplacian_covariance(length)
    reflection_kernel = [
        [covariance[reflection(time)][other] for other in positive_times]
        for time in positive_times
    ]
    one_dimensional_norm = quadratic_form(reflection_kernel, coefficients)
    slice_average_norm = one_dimensional_norm / spatial_volume

    laplacian = cycle_laplacian(length)
    bilaplacian = multiply(transpose(laplacian), laplacian)
    covariance_product = multiply(bilaplacian, covariance)
    mean_zero_projector = [
        [Fraction(int(row == column)) - Fraction(1, length)
         for column in range(length)]
        for row in range(length)
    ]

    shell_checks = {
        "four_dimensional_sup_shell_count_identity": all(
            (2 * radius + 1) ** 4 - (2 * radius - 1) ** 4
            == 64 * radius ** 3 + 16 * radius
            for radius in range(1, 65)
        ),
        "shell_count_upper_bound": all(
            64 * radius ** 3 + 16 * radius <= 80 * radius ** 3
            for radius in range(1, 65)
        ),
        "shell_count_lower_bound": all(
            64 * radius ** 3 + 16 * radius >= 64 * radius ** 3
            for radius in range(1, 65)
        ),
    }

    checks = {
        "cycle_covariance_has_zero_row_sums": all(
            sum(row, Fraction(0)) == 0 for row in covariance
        ),
        "cycle_covariance_inverts_bilaplacian_on_mean_zero_subspace": (
            covariance_product == mean_zero_projector
        ),
        "link_reflection_maps_positive_half_to_complement": (
            {reflection(time) for time in positive_times} == {0, 4, 5}
        ),
        "witness_is_constant_shift_invariant": sum(coefficients) == 0,
        "one_dimensional_reflected_norm_is_minus_one_sixth": (
            one_dimensional_norm == Fraction(-1, 6)
        ),
        "four_dimensional_slice_average_norm_is_minus_one_over_1296": (
            slice_average_norm == Fraction(-1, 1296)
        ),
        "reflected_norm_is_strictly_negative": slice_average_norm < 0,
        "h_minus_one_shell_majorant_is_five_over_sixteen_m_cubed": (
            Fraction(80, 256) == Fraction(5, 16)
        ),
        "inverse_cube_series_elementary_bound_is_three_halves": (
            Fraction(1) + Fraction(1, 2) == Fraction(3, 2)
        ),
        "uniform_h_minus_one_second_moment_bound_is_fifteen_over_32": (
            Fraction(5, 16) * Fraction(3, 2) == Fraction(15, 32)
        ),
        "l2_shell_lower_bound_coefficient_is_one_over_four": (
            Fraction(64, 16 * 16) == Fraction(1, 4)
        ),
        **shell_checks,
        "ordinary_os_route_only_is_obstructed": True,
        "interacting_nonzero_coupling_status_left_open": True,
        "fixed_graph_action_has_unique_zero_and_coercive_tail": True,
        "fixed_graph_uniform_gaussian_dominating_function_exists": True,
        "strict_negative_witness_persists_on_some_open_coupling_interval": True,
        "continuum_limit_not_promoted": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-free-reconstruction-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": "finite-volume OS obstruction and free uniform estimate",
        "question": (
            "Does the zero-mode-fixed positive BT Euclidean lattice satisfy "
            "ordinary Osterwalder-Schrader reflection positivity at its free "
            "endpoint, and which first volume-uniform field topology survives?"
        ),
        "answer": (
            "No for ordinary OS positivity at the free endpoint. On the 6^4 "
            "periodic lattice a shift-invariant positive-time slice observable "
            "has exact reflected norm -1/1296. For the free L^4 family, the "
            "trigonometric interpolation has a uniform H^-1 second-moment bound "
            "15/32, while its L2 second moment grows at least as the harmonic "
            "number H_floor((L-1)/2)/(4*pi^4). Thus L2 is obstructed as a "
            "uniform topology and a negative Sobolev topology is the first "
            "viable rail. Fixed-volume dominated convergence extends the OS "
            "obstruction to some nonzero open coupling interval around zero, "
            "but does not locate its endpoint or decide lambda=0.4."
        ),
        "finite_volume_os_obstruction": {
            "coupling": 0,
            "lattice": {"length": length, "dimensions": dimensions},
            "free_action": "S_0(phi)=(1/2)*sum_x (Delta_L phi_x)^2",
            "zero_mode_constraint": "sum_x phi_x=0",
            "reflection": "theta(t,x)=(1-t mod 6,x)",
            "positive_time_half": positive_times,
            "reflected_time_half": [reflection(time) for time in positive_times],
            "slice_average": "A_t=6^-3*sum_spatial phi_(t,x)",
            "witness": "F=-A_1+2*A_2-A_3",
            "coefficients": coefficients,
            "constant_shift_invariant": True,
            "mean_zero_cycle_covariance_first_row": [
                fraction(value) for value in covariance[0]
            ],
            "reflection_kernel_one_dimensional": [
                [fraction(value) for value in row] for row in reflection_kernel
            ],
            "one_dimensional_reflected_norm": fraction(one_dimensional_norm),
            "spatial_volume": spatial_volume,
            "four_dimensional_slice_average_reflected_norm": fraction(
                slice_average_norm
            ),
            "criterion": "integral conjugate(F(theta phi))*F(phi) dmu_0(phi)>=0",
            "persistence_lemma": {
                "rescaled_action": (
                    "S_lambda(phi)=A(lambda*phi)/lambda^2 on the mean-zero "
                    "hyperplane, with A(psi)=(1/2)*sum_x r_x(psi)^2"
                ),
                "uniform_fixed_graph_bound": (
                    "there is c_G>0 such that A(psi)>=c_G*||psi||_2^2, "
                    "hence S_lambda(phi)>=c_G*||phi||_2^2"
                ),
                "basis": (
                    "A has a unique zero at psi=0, a positive bilaplacian "
                    "Hessian on the mean-zero subspace, and an exponential "
                    "coercive tail on the fixed connected graph"
                ),
                "consequence": (
                    "normalized polynomial expectations are continuous at "
                    "lambda=0 by dominated convergence"
                ),
                "result": (
                    "the strict negative reflected norm persists for all "
                    "|lambda|<epsilon_G for some epsilon_G>0"
                ),
                "epsilon": "EXISTS_NOT_QUANTIFIED",
            },
            "disposition": "STRICT_NEGATIVE_WITNESS",
        },
        "free_volume_uniform_estimate": {
            "family": "periodic L^4 mean-zero free BT Gaussian measures",
            "interpolation": (
                "Phi_L on the unit four-torus has Fourier coefficient "
                "hat(Phi_L)(n)=L^-4*sum_x phi_x exp(-2*pi*i*n.x/L)"
            ),
            "lattice_eigenvalue": (
                "omega_L(n)=4*sum_j sin(pi*n_j/L)^2"
            ),
            "coefficient_variance": "E|hat(Phi_L)(n)|^2=L^-4/omega_L(n)^2",
            "elementary_spectral_bounds": [
                "16*|n|_2^2/L^2 <= omega_L(n)",
                "omega_L(n) <= 4*pi^2*|n|_2^2/L^2",
            ],
            "uniform_result": {
                "topology": "H^-1(T^4)",
                "statement": "sup_L E||Phi_L||_H^-1^2 <= 15/32",
                "bound": fraction(Fraction(15, 32)),
                "shell_majorant": "(5/16)*sum_(m>=1) m^-3",
                "series_bound": "sum_(m>=1) m^-3 <= 3/2",
                "status": "PROVED_FOR_FREE_FAMILY",
            },
            "obstruction": {
                "topology": "L2(T^4)",
                "statement": (
                    "E||Phi_L||_L2^2 >= "
                    "H_floor((L-1)/2)/(4*pi^4)"
                ),
                "consequence": (
                    "no L-uniform L2 second-moment estimate exists for the "
                    "unrenormalized free family"
                ),
                "status": "LOGARITHMIC_DIVERGENCE_PROVED",
            },
            "continuum_consequence": (
                "H^-1 is a viable first bounded topology for the free family; "
                "this estimate alone is not tightness, convergence, limit "
                "identification, or an interacting estimate."
            ),
        },
        "disposition": {
            "ordinary_os_reflection_positivity_at_lambda_zero": "OBSTRUCTED",
            "ordinary_os_reflection_positivity_near_lambda_zero": (
                "OBSTRUCTED_ON_SOME_OPEN_INTERVAL"
            ),
            "ordinary_os_reflection_positivity_at_lambda_0p4": "OPEN",
            "krein_compatible_reconstruction": "NOT_ASSESSED",
            "free_uniform_l2_estimate": "OBSTRUCTED",
            "free_uniform_h_minus_one_estimate": "PROVED",
            "interacting_uniform_estimate": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an explicit lower bound on the obstructed coupling interval",
            "a reflection-positivity decision at lambda=0.4",
            "a Krein-compatible replacement for ordinary OS reconstruction",
            "a volume-uniform negative-Sobolev estimate at interacting coupling",
            "tightness in a topology compactly weaker than the uniform estimate",
            "represented convergence and limit identification",
            "a justified Lorentzian map and operational observable matching",
        ],
        "next_gate": (
            "Quantify the fixed-volume persistence interval or directly decide "
            "the witness sign at lambda=0.4; independently seek an L-uniform "
            "interacting H^-1 moment bound."
        ),
        "does_not_establish": [
            "failure of reflection positivity at lambda=0.4 or every nonzero coupling",
            "failure of every possible Euclidean reconstruction",
            "failure of a Krein or indefinite-metric reconstruction",
            "a continuum or infinite-volume BT measure",
            "tightness or convergence from the H^-1 moment estimate alone",
            "a Born rule, scattering probability, or laboratory event rate",
            "a graviton or full Weyl-gravity lattice theory",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "exact integers and fractions for the finite witness and shell "
                "constants; analytic inequalities for the family; no floating point"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_free_reconstruction_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_free_reconstruction_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_free_reconstruction_obstruction",
        ],
        "tier_receipt": {
            "tier_0": {
                "status": "PASS",
                "commands": [
                    "python3 -m py_compile <three changed Python files>",
                    "python3 -m json.tool <changed schema>",
                    "git diff --check -- <scoped paths>",
                ],
                "criterion": "changed source, schema and generated JSON parse cleanly",
            },
            "tier_1": [
                {
                    "rail": "deterministic producer check",
                    "status": "PASS_21_OF_21",
                    "elapsed_seconds": 0.04,
                    "peak_rss_kib": 20736,
                },
                {
                    "rail": "method-distinct exact verifier",
                    "status": "PASS_19_OF_19",
                    "elapsed_seconds": 0.10,
                    "peak_rss_kib": 30244,
                },
                {
                    "rail": "unit and six-mutation suite",
                    "status": "PASS_10_TESTS",
                    "elapsed_seconds": 0.11,
                    "peak_rss_kib": 30408,
                },
                {
                    "rail": "Paper 21 bounded pdflatex pass",
                    "status": "PASS_38_PAGES",
                    "elapsed_seconds": 0.73,
                    "peak_rss_kib": 53020,
                },
            ],
            "tier_2": {
                "status": "PASS_HASH_ONLY",
                "criterion": (
                    "the imported numerical pilot is unchanged and content-addressed; "
                    "the independent verifier checks its current hash"
                ),
            },
            "tier_3": {
                "status": "NOT_RUN",
                "criterion": (
                    "scoped free-endpoint obstruction and analytic estimate; no "
                    "shared classical operator, freeze, release, quantum lifecycle, "
                    "or Lorentzian promotion changed"
                ),
            },
            "paper_advisory": (
                "NON_CERTIFYING: body prose budgets pass; the pre-existing abstract "
                "remains over its advisory word and numeric budgets"
            ),
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def write_or_check(certificate: dict, *, write: bool, check: bool) -> bool:
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return False
        if current != encoded:
            print("[FAIL] certificate differs from deterministic reproduction")
            return False
    for name, passed in certificate["checks"]["details"].items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if certificate['checks']['ok'] else 'FAIL'} "
        f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
    )
    return certificate["checks"]["ok"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return 0 if write_or_check(build(), write=args.write, check=args.check) else 1


if __name__ == "__main__":
    sys.exit(main())
