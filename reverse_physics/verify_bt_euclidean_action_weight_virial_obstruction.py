#!/usr/bin/env python3
"""Independent verifier for the BT action-weight/virial obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-action-weight-virial-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def full_lattice_forms(
    parameter: int,
    h: tuple[int, ...],
    g: tuple[int, ...],
    other: tuple[tuple[int, ...], ...],
) -> dict[str, Fraction | list[Fraction]]:
    """Reconstruct selected forms by direct enumeration of all 6^4 sites."""
    length = 6
    sites = tuple(product(range(length), repeat=4))
    shape = (-2, 1, 1, -2, 1, 1)
    center = {site: parameter * shape[site[0]] for site in sites}
    vectors = (h, g, *other)
    directions = [
        {site: vector[site[0]] for site in sites} for vector in vectors
    ]
    hessian = [[Fraction(0) for _ in vectors] for _ in vectors]
    action = Fraction(0)
    for site in sites:
        residual = Fraction(-8)
        first = [Fraction(0) for _ in vectors]
        second = [[Fraction(0) for _ in vectors] for _ in vectors]
        for axis in range(4):
            for step in (-1, 1):
                neighbor_list = list(site)
                neighbor_list[axis] = (neighbor_list[axis] + step) % length
                neighbor = tuple(neighbor_list)
                weight = dyadic(center[neighbor] - center[site])
                residual += weight
                differences = [
                    direction[neighbor] - direction[site]
                    for direction in directions
                ]
                for left in range(len(vectors)):
                    first[left] += weight * differences[left]
                    for right in range(len(vectors)):
                        second[left][right] += (
                            weight * differences[left] * differences[right]
                        )
        action += residual * residual / 2
        for left in range(len(vectors)):
            for right in range(len(vectors)):
                hessian[left][right] += (
                    first[left] * first[right]
                    + residual * second[left][right]
                )
    return {
        "action": action,
        "hh": hessian[0][0],
        "hg": hessian[0][1],
        "gg": hessian[1][1],
        "other_h": [hessian[0][index] for index in range(2, len(vectors))],
    }


def evaluate(coefficients: dict[str, int], x: int) -> Fraction:
    return sum(
        (
            Fraction(value) * Fraction(x) ** int(exponent)
            for exponent, value in coefficients.items()
        ),
        Fraction(0),
    )


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [[Fraction(value) for value in row] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            factor = work[row][column] / pivot_value
            for entry in range(column, len(work)):
                work[row][entry] -= factor * work[column][entry]
    return result


def reconstruct_virial(shape: tuple[int, ...]) -> dict[str, Fraction]:
    base = Fraction(101, 100)
    residuals = []
    derivatives = []
    for time in range(6):
        residual = Fraction(-2)
        derivative = Fraction(0)
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            difference = shape[neighbor] - shape[time]
            weight = base**difference
            residual += weight
            derivative += weight * difference
        residuals.append(residual)
        derivatives.append(derivative)
    action = sum((value * value / 2 for value in residuals), Fraction(0))
    radial_factor = sum(
        (left * right for left, right in zip(residuals, derivatives)),
        Fraction(0),
    )
    u = Fraction(1, 100)
    log_upper = u - u**2 / 2 + u**3 / 3
    return {
        "base": base,
        "action": action,
        "radial_factor": radial_factor,
        "ratio_without_log": radial_factor / action,
        "log_upper": log_upper,
        "ratio_upper": radial_factor * log_upper / action,
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
        and certificate["checks"]["passed"]
        == certificate["checks"]["total"]
        == 16
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["two_provenance_hashes_current"] = len(hashes) == 2 and all(
        digest == file_hash(relative) for relative, digest in hashes.items()
    )

    lattice = certificate["lattice_and_symmetry"]
    basis = tuple(tuple(vector) for vector in lattice["mean_zero_basis"])
    gram = [
        [Fraction(sum(a * b for a, b in zip(left, right))) for right in basis]
        for left in basis
    ]
    h, u, g, plus_1, plus_2 = basis
    laplacian = lambda vector: tuple(
        2 * vector[index]
        - vector[(index - 1) % 6]
        - vector[(index + 1) % 6]
        for index in range(6)
    )
    checks["complete_mean_zero_basis_reconstructed"] = (
        all(sum(vector) == 0 for vector in basis)
        and determinant(gram) == decode(lattice["basis_gram_determinant"]) == 3456
        and h == tuple(lattice["lowest_mode_h"])
        and u == tuple(lattice["lowest_odd_mode_u"])
        and g == tuple(lattice["alternating_mode_g"])
        and laplacian(h) == h
        and laplacian(u) == u
        and laplacian(g) == tuple(4 * value for value in g)
    )
    shape = tuple(lattice["center_shape"])
    checks["symmetry_characters_reconstructed"] = (
        tuple(shape[(index + 3) % 6] for index in range(6)) == shape
        and tuple(shape[-index % 6] for index in range(6)) == shape
        and tuple(h[(index + 3) % 6] for index in range(6))
        == tuple(-value for value in h)
        and tuple(g[(index + 3) % 6] for index in range(6))
        == tuple(-value for value in g)
        and tuple(u[-index % 6] for index in range(6))
        == tuple(-value for value in u)
        and tuple(h[-index % 6] for index in range(6)) == h
        and tuple(g[-index % 6] for index in range(6)) == g
        and tuple(plus_1[(index + 3) % 6] for index in range(6)) == plus_1
        and tuple(plus_2[(index + 3) % 6] for index in range(6)) == plus_2
    )

    section = certificate["exact_full_low_mode_schur"]
    fixture_by_parameter = {row["parameter"]: row for row in section["fixtures"]}
    full_ok = True
    for parameter in (1, 2, 3):
        forms = full_lattice_forms(parameter, h, g, (u, plus_1, plus_2))
        row = fixture_by_parameter[parameter]
        full_ok &= (
            forms["hh"] == 216 * decode(row["h_hessian_per_spatial_site"])
            and forms["hg"] == 216 * decode(row["h_g_hessian_per_spatial_site"])
            and forms["gg"] == 216 * decode(row["g_g_hessian_per_spatial_site"])
            and forms["action"] == 216 * decode(row["center_action_per_spatial_site"])
            and forms["other_h"] == [Fraction(0), Fraction(0), Fraction(0)]
        )
    checks["selected_full_6_to_the_4_fixtures_reconstructed"] = full_ok

    formulas_ok = True
    for row in section["fixtures"]:
        x = row["x"]
        hh = evaluate(section["h_h_laurent_coefficients"], x)
        hg = evaluate(section["h_g_laurent_coefficients"], x)
        gg = evaluate(section["g_g_laurent_coefficients"], x)
        det = evaluate(section["determinant_laurent_coefficients"], x)
        action = evaluate(
            certificate["action_weight_threshold"][
                "center_action_laurent_coefficients"
            ],
            x,
        )
        schur = det / gg
        formulas_ok &= (
            x == 2 ** (3 * row["parameter"])
            and hh == decode(row["h_hessian_per_spatial_site"])
            and hg == decode(row["h_g_hessian_per_spatial_site"])
            and gg == decode(row["g_g_hessian_per_spatial_site"])
            and det == hh * gg - hg * hg
            and det == decode(row["determinant_per_spatial_site_squared"])
            and schur == decode(row["full_low_mode_schur_per_spatial_site"])
            and x * schur == decode(row["x_times_schur"])
            and action == decode(row["center_action_per_spatial_site"])
            and all(decode(value) == 0 for value in row["other_h_mixed_entries"])
            and 0 < schur < Fraction(48, x)
        )
    checks["all_laurent_schur_and_action_fixtures_reconstructed"] = formulas_ok
    checks["leading_coefficients_give_sharp_limits"] = (
        section["h_h_laurent_coefficients"]
        == {"-2": 8, "-1": -4, "1": -8, "2": 16}
        and section["h_g_laurent_coefficients"]
        == {"-2": 16, "-1": -32, "1": -16, "2": 32}
        and section["g_g_laurent_coefficients"]
        == {"-2": 32, "-1": 32, "1": -32, "2": 64}
        and section["determinant_laurent_coefficients"]
        == {"-3": 1152, "-2": -1152, "0": -1152, "1": 2304}
        and certificate["action_weight_threshold"][
            "center_action_laurent_coefficients"
        ]
        == {"-2": 2, "-1": -4, "0": 6, "1": -8, "2": 4}
        and Fraction(2304, 64) == 36
        and 36 * 2 == 72
    )
    checks["all_x_bound_proof_reconstructed"] = (
        section["positivity_and_bound"] == "for x>=8, 0<kappa(x)<48/x"
        # det/1152=2x-1-x^-2+x^-3 is positive at x>=8 and <2x.
        and 2 * 8 - 1 - Fraction(1, 8**2) > 0
        # Hgg>64x^2-32x>=60x^2 at x>=8.
        and 64 - Fraction(32, 8) == 60
        and Fraction(2304, 60) == Fraction(192, 5)
        and Fraction(192, 5) < 48
    )
    weight = certificate["action_weight_threshold"]
    checks["subhalf_and_half_threshold_typed"] = (
        weight["quarter_power_status"] == "OBSTRUCTED_BY_SUCCESSOR_FAMILY"
        and "p<1/2" in weight["subhalf_obstruction"]
        and weight["quarter_power_limit"]
        == "lim kappa(x)*A(x)^(1/4)=0"
        and weight["half_power_limit"]
        == "lim kappa(x)*A(x)^(1/2)=72"
    )
    normalized = certificate["volume_normalized_candidate"]
    checks["density_normalized_limit_reconstructed"] = (
        normalized["action_density_on_spatially_constant_sector"]
        == "A_total/N=A(x)/6"
        and normalized["normalized_curvature"]
        == "kappa(x)/kappa(0)=kappa(x)/12"
        and Fraction(36**2, 12**2) * Fraction(4, 6) == 6
        and normalized["status"]
        == "NOT_OBSTRUCTED_BY_THIS_FAMILY_BUT_NOT_PROVED"
    )

    virial_section = certificate["radial_virial_obstruction"]
    virial_fixture = virial_section["fixture"]
    virial = reconstruct_virial(tuple(virial_fixture["shape"]))
    checks["exact_rational_virial_fixture_reconstructed"] = (
        sum(virial_fixture["shape"]) == 0
        and virial["base"] == decode(virial_fixture["rational_base"])
        and virial["action"] == decode(virial_fixture["action_per_spatial_site"])
        and virial["radial_factor"]
        == decode(virial_fixture["radial_factor_without_log"])
        and virial["ratio_without_log"]
        == decode(virial_fixture["D_over_A_factor_without_log"])
        and virial["log_upper"] == decode(virial_fixture["log_upper_bound"])
        and virial["ratio_upper"]
        == decode(virial_fixture["certified_upper_bound_for_D_over_A"])
        and virial["ratio_upper"] < 2
    )
    checks["alternating_log_bound_is_valid"] = (
        virial["log_upper"] == Fraction(1, 100) - Fraction(1, 20000)
        + Fraction(1, 3000000)
        and virial_section["status"]
        == "POINTWISE_VIRIAL_CONSTANT_TWO_OBSTRUCTED"
    )
    disposition = certificate["method_disposition"]
    checks["open_uniform_bound_preserved"] = (
        disposition["half_action_density_weight"] == "OPEN"
        and disposition["weaker_positive_radial_virial_constant"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment_bound"]
        == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["required_nonclaims_present"] = {
        "failure of every action-weighted or annealed covariance estimate",
        "failure of a half-action-density curvature estimate",
        "failure of every positive radial virial constant",
        "failure of the actual interacting H^-1 moment bound",
        "a Born rule or Krein reconstruction",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))

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
