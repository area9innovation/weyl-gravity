#!/usr/bin/env python3
"""Independent PBW consumer for the gauge-fixed 54-row Berger complex."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _identity_matrix,
    _matrix_add,
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    ZERO,
    _adjoint_matrix,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-gauge-fixed-nonminimal-completion-v1.schema.json"
UNFIXED = ROOT / "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
MINIMAL = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
RETAINED = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
MINIMAL_TO_EXTENDED = (
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    49, 50, 51, 52, 53,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(rows: int, columns: int):
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def _one(value=1):
    return LinearOperator.from_terms(((0, (), value),))


def _negative(matrix):
    return [[entry.scale(-1) for entry in row] for row in matrix]


def _subtract(left, right):
    return _matrix_add(left, _negative(right))


def _embed(target, block, row_indices, column_indices) -> None:
    rows = row_indices if isinstance(row_indices, tuple) else tuple(range(row_indices, row_indices + len(block)))
    columns = column_indices if isinstance(column_indices, tuple) else tuple(range(column_indices, column_indices + len(block[0])))
    for row, target_row in enumerate(rows):
        for column, target_column in enumerate(columns):
            target[target_row][target_column] = block[row][column]


def _multiply(outer, inner):
    output = _zero(len(outer), len(inner[0]))
    support = {
        middle: [(column, entry) for column, entry in enumerate(row) if entry.terms]
        for middle, row in enumerate(inner)
    }
    for row, entries in enumerate(outer):
        for middle, left in enumerate(entries):
            if left.terms:
                for column, right in support[middle]:
                    output[row][column] = output[row][column] + left.compose(right)
    return output


def _is_zero(matrix) -> bool:
    return all(not entry.terms for row in matrix for entry in row)


def _reconstruct_unfixed() -> list[list[LinearOperator]]:
    retained = json.loads(RETAINED.read_text())
    k = _matrix_from_record(retained["q1_blocks"]["K_spatial"])
    h = _matrix_from_record(retained["q1_blocks"]["H_retained"])
    l = _matrix_from_record(retained["q1_blocks"]["minus_K_spatial_sharp"])
    q34 = _zero(34, 34)
    _embed(q34, k, 5, 0)
    _embed(q34, h, 17, 5)
    _embed(q34, l, 29, 17)
    q34[15][4] = _one(-1)
    q34[16][3] = _one()
    q34[32][28] = _one(-1)
    q34[33][27] = _one()
    q54 = _zero(54, 54)
    _embed(q54, q34, MINIMAL_TO_EXTENDED, MINIMAL_TO_EXTENDED)
    for index in range(5):
        q54[44 + index][17 + index] = _one()
        q54[39 + index][22 + index] = _one()
    return q54


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) <= set(schema["properties"])
    refs = payload["dependency_refs"]
    assert refs["unfixed_nonminimal"]["sha256"] == _sha256(UNFIXED)
    assert refs["minimal_34"]["sha256"] == _sha256(MINIMAL)

    assert payload["operator_semantics"]["portable_name"] == "classical_unary_q1"
    assert payload["operator_semantics"]["not_quantum_loop_operator"] is True
    assert payload["row_layout"]["total_rows"] == 54
    assert sorted(row["index"] for row in payload["row_layout"]["component_rows"]) == list(range(54))

    nilpotent = _matrix_from_record(payload["gauge_fermion"]["canonical_shear_nilpotent_part"])
    identity = _identity_matrix(54)
    shear = _matrix_add(identity, nilpotent)
    inverse = _subtract(identity, nilpotent)
    assert _is_zero(_multiply(nilpotent, nilpotent))
    assert _is_zero(_subtract(_multiply(shear, inverse), identity))

    omega = _matrix_from_record(payload["contraction"]["cyclic_pairing"])
    assert _is_zero(
        _subtract(_multiply(_multiply(_adjoint_matrix(shear), omega), shear), omega)
    )

    q_unfixed = _reconstruct_unfixed()
    q_gauge_fixed = _matrix_from_record(payload["classical_unary_q1"]["matrix"])
    reconstructed = _multiply(_multiply(shear, q_unfixed), inverse)
    assert _is_zero(_subtract(q_gauge_fixed, reconstructed))
    assert _is_zero(_multiply(q_gauge_fixed, q_gauge_fixed))

    iota = _matrix_from_record(payload["contraction"]["iota_cl"])
    projection = _matrix_from_record(payload["contraction"]["pi_cl"])
    homotopy = _matrix_from_record(payload["contraction"]["S_cl"])
    assert _is_zero(_subtract(_multiply(projection, iota), _identity_matrix(26)))
    assert _is_zero(
        _subtract(
            _matrix_add(_multiply(q_gauge_fixed, homotopy), _multiply(homotopy, q_gauge_fixed)),
            _subtract(identity, _multiply(iota, projection)),
        )
    )
    assert _is_zero(_multiply(homotopy, homotopy))
    assert _is_zero(_multiply(projection, homotopy))
    assert _is_zero(_multiply(homotopy, iota))

    flags = payload["flags"]
    assert flags["BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM"] is True
    assert flags["BERGER_NONMINIMAL_COMPLETION"] is True
    assert flags["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is True
    for key in (
        "CLASSICAL_SUPPORT_LOCAL_Q2",
        "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
        "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
        "BERGER_CAUSAL_GREEN_HOMOTOPY",
        "BERGER_HADAMARD_DATA",
        "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
    ):
        assert flags[key] is False
    assert payload["next_gate"] == "CLASSICAL_SUPPORT_LOCAL_Q2_AND_D_ACTION"
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION_INDEPENDENT: PASS")
    print("complete gauge-fixed 54-row classical_unary_q1 and contraction: PASS")
    print("ell_2, D-equivariance, nonlinear KT, causal and Hadamard: OPEN")


if __name__ == "__main__":
    main()
