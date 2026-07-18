#!/usr/bin/env python3
"""Independent replay of formal K sensitivity and admissibility."""

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


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json"
WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    jet_ref = payload["dependency_refs"]["jet_aware_first_BGG"]
    jet = json.loads((ROOT / jet_ref["path"]).read_text())
    if jet["exact_data"]["operator_variations"]["first_BGG"]["nonzero_coefficients"] != 0:
        raise AssertionError("authoritative first-BGG variation is nonzero")

    base = fixture()
    layers = _pbw_layers()
    h0, h1, c0 = layers["H0"].base, layers["H1"].base, layers["C0"].base
    l0, l1 = base["corrected_l0"], base["corrected_l1"]
    first_bgg = h0.compose(base["k_p0"], l0)
    constraint_responses = []
    for column in range(15):
        correction = {(): sp.zeros(1, 15)}
        correction[()][0, column] = 1
        constraint_responses.append(h0.compose(correction, l0))
    for word in WORDS:
        for column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, column] = 1
            constraint_responses.append(_scale(h0.compose(correction, first_bgg), -1))
    constraint_keys = sorted(
        {(word, column) for response in constraint_responses for word, matrix in response.items() for column in range(matrix.cols)},
        key=lambda item: (len(item[0]), item[0], item[1]),
    )
    constraint = sp.Matrix([[response.get(word, sp.zeros(1, 4))[0, column] for response in constraint_responses] for word, column in constraint_keys])
    inverse = constraint.inv()

    obstruction_ref = payload["dependency_refs"]["normalized_L0_obstruction"]
    obstruction = json.loads((ROOT / obstruction_ref["path"]).read_text())
    witness_terms = obstruction["exact_data"]["normalized_left_null_witness"]["terms"]
    sensitivities = []
    basis = []
    for word in WORDS:
        for output_row in range(9):
            for input_column in range(4):
                delta_k = {word: sp.zeros(9, 4)}
                delta_k[word][output_row, input_column] = 1
                source = h0.compose(l1, delta_k)
                delta_d = sp.zeros(60, 15)
                delta_l1 = {basis_word: sp.zeros(60, 9) for basis_word in WORDS}
                for row in range(60):
                    target = sp.Matrix([source.get(key_word, sp.zeros(60, 4))[row, column] for key_word, column in constraint_keys])
                    solution = inverse * target
                    delta_d[row, :] = solution[:15, :].T
                    for word_index, basis_word in enumerate(WORDS):
                        delta_l1[basis_word][row, :] = solution[15 + 9 * word_index : 15 + 9 * (word_index + 1), :].T
                delta_l1 = _clean(delta_l1)
                response = _add(
                    c0.compose(base["middle"]["yang_mills_middle"], {(): delta_d}),
                    _scale(c0.compose(h1.compose(base["middle"]["yang_mills_middle"], delta_l1), base["k_p0"]), -1),
                    _scale(c0.compose(base["phi"], h0.compose(delta_k, {(): base["projection0"]})), -1),
                )
                value = sp.expand(sum(
                    sp.sympify(term["coefficient"]) * response.get(tuple(term["word"]), sp.zeros(60, 15))[term["output_row"], term["input_column"]]
                    for term in witness_terms
                ))
                sensitivities.append(value)
                basis.append({"word": list(word), "output_row": output_row, "input_column": input_column})

    screen = payload["exact_data"]["formal_screen"]
    if screen["basis"] != basis:
        raise AssertionError("formal K basis drifted")
    serialized = _deserialize(screen["sensitivity_map"])
    if serialized != sp.Matrix([sensitivities]):
        raise AssertionError("formal K sensitivity map drifted")
    nonzero = [{**basis[index], "value": str(value)} for index, value in enumerate(sensitivities) if value != 0]
    if screen["nonzero_directions"] != nonzero or len(nonzero) != 23:
        raise AssertionError("formal K sensitive directions drifted")
    if payload["flags"]["TRANSVERSE_ACTION_DERIVED_K_CORRECTION_AVAILABLE"] is not False:
        raise AssertionError("inadmissible K repair was promoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1 independent verification: PASS")
