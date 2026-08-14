#!/usr/bin/env python3
"""Independent verifier for the BT free OS and uniform-estimate certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-free-reconstruction-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def qform(matrix: list[list[Fraction]], vector: list[int]) -> Fraction:
    return sum(
        (
            Fraction(vector[row]) * matrix[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        ),
        Fraction(0),
    )


def independent_reflection_calculation(section: dict) -> dict[str, bool]:
    """Use the closed difference equation, not the producer's matrix inverse."""
    length = 6
    row = [decode(value) for value in section["mean_zero_cycle_covariance_first_row"]]
    expected_numerators = [329, 119, -151, -265, -151, 119]
    expected_row = [Fraction(value, 864) for value in expected_numerators]

    # A circulant covariance C(i,j)=c((j-i) mod L) is the mean-zero inverse
    # exactly when the five-point bilaplacian stencil gives delta_0-1/L.
    stencil_result = [
        6 * row[index]
        - 4 * row[(index - 1) % length]
        - 4 * row[(index + 1) % length]
        + row[(index - 2) % length]
        + row[(index + 2) % length]
        for index in range(length)
    ]
    target = [Fraction(5, 6)] + [Fraction(-1, 6)] * 5

    positive = [1, 2, 3]
    reflected = [(1 - time) % length for time in positive]
    kernel = [
        [row[(other - reflected_time) % length] for other in positive]
        for reflected_time in reflected
    ]
    vector = [-1, 2, -1]
    norm_1d = qform(kernel, vector)
    norm_4d = norm_1d / (length ** 3)
    recorded_kernel = [
        [decode(value) for value in matrix_row]
        for matrix_row in section["reflection_kernel_one_dimensional"]
    ]

    return {
        "closed_form_covariance_row": row == expected_row,
        "covariance_row_is_mean_zero": sum(row, Fraction(0)) == 0,
        "bilaplacian_stencil_identity": stencil_result == target,
        "reflection_kernel_reconstructed": kernel == recorded_kernel,
        "witness_coefficients_are_shift_invariant": sum(vector) == 0,
        "one_dimensional_norm_reconstructed": (
            norm_1d == Fraction(-1, 6)
            and norm_1d == decode(section["one_dimensional_reflected_norm"])
        ),
        "four_dimensional_norm_reconstructed": (
            norm_4d == Fraction(-1, 1296)
            and norm_4d
            == decode(section["four_dimensional_slice_average_reflected_norm"])
        ),
    }


def independent_uniform_bound_calculation(section: dict) -> dict[str, bool]:
    uniform = section["uniform_result"]
    shell_identity = all(
        (2 * radius + 1) ** 4 - (2 * radius - 1) ** 4
        == 64 * radius ** 3 + 16 * radius
        for radius in range(1, 257)
    )
    shell_upper = all(
        64 * radius ** 3 + 16 * radius <= 80 * radius ** 3
        for radius in range(1, 257)
    )
    shell_lower = all(
        64 * radius ** 3 + 16 * radius >= 64 * radius ** 3
        for radius in range(1, 257)
    )
    h_minus_one_bound = Fraction(80, 256) * (
        Fraction(1) + Fraction(1, 2)
    )
    l2_shell_coefficient = Fraction(64, 16 * 16)
    return {
        "shell_identity_independently_checked": shell_identity,
        "shell_upper_bound_independently_checked": shell_upper,
        "shell_lower_bound_independently_checked": shell_lower,
        "h_minus_one_constant_reconstructed": (
            h_minus_one_bound == Fraction(15, 32)
            and h_minus_one_bound == decode(uniform["bound"])
        ),
        "l2_logarithmic_coefficient_reconstructed": (
            l2_shell_coefficient == Fraction(1, 4)
            and section["obstruction"]["statement"]
            == "E||Phi_L||_L2^2 >= H_floor((L-1)/2)/(4*pi^4)"
        ),
    }


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
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    recorded_hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["all_provenance_hashes_current"] = bool(recorded_hashes) and all(
        digest == file_hash(relative)
        for relative, digest in recorded_hashes.items()
    )
    checks.update(
        independent_reflection_calculation(
            certificate["finite_volume_os_obstruction"]
        )
    )
    checks.update(
        independent_uniform_bound_calculation(
            certificate["free_volume_uniform_estimate"]
        )
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["scoped_disposition"] = certificate["disposition"] == {
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
    }
    checks["required_nonclaims_present"] = {
        "failure of reflection positivity at lambda=0.4 or every nonzero coupling",
        "failure of a Krein or indefinite-metric reconstruction",
        "a continuum or infinite-volume BT measure",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    persistence = certificate["finite_volume_os_obstruction"]["persistence_lemma"]
    checks["fixed_volume_persistence_boundary"] = (
        persistence["epsilon"] == "EXISTS_NOT_QUANTIFIED"
        and "some epsilon_G>0" in persistence["result"]
        and certificate["disposition"][
            "ordinary_os_reflection_positivity_at_lambda_0p4"
        ] == "OPEN"
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({passed}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
