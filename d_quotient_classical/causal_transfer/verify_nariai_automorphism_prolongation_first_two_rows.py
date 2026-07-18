#!/usr/bin/env python3
"""Independent consumer of the Nariai automorphism prolongation."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    OUTPUT,
    SCHEMA,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _lc_adjoint_curvature,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    matrix = sp.zeros(rows, columns)
    for row, column, coefficient in value["entries"]:
        matrix[row, column] = sp.Rational(coefficient)
    payload = sp.srepr(sp.ImmutableSparseMatrix(matrix))
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("independent sparse matrix digest mismatch")
    return matrix


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    table = {
        tuple(item["word"]): _matrix(item["matrix"])
        for item in value["entries"]
    }
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("independent sparse table digest mismatch")
    return table


def _entries(table) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def main() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    operators = {name: _table(table) for name, table in value["exact_operators"].items()}
    middle = middle_fixture()
    p0 = middle["screen"].harmonic_p0

    projection = {
        word: p0 * matrix for word, matrix in operators["L0_corrected"].items()
    }
    projection[()] = projection.get((), sp.zeros(4)) - sp.eye(4)
    if _entries({word: matrix for word, matrix in projection.items() if matrix != sp.zeros(*matrix.shape)}):
        raise ValueError("independent p0 L0 replay failed")

    first = _add(
        middle["pbw_h0"].compose(
            operators["d_aut"], operators["L0_corrected"]
        ),
        _scale(
            middle["pbw_h0"].compose(
                operators["L1_corrected"], middle["first_bgg"]
            ),
            -1,
        ),
    )
    if first:
        raise ValueError("independent automorphism first-square replay failed")

    expected_kp = {
        word: matrix * p0 for word, matrix in middle["first_bgg"].items()
    }
    if operators["K_p0"] != expected_kp:
        raise ValueError("serialized K p0 drifted")

    background = NariaiBackground()
    pbw_c0 = FibrePBW(
        _tensor_product_curvature(
            background, _lc_adjoint_curvature(), 0
        ),
        background,
        "independent-C0-automorphism",
    )
    degree_one = _add(
        pbw_c0.compose(
            middle["yang_mills_middle"], operators["d_aut"]
        ),
        _scale(
            pbw_c0.compose(operators["Phi"], operators["K_p0"]),
            -1,
        ),
    )
    if degree_one:
        raise ValueError("independent prolonged complex replay failed")

    graph_constraint = _add(
        middle["pbw_h1"].compose(
            middle["yang_mills_middle"], operators["L1_corrected"]
        ),
        _scale(operators["Phi"], -1),
    )
    if graph_constraint:
        raise ValueError("independent metric graph constraint replay failed")
    flags = value["flags"]
    if flags["CYCLIC_COTANGENT_COMPLETION"] is not False:
        raise ValueError("cyclic completion was overpromoted")
    if flags["FULL_PARENT_METRIC_QUASI_ISOMORPHISM"] is not False:
        raise ValueError("full quasi-isomorphism was overpromoted")
    if flags["NARIAI_GREEN_HOMOTOPY"] is not False:
        raise ValueError("Green homotopy was overpromoted")
    print(f"{value['result_id']}: independently verified")


if __name__ == "__main__":
    main()
