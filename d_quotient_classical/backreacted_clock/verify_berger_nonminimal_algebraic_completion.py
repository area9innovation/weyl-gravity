#!/usr/bin/env python3
"""Independent sparse consumer for the 54-row Berger nonminimal extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import _load_matrix
except ModuleNotFoundError:  # Direct script execution.
    from verify_berger_retained_minimal_operator import _load_matrix


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-nonminimal-algebraic-completion-v1.schema.json"
MINIMAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
MINIMAL_TO_EXTENDED = (
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    49, 50, 51, 52, 53,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _constant(record: dict[str, object]) -> sp.Matrix:
    matrix = _load_matrix(record)
    result = sp.zeros(len(matrix), len(matrix[0]))
    for row, entries in enumerate(matrix):
        for column, operator in enumerate(entries):
            if any(word for word in operator):
                raise AssertionError("contraction record is not pointwise")
            result[row, column] = operator.get((), 0)
    return result


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) <= set(schema["properties"])
    for name in ("pbwOperatorRecord", "pbwMatrixEntry", "pbwTerm"):
        assert name in schema["$defs"]
    refs = payload["dependency_refs"]
    assert refs["minimal_34"]["sha256"] == _sha256(MINIMAL_CERTIFICATE)
    assert refs["retained_classical_unary_q1"]["sha256"] == _sha256(Q1_CERTIFICATE)

    rows = payload["row_layout"]
    assert rows["total_rows"] == 54
    assert rows["degree_ranks"] == [5, 22, 22, 5]
    assert sorted(row["index"] for row in rows["component_rows"]) == list(range(54))
    assert len({row["row_id"] for row in rows["component_rows"]}) == 54

    contraction = payload["contraction"]
    minimal_iota = _constant(contraction["minimal_iota"])
    minimal_pi = _constant(contraction["minimal_pi"])
    s_nm = _constant(contraction["S_nonminimal"])
    iota = _constant(contraction["iota_cl"])
    projection = _constant(contraction["pi_cl"])
    homotopy = _constant(contraction["S_cl"])
    q_nm = _constant(payload["nonminimal_unary_extension"]["matrix"])

    expected_iota = sp.zeros(54, 34)
    expected_pi = sp.zeros(34, 54)
    for old, new in enumerate(MINIMAL_TO_EXTENDED):
        expected_iota[new, old] = 1
        expected_pi[old, new] = 1
    assert minimal_iota == expected_iota
    assert minimal_pi == expected_pi

    expected_q_nm = sp.zeros(54)
    expected_s_nm = sp.zeros(54)
    for index in range(5):
        expected_q_nm[44 + index, 17 + index] = 1
        expected_q_nm[39 + index, 22 + index] = 1
        expected_s_nm[17 + index, 44 + index] = 1
        expected_s_nm[22 + index, 39 + index] = 1
    assert q_nm == expected_q_nm
    assert s_nm == expected_s_nm
    assert q_nm * q_nm == sp.zeros(54)

    q_clock = sp.zeros(34)
    q_clock[15, 4] = -1
    q_clock[16, 3] = 1
    q_clock[32, 28] = -1
    q_clock[33, 27] = 1
    q_contractible = minimal_iota * q_clock * minimal_pi + q_nm
    assert projection * iota == sp.eye(26)
    assert q_contractible * homotopy + homotopy * q_contractible == sp.eye(54) - iota * projection
    assert homotopy * homotopy == sp.zeros(54)
    assert projection * homotopy == sp.zeros(26, 54)
    assert homotopy * iota == sp.zeros(54, 26)

    companion = payload["gauge_fermion_template"]
    assert companion["curved_companion"]["shape"] == [5, 10]
    assert companion["companion_row_orders"] == [3, 3, 3, 3, 4]
    assert companion["canonical_transform_applied"] is False
    flags = payload["flags"]
    for key in (
        "BERGER_NONMINIMAL_ROWS_COMPLETE",
        "BERGER_NONMINIMAL_DIRECT_SUM_CONTRACTION",
        "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION",
        "BERGER_CURVED_COMPANION_DERIVED",
    ):
        assert flags[key] is True
    for key, value in flags.items():
        if key not in {
            "BERGER_NONMINIMAL_ROWS_COMPLETE",
            "BERGER_NONMINIMAL_DIRECT_SUM_CONTRACTION",
            "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION",
            "BERGER_CURVED_COMPANION_DERIVED",
        }:
            assert value is False, key
    assert payload["next_gate"] == "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM"
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION_INDEPENDENT: PASS")
    print("54 rows, twenty-row quartet and 54-to-26 contraction: PASS")
    print("gauge-fermion shear, ell_2, D-equivariance, KT, causal and Hadamard: OPEN")


if __name__ == "__main__":
    main()
