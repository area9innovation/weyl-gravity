#!/usr/bin/env python3
"""Independent replay of the first-order transverse Schur solution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import (
    _deserialize,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json"
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict) -> dict[tuple[int, ...], sp.Matrix]:
    return {
        tuple(entry["word"]): _deserialize(entry["matrix"])
        for entry in record["entries"]
    }


def verify() -> None:
    payload = json.loads(CERT.read_text())
    dependency_record = payload["dependency_refs"]["jet_aware_middle_schur"]
    dependency_path = ROOT / dependency_record["path"]
    if _sha(dependency_path) != dependency_record["sha256"]:
        raise AssertionError("jet-aware dependency hash mismatch")
    dependency = json.loads(dependency_path.read_text())
    if dependency["result_id"] != dependency_record["result_id"]:
        raise AssertionError("jet-aware dependency id mismatch")

    defect = _table(
        dependency["exact_data"]["differential_schur_gate"][
            "unrepaired_gauge_defect"
        ]
    )
    correction = _table(payload["exact_data"]["unique_first_order_correction"])
    middle = middle_fixture()
    pbw = middle["pbw_h0"]
    first_bgg = middle["first_bgg"]

    responses = []
    equation_keys = {
        (word, column)
        for word, matrix in defect.items()
        for column in range(matrix.cols)
    }
    for word in ANSATZ_WORDS:
        for middle_index in range(9):
            basis = {word: sp.zeros(1, 9)}
            basis[word][0, middle_index] = 1
            response = pbw.compose(basis, first_bgg)
            responses.append(response)
            equation_keys.update(
                (response_word, column)
                for response_word, matrix in response.items()
                for column in range(matrix.cols)
            )
    ordered_keys = sorted(
        equation_keys, key=lambda item: (len(item[0]), item[0], item[1])
    )
    coefficient_map = sp.Matrix(
        [
            [
                response.get(word, sp.zeros(1, 4))[0, column]
                for response in responses
            ]
            for word, column in ordered_keys
        ]
    )
    if coefficient_map.shape != (60, 45) or coefficient_map.rank() != 45:
        raise AssertionError("independent first-order coefficient map drifted")

    for output_row in range(9):
        serialized_solution = sp.Matrix(
            [correction.get(word, sp.zeros(9))[output_row, middle_index]
             for word in ANSATZ_WORDS for middle_index in range(9)]
        )
        target = sp.Matrix(
            [-defect.get(word, sp.zeros(9, 4))[output_row, column]
             for word, column in ordered_keys]
        )
        if coefficient_map * serialized_solution != target:
            raise AssertionError(f"serialized solution failed in row {output_row}")
        if coefficient_map.row_join(target).rank() != 45:
            raise AssertionError(f"augmented rank failed in row {output_row}")

    response = pbw.compose(correction, first_bgg)
    for word in set(response) | set(defect):
        if response.get(word, sp.zeros(9, 4)) + defect.get(word, sp.zeros(9, 4)) != sp.zeros(9, 4):
            raise AssertionError(f"corrected gauge residual at {word}")
    if payload["flags"]["TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION"] is not False:
        raise AssertionError("action-derived identification was overpromoted")
    if payload["flags"]["TRANSVERSE_CYCLIC_SCHUR_VARIATION"] is not False:
        raise AssertionError("cyclicity was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1 independent verification: PASS")
