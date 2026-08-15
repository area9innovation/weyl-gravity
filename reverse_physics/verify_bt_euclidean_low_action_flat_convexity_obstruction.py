#!/usr/bin/env python3
"""Independent verifier for the low-action BT flat-convexity obstruction."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_ACTION_FLAT_"
    "CONVEXITY_OBSTRUCTION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-low-action-flat-"
    "convexity-obstruction-v1.schema.json"
)
TAIL_CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_"
    "CURRENT_SPIKE_GATE_V1.json"
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
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
        value = work[column][column]
        result *= value
        for entry in range(column, len(work)):
            work[column][entry] /= value
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            for entry in range(column, len(work)):
                work[row][entry] -= scale * work[column][entry]
    return result


def solve(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    size = len(matrix)
    work = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular interpolation matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        value = work[column][column]
        work[column] = [entry / value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [row[-1] for row in work]


def interpolate_at_integer_points(values: list[Fraction]) -> list[Fraction]:
    size = len(values)
    vandermonde = [
        [Fraction(point) ** power for power in range(size)]
        for point in range(size)
    ]
    return solve(vandermonde, values)


def characteristic_coefficients(
    kinetic: list[list[Fraction]], direction: list[Fraction]
) -> dict[tuple[int, int], Fraction]:
    """Interpolate det(K+t*diag(h)-zI), independently of K-plus."""

    size = len(kinetic)
    z_coefficients_by_t: list[list[Fraction]] = []
    for t_value in range(3):
        determinant_values = []
        for z_value in range(size + 1):
            matrix = [row[:] for row in kinetic]
            for index in range(size):
                matrix[index][index] += (
                    Fraction(t_value) * direction[index] - z_value
                )
            determinant_values.append(determinant(matrix))
        z_coefficients_by_t.append(
            interpolate_at_integer_points(determinant_values)
        )
    result: dict[tuple[int, int], Fraction] = {}
    for z_power in range(size + 1):
        t_coefficients = interpolate_at_integer_points(
            [row[z_power] for row in z_coefficients_by_t]
        )
        for t_power, value in enumerate(t_coefficients):
            if value:
                result[(t_power, z_power)] = value
    return result


def partial(
    polynomial: dict[tuple[int, int], Fraction], dt: int, dz: int
) -> Fraction:
    coefficient = polynomial.get((dt, dz), Fraction(0))
    return coefficient * math.factorial(dt) * math.factorial(dz)


def reconstruct() -> dict:
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
    size = 16
    direction = [Fraction(0) for _ in range(size)]
    direction[0] = 1
    direction[8] = -1
    residual = [
        omega[(site - 1) % size] / omega[site]
        + omega[(site + 1) % size] / omega[site]
        - 2
        for site in range(size)
    ]
    mean = sum(residual, Fraction(0)) / size
    potential = [value - mean for value in residual]
    kinetic = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        kinetic[site][site] = 2 + residual[site]
        kinetic[site][(site - 1) % size] = -1
        kinetic[site][(site + 1) % size] = -1

    polynomial = characteristic_coefficients(kinetic, direction)
    p_z = partial(polynomial, 0, 1)
    p_t = partial(polynomial, 1, 0)
    p_tt = partial(polynomial, 2, 0)
    p_tz = partial(polynomial, 1, 1)
    p_zz = partial(polynomial, 0, 2)
    eigenvalue_prime = -p_t / p_z
    eigenvalue_second = -(
        p_tt
        + 2 * p_tz * eigenvalue_prime
        + p_zz * eigenvalue_prime**2
    ) / p_z
    determinant_value = -p_z
    determinant_prime = -(
        p_tz + p_zz * eigenvalue_prime
    )
    determinant_second = -(
        partial(polynomial, 2, 1)
        + 2 * partial(polynomial, 1, 2) * eigenvalue_prime
        + partial(polynomial, 0, 3) * eigenvalue_prime**2
        + p_zz * eigenvalue_second
    )
    logdet_second = (
        determinant_second / determinant_value
        - (determinant_prime / determinant_value) ** 2
    )
    norm_squared = sum((value * value for value in omega), Fraction(0))
    hellmann_prime = sum(
        (direction[index] * omega[index] ** 2 for index in range(size)),
        Fraction(0),
    ) / norm_squared
    coupling = Fraction(2, 5)
    gaussian_one = (
        sum((value * value for value in direction), Fraction(0))
        + size * (eigenvalue_prime**2 - mean * eigenvalue_second)
    ) / (coupling * coupling)
    action_one = sum((value * value for value in residual), Fraction(0)) / 2

    # cos(pi/8)=sqrt(2+sqrt(2))/2 < 37/40 follows by two
    # positive squarings from sqrt(2)<569/400.
    radical_bound_ok = Fraction(2) < Fraction(569, 400) ** 2
    transverse_gap_lower = Fraction(3, 20)
    transverse_count = size**3 - 1
    trace_factor = Fraction(size, 1) / transverse_gap_lower
    transverse_upper = -eigenvalue_second * transverse_count * trace_factor
    gaussian_four = size**3 * gaussian_one
    full_upper = gaussian_four + logdet_second + transverse_upper
    return {
        "omega": omega,
        "direction": direction,
        "residual": residual,
        "mean": mean,
        "potential": potential,
        "kinetic": kinetic,
        "norm_squared": norm_squared,
        "hellmann_prime": hellmann_prime,
        "eigenvalue_prime": eigenvalue_prime,
        "eigenvalue_second": eigenvalue_second,
        "logdet_second": logdet_second,
        "gaussian_one": gaussian_one,
        "gaussian_four": gaussian_four,
        "action_density": action_one / size,
        "radical_bound_ok": radical_bound_ok,
        "transverse_count": transverse_count,
        "trace_factor": trace_factor,
        "transverse_upper": transverse_upper,
        "full_upper": full_upper,
    }


def verify(certificate: dict | None = None) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if certificate is None:
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            certificate = json.load(handle)
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    with open(os.path.join(ROOT, TAIL_CERT_REL), encoding="utf-8") as handle:
        imported_tail = json.load(handle)["lambda_point_four_bulk_tail"]
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
    except jsonschema.ValidationError as error:
        failures.append(f"schema: {error.message}")
        return False, failures

    exact = reconstruct()
    fixture = certificate["exact_longitudinal_fixture"]
    low_action = certificate["low_action_statement"]
    transverse = certificate["transverse_block_bound"]
    disposition = certificate["method_disposition"]

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(
        [dec(value) for value in fixture["omega"]] == exact["omega"],
        "ground vector drift",
    )
    require(
        [dec(value) for value in fixture["direction"]] == exact["direction"],
        "direction drift",
    )
    require(
        [dec(value) for value in fixture["residual"]] == exact["residual"],
        "residual drift",
    )
    require(
        [dec(value) for value in fixture["centered_potential"]]
        == exact["potential"],
        "potential drift",
    )
    require(
        all(
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
        "declared ground vector is not null",
    )
    require(
        exact["eigenvalue_prime"] == exact["hellmann_prime"],
        "characteristic and Hellmann--Feynman derivatives disagree",
    )
    require(
        dec(fixture["lowest_eigenvalue_first_derivative"])
        == exact["eigenvalue_prime"],
        "first eigenvalue derivative drift",
    )
    require(
        dec(fixture["lowest_eigenvalue_second_derivative"])
        == exact["eigenvalue_second"],
        "second eigenvalue derivative drift",
    )
    require(exact["eigenvalue_second"] < 0, "ground eigenvalue is not concave")
    require(
        dec(fixture["log_pseudodeterminant_second_derivative"])
        == exact["logdet_second"],
        "longitudinal log determinant curvature drift",
    )
    require(
        dec(fixture["longitudinal_gaussian_second_derivative"])
        == exact["gaussian_one"],
        "longitudinal Gaussian curvature drift",
    )
    require(
        dec(fixture["four_dimensional_gaussian_second_derivative"])
        == exact["gaussian_four"],
        "four-dimensional Gaussian curvature drift",
    )
    require(exact["radical_bound_ok"], "rational radical bound failed")
    require(
        exact["transverse_count"] == transverse["nonzero_transverse_mode_count"]
        == 4095,
        "transverse mode count drift",
    )
    require(
        dec(transverse["summed_trace_factor"])
        == exact["transverse_count"] * exact["trace_factor"]
        == 436800,
        "transverse trace factor drift",
    )
    require(
        dec(transverse["summed_curvature_upper_bound"])
        == exact["transverse_upper"],
        "transverse curvature bound drift",
    )
    require(
        dec(low_action["action_density"])
        == exact["action_density"]
        == Fraction(5121, 160)
        < dec(low_action["certified_tail_cutoff_density"])
        == 50,
        "low-action comparison drift",
    )
    require(
        low_action["certified_tail_cutoff_density"]
        == imported_tail["action_density_cutoff"]
        and low_action["coupling"] == imported_tail["lambda"]
        and low_action["tail_rate"] == imported_tail["tail_rate"],
        "imported action-tail parameters drift",
    )
    require(
        dec(fixture["full_four_dimensional_curvature_upper_bound"])
        == exact["full_upper"]
        < 0,
        "full curvature upper bound is not negative",
    )
    require(
        disposition["global_convexity_on_A_below_50N"]
        == "OBSTRUCTED_BY_EXACT_16_TO_THE_FOUR_WITNESS",
        "low-action convexity obstruction weakened",
    )
    require(
        disposition["controlled_bad_volume_sequence_for_actual_moment"]
        == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"]
        == "OPEN",
        "method obstruction promoted to moment divergence",
    )
    require(
        disposition["born_rule"] == "NOT_ESTABLISHED"
        and disposition["krein_reconstruction"] == "NOT_ASSESSED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "reconstruction boundary weakened",
    )
    for item in certificate["provenance"]["inputs"]:
        require(
            item["sha256"] == sha256(item["path"]),
            f"hash drift: {item['path']}",
        )
    return not failures, failures


def main() -> int:
    ok, failures = verify()
    if not ok:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    print("BT low-action flat-convexity obstruction verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
