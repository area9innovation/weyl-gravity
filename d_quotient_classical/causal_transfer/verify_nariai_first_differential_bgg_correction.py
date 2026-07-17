#!/usr/bin/env python3
"""Independent replay of the Nariai first-BGG strictification obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    SCHEMA,
    OUTPUT,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    matrix = sp.zeros(rows, columns)
    for row, column, entry in value["entries"]:
        matrix[row, column] = sp.Rational(entry)
    digest = hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
    ).hexdigest()
    if digest != value["sha256"]:
        raise ValueError("serialized sparse matrix digest drifted")
    return matrix


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    result = {
        tuple(item["word"]): _matrix(item["matrix"])
        for item in value["entries"]
    }
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(result[word]))}"
        for word in sorted(result)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("serialized operator-table digest drifted")
    return result


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

    # Consume the portable coefficient tables and solve the compatibility
    # problem independently of the producer's row solver.
    data = value["exact_data"]
    k = _table(data["first_bgg_operator"])
    defect = _table(data["original_chain_defect"])
    exported_x = _matrix(data["candidate_DeltaL1"])
    exported_y = _matrix(data["candidate_DeltaL0"])
    x = sp.zeros(60, 9)
    y_candidates: dict[int, list[sp.Matrix]] = {index: [] for index in range(15)}
    for row in range(60):
        form = row // 15
        transverse = [axis for axis in range(4) if axis != form]
        k_stack = sp.Matrix.hstack(*(k[(axis,)] for axis in transverse))
        d_stack = sp.Matrix.hstack(*(defect[(axis,)][row, :] for axis in transverse))
        solution, parameters = k_stack.T.gauss_jordan_solve(d_stack.T)
        if parameters.rows:
            raise ValueError("independent transverse solution was not unique")
        x[row, :] = solution.T
        y_candidates[row % 15].append(
            x[row, :] * k[(form,)] - defect[(form,)][row, :]
        )
    if x != exported_x:
        raise ValueError("exported DeltaL1 differs from independent exact solve")
    y = sp.Matrix.vstack(*(rows[0] for rows in y_candidates.values()))
    if y != exported_y:
        raise ValueError("exported DeltaL0 representative drifted")

    witnesses = []
    for adjoint, rows in y_candidates.items():
        for form, row in enumerate(rows[1:], start=1):
            for column, entry in enumerate(row - rows[0]):
                if entry:
                    witnesses.append([adjoint, form, column, str(entry)])
    if len(witnesses) != 12 or {item[3] for item in witnesses} != {"1/3"}:
        raise ValueError(f"cross-form witness drifted: {witnesses}")
    if witnesses[0] != [11, 1, 0, "1/3"]:
        raise ValueError("normalized earliest witness drifted")
    if value["exact_checks"]["harmonic_projection_defect_ranks"] != [0, 0]:
        raise ValueError("harmonic normalization receipt drifted")
    if value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] is not False:
        raise ValueError("full curved HPL was overpromoted")
    print("NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
