#!/usr/bin/env python3
"""Obstruct the complete local order-two Phi-only transverse repair."""

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
from d_quotient_classical.causal_transfer.nariai_transverse_first_order_schur_solve import _sparse
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import _deserialize, _pbw_layers


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JET_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
PHI1_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-phi-second-order-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-phi-second-order-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_phi_second_order_obstruction.py"
TESTS = HERE / "tests/test_nariai_transverse_phi_second_order_obstruction.py"
WORDS = ((), (0,), (1,), (2,), (3,), (0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict[str, Any]) -> dict[tuple[int, ...], sp.Matrix]:
    return {tuple(entry["word"]): _deserialize(entry["matrix"]) for entry in record["entries"]}


def _matrix_receipt(matrix: sp.Matrix, rank: int) -> dict[str, Any]:
    entries = [[row, column, str(matrix[row, column])] for row in range(matrix.rows) for column in range(matrix.cols) if matrix[row, column] != 0]
    canonical = json.dumps({"shape": [matrix.rows, matrix.cols], "entries": entries}, sort_keys=True, separators=(",", ":"))
    return {"shape": [matrix.rows, matrix.cols], "rank": rank, "nonzero_coefficients": len(entries), "sha256": hashlib.sha256(canonical.encode()).hexdigest()}


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    jet = json.loads(JET_INPUT.read_text())
    phi1 = json.loads(PHI1_INPUT.read_text())
    if phi1["flags"]["TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_EXACT"] is not True:
        raise AssertionError("first-order Phi obstruction unavailable")
    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    pbw = _pbw_layers()["C0"].base
    k_p0 = fixture()["k_p0"]
    responses = []
    basis = []
    keys = {(word, column) for word, matrix in defect.items() for column in range(matrix.cols)}
    for word in WORDS:
        for middle_column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, middle_column] = 1
            response = pbw.compose(correction, k_p0)
            responses.append(response)
            basis.append({"word": list(word), "middle_column": middle_column})
            keys.update((response_word, column) for response_word, matrix in response.items() for column in range(matrix.cols))
    keys = sorted(keys, key=lambda item: (len(item[0]), item[0], item[1]))
    coefficient_map = sp.Matrix([
        [response.get(word, sp.zeros(1, 15))[0, column] for response in responses]
        for word, column in keys
    ])
    _, column_pivots = coefficient_map.rref()
    independent_columns = list(column_pivots)
    _, row_pivots = coefficient_map[:, independent_columns].T.rref()
    independent_rows = list(row_pivots)
    minor_determinant = sp.factor(coefficient_map[independent_rows, independent_columns].det())
    rank = len(independent_columns)
    if rank != 130 or minor_determinant == 0:
        raise AssertionError("order-two Phi rank drifted")

    targets = [sp.Matrix([defect.get(word, sp.zeros(60, 15))[row, column] for word, column in keys]) for row in range(60)]
    augmented_ranks = [coefficient_map.row_join(target).rank() for target in targets]
    consistent_rows = [row for row, value in enumerate(augmented_ranks) if value == rank]
    obstructed_rows = [row for row, value in enumerate(augmented_ranks) if value > rank]
    if len(consistent_rows) != 29 or len(obstructed_rows) != 31:
        raise AssertionError("order-two Phi obstruction multiplicities drifted")

    witness_row = obstructed_rows[0]
    augmented = coefficient_map.row_join(targets[witness_row])
    _, selected_rows = augmented.T.rref()
    selected = list(selected_rows)
    selected_map = coefficient_map[selected, :]
    selected_target = targets[witness_row][selected, :]
    witness = selected_map.T.nullspace()[0]
    witness = (witness / (witness.T * selected_target)[0]).applyfunc(sp.expand)
    witness_terms = [
        {"word": list(keys[selected[index]][0]), "input_column": keys[selected[index]][1], "coefficient": str(value)}
        for index, value in enumerate(witness) if value != 0
    ]
    if len(witness_terms) != 2 or witness.T * selected_map != sp.zeros(1, 135) or (witness.T * selected_target)[0] != 1:
        raise AssertionError("order-two Phi witness drifted")

    equation_records = [{"word": list(word), "input_column": column} for word, column in keys]
    return {
        "ansatz": {
            "scope": "Phi row only; complete local differential order at most two",
            "words": [list(word) for word in WORDS],
            "basis": basis,
            "unknowns_per_output_row": len(basis),
            "output_rows": 60,
        },
        "coefficient_system": {
            "shape": [coefficient_map.rows, coefficient_map.cols],
            "rank": rank,
            "kernel_dimension": coefficient_map.cols - rank,
            "matrix_receipt": _matrix_receipt(coefficient_map, rank),
            "equation_basis": equation_records,
            "full_rank_minor": {
                "rows": [equation_records[index] for index in independent_rows],
                "columns": independent_columns,
                "determinant": str(minor_determinant),
            },
            "augmented_ranks": augmented_ranks,
            "consistent_rows": consistent_rows,
            "obstructed_rows": obstructed_rows,
        },
        "normalized_left_null_witness": {
            "output_row": witness_row,
            "support_size": len(witness_terms),
            "terms": witness_terms,
            "left_null_target_value": "1",
        },
        "interpretation": {
            "order_two_Phi_only_repair_exists": False,
            "complete_coupled_SDR_obstructed": False,
            "required_next_ansatz": "neighbouring equation/constraint/cotangent rows or a homotopy-coherent equation cone, with action-derived cyclic completion",
        },
    }


