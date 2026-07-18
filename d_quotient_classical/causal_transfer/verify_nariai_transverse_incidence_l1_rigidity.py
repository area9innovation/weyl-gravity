#!/usr/bin/env python3
"""Independent replay of the transverse incidence/L1 rigidity theorem."""

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


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json"
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for ref in payload["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {ref['result_id']}")

    base = fixture()
    pbw = _pbw_layers()["H0"].base
    l0 = base["corrected_l0"]
    first_bgg = pbw.compose(base["k_p0"], l0)
    if _table(payload["exact_data"]["normalization"]["reconstructed_first_BGG"]) != first_bgg:
        raise AssertionError("first BGG reconstruction drifted")
    projection = pbw.compose({(): base["projection0"]}, l0)
    projection[()] = projection.get((), sp.zeros(4)) - sp.eye(4)
    if any(matrix != sp.zeros(*matrix.shape) for matrix in projection.values()):
        raise AssertionError("p0 L0 normalization failed")

    responses = []
    unknowns = []
    for column in range(15):
        correction = {(): sp.zeros(1, 15)}
        correction[()][0, column] = 1
        responses.append(pbw.compose(correction, l0))
        unknowns.append({"row": "delta_d_aut", "word": [], "input_column": column})
    for word in ANSATZ_WORDS:
        for column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, column] = 1
            response = pbw.compose(correction, first_bgg)
            responses.append({key: -matrix for key, matrix in response.items()})
            unknowns.append({"row": "delta_L1", "word": list(word), "input_column": column})
    keys = sorted(
        {(word, column) for response in responses for word, matrix in response.items() for column in range(matrix.cols)},
        key=lambda item: (len(item[0]), item[0], item[1]),
    )
    matrix = sp.Matrix([
        [response.get(word, sp.zeros(1, 4))[0, column] for response in responses]
        for word, column in keys
    ])
    record = payload["exact_data"]["constraint_system"]
    if matrix.shape != (60, 60) or matrix.rank() != 60:
        raise AssertionError("constraint-map rank replay failed")
    if sp.factor(matrix.det()) != sp.sympify(record["determinant"]):
        raise AssertionError("determinant replay failed")
    if _deserialize(record["coefficient_map"]) != matrix:
        raise AssertionError("serialized coefficient map drifted")
    if record["unknown_basis"] != unknowns:
        raise AssertionError("unknown basis drifted")
    if record["equation_keys"] != [
        {"word": list(word), "input_column": column} for word, column in keys
    ]:
        raise AssertionError("equation basis drifted")

    jet_ref = payload["dependency_refs"]["jet_aware_shifted_chain"]
    jet = json.loads((ROOT / jet_ref["path"]).read_text())
    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    if sum(value != 0 for coefficient in defect.values() for value in coefficient) != 207:
        raise AssertionError("shifted defect drifted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("complete SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1 independent verification: PASS")
