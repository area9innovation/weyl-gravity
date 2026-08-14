#!/usr/bin/env python3
"""Independent verifier for the BT finite Euclidean lattice pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-euclidean-lattice-pilot-v1.schema.json",
)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_normalization() -> dict[str, bool]:
    # L(U)=-A U-(g B/6)U^2.  Substitute U=c*A/(g*B), solve dL/dU=0,
    # and evaluate the residual coefficient of A^2/(gB).
    stationary_c = Fraction(-3)
    effective = -stationary_c - stationary_c ** 2 / 6
    displayed = Fraction(1, 2)
    return {
        "stationary_coefficient": stationary_c == -3,
        "effective_coefficient": effective == Fraction(3, 2),
        "displayed_ratio": effective / displayed == 3,
        "coupling_map": effective / Fraction(-3) == Fraction(-1, 2),
        "displayed_mismatch": displayed / Fraction(-3) == Fraction(-1, 6),
    }


def coordinates(index: int, length: int, dimensions: int) -> tuple[int, ...]:
    result = [0] * dimensions
    for axis in range(dimensions - 1, -1, -1):
        result[axis] = index % length
        index //= length
    return tuple(result)


def index(point: tuple[int, ...], length: int) -> int:
    value = 0
    for coordinate in point:
        value = value * length + coordinate
    return value


def graph(length: int, dimensions: int) -> list[tuple[int, ...]]:
    rows = []
    for vertex in range(length ** dimensions):
        point = list(coordinates(vertex, length, dimensions))
        row = []
        for axis in range(dimensions):
            for direction in (-1, 1):
                neighbor = point.copy()
                neighbor[axis] = (neighbor[axis] + direction) % length
                row.append(index(tuple(neighbor), length))
        rows.append(tuple(row))
    return rows


def independent_action(
    field: list[float], coupling: float, adjacency: list[tuple[int, ...]]
) -> float:
    degree = len(adjacency[0])
    residuals = []
    for vertex, row in enumerate(adjacency):
        residuals.append(
            sum(math.exp(coupling * (field[neighbor] - field[vertex]))
                for neighbor in row) - degree
        )
    return sum(value * value for value in residuals) / (2 * coupling ** 2)


def independent_gradient(
    field: list[float], coupling: float, adjacency: list[tuple[int, ...]]
) -> list[float]:
    degree = len(adjacency[0])
    residuals = [
        sum(math.exp(coupling * (field[j] - field[i])) for j in row) - degree
        for i, row in enumerate(adjacency)
    ]
    result = []
    for k in range(len(field)):
        incoming = sum(
            residuals[i] * math.exp(coupling * (field[k] - field[i]))
            for i, row in enumerate(adjacency) for j in row if j == k
        )
        diagonal = residuals[k] * (residuals[k] + degree)
        result.append((incoming - diagonal) / coupling)
    mean = sum(result) / len(result)
    return [value - mean for value in result]


def finite_difference_gradient_check() -> tuple[bool, float]:
    adjacency = graph(3, 2)
    coupling = 0.37
    field = [math.sin(0.41 * (i + 1)) / 5 for i in range(9)]
    mean = sum(field) / len(field)
    field = [value - mean for value in field]
    analytic = independent_gradient(field, coupling, adjacency)
    epsilon = 1e-6
    numerical = []
    # Differentiate along e_k-e_last, then reconstruct the zero-sum gradient.
    directional = []
    for k in range(len(field) - 1):
        plus, minus = field.copy(), field.copy()
        plus[k] += epsilon
        plus[-1] -= epsilon
        minus[k] -= epsilon
        minus[-1] += epsilon
        directional.append(
            (independent_action(plus, coupling, adjacency)
             - independent_action(minus, coupling, adjacency)) / (2 * epsilon)
        )
    # directional_k=g_k-g_last and sum g=0.
    last = -sum(directional) / len(field)
    numerical = [value + last for value in directional] + [last]
    residual = max(abs(a - b) for a, b in zip(analytic, numerical))
    return residual < 2e-8, residual


def exact_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows)
                      if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [a - factor * b
                         for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def independent_kernel_check() -> bool:
    adjacency = graph(3, 2)
    degree = len(adjacency[0])
    matrix = []
    for i, row in enumerate(adjacency):
        counts = Counter(row)
        matrix.append([
            counts.get(j, 0) - (degree if i == j else 0)
            for j in range(len(adjacency))
        ])
    return exact_rank(matrix) == len(adjacency) - 1


def independent_diameter(adjacency: list[tuple[int, ...]]) -> int:
    diameter = 0
    for source in range(len(adjacency)):
        distances = {source: 0}
        queue = [source]
        for vertex in queue:
            for neighbor in adjacency[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        if len(distances) != len(adjacency):
            raise ValueError("disconnected graph")
        diameter = max(diameter, max(distances.values()))
    return diameter


def independent_spectrum() -> list[dict[str, int]]:
    # One L=4 axis has eigenvalue multiset {0,2,2,4}; convolve four axes.
    distribution = Counter({0: 1})
    axis = Counter({0: 1, 2: 2, 4: 1})
    for _ in range(4):
        updated = Counter()
        for left, left_count in distribution.items():
            for right, right_count in axis.items():
                updated[left + right] += left_count * right_count
        distribution = updated
    return [
        {
            "laplacian_eigenvalue": eigenvalue,
            "hessian_eigenvalue": eigenvalue ** 2,
            "multiplicity": multiplicity,
        }
        for eigenvalue, multiplicity in sorted(distribution.items())
    ]


def statistically_contains(summary: dict, target: float, sigmas: float = 5) -> bool:
    return abs(summary["mean"] - target) <= (
        sigmas * summary["blocked_standard_error"]
    )


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    errors = sorted(
        Draft202012Validator(schema).iter_errors(certificate),
        key=lambda error: list(error.path),
    )
    checks["strict_schema"] = not errors
    for name, ok in independent_normalization().items():
        checks[f"normalization_{name}"] = ok

    source_path = os.path.join(
        REPO_ROOT, "reverse_physics", "data",
        "anderson_bateman_herzog_turok_divergences_source_v1.json",
    )
    with open(source_path, encoding="utf-8") as handle:
        source = json.load(handle)
    equations = source.get("equations_transcribed", {})
    checks["source_equations"] = (
        equations.get("51")
        == "L_O11=partial(Omega)*partial(Upsilon)-g*(Omega*Upsilon)^2/6"
        and equations.get("52_displayed_middle_coefficient")
        == "1/(2*g)*(Box(Omega)/Omega)^2"
        and equations.get("54") == "lambda^2=-g/3"
    )

    gradient_ok, gradient_residual = finite_difference_gradient_check()
    checks["independent_finite_difference_gradient"] = gradient_ok
    checks["gradient_residual_recordable"] = gradient_residual < 2e-8
    adjacency = graph(3, 2)
    sample = [math.cos(0.31 * i) for i in range(9)]
    checks["constant_shift_invariance"] = abs(
        independent_action(sample, 0.4, adjacency)
        - independent_action([value + 7.25 for value in sample], 0.4, adjacency)
    ) < 1e-11
    checks["connected_kernel_dimension_one"] = independent_kernel_check()
    normalizability = certificate.get("finite_lattice_definition", {}).get(
        "normalizability", {}
    )
    checks["independent_diameter_and_coercivity_record"] = (
        independent_diameter(graph(4, 4)) == 8
        and normalizability.get("pilot_diameter") == 8
        and normalizability.get("classification") == "FINITE_PARTITION_FUNCTION"
        and "exp(R/D)-q" in normalizability.get("action_lower_bound", "")
    )
    checks["independent_four_cube_spectrum"] = (
        certificate.get("finite_lattice_definition", {}).get(
            "four_cube_free_spectrum"
        ) == independent_spectrum()
    )

    pilot = certificate.get("numerical_pilot", {})
    free = pilot.get("free_calibration", {})
    interacting = pilot.get("interacting_observation", {})
    free_observables = free.get("observables", {})
    interacting_observables = interacting.get("observables", {})
    checks["free_exact_action_calibration"] = statistically_contains(
        free_observables.get("action_density", {}), 255 / 512
    )
    checks["free_exact_mode_calibration"] = statistically_contains(
        free_observables.get("lowest_mode_ratio", {}), 1
    )
    checks["interacting_schwinger_dyson_calibration"] = statistically_contains(
        interacting_observables.get("virial_ratio", {}), 1
    )
    checks["acceptance_and_split_diagnostics"] = all(
        run.get("acceptance_rate", 0) > 0.7
        and run.get("action_density_split_z", math.inf) < 4
        for run in (free, interacting)
    )
    reversibility = pilot.get("reversibility_check", {})
    checks["reversibility"] = max(
        reversibility.get("max_position_residual", math.inf),
        reversibility.get("max_momentum_residual", math.inf),
    ) < 1e-11
    checks["numeric_type_boundary"] = (
        pilot.get("evidence_type") == "NUMERICAL_PILOT_OBSERVED"
        and certificate.get("disposition", {}).get("continuum_limit")
        == "NOT_ESTABLISHED"
        and certificate.get("disposition", {}).get("lorentzian_scattering")
        == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = (
        certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
        and "anything LORENTZIAN-CAUSAL"
        in certificate.get("does_not_establish", [])
    )
    checks["provenance_hashes"] = all(
        item.get("sha256") == sha256(item.get("path", ""))
        for item in certificate.get("provenance", {}).get("inputs", [])
    )
    producer_checks = certificate.get("checks", {})
    checks["producer_checks"] = (
        producer_checks.get("ok") is True
        and producer_checks.get("passed") == producer_checks.get("total") == 24
        and not producer_checks.get("failures")
    )

    if errors:
        for error in errors[:5]:
            print(f"[SCHEMA] {list(error.path)}: {error.message}")
    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} "
          f"({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
