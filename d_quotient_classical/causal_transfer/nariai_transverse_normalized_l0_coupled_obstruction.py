#!/usr/bin/env python3
"""Obstruct the complete normalized L0-driven transverse coupled repair."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import fixture
from d_quotient_classical.causal_transfer.nariai_transverse_first_order_schur_solve import _serialize_table, _sparse
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import _deserialize, _pbw_layers


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JET_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
PHI_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json"
RIGIDITY_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-normalized-l0-coupled-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-normalized-l0-coupled-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_normalized_l0_coupled_obstruction.py"
TESTS = HERE / "tests/test_nariai_transverse_normalized_l0_coupled_obstruction.py"
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _matrix_receipt(matrix: sp.Matrix, rank: int) -> dict[str, Any]:
    entries = [[row, column, str(matrix[row, column])] for row in range(matrix.rows) for column in range(matrix.cols) if matrix[row, column] != 0]
    canonical = json.dumps({"shape": [matrix.rows, matrix.cols], "entries": entries}, sort_keys=True, separators=(",", ":"))
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": rank,
        "nonzero_coefficients": len(entries),
        "sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def _table(record: dict[str, Any]) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def _clean(table: dict[tuple[int, ...], sp.Matrix]) -> dict[tuple[int, ...], sp.Matrix]:
    return {word: matrix.applyfunc(sp.expand) for word, matrix in table.items() if matrix != sp.zeros(*matrix.shape)}


def _add(*tables: dict[tuple[int, ...], sp.Matrix]) -> dict[tuple[int, ...], sp.Matrix]:
    result: dict[tuple[int, ...], sp.Matrix] = {}
    for table in tables:
        for word, matrix in table.items():
            result[word] = result.get(word, sp.zeros(*matrix.shape)) + matrix
    return _clean(result)


def _scale(table: dict[tuple[int, ...], sp.Matrix], scalar: sp.Expr) -> dict[tuple[int, ...], sp.Matrix]:
    return _clean({word: scalar * matrix for word, matrix in table.items()})


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _constraint_map(pbw, l0, first_bgg):
    responses = []
    for column in range(15):
        correction = {(): sp.zeros(1, 15)}
        correction[()][0, column] = 1
        responses.append(pbw.compose(correction, l0))
    for word in ANSATZ_WORDS:
        for column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, column] = 1
            responses.append(_scale(pbw.compose(correction, first_bgg), -1))
    keys = sorted(
        {(word, column) for response in responses for word, matrix in response.items() for column in range(matrix.cols)},
        key=lambda item: (len(item[0]), item[0], item[1]),
    )
    matrix = sp.Matrix([
        [response.get(word, sp.zeros(1, 4))[0, column] for response in responses]
        for word, column in keys
    ])
    return matrix, keys


def _old_witness(operator: dict[tuple[int, ...], sp.Matrix], phi_payload: dict[str, Any]) -> sp.Expr:
    record = phi_payload["exact_data"]["normalized_left_null_witness"]
    output_row = record["output_row"]
    value = 0
    for term in record["terms"]:
        word = tuple(term["word"])
        column = term["input_column"]
        value += sp.sympify(term["coefficient"]) * operator.get(word, sp.zeros(60, 15))[output_row, column]
    return sp.expand(value)


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    jet_payload = json.loads(JET_INPUT.read_text())
    phi_payload = json.loads(PHI_INPUT.read_text())
    rigidity_payload = json.loads(RIGIDITY_INPUT.read_text())
    if rigidity_payload["flags"]["TRANSVERSE_INCIDENCE_L1_RIGIDITY_EXACT"] is not True:
        raise AssertionError("rigid incidence/L1 solve unavailable")

    base = fixture()
    layers = _pbw_layers()
    pbw_h0 = layers["H0"].base
    pbw_h1 = layers["H1"].base
    pbw_c0 = layers["C0"].base
    l0 = base["corrected_l0"]
    k_p0 = base["k_p0"]
    middle = base["middle"]["yang_mills_middle"]
    d_aut = base["d_aut"]
    p0 = base["projection0"]
    first_bgg = pbw_h0.compose(k_p0, l0)
    constraint, constraint_keys = _constraint_map(pbw_h0, l0, first_bgg)
    if constraint.shape != (60, 60) or constraint.det() == 0:
        raise AssertionError("rigid constraint map drifted")
    inverse = constraint.inv()

    complement = sp.eye(15) - l0[()] * p0
    _, pivot_columns = complement.rref()
    if len(pivot_columns) != 11 or p0 * complement != sp.zeros(4, 15):
        raise AssertionError("normalized L0 complement drifted")

    responses = []
    correction_records = []
    old_sensitivities = []
    max_first_square_defect = 0
    for pivot_column in pivot_columns:
        for output_column in range(4):
            delta_l0 = sp.zeros(15, 4)
            delta_l0[:, output_column] = complement[:, pivot_column]
            source = pbw_h0.compose(d_aut, {(): delta_l0})
            delta_d = sp.zeros(60, 15)
            delta_l1 = {word: sp.zeros(60, 9) for word in ANSATZ_WORDS}
            for output_row in range(60):
                target = sp.Matrix([
                    source.get(word, sp.zeros(60, 4))[output_row, column]
                    for word, column in constraint_keys
                ])
                solution = -inverse * target
                delta_d[output_row, :] = solution[:15, :].T
                for word_index, word in enumerate(ANSATZ_WORDS):
                    delta_l1[word][output_row, :] = solution[
                        15 + 9 * word_index : 15 + 9 * (word_index + 1), :
                    ].T
            delta_l1 = _clean(delta_l1)
            first_square = _add(
                pbw_h0.compose({(): delta_d}, l0),
                source,
                _scale(pbw_h0.compose(delta_l1, first_bgg), -1),
            )
            max_first_square_defect = max(max_first_square_defect, _count(first_square))
            response = _add(
                pbw_c0.compose(middle, {(): delta_d}),
                _scale(pbw_c0.compose(pbw_h1.compose(middle, delta_l1), k_p0), -1),
            )
            sensitivity = _old_witness(response, phi_payload)
            if sensitivity != 0:
                old_sensitivities.append({
                    "pivot_column": pivot_column,
                    "output_column": output_column,
                    "value": str(sensitivity),
                })
            responses.append(response)
            correction_records.append({
                "pivot_column": pivot_column,
                "output_column": output_column,
                "delta_L0": _sparse(delta_l0),
                "delta_d_aut": _serialize_table({(): delta_d}),
                "delta_L1": _serialize_table(delta_l1),
            })
    if max_first_square_defect != 0 or len(responses) != 44:
        raise AssertionError("normalized L0 coupled family failed first-square closure")

    shifted_defect = _table(jet_payload["exact_data"]["identity_defects"]["shifted_chain_variation"])
    equation_keys = sorted(
        {
            (word, output_row, input_column)
            for operator in (shifted_defect, *responses)
            for word, matrix in operator.items()
            for output_row in range(matrix.rows)
            for input_column in range(matrix.cols)
            if matrix[output_row, input_column] != 0
        },
        key=lambda item: (len(item[0]), item[0], item[1], item[2]),
    )
    response_map = sp.Matrix([
        [operator.get(word, sp.zeros(60, 15))[output_row, input_column] for operator in responses]
        for word, output_row, input_column in equation_keys
    ])
    target = sp.Matrix([
        -shifted_defect.get(word, sp.zeros(60, 15))[output_row, input_column]
        for word, output_row, input_column in equation_keys
    ])
    _, row_pivots = response_map.row_join(target).T.rref()
    selected = list(row_pivots)
    augmented_rank = len(selected)
    selected_map = response_map[selected, :]
    selected_target = target[selected, :]
    _, local_rank_rows = selected_map.T.rref()
    rank_rows = [selected[index] for index in local_rank_rows]
    rank_minor_determinant = sp.factor(response_map[rank_rows, :].det())
    rank = len(rank_rows)
    if rank != 44 or augmented_rank != 45 or rank_minor_determinant == 0:
        raise AssertionError("normalized L0 obstruction ranks drifted")
    witness = selected_map.T.nullspace()[0]
    witness = (witness / (witness.T * selected_target)[0]).applyfunc(sp.expand)
    witness_terms = [
        {
            "word": list(equation_keys[selected[index]][0]),
            "output_row": equation_keys[selected[index]][1],
            "input_column": equation_keys[selected[index]][2],
            "coefficient": str(value),
        }
        for index, value in enumerate(witness)
        if value != 0
    ]
    left_defect = (witness.T * selected_map).applyfunc(sp.expand)
    target_value = sp.expand((witness.T * selected_target)[0])
    if len(witness_terms) != 5 or left_defect != sp.zeros(1, 44) or target_value != 1:
        raise AssertionError("compact normalized obstruction witness drifted")

    equation_basis_records = [
        {"word": list(word), "output_row": row, "input_column": column}
        for word, row, column in equation_keys
    ]
    response_record = _matrix_receipt(response_map, rank)
    target_record = _matrix_receipt(target, 1)

    return {
        "normalized_L0_family": {
            "equation": "p0 delta_L0 = 0",
            "complement": _sparse(complement),
            "complement_rank": complement.rank(),
            "pivot_columns": list(pivot_columns),
            "family_dimension": len(responses),
            "basis_labels": [
                {"pivot_column": pivot, "output_column": output}
                for pivot in pivot_columns for output in range(4)
            ],
        },
        "induced_corrections": correction_records,
        "first_square": {
            "equation": "delta_d_aut L0 + d_aut delta_L0 - delta_L1 K = 0",
            "rigid_map_shape": [constraint.rows, constraint.cols],
            "rigid_map_determinant": str(sp.factor(constraint.det())),
            "max_nonzero_defect_coefficients": max_first_square_defect,
        },
        "shifted_chain_system": {
            "equation": "response(delta_L0) = - shifted_chain_defect",
            "shape": [response_map.rows, response_map.cols],
            "rank": rank,
            "augmented_rank": augmented_rank,
            "kernel_dimension": response_map.cols - rank,
            "nonzero_coefficients": sum(value != 0 for value in response_map),
            "response_map_receipt": response_record,
            "target_receipt": target_record,
            "equation_basis_receipt": {
                "count": len(equation_basis_records),
                "sha256": _json_sha(equation_basis_records),
            },
            "full_column_rank_minor": {
                "rows": [equation_basis_records[index] for index in rank_rows],
                "determinant": str(rank_minor_determinant),
            },
        },
        "normalized_left_null_witness": {
            "support_size": len(witness_terms),
            "terms": witness_terms,
            "left_null_map_defect": _sparse(left_defect),
            "left_null_target_value": str(target_value),
        },
        "superseded_phi_witness": {
            "reachable": bool(old_sensitivities),
            "nonzero_basis_sensitivities": old_sensitivities,
            "interpretation": "the earlier Phi-only two-term witness is not an obstruction to this enlarged normalized-L0 family",
        },
        "interpretation": {
            "normalized_L0_coupled_repair_exists": False,
            "complete_coupled_SDR_obstructed": False,
            "required_next_ansatz": "vary K/p0 and neighbouring equation/constraint/cotangent rows coherently, or increase differential order, with action-derived cyclic completion",
        },
    }


def build() -> dict[str, Any]:
    exact = exact_data()
    return {
        "schema": "nariai-transverse-normalized-l0-coupled-obstruction-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1",
        "result_state": "NORMALIZED_L0_DRIVEN_INCIDENCE_L1_FAMILY_OBSTRUCTED_BY_FIVE_TERM_WITNESS",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_shifted_chain": {"path": str(JET_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", "sha256": _sha(JET_INPUT)},
            "phi_only_obstruction": {"path": str(PHI_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1", "sha256": _sha(PHI_INPUT)},
            "incidence_L1_rigidity": {"path": str(RIGIDITY_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1", "sha256": _sha(RIGIDITY_INPUT)},
        },
        "exact_data": exact,
        "exact_checks": {
            "normalized_L0_family_dimension_44": exact["normalized_L0_family"]["family_dimension"] == 44,
            "all_induced_first_squares_exact": exact["first_square"]["max_nonzero_defect_coefficients"] == 0,
            "response_map_full_column_rank": exact["shifted_chain_system"]["rank"] == 44,
            "augmented_rank_obstructed": exact["shifted_chain_system"]["augmented_rank"] == 45,
            "five_term_witness_left_null": exact["normalized_left_null_witness"]["support_size"] == 5 and exact["normalized_left_null_witness"]["left_null_map_defect"]["rank"] == 0,
            "five_term_witness_normalized": exact["normalized_left_null_witness"]["left_null_target_value"] == "1",
            "old_Phi_witness_reachable": exact["superseded_phi_witness"]["reachable"] is True,
            "complete_SDR_not_overclaimed": exact["interpretation"]["complete_coupled_SDR_obstructed"] is False,
        },
        "flags": {
            "TRANSVERSE_NORMALIZED_L0_COUPLED_SHIFTED_CHAIN_REPAIR": False,
            "TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_EXACT": True,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_K_P0_CONSTRAINT_COTANGENT_COUPLED_VARIATION",
        "claim_boundary": "This certificate exhausts the 44-dimensional normalized algebraic L0 family p0 delta_L0=0. For every basis direction it solves the unique algebraic-incidence/order-at-most-one-L1 pair that preserves the complete first BGG square. The resulting shifted-chain response map has rank 44 and augmented rank 45; a normalized five-term algebraic left-null witness proves inconsistency. The older Phi-only witness is reachable in this enlarged family and is explicitly superseded as the decisive obstruction. This does not obstruct coherent K/p0, equation/constraint/cotangent, higher-order, complete rank-310 SDR, or causal corrections.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_normalized_l0_coupled_obstruction --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_normalized_l0_coupled_obstruction.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_normalized_l0_coupled_obstruction",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-normalized-l0-coupled-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    witness = data["normalized_left_null_witness"]
    terms = " + ".join(
        f"({term['coefficient']}) E[{term['word']},{term['output_row']},{term['input_column']}]"
        for term in witness["terms"]
    )
    return rf"""# Transverse Nariai normalized-L0 coupled obstruction

The normalized splitting family (p_0\delta L_0=0) has dimension 44.  Each
basis direction determines a unique algebraic incidence correction and
order-at-most-one (\delta L_1) preserving the complete first BGG square.
The resulting shifted-chain response map has shape
`{data['shifted_chain_system']['shape']}`, rank 44 and augmented rank 45.

The normalized compact witness is

```text
{terms}
```

It annihilates all 44 responses and evaluates to one on the target.  The old
Phi-only witness is reachable here, so it is superseded rather than reused.
The result does not obstruct coherent `K/p0`, equation/constraint/cotangent,
higher-order, rank-310 SDR, or causal corrections.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("normalized-L0 coupled obstruction artifact is stale")
    print("NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
