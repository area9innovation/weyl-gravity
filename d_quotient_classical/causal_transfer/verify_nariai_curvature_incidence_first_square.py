#!/usr/bin/env python3
"""Independent portable-table replay of the Nariai curvature-incidence identity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
    _coordinate_map,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-first-square-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    matrix = sp.zeros(rows, columns)
    for row, column, entry in value["entries"]:
        matrix[row, column] = sp.Rational(entry)
    digest = hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest()
    if digest != value["sha256"]:
        raise ValueError("serialized sparse matrix digest drifted")
    return matrix


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    result = {tuple(item["word"]): _matrix(item["matrix"]) for item in value["entries"]}
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(result[word]))}"
        for word in sorted(result)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("serialized table digest drifted")
    return result


def _weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
    metric = sp.diag(-1, 1, 1, 1)
    same_factor = all(index < 2 for index in (a, b, c, d)) or all(
        index >= 2 for index in (a, b, c, d)
    )
    riemann = (
        metric[a, c] * metric[b, d] - metric[a, d] * metric[b, c]
        if same_factor
        else sp.Integer(0)
    )
    return sp.simplify(
        riemann
        - sp.Rational(1, 2)
        * (
            metric[a, c] * metric[d, b]
            - metric[a, d] * metric[c, b]
            - metric[b, c] * metric[d, a]
            + metric[b, d] * metric[c, a]
        )
        + sp.Rational(2, 3)
        * (metric[a, c] * metric[d, b] - metric[a, d] * metric[c, b])
    )


def verify() -> dict[str, object]:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    for name, dependency in value["dependency_refs"].items():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency drifted: {name}")

    names, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    metric = sp.diag(-1, 1, 1, 1)
    incidence = sp.zeros(60, 4)
    curvature: dict[tuple[int, ...], sp.Matrix] = {}
    adjoint_blocks: list[sp.Matrix] = []
    for left in range(4):
        for right in range(left + 1, 4):
            standard = sp.zeros(6)
            for raised in range(4):
                for lowered in range(4):
                    standard[1 + raised, 1 + lowered] = sum(
                        metric[raised, contracted] * _weyl(left, right, contracted, lowered)
                        for contracted in range(4)
                    )
            coordinates = left_inverse * standard.reshape(36, 1)
            if embedded * coordinates != standard.reshape(36, 1):
                raise ValueError("independent curvature escaped the adjoint basis")
            curvature[(left, right)] = coordinates
            adjoint_blocks.append(
                sp.Matrix.hstack(
                    *(
                        left_inverse
                        * (standard * generator - generator * standard).reshape(36, 1)
                        for generator in basis
                    )
                )
            )
            incidence[15 * left : 15 * (left + 1), right] = coordinates
            incidence[15 * right : 15 * (right + 1), left] = -coordinates

    data = value["exact_data"]
    exported_curvature = _table(data["normal_tractor_curvature_coordinates"])
    exported_incidence = _matrix(data["curvature_incidence"])
    exported_adjoint_square = _matrix(data["reconstructed_adjoint_curvature_square"])
    residual = _table(data["corrected_first_square_residual"])
    if curvature != exported_curvature:
        raise ValueError("independent normal-tractor curvature reconstruction drifted")
    if incidence != exported_incidence:
        raise ValueError("independent curvature-incidence reconstruction drifted")
    if sp.Matrix.vstack(*adjoint_blocks) != exported_adjoint_square:
        raise ValueError("independent adjoint-curvature reconstruction drifted")
    if _matrix(data["normal_tractor_square_defect"]) != sp.zeros(90, 15):
        raise ValueError("incidence curvature differs from the normal tractor square")
    if set(residual) != {()} or residual[()] != incidence:
        raise ValueError("first-square residue is not curvature incidence")
    if _matrix(data["relative_chain_defect"]) != sp.zeros(60, 4):
        raise ValueError("relative first square did not close")
    if _matrix(data["wrong_sign_defect"]) != 2 * incidence:
        raise ValueError("incidence sign guard drifted")
    support = sorted({row % 15 for row, _ in incidence.todok()})
    if support != list(range(4, 10)) or [names[index] for index in support] != value["exact_checks"]["adjoint_support_names"]:
        raise ValueError("curvature incidence escaped the Lorentz slot")
    if value["flags"]["CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE"] is not False:
        raise ValueError("mapping-cone completion was overpromoted")
    print("NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
