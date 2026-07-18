#!/usr/bin/env python3
"""Solve the complete first-order transverse Nariai Schur gauge equation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import (
    _clean,
    _deserialize,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-first-order-schur-solve.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-first-order-schur-solve-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_first_order_schur_solve.py"
TESTS = HERE / "tests/test_nariai_transverse_first_order_schur_solve.py"


Table = dict[tuple[int, ...], sp.Matrix]
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
        "sha256": hashlib.sha256(
            sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
        ).hexdigest(),
    }


def _table(record: dict[str, Any]) -> Table:
    return {
        tuple(entry["word"]): _deserialize(entry["matrix"])
        for entry in record["entries"]
    }


def _serialize_table(table: Table) -> dict[str, Any]:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return {
        "orders": sorted({len(word) for word in table}),
        "nonzero_coefficients": sum(
            value != 0 for matrix in table.values() for value in matrix
        ),
        "entries": [
            {"word": list(word), "matrix": _sparse(table[word])}
            for word in sorted(table)
        ],
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def solve() -> dict[str, Any]:
    dependency = json.loads(INPUT.read_text())
    if dependency["result_id"] != "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1":
        raise AssertionError("jet-aware Schur dependency drifted")
    if dependency["flags"]["TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE"] is not True:
        raise AssertionError("complete curvature-jet coverage is unavailable")

    defect = _table(
        dependency["exact_data"]["differential_schur_gate"][
            "unrepaired_gauge_defect"
        ]
    )
    middle = middle_fixture()
    first_bgg = middle["first_bgg"]
    pbw = middle["pbw_h0"]

    responses: list[Table] = []
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
    coefficient_rank = coefficient_map.rank()
    if coefficient_map.cols != 45 or coefficient_rank != 45:
        raise AssertionError("complete first-order Schur map lost injectivity")

    correction = {word: sp.zeros(9, 9) for word in ANSATZ_WORDS}
    augmented_ranks: list[int] = []
    free_parameter_counts: list[int] = []
    for output_row in range(9):
        target = sp.Matrix(
            [
                -defect.get(word, sp.zeros(9, 4))[output_row, column]
                for word, column in ordered_keys
            ]
        )
        augmented_rank = coefficient_map.row_join(target).rank()
        augmented_ranks.append(augmented_rank)
        if augmented_rank != coefficient_rank:
            raise AssertionError(f"first-order Schur row {output_row} is inconsistent")
        solution, parameters = coefficient_map.gauss_jordan_solve(target)
        free_parameter_counts.append(parameters.rows)
        if parameters.rows:
            raise AssertionError("first-order Schur solution ceased to be unique")
        for index, value in enumerate(solution):
            word = ANSATZ_WORDS[index // 9]
            correction[word][output_row, index % 9] = sp.expand(value)
    correction = _clean(correction)

    response = pbw.compose(correction, first_bgg)
    residual = _clean(
        {
            word: (
                response.get(word, sp.zeros(9, 4))
                + defect.get(word, sp.zeros(9, 4))
            ).applyfunc(sp.expand)
            for word in set(response) | set(defect)
        }
    )
    if residual:
        raise AssertionError("first-order Schur correction did not close the gauge row")

    return {
        "ansatz": {
            "operator_type": "H1_to_H1dual",
            "formula": "Qdot=Q0+sum_a Qa nabla_a",
            "derivative_orders": [0, 1],
            "unknowns_per_output_row": 45,
            "output_rows": 9,
            "total_unknowns": 405,
            "equations_per_output_row": len(ordered_keys),
            "equation_orders": sorted({len(word) for word, _ in ordered_keys}),
        },
        "linear_system": {
            "coefficient_map_shape": [coefficient_map.rows, coefficient_map.cols],
            "coefficient_map_rank": coefficient_rank,
            "augmented_ranks": augmented_ranks,
            "free_parameter_counts": free_parameter_counts,
            "equation_keys": [
                {"word": list(word), "input_column": column}
                for word, column in ordered_keys
            ],
            "coefficient_map": _sparse(coefficient_map),
        },
        "unique_first_order_correction": _serialize_table(correction),
        "corrected_gauge_residual": _serialize_table(residual),
        "interpretation": {
            "local_first_order_gauge_repair_exists": True,
            "local_first_order_gauge_repair_unique_in_complete_ansatz": True,
            "action_derived_identification": False,
            "cyclicity_with_authoritative_action_pairing": False,
            "reason_for_fail_closed_boundary": "gauge closure and ansatz uniqueness do not by themselves derive the correction from the Weyl-squared action or certify the cyclic Hom-bundle adjoint",
        },
    }


def build() -> dict[str, Any]:
    exact = solve()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "nariai-transverse-first-order-schur-solve-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1",
        "result_state": "COMPLETE_FIRST_ORDER_LOCAL_GAUGE_SCHUR_EXISTS_UNIQUELY_ACTION_AND_CYCLIC_IDENTIFICATION_OPEN",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_middle_schur": {
                "path": str(INPUT.relative_to(ROOT)),
                "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1",
                "sha256": _sha(INPUT),
            }
        },
        "exact_data": exact,
        "exact_checks": {
            "complete_first_order_ansatz": exact["ansatz"]["total_unknowns"] == 405,
            "coefficient_map_full_column_rank": exact["linear_system"]["coefficient_map_rank"] == 45,
            "all_nine_rows_consistent": exact["linear_system"]["augmented_ranks"] == [45] * 9,
            "solution_unique": exact["linear_system"]["free_parameter_counts"] == [0] * 9,
            "corrected_gauge_residual_zero": exact["corrected_gauge_residual"]["nonzero_coefficients"] == 0,
            "action_identification_not_promoted": exact["interpretation"]["action_derived_identification"] is False,
            "cyclicity_not_promoted": exact["interpretation"]["cyclicity_with_authoritative_action_pairing"] is False,
        },
        "flags": {
            "TRANSVERSE_FIRST_ORDER_GAUGE_SCHUR_EXISTS": True,
            "TRANSVERSE_FIRST_ORDER_GAUGE_SCHUR_UNIQUE": True,
            "TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION": False,
            "TRANSVERSE_CYCLIC_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_ACTION_AND_CYCLIC_IDENTIFICATION_OF_UNIQUE_FIRST_ORDER_SCHUR",
        "claim_boundary": "This exact calculation exhausts the complete local first-order H1-to-H1dual Schur ansatz in the declared covariant PBW frame. The 60-by-45 coefficient map has full column rank, all nine output rows are consistent, and the resulting 59-coefficient correction is unique and kills the complete transverse endpoint gauge defect. This proves local first-order gauge repair, not that the correction is the variation of the action-derived Bach Hessian or that it is cyclic for the authoritative action/Hom-bundle adjoint. The rank-310 SDR and causal transfer remain open.",
        "source_manifest": sources,
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_first_order_schur_solve --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_first_order_schur_solve.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_first_order_schur_solve",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-first-order-schur-solve-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return f"""# Transverse Nariai first-order Schur solve

The complete local first-order ansatz

\\[
\\dot Q=Q_0+Q^a\\nabla_a:H_1\\longrightarrow H_1^\\vee
\\]

has 45 unknown coefficients per output row.  Its exact coefficient map into
the differentiated gauge equation has shape
`{data['linear_system']['coefficient_map_shape'][0]} x {data['linear_system']['coefficient_map_shape'][1]}`
and rank `{data['linear_system']['coefficient_map_rank']}`.  Every one of the
nine augmented systems has the same rank and no free parameter.

The unique correction contains
`{data['unique_first_order_correction']['nonzero_coefficients']}` nonzero PBW
coefficients and gives a zero corrected gauge residual.

This closes the local gauge-repair existence question.  It does **not** yet
identify the correction with the transverse variation of the action-derived
Bach Hessian, and it does not promote cyclicity through the authoritative
action/Hom-bundle adjoint.  Those are the next gate; the complete rank-310 SDR
and causal transfer remain open.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check:
        if json.loads(OUTPUT.read_text()) != payload:
            raise AssertionError("first-order Schur artifact is stale")
    print("NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1: PASS")


if __name__ == "__main__":
    main()
