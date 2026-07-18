#!/usr/bin/env python3
"""Independent consumer of the action-derived Nariai Bach endpoint."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _scale,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    OUTPUT,
    SCHEMA,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    output = {}
    for item in value["entries"]:
        matrix_value = item["matrix"]
        rows, columns = matrix_value["shape"]
        matrix = sp.zeros(rows, columns)
        for row, column, coefficient in matrix_value["entries"]:
            matrix[row, column] = sp.Rational(coefficient)
        output[tuple(item["word"])] = matrix
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(output[word]))}"
        for word in sorted(output)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("independent Bach coefficient digest mismatch")
    return output


def main() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    action = _table(value["exact_operator"]["coefficients"])
    middle = middle_fixture()
    corrected = _add(
        middle["compressed_middle"], {(): middle["endpoint_correction"]}
    )
    if _add(corrected, _scale(action, 2)):
        raise ValueError("independent parent/Bach compression replay failed")
    if middle["pbw_h0"].compose(action, middle["first_bgg"]):
        raise ValueError("independent Bach gauge replay failed")

    # Reconstruct the STF carrier without using the producer's tensor helper
    # and test the exact product-scaling direction against the emitted table.
    algebraic = middle["algebraic"]
    eta = sp.diag(-1, 1, 1, 1)
    carrier = sp.zeros(16, 9)
    for column in range(9):
        for a in range(4):
            for b in range(4):
                carrier[4 * a + b, column] = (
                    eta[b, b] * algebraic.i1[15 * a + b, column]
                )
    tensor_metric = sp.diag(
        *(eta[a, a] * eta[b, b] for a in range(4) for b in range(4))
    )
    gram = carrier.T * tensor_metric * carrier
    direction = sp.Matrix(
        [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1]
    )
    coordinates, parameters = carrier.gauss_jordan_solve(direction)
    if parameters.rows:
        raise ValueError("independent product direction missed STF carrier")
    output_coordinates = gram.inv() * action[()] * coordinates
    output_tensor = (carrier * output_coordinates).reshape(4, 4)
    expected = sp.diag(
        -sp.Rational(4, 3),
        sp.Rational(4, 3),
        -sp.Rational(4, 3),
        -sp.Rational(4, 3),
    )
    if output_tensor != expected:
        raise ValueError("independent product-scaling replay failed")

    checks = value["exact_checks"]
    zero_keys = (
        "tensor_symmetry_defects",
        "tensor_trace_defect_entries",
        "tensor_divergence_defect_entries",
        "B_action_K_defect_entries",
        "corrected_parent_plus_2_B_action_defect_entries",
    )
    if any(checks[key] != 0 for key in zero_keys):
        raise ValueError("Nariai Bach exact checks are incomplete")
    if value["flags"]["RELATIVE_CYCLIC_PAIRING_RECONCILED"] is not False:
        raise ValueError("relative cyclic pairing was overpromoted")
    if value["flags"]["NARIAI_GREEN_HOMOTOPY"] is not False:
        raise ValueError("Nariai Green homotopy was overpromoted")
    print(f"{value['result_id']}: independently verified")


if __name__ == "__main__":
    main()
