#!/usr/bin/env python3
"""Independent replay of the normalized-L0 coupled obstruction."""

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


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def _clean(table):
    return {word: matrix.applyfunc(sp.expand) for word, matrix in table.items() if matrix != sp.zeros(*matrix.shape)}


def _add(*tables):
    result = {}
    for table in tables:
        for word, matrix in table.items():
            result[word] = result.get(word, sp.zeros(*matrix.shape)) + matrix
    return _clean(result)


def _scale(table, scalar):
    return _clean({word: scalar * matrix for word, matrix in table.items()})


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for ref in payload["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {ref['result_id']}")

    base = fixture()
    layers = _pbw_layers()
    h0, h1, c0 = layers["H0"].base, layers["H1"].base, layers["C0"].base
    l0 = base["corrected_l0"]
    first_bgg = h0.compose(base["k_p0"], l0)
    complement = sp.eye(15) - l0[()] * base["projection0"]
    family = payload["exact_data"]["normalized_L0_family"]
    if _deserialize(family["complement"]) != complement:
        raise AssertionError("L0 complement drifted")
    if base["projection0"] * complement != sp.zeros(4, 15):
        raise AssertionError("normalization failed")
    _, pivots = complement.rref()
    expected_labels = [(pivot, output) for pivot in pivots for output in range(4)]

    responses = []
    records = payload["exact_data"]["induced_corrections"]
    if [(record["pivot_column"], record["output_column"]) for record in records] != expected_labels:
        raise AssertionError("basis coverage drifted")
    for record in records:
        delta_l0 = _deserialize(record["delta_L0"])
        expected_l0 = sp.zeros(15, 4)
        expected_l0[:, record["output_column"]] = complement[:, record["pivot_column"]]
        if delta_l0 != expected_l0:
            raise AssertionError("serialized L0 basis drifted")
        delta_d = _table(record["delta_d_aut"])
        delta_l1 = _table(record["delta_L1"])
        first_square = _add(
            h0.compose(delta_d, l0),
            h0.compose(base["d_aut"], {(): delta_l0}),
            _scale(h0.compose(delta_l1, first_bgg), -1),
        )
        if first_square:
            raise AssertionError("induced first square failed")
        response = _add(
            c0.compose(base["middle"]["yang_mills_middle"], delta_d),
            _scale(c0.compose(h1.compose(base["middle"]["yang_mills_middle"], delta_l1), base["k_p0"]), -1),
        )
        if response != _table(record["shifted_chain_response"]):
            raise AssertionError("serialized response drifted")
        responses.append(response)

    jet_ref = payload["dependency_refs"]["jet_aware_shifted_chain"]
    jet = json.loads((ROOT / jet_ref["path"]).read_text())
    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    system = payload["exact_data"]["shifted_chain_system"]
    keys = [(tuple(item["word"]), item["output_row"], item["input_column"]) for item in system["equation_keys"]]
    response_map = sp.Matrix([
        [operator.get(word, sp.zeros(60, 15))[row, column] for operator in responses]
        for word, row, column in keys
    ])
    target = sp.Matrix([-defect.get(word, sp.zeros(60, 15))[row, column] for word, row, column in keys])
    if _deserialize(system["response_map"]) != response_map or _deserialize(system["target"]) != target:
        raise AssertionError("serialized linear system drifted")
    rank_rows = system["full_column_rank_minor_rows"]
    if len(rank_rows) != 44:
        raise AssertionError("full-column-rank minor coverage failed")
    determinant = sp.factor(response_map[rank_rows, :].det())
    if determinant == 0 or determinant != sp.sympify(system["full_column_rank_minor_determinant"]):
        raise AssertionError("full-column-rank minor failed")

    witness_record = payload["exact_data"]["normalized_left_null_witness"]
    witness = sp.zeros(len(keys), 1)
    for term in witness_record["terms"]:
        index = term["equation_index"]
        if keys[index] != (tuple(term["word"]), term["output_row"], term["input_column"]):
            raise AssertionError("witness coordinate drifted")
        witness[index] = sp.sympify(term["coefficient"])
    if witness.T * response_map != sp.zeros(1, 44):
        raise AssertionError("witness is not left-null")
    if (witness.T * target)[0] != 1:
        raise AssertionError("witness target normalization failed")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("complete SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1 independent verification: PASS")