def build() -> dict[str, Any]:
    exact = exact_data()
    return {
        "schema": "nariai-transverse-phi-second-order-obstruction-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1",
        "result_state": "COMPLETE_ORDER_TWO_PHI_ONLY_REPAIR_OBSTRUCTED_IN_31_OF_60_ROWS",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_shifted_chain": {"path": str(JET_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", "sha256": _sha(JET_INPUT)},
            "first_order_Phi_obstruction": {"path": str(PHI1_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1", "sha256": _sha(PHI1_INPUT)},
        },
        "exact_data": exact,
        "exact_checks": {
            "complete_order_two_basis": exact["ansatz"]["unknowns_per_output_row"] == 135,
            "rank_130": exact["coefficient_system"]["rank"] == 130,
            "kernel_dimension_five": exact["coefficient_system"]["kernel_dimension"] == 5,
            "twenty_nine_rows_consistent": len(exact["coefficient_system"]["consistent_rows"]) == 29,
            "thirty_one_rows_obstructed": len(exact["coefficient_system"]["obstructed_rows"]) == 31,
            "normalized_two_term_witness": exact["normalized_left_null_witness"]["support_size"] == 2 and exact["normalized_left_null_witness"]["left_null_target_value"] == "1",
            "complete_SDR_not_overclaimed": exact["interpretation"]["complete_coupled_SDR_obstructed"] is False,
        },
        "flags": {
            "TRANSVERSE_ORDER_TWO_PHI_ONLY_SHIFTED_CHAIN_REPAIR": False,
            "TRANSVERSE_ORDER_TWO_PHI_ONLY_OBSTRUCTION_EXACT": True,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_EQUATION_CONSTRAINT_COTANGENT_COUPLED_VARIATION",
        "claim_boundary": "This exact screen exhausts every local Phi-row correction through differential order two. Its 525-by-135 coefficient map has rank 130 and kernel dimension five. Twenty-nine target rows are consistent, while 31 have augmented rank 131. A normalized two-term witness in row zero certifies inconsistency. This does not obstruct coupled equation/constraint/cotangent or homotopy-coherent equation-cone corrections, higher-order ansatzes with their induced top-order cancellation constraints, the complete SDR, or causal transfer.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_phi_second_order_obstruction --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_phi_second_order_obstruction.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_phi_second_order_obstruction",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-phi-second-order-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    terms = " + ".join(f"({term['coefficient']}) E[{term['word']},{term['input_column']}]" for term in data["normalized_left_null_witness"]["terms"])
    return f"""# Transverse Nariai order-two Phi obstruction

The complete local order-at-most-two Phi-only map has shape
`{data['coefficient_system']['shape']}`, rank 130 and kernel dimension five.
Exactly 29 output rows are consistent and 31 are obstructed.  The normalized
row-zero witness is

```text
{terms}
```

It annihilates the complete 135-direction ansatz and evaluates to one on the
target.  Coupled equation/constraint/cotangent and homotopy-coherent cone
corrections remain open.
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
        raise AssertionError("order-two Phi obstruction artifact is stale")
    print("NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
