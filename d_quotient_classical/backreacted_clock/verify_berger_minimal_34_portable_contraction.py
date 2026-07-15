#!/usr/bin/env python3
"""Independent sparse consumer for the portable 34-row contraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import (
        _load_matrix,
    )
except ModuleNotFoundError:  # Direct script execution.
    from verify_berger_retained_minimal_operator import _load_matrix


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
LAYOUT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
RETAINED_TO_FULL = (
    0, 1, 2,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    29, 30, 31,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _zero(rows: int, columns: int):
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _embed(target, block, row_offset: int, column_offset: int) -> None:
    for row in range(len(block)):
        for column in range(len(block[0])):
            target[row + row_offset][column + column_offset] = block[row][column]


def _numeric_constant(matrix) -> sp.Matrix:
    output = sp.zeros(len(matrix), len(matrix[0]))
    for row in range(len(matrix)):
        for column in range(len(matrix[0])):
            operator = matrix[row][column]
            if any(word for word in operator):
                raise AssertionError("contraction map is not order zero")
            output[row, column] = operator.get((), 0)
    return output


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    q1 = json.loads(Q1_CERTIFICATE.read_text())
    refs = payload["dependency_refs"]
    assert refs["retained_classical_unary_q1"]["sha256"] == _sha256(Q1_CERTIFICATE)
    assert refs["clock_sdr"]["sha256"] == _sha256(CLOCK_CERTIFICATE)
    assert refs["retained_layout"]["sha256"] == _sha256(LAYOUT_CERTIFICATE)

    k = _load_matrix(q1["q1_blocks"]["K_spatial"])
    h = _load_matrix(q1["q1_blocks"]["H_retained"])
    l = _load_matrix(q1["q1_blocks"]["minus_K_spatial_sharp"])
    expected_k = _zero(12, 5)
    _embed(expected_k, k, 0, 0)
    expected_k[10][4] = {(): -1}
    expected_k[11][3] = {(): 1}
    expected_h = _zero(12, 12)
    _embed(expected_h, h, 0, 0)
    expected_l = _zero(5, 12)
    _embed(expected_l, l, 0, 0)
    expected_l[3][11] = {(): -1}
    expected_l[4][10] = {(): 1}

    frozen = payload["classical_unary_q1"]
    assert frozen["retained_blocks_ref"] == "dependency_refs.retained_classical_unary_q1"
    assert frozen["full_shape"] == [34, 34]
    assert frozen["degree_ranks"] == [5, 12, 12, 5]
    assembly = frozen["assembly"]
    assert assembly["K_spatial_embedding"] == {"row_offset": 5, "column_offset": 0}
    assert assembly["H_retained_embedding"] == {"row_offset": 17, "column_offset": 5}
    assert assembly["minus_K_spatial_sharp_embedding"] == {"row_offset": 29, "column_offset": 17}

    contraction = payload["contraction"]
    iota = _numeric_constant(_load_matrix(contraction["iota_cl"]))
    projection = _numeric_constant(_load_matrix(contraction["pi_cl"]))
    homotopy = _numeric_constant(_load_matrix(contraction["S_cl"]))
    p_retained = _numeric_constant(_load_matrix(contraction["P_retained"]))
    p_clock = _numeric_constant(_load_matrix(contraction["P_clock"]))
    expected_iota = sp.zeros(34, 26)
    expected_projection = sp.zeros(26, 34)
    for retained_index, full_index in enumerate(RETAINED_TO_FULL):
        expected_iota[full_index, retained_index] = 1
        expected_projection[retained_index, full_index] = 1
    assert iota == expected_iota
    assert projection == expected_projection
    assert projection * iota == sp.eye(26)
    assert p_retained == iota * projection
    assert p_clock == sp.eye(34) - p_retained

    q_clock = sp.zeros(34)
    q_clock[15, 4] = -1
    q_clock[16, 3] = 1
    q_clock[32, 28] = -1
    q_clock[33, 27] = 1
    assert _numeric_constant(_load_matrix(frozen["clock_extension"])) == q_clock
    assert q_clock * homotopy + homotopy * q_clock == p_clock
    assert homotopy * homotopy == sp.zeros(34)
    assert projection * homotopy == sp.zeros(26, 34)
    assert homotopy * iota == sp.zeros(34, 26)

    semantics = payload["operator_semantics"]
    assert semantics["portable_name"] == "classical_unary_q1"
    assert semantics["not_quantum_loop_operator"] is True
    flags = payload["flags"]
    assert flags["BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS"] is True
    for key in (
        "BERGER_NONMINIMAL_COMPLETION",
        "CLASSICAL_SUPPORT_LOCAL_Q2",
        "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
        "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
        "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
        "BERGER_CAUSAL_GREEN_HOMOTOPY",
        "BERGER_HADAMARD_DATA",
        "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
    ):
        assert flags[key] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_MINIMAL_34_PORTABLE_CONTRACTION_INDEPENDENT: PASS")
    print("all 34 minimal rows and iota_cl, pi_cl, S_cl: PASS")
    print("nonminimal, ell_2^cl, D-equivariance, KT, causal, and Hadamard: OPEN")


if __name__ == "__main__":
    main()
