#!/usr/bin/env python3
"""Independent replay of the complete order-two Phi obstruction."""

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


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def _receipt(matrix: sp.Matrix, rank: int) -> dict:
    entries = [[row, column, str(matrix[row, column])] for row in range(matrix.rows) for column in range(matrix.cols) if matrix[row, column] != 0]
    canonical = json.dumps({"shape": [matrix.rows, matrix.cols], "entries": entries}, sort_keys=True, separators=(",", ":"))
    return {"shape": [matrix.rows, matrix.cols], "rank": rank, "nonzero_coefficients": len(entries), "sha256": hashlib.sha256(canonical.encode()).hexdigest()}


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for ref in payload["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {ref['result_id']}")
    jet_ref = payload["dependency_refs"]["jet_aware_shifted_chain"]
    jet = json.loads((ROOT / jet_ref["path"]).read_text())
    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    data = payload["exact_data"]
    words = tuple(tuple(word) for word in data["ansatz"]["words"])
    responses = []
    basis = []
    keys = {(word, column) for word, matrix in defect.items() for column in range(matrix.cols)}
    pbw = _pbw_layers()["C0"].base
    k_p0 = fixture()["k_p0"]
    for word in words:
        for middle_column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, middle_column] = 1
            response = pbw.compose(correction, k_p0)
            responses.append(response)
            basis.append({"word": list(word), "middle_column": middle_column})
            keys.update((response_word, column) for response_word, matrix in response.items() for column in range(matrix.cols))
    if basis != data["ansatz"]["basis"]:
        raise AssertionError("order-two basis drifted")
    keys = sorted(keys, key=lambda item: (len(item[0]), item[0], item[1]))
    records = [{"word": list(word), "input_column": column} for word, column in keys]
    if records != data["coefficient_system"]["equation_basis"]:
        raise AssertionError("equation basis drifted")
    matrix = sp.Matrix([[response.get(word, sp.zeros(1, 15))[0, column] for response in responses] for word, column in keys])
    system = data["coefficient_system"]
    if _receipt(matrix, 130) != system["matrix_receipt"]:
        raise AssertionError("coefficient-map receipt drifted")
    row_index = {(word, column): index for index, (word, column) in enumerate(keys)}
    minor_rows = [row_index[(tuple(item["word"]), item["input_column"])] for item in system["full_rank_minor"]["rows"]]
    minor_columns = system["full_rank_minor"]["columns"]
    determinant = sp.factor(matrix[minor_rows, minor_columns].det())
    if determinant == 0 or determinant != sp.sympify(system["full_rank_minor"]["determinant"]):
        raise AssertionError("rank minor drifted")

    targets = [sp.Matrix([defect.get(word, sp.zeros(60, 15))[row, column] for word, column in keys]) for row in range(60)]
    augmented = [matrix.row_join(target).rank() for target in targets]
    if augmented != system["augmented_ranks"]:
        raise AssertionError("augmented ranks drifted")
    witness_record = data["normalized_left_null_witness"]
    witness = sp.zeros(len(keys), 1)
    for term in witness_record["terms"]:
        witness[row_index[(tuple(term["word"]), term["input_column"])]] = sp.sympify(term["coefficient"])
    if witness.T * matrix != sp.zeros(1, 135):
        raise AssertionError("witness is not left-null")
    if (witness.T * targets[witness_record["output_row"]])[0] != 1:
        raise AssertionError("witness target normalization failed")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("complete SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1 independent verification: PASS")
