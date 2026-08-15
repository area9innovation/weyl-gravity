#!/usr/bin/env python3
"""Independent verifier for the Riemannian/electrical BT Witten bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-riemannian-electrical-witten-bridge-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_PIOLA_WARD_CANCELLATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_SCHUR_GATE_V1.json",
]


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def frac_vector(values: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(frac(value) for value in values)


def frac_matrix(
    values: list[list[dict[str, int]]]
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(frac_vector(row) for row in values)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return tuple(tuple(row) for row in zip(*matrix))


def multiply(left, right):
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
            for j in range(len(right[0]))
        )
        for i in range(len(left))
    )


def matrix_vector(matrix, vector):
    return tuple(
        sum((entry * value for entry, value in zip(row, vector)), Fraction())
        for row in matrix
    )


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction())


def determinant(matrix):
    work = [list(row) for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(row for row in range(column, len(work)) if work[row][column])
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return result


def inverse(matrix):
    size = len(matrix)
    work = [
        list(row) + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return tuple(tuple(row[size:]) for row in work)


def independent_fixture() -> dict:
    omega = (Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2))
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    residual = tuple(
        (omega[(x - 1) % 4] + omega[(x + 1) % 4] - 2 * omega[x]) / omega[x]
        for x in range(4)
    )
    kinetic = [[Fraction() for _ in range(4)] for _ in range(4)]
    conductance = [[Fraction() for _ in range(4)] for _ in range(4)]
    for x in range(4):
        kinetic[x][x] = 2 + residual[x]
    for x, y in edges:
        kinetic[x][y] = kinetic[y][x] = -1
        c = omega[x] * omega[y]
        conductance[x][x] += c
        conductance[y][y] += c
        conductance[x][y] -= c
        conductance[y][x] -= c
    k = tuple(tuple(row) for row in kinetic)
    b = tuple(tuple(row) for row in conductance)
    source = (Fraction(1), Fraction(-1), Fraction(), Fraction())

    root = 3
    b_minor = tuple(
        tuple(entry for j, entry in enumerate(row) if j != root)
        for i, row in enumerate(b) if i != root
    )
    pinned_rest = matrix_vector(inverse(b_minor), source[:3])
    pinned = pinned_rest + (Fraction(),)
    omega2 = tuple(value * value for value in omega)
    shift = dot(omega2, pinned) / sum(omega2, Fraction())
    weighted_gauge = tuple(value - shift for value in pinned)
    alpha = tuple(-omega2[x] * weighted_gauge[x] for x in range(4))

    weighted_potential = tuple(residual[x] / omega2[x] for x in range(4))
    score = tuple(-value for value in matrix_vector(b, weighted_potential))

    basis = (
        (Fraction(1), Fraction(), Fraction(), Fraction(-1)),
        (Fraction(), Fraction(1), Fraction(), Fraction(-1)),
        (Fraction(), Fraction(), Fraction(1), Fraction(-1)),
    )
    jacobian_columns = []
    for h in basis:
        dr = []
        for x in range(4):
            dr.append(sum(
                (omega[y] / omega[x] * (h[y] - h[x])
                 for y in ((x - 1) % 4, (x + 1) % 4)),
                Fraction(),
            ))
        mean = sum(dr, Fraction()) / 4
        jacobian_columns.append(tuple(value - mean for value in dr))
    jacobian = tuple(
        tuple(jacobian_columns[column][row] for column in range(3))
        for row in range(3)
    )
    carrier_gram = multiply(basis, transpose(basis))
    jacobian_inverse = inverse(jacobian)
    metric = multiply(multiply(transpose(jacobian_inverse), carrier_gram), jacobian_inverse)
    cometric = inverse(metric)
    coordinate_h = ((Fraction(1),), (Fraction(-1),), (Fraction(),))
    coordinate_alpha = multiply(transpose(jacobian_inverse), coordinate_h)
    norm = multiply(multiply(transpose(coordinate_alpha), cometric), coordinate_alpha)[0][0]
    return {
        "omega": omega,
        "residual": residual,
        "kinetic": k,
        "b": b,
        "source": source,
        "pinned": pinned,
        "weighted_gauge": weighted_gauge,
        "alpha": alpha,
        "weighted_potential": weighted_potential,
        "score": score,
        "electrical": dot(source, pinned),
        "weighted_energy": dot(weighted_potential, matrix_vector(b, weighted_potential)),
        "source_energy": dot(source, matrix_vector(b, source)),
        "directional_score": dot(source, score),
        "jacobian": jacobian,
        "carrier_gram": carrier_gram,
        "metric": metric,
        "cometric": cometric,
        "coordinate_alpha": tuple(row[0] for row in coordinate_alpha),
        "norm": norm,
        "relative_volume_squared": determinant(metric) / determinant(carrier_gram),
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False
    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(cert))
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes_current"] = (
        [item.get("path") for item in inputs] == EXPECTED_INPUTS
        and all(item.get("sha256") == file_hash(item["path"]) for item in inputs)
    )

    exact = independent_fixture()
    public = cert.get("cycle_four_fixture", {})
    diagonal = tuple(
        tuple(exact["omega"][i] if i == j else Fraction() for j in range(4))
        for i in range(4)
    )
    checks["independent_ground_transform"] = (
        multiply(multiply(diagonal, exact["kinetic"]), diagonal) == exact["b"]
        and frac_matrix(public.get("conductance_laplacian", [])) == exact["b"]
    )
    checks["independent_green_source"] = (
        matrix_vector(exact["b"], exact["pinned"]) == exact["source"]
        and exact["pinned"][3] == 0
        and matrix_vector(exact["b"], exact["weighted_gauge"]) == exact["source"]
        and dot(tuple(x * x for x in exact["omega"]), exact["weighted_gauge"]) == 0
        and frac_vector(public.get("pinned_green_potential_root_3", [])) == exact["pinned"]
        and frac_vector(public.get("flat_source_covector", []))
        == exact["alpha"]
        == (Fraction(-9, 25), Fraction(9, 25), Fraction(1, 25), Fraction(-1, 25))
        and frac(public.get("electrical_energy", {})) == exact["electrical"] == Fraction(9, 20)
    )
    checks["independent_score_current"] = (
        frac_vector(public.get("weighted_potential", [])) == exact["weighted_potential"]
        and frac_vector(public.get("action_score_vector", []))
        == exact["score"]
        == (Fraction(9, 4), Fraction(3), Fraction(9, 4), Fraction(-15, 2))
        and frac(public.get("directional_action_score", {}))
        == exact["directional_score"] == Fraction(-3, 4)
        and frac(public.get("weighted_potential_energy", {}))
        == exact["weighted_energy"] == Fraction(117, 2)
        and frac(public.get("source_conductance_energy", {}))
        == exact["source_energy"] == Fraction(21, 2)
    )
    checks["independent_metric_and_volume"] = (
        frac_matrix(public.get("coordinate_jacobian", [])) == exact["jacobian"]
        and frac_matrix(public.get("riemannian_metric", [])) == exact["metric"]
        and frac_matrix(public.get("riemannian_cometric", [])) == exact["cometric"]
        and frac_vector(public.get("coordinate_source_covector", [])) == exact["coordinate_alpha"]
        and frac(public.get("physical_source_norm", {})) == exact["norm"] == 2
        and frac(public.get("relative_volume_factor_squared", {}))
        == exact["relative_volume_squared"] == Fraction(16, 15625)
    )
    parallel = cert.get("parallel_source_witten_identity", {})
    checks["parallel_source_witten_identity"] = (
        parallel.get("source_one_form") == "alpha_h=d_u F_h=L_psi^(-T)h"
        and parallel.get("operator_identity") == "L_1(dF_h)=d(L_0 F_h)=d(D_h S)"
        and "E_mu[(D_h S)^2]=E_mu[D_h^2 S]"
        in parallel.get("quadratic_form_identity", "")
        and "omega(p)^2*||h||^2/lambda^2" in parallel.get("vacuum_value", "")
        and parallel.get("status") == "PROVED_FINITE_VOLUME_IDENTITY"
    )
    disposition = cert.get("method_disposition", {})
    checks["coordinate_and_claim_boundary"] = (
        disposition.get("flat_potential_euclidean_dirichlet_substitution")
        == "OBSTRUCTED_AS_WRONG_METRIC"
        and disposition.get("physical_witten_metric_and_cometric") == "PROVED"
        and disposition.get("parallel_source_connection_cancellation") == "PROVED"
        and disposition.get("parallel_source_current_susceptibility_identity") == "PROVED"
        and disposition.get("pinned_gff_representation_of_source_resolvent") == "PROVED"
        and disposition.get("volume_uniform_annealed_witten_coercivity") == "OPEN"
        and disposition.get("actual_interacting_h_minus_one_second_moment") == "OPEN"
    )
    published = cert.get("checks", {})
    checks["producer_checks_consistent"] = (
        published.get("ok") is True
        and published.get("passed") == published.get("total") == 15
        and published.get("failures") == []
        and all(published.get("details", {}).values())
    )
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    ok = all(checks.values())
    print(
        "BT Riemannian electrical Witten independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
