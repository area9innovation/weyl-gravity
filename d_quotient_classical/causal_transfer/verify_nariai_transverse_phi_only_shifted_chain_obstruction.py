#!/usr/bin/env python3
"""Independent replay of the Phi-only shifted-chain obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import fixture
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import _deserialize, _pbw_layers


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json"
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def _matrix(record: dict) -> sp.Matrix:
    return _deserialize(record)


def verify() -> None:
    payload = json.loads(CERT.read_text())
    jet_ref = payload["dependency_refs"]["jet_aware_shifted_chain"]
    jet_path = ROOT / jet_ref["path"]
    if _sha(jet_path) != jet_ref["sha256"]:
        raise AssertionError("jet dependency hash mismatch")
    jet = json.loads(jet_path.read_text())
    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    k_p0 = fixture()["k_p0"]
    pbw = _pbw_layers()["C0"].base
    responses = []
    keys = {(word, column) for word, matrix in defect.items() for column in range(matrix.cols)}
    for word in ANSATZ_WORDS:
        for middle_index in range(9):
            basis = {word: sp.zeros(1, 9)}
            basis[word][0, middle_index] = 1
            response = pbw.compose(basis, k_p0)
            responses.append(response)
            keys.update((response_word, column) for response_word, matrix in response.items() for column in range(matrix.cols))
    keys = sorted(keys, key=lambda item: (len(item[0]), item[0], item[1]))
    coefficient_map = sp.Matrix([
        [response.get(word, sp.zeros(1, 15))[0, column] for response in responses]
        for word, column in keys
    ])
    if coefficient_map.shape != (225, 45) or coefficient_map.rank() != 45:
        raise AssertionError("coefficient map replay failed")
    if _matrix(payload["exact_data"]["linear_system"]["coefficient_map"]) != coefficient_map:
        raise AssertionError("serialized coefficient map drifted")
    augmented = []
    targets = []
    for row in range(60):
        target = sp.Matrix([defect.get(word, sp.zeros(60, 15))[row, column] for word, column in keys])
        targets.append(target)
        augmented.append(coefficient_map.row_join(target).rank())
    if augmented != payload["exact_data"]["linear_system"]["augmented_ranks"]:
        raise AssertionError("augmented ranks drifted")

    record = payload["exact_data"]["normalized_left_null_witness"]
    witness = sp.zeros(225, 1)
    for term in record["terms"]:
        index = term["equation_index"]
        if keys[index] != (tuple(term["word"]), term["input_column"]):
            raise AssertionError("witness equation key drifted")
        witness[index] = sp.sympify(term["coefficient"])
    target = sp.Matrix([defect.get(word, sp.zeros(60, 15))[record["output_row"], column] for word, column in keys])
    if witness.T * coefficient_map != sp.zeros(1, 45):
        raise AssertionError("witness is not left-null")
    if (witness.T * target)[0] != 1:
        raise AssertionError("witness did not normalize target to one")
    serialized_solutions = payload["exact_data"]["consistent_row_solutions"]
    expected_consistent = payload["exact_data"]["linear_system"]["consistent_rows"]
    if sorted(map(int, serialized_solutions)) != expected_consistent:
        raise AssertionError("consistent-row solution coverage drifted")
    for row_text, operator_record in serialized_solutions.items():
        row = int(row_text)
        operator = _table(operator_record)
        vector = sp.Matrix([
            operator.get(word, sp.zeros(1, 9))[0, middle_index]
            for word in ANSATZ_WORDS for middle_index in range(9)
        ])
        if coefficient_map * vector != targets[row]:
            raise AssertionError(f"consistent-row solution failed in row {row}")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("complete SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1 independent verification: PASS")
