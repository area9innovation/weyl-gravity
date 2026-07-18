#!/usr/bin/env python3
"""Independent consumer for the action-paired Nariai metric Bach complex."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    OUTPUT as BACH_CERTIFICATE,
)
from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import (
    OUTPUT,
    SCHEMA,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    output = sp.zeros(rows, columns)
    for row, column, coefficient in value["entries"]:
        output[row, column] = sp.Rational(coefficient)
    payload = sp.srepr(sp.ImmutableSparseMatrix(output))
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("independent sparse-matrix digest mismatch")
    return output


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    output = {}
    for item in value["entries"]:
        output[tuple(item["word"])] = _matrix(item["matrix"])
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(output[word]))}"
        for word in sorted(output)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("independent sparse-table digest mismatch")
    return output


def main() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    action = json.loads(BACH_CERTIFICATE.read_text())
    if value["complex"]["B_action_sha256"] != action["exact_operator"]["sha256"]:
        raise ValueError("Bach endpoint digest was not preserved")

    pairing = value["action_pairing"]
    ghost = _matrix(pairing["ghost_identity_pairing"])
    field = _matrix(pairing["field_equation_pairing"])
    if ghost != sp.diag(-1, 1, 1, 1) or field != sp.eye(9):
        raise ValueError("action-coordinate evaluation pairings drifted")

    operators = value["exact_operators"]
    gauge = _table(operators["K"])
    adjoint = _table(operators["Ksharp"])
    bach = _table(action["exact_operator"]["coefficients"])
    middle = middle_fixture()
    if gauge != middle["first_bgg"]:
        raise ValueError("serialized K does not equal the independent BGG operator")
    independently_derived = {
        word: (-ghost.inv() * matrix.T * field).applyfunc(sp.expand)
        for word, matrix in gauge.items()
    }
    if adjoint != independently_derived:
        raise ValueError("Ksharp is not the typed formal adjoint of K")

    if middle["pbw_h0"].compose(bach, gauge):
        raise ValueError("independent B K replay failed")

    # Reconstruct the tensor-coordinate output and take its divergence without
    # importing the producer's tensor helper or its recorded defect count.
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
    tensor_coordinates = {word: gram.inv() * matrix for word, matrix in bach.items()}
    divergence = {}
    for axis in range(4):
        matrix = sp.zeros(4, 9)
        for b in range(4):
            matrix[b, :] = eta[axis, axis] * carrier[4 * axis + b, :]
        divergence[(axis,)] = matrix
    if middle["pbw_h1"].compose(divergence, tensor_coordinates):
        raise ValueError("independent tensor divergence replay failed")

    checks = value["exact_checks"]
    if checks["B_K_defect_entries"] or checks["Ksharp_B_defect_entries"]:
        raise ValueError("metric Bach Noether identities failed")
    if checks["abstract_Q_squared_mod_Noether"] is not True:
        raise ValueError("abstract four-row differential does not square")
    if checks["abstract_odd_cyclicity"] is not True:
        raise ValueError("abstract four-row differential is not odd cyclic")
    if value["flags"]["RELATIVE_EQUATION_IDENTITY_CONE"] is not False:
        raise ValueError("relative cone was overpromoted")
    if value["flags"]["NARIAI_GREEN_HOMOTOPY"] is not False:
        raise ValueError("Green homotopy was overpromoted")
    print(f"{value['result_id']}: independently verified")


if __name__ == "__main__":
    main()
