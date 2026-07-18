#!/usr/bin/env python3
"""Obstruct a first-order Phi-only repair of the transverse shifted chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_transverse_first_order_schur_solve import (
    _serialize_table,
    _sparse,
)
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import (
    _deserialize,
    _pbw_layers,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JET_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
SCHUR_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-phi-only-shifted-chain-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-phi-only-shifted-chain-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_phi_only_shifted_chain_obstruction.py"
TESTS = HERE / "tests/test_nariai_transverse_phi_only_shifted_chain_obstruction.py"


Table = dict[tuple[int, ...], sp.Matrix]
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict[str, Any]) -> Table:
    return {
        tuple(entry["word"]): _deserialize(entry["matrix"])
        for entry in record["entries"]
    }


def exact_data() -> dict[str, Any]:
    jet = json.loads(JET_INPUT.read_text())
    schur = json.loads(SCHUR_INPUT.read_text())
    if jet["flags"]["TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE"] is not True:
        raise AssertionError("jet-aware shifted-chain input unavailable")
    if schur["flags"]["TRANSVERSE_FIRST_ORDER_GAUGE_SCHUR_UNIQUE"] is not True:
        raise AssertionError("unique endpoint Schur input unavailable")

    defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    automorphism = automorphism_fixture()
    k_p0 = automorphism["k_p0"]
    pbw = _pbw_layers()["C0"].base

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
            response = pbw.compose(basis, k_p0)
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
                response.get(word, sp.zeros(1, 15))[0, column]
                for response in responses
            ]
            for word, column in ordered_keys
        ]
    )
    rank = coefficient_map.rank()
    if coefficient_map.shape != (225, 45) or rank != 45:
        raise AssertionError("Phi-only coefficient map drifted")

    targets = [
        sp.Matrix(
            [
                defect.get(word, sp.zeros(60, 15))[output_row, column]
                for word, column in ordered_keys
            ]
        )
        for output_row in range(60)
    ]
    augmented_ranks = [coefficient_map.row_join(target).rank() for target in targets]
    consistent_rows = [row for row, value in enumerate(augmented_ranks) if value == rank]
    obstructed_rows = [row for row, value in enumerate(augmented_ranks) if value > rank]
    if len(consistent_rows) != 22 or len(obstructed_rows) != 38:
        raise AssertionError("Phi-only obstruction multiplicities drifted")

    left_kernel = coefficient_map.T.nullspace()
    witness_row = obstructed_rows[0]
    target = targets[witness_row]
    witness = next(vector for vector in left_kernel if (vector.T * target)[0] != 0)
    witness = (witness / (witness.T * target)[0]).applyfunc(sp.expand)
    left_defect = (witness.T * coefficient_map).applyfunc(sp.expand)
    target_value = sp.expand((witness.T * target)[0])
    if left_defect != sp.zeros(1, 45) or target_value != 1:
        raise AssertionError("normalized left-null witness failed")

    witness_terms = [
        {
            "equation_index": index,
            "word": list(ordered_keys[index][0]),
            "input_column": ordered_keys[index][1],
            "coefficient": str(value),
        }
        for index, value in enumerate(witness)
        if value != 0
    ]
    if len(witness_terms) != 2:
        raise AssertionError("minimal normalized witness support drifted")

    consistent_solutions: dict[str, dict[str, Any]] = {}
    for row in consistent_rows:
        solution, parameters = coefficient_map.gauss_jordan_solve(targets[row])
        if parameters.rows:
            raise AssertionError("consistent Phi-only row ceased to be unique")
        table = {word: sp.zeros(1, 9) for word in ANSATZ_WORDS}
        for index, value in enumerate(solution):
            table[ANSATZ_WORDS[index // 9]][0, index % 9] = sp.expand(value)
        table = {word: matrix for word, matrix in table.items() if matrix != sp.zeros(1, 9)}
        consistent_solutions[str(row)] = _serialize_table(table)

    return {
        "attempted_repair": {
            "equation": "Phi_dot_correction Kp0 = shifted_chain_defect",
            "scope": "Phi row only; complete local differential order at most one",
            "unknowns_per_output_row": 45,
            "output_rows": 60,
            "total_unknowns": 2700,
            "target_orders": sorted({len(word) for word in defect}),
            "ansatz_orders": [0, 1],
        },
        "linear_system": {
            "shape": [coefficient_map.rows, coefficient_map.cols],
            "rank": rank,
            "augmented_ranks": augmented_ranks,
            "consistent_rows": consistent_rows,
            "obstructed_rows": obstructed_rows,
            "coefficient_map": _sparse(coefficient_map),
            "equation_keys": [
                {"word": list(word), "input_column": column}
                for word, column in ordered_keys
            ],
        },
        "normalized_left_null_witness": {
            "output_row": witness_row,
            "support_size": len(witness_terms),
            "terms": witness_terms,
            "left_null_map_defect": _sparse(left_defect),
            "left_null_target_value": str(target_value),
        },
        "consistent_row_solutions": consistent_solutions,
        "shifted_chain_defect": _serialize_table(defect),
        "interpretation": {
            "first_order_Phi_only_repair_exists": False,
            "full_coupled_SDR_repair_obstructed": False,
            "required_next_ansatz": "coupled variations of the incidence/splitting/constraint rows, or a higher-order Phi correction, with cyclic cotangent completion",
        },
    }


def build() -> dict[str, Any]:
    exact = exact_data()
    return {
        "schema": "nariai-transverse-phi-only-shifted-chain-obstruction-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1",
        "result_state": "FIRST_ORDER_PHI_ONLY_SHIFTED_CHAIN_REPAIR_OBSTRUCTED_BY_NORMALIZED_LEFT_NULL_WITNESS",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_shifted_chain": {"path": str(JET_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", "sha256": _sha(JET_INPUT)},
            "unique_endpoint_schur": {"path": str(SCHUR_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1", "sha256": _sha(SCHUR_INPUT)},
        },
        "exact_data": exact,
        "exact_checks": {
            "coefficient_map_full_column_rank": exact["linear_system"]["rank"] == 45,
            "twenty_two_rows_consistent": len(exact["linear_system"]["consistent_rows"]) == 22,
            "thirty_eight_rows_obstructed": len(exact["linear_system"]["obstructed_rows"]) == 38,
            "normalized_witness_is_left_null": exact["normalized_left_null_witness"]["left_null_map_defect"]["rank"] == 0,
            "normalized_witness_detects_target": exact["normalized_left_null_witness"]["left_null_target_value"] == "1",
            "full_coupled_repair_not_overclaimed": exact["interpretation"]["full_coupled_SDR_repair_obstructed"] is False,
        },
        "flags": {
            "TRANSVERSE_FIRST_ORDER_PHI_ONLY_SHIFTED_CHAIN_REPAIR": False,
            "TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_EXACT": True,
            "TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION": False,
            "TRANSVERSE_CYCLIC_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_COUPLED_INCIDENCE_SPLITTING_CONSTRAINT_SDR_VARIATION",
        "claim_boundary": "This exact screen exhausts the complete local order-at-most-one correction of the Phi row alone in the transverse shifted-chain identity. The 225-by-45 coefficient map has rank 45, but 38 of 60 output rows have augmented rank 46. A normalized two-term left-null witness in output row zero annihilates the full ansatz map and pairs to one with the target. Thus a first-order Phi-only repair is impossible. This does not obstruct a coupled correction of the incidence, splitting and constraint rows, a higher-order Phi correction, the complete rank-310 SDR, or causal transfer.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_phi_only_shifted_chain_obstruction --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_phi_only_shifted_chain_obstruction.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_phi_only_shifted_chain_obstruction",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-phi-only-shifted-chain-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    witness = data["normalized_left_null_witness"]
    terms = " + ".join(
        f"({term['coefficient']}) E[{term['word']},{term['input_column']}]"
        for term in witness["terms"]
    )
    return f"""# Transverse Nariai Phi-only shifted-chain obstruction

The complete local first-order attempt

\\[
\\dot\\Phi_{{\\rm corr}}(Kp_0)=\\Delta_{{\\rm shifted}}
\\]

has a `225 x 45` coefficient map of rank 45 on each of the sixty output rows.
Exactly 22 rows are consistent; 38 have augmented rank 46.

The normalized witness in output row `{witness['output_row']}` is

```text
{terms}
```

It annihilates every ansatz column and evaluates to `1` on the target.  This
is an exact obstruction to a first-order correction of `Phi` alone.  It is
not an obstruction to the coupled incidence/splitting/constraint variation,
to a higher-order `Phi` correction, to the rank-310 SDR, or to causal transfer.
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
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("Phi-only shifted-chain artifact is stale")
    print("NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
