#!/usr/bin/env python3
"""Certify rigidity of the smallest coupled transverse incidence/L1 repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture,
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
PHI_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-incidence-l1-rigidity.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-incidence-l1-rigidity-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_incidence_l1_rigidity.py"
TESTS = HERE / "tests/test_nariai_transverse_incidence_l1_rigidity.py"

ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(record: dict[str, Any]) -> dict[tuple[int, ...], sp.Matrix]:
    return {
        tuple(entry["word"]): _deserialize(entry["matrix"])
        for entry in record["entries"]
    }


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _subtract_identity(table: dict[tuple[int, ...], sp.Matrix], size: int) -> dict[tuple[int, ...], sp.Matrix]:
    result = {word: matrix.copy() for word, matrix in table.items()}
    result[()] = result.get((), sp.zeros(size)) - sp.eye(size)
    return {word: matrix for word, matrix in result.items() if matrix != sp.zeros(*matrix.shape)}


def exact_data() -> dict[str, Any]:
    jet = json.loads(JET_INPUT.read_text())
    phi = json.loads(PHI_INPUT.read_text())
    if jet["flags"]["TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE"] is not True:
        raise AssertionError("jet-aware transverse input unavailable")
    if phi["flags"]["TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_EXACT"] is not True:
        raise AssertionError("Phi-only obstruction input unavailable")

    base = fixture()
    pbw = _pbw_layers()["H0"].base
    l0 = base["corrected_l0"]
    k_p0 = base["k_p0"]
    p0 = base["projection0"]
    first_bgg = pbw.compose(k_p0, l0)
    projection_defect = _subtract_identity(pbw.compose({(): p0}, l0), 4)
    if projection_defect:
        raise AssertionError("p0 L0 normalization drifted")

    responses: list[dict[tuple[int, ...], sp.Matrix]] = []
    unknowns: list[dict[str, Any]] = []
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

    equation_keys = sorted(
        {
            (word, column)
            for response in responses
            for word, matrix in response.items()
            for column in range(matrix.cols)
        },
        key=lambda item: (len(item[0]), item[0], item[1]),
    )
    coefficient_map = sp.Matrix(
        [
            [
                response.get(word, sp.zeros(1, 4))[0, column]
                for response in responses
            ]
            for word, column in equation_keys
        ]
    )
    rank = coefficient_map.rank()
    determinant = sp.factor(coefficient_map.det())
    if coefficient_map.shape != (60, 60) or rank != 60 or determinant == 0:
        raise AssertionError("incidence/L1 homogeneous constraint map ceased to be invertible")

    shifted_defect = _table(jet["exact_data"]["identity_defects"]["shifted_chain_variation"])
    shifted_count = _count(shifted_defect)
    if shifted_count != 207:
        raise AssertionError("shifted-chain defect count drifted")

    return {
        "ansatz": {
            "equation": "delta_d_aut L0 - delta_L1 K = 0",
            "delta_d_aut_order": 0,
            "delta_L1_orders": [0, 1],
            "unknowns_per_output_row": 60,
            "output_rows": 60,
            "scope": "homogeneous preservation of the complete first BGG square; no delta_L0, delta_K, delta_p0, constraint-row, or cyclic-dual variation",
        },
        "normalization": {
            "p0_L0_minus_identity": _serialize_table(projection_defect),
            "reconstructed_first_BGG": _serialize_table(first_bgg),
        },
        "constraint_system": {
            "shape": [coefficient_map.rows, coefficient_map.cols],
            "rank": rank,
            "determinant": str(determinant),
            "kernel_dimension": coefficient_map.cols - rank,
            "nonzero_coefficients": sum(value != 0 for value in coefficient_map),
            "coefficient_map": _sparse(coefficient_map),
            "unknown_basis": unknowns,
            "equation_keys": [
                {"word": list(word), "input_column": column}
                for word, column in equation_keys
            ],
        },
        "unrepaired_shifted_chain": {
            "nonzero_coefficients": shifted_count,
            "operator": _serialize_table(shifted_defect),
        },
        "interpretation": {
            "nonzero_homogeneous_incidence_L1_correction_exists": False,
            "shifted_chain_repaired_in_this_ansatz": False,
            "complete_coupled_SDR_obstructed": False,
            "required_next_ansatz": "vary L0, K/p0, or neighbouring constraint/cotangent rows coherently, or increase differential order; impose action-derived cyclicity in the same solve",
        },
    }


def build() -> dict[str, Any]:
    exact = exact_data()
    return {
        "schema": "nariai-transverse-incidence-l1-rigidity-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1",
        "result_state": "COMPLETE_ALGEBRAIC_INCIDENCE_FIRST_ORDER_L1_HOMOGENEOUS_REPAIR_IS_RIGID",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_shifted_chain": {"path": str(JET_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", "sha256": _sha(JET_INPUT)},
            "phi_only_obstruction": {"path": str(PHI_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1", "sha256": _sha(PHI_INPUT)},
        },
        "exact_data": exact,
        "exact_checks": {
            "projection_normalization_exact": exact["normalization"]["p0_L0_minus_identity"]["nonzero_coefficients"] == 0,
            "constraint_map_square": exact["constraint_system"]["shape"] == [60, 60],
            "constraint_map_invertible": exact["constraint_system"]["rank"] == 60 and exact["constraint_system"]["determinant"] != "0",
            "homogeneous_kernel_zero": exact["constraint_system"]["kernel_dimension"] == 0,
            "shifted_chain_still_nonzero": exact["unrepaired_shifted_chain"]["nonzero_coefficients"] == 207,
            "complete_SDR_not_overclaimed": exact["interpretation"]["complete_coupled_SDR_obstructed"] is False,
        },
        "flags": {
            "TRANSVERSE_ALGEBRAIC_INCIDENCE_FIRST_ORDER_L1_FREEDOM": False,
            "TRANSVERSE_INCIDENCE_L1_RIGIDITY_EXACT": True,
            "TRANSVERSE_SHIFTED_CHAIN_REPAIRED": False,
            "TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION": False,
            "TRANSVERSE_CYCLIC_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_L0_K_CONSTRAINT_COUPLED_SDR_VARIATION",
        "claim_boundary": "This certificate exhausts the homogeneous correction pair consisting of an algebraic variation of the C0-to-C1 incidence row and an order-at-most-one variation of L1, while the complete first BGG square is held exact. Per output row the exact 60-by-60 constraint map has determinant -1/2^36, hence the only allowed pair is zero. Because the transverse shifted-chain defect has 207 nonzero coefficients, this pair cannot repair it. The result does not obstruct coherent variations of L0, K/p0, neighbouring equation/constraint/cotangent rows, higher differential order, the complete rank-310 SDR, or causal transfer.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_incidence_l1_rigidity --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_incidence_l1_rigidity.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_incidence_l1_rigidity",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-incidence-l1-rigidity-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    system = payload["exact_data"]["constraint_system"]
    return rf"""# Transverse Nariai incidence/L1 rigidity

The smallest coupled homogeneous repair preserves the complete first BGG
square,

\[
\delta d_{{\rm aut}}L_0-\delta L_1K=0,
\]

with algebraic `delta_d_aut` and order-at-most-one `delta_L1`.  For every
output row its exact coefficient map has shape `{system['shape']}`, rank
`{system['rank']}`, and determinant `{system['determinant']}`.  Its kernel is
zero, so no nonzero pair in this ansatz can act on the 207-coefficient
shifted-chain defect.

This supersedes any coefficient-layer-only sensitivity screen: preserving one
algebraic coefficient is weaker than preserving the full differential first
square.  The theorem does not cover coherent variations of `L0`, `K/p0`,
neighbouring constraint/cotangent rows, higher order, the rank-310 SDR, or
causal transfer.
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
        raise AssertionError("incidence/L1 rigidity artifact is stale")
    print("NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1: PASS")


if __name__ == "__main__":
    main()
