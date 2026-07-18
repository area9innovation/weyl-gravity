#!/usr/bin/env python3
"""Unique factorized endpoint completion along the transverse Nariai tangent."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    jet_add,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import endpoint_operator
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    _table_add,
    _table_scale,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _count,
    _deserialize_table,
    _difference,
    _table,
)
from d_quotient_classical.causal_transfer.nariai_transverse_factorized_hom_schur_replay import operator_data


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-factorized-endpoint-completion.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-factorized-endpoint-completion-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_factorized_endpoint_completion.py"
TESTS = HERE / "tests/test_nariai_transverse_factorized_endpoint_completion.py"
SCHUR_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json"
UPPER_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json"
OLD_SOLVE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json"
SCHUR_PRODUCER = HERE / "nariai_transverse_factorized_hom_schur_replay.py"
UPPER_PRODUCER = HERE / "nariai_transverse_relative_saddle_upper_chain.py"


Table = dict[tuple[int, ...], sp.Matrix]
ANSATZ_WORDS = ((), (0,), (1,), (2,), (3,))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _solve_correction(defect: Table, pbw, gauge) -> dict[str, Any]:
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
            response = pbw.compose(
                parallel_zero_variation(basis, f"basis-{word}-{middle_index}"),
                gauge,
                f"response-{word}-{middle_index}",
            ).base
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
    rank = coefficient_map.rank()
    if coefficient_map.shape != (60, 45) or rank != 45:
        raise AssertionError("factorized endpoint correction map drifted")
    correction = {word: sp.zeros(9, 9) for word in ANSATZ_WORDS}
    augmented_ranks = []
    free_parameters = []
    for output_row in range(9):
        target = sp.Matrix(
            [
                -defect.get(word, sp.zeros(9, 4))[output_row, column]
                for word, column in ordered_keys
            ]
        )
        augmented_ranks.append(coefficient_map.row_join(target).rank())
        solution, parameters = coefficient_map.gauss_jordan_solve(target)
        free_parameters.append(parameters.rows)
        if augmented_ranks[-1] != rank or parameters.rows:
            raise AssertionError(f"factorized endpoint row {output_row} is not unique")
        for index, value in enumerate(solution):
            word = ANSATZ_WORDS[index // 9]
            correction[word][output_row, index % 9] = sp.expand(value)
    correction = {
        word: matrix for word, matrix in correction.items() if matrix != sp.zeros(9)
    }
    response = pbw.compose(
        parallel_zero_variation(correction, "Qdot-solution"),
        gauge,
        "Qdot-K-response",
    ).base
    residual = _table_add(defect, response)
    if residual:
        raise AssertionError("factorized endpoint correction missed the gauge row")
    return {
        "correction": correction,
        "residual": residual,
        "coefficient_map_shape": list(coefficient_map.shape),
        "coefficient_map_rank": rank,
        "augmented_ranks": augmented_ranks,
        "free_parameter_counts": free_parameters,
        "equation_key_count": len(ordered_keys),
    }


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    data = operator_data()
    value = data["value"]
    pbw = value["pbw"]["H0"]
    gauge = value["K"]
    action_bach = endpoint_operator()["action_bach"]

    # Reconcile the authoritative factorized Hom adjoint with the independently
    # action-derived base endpoint.  The historical correction used a
    # post-normal-order adjoint and is intentionally not reused.
    base_correction = _table_add(
        _table_scale(action_bach, sp.Integer(-2)),
        _table_scale(data["schur"].base, sp.Integer(-1)),
    )
    old_base = {(): value["middle"]["endpoint_correction"]}
    base_endpoint = _table_add(data["schur"].base, base_correction)
    base_action_defect = _table_add(
        base_endpoint, _table_scale(action_bach, sp.Integer(2))
    )
    endpoint0 = jet_add(
        data["schur"],
        parallel_zero_variation(base_correction, "Q-factorized-base"),
        name="factorized-endpoint-before-Qdot",
    )
    gauge_operator = pbw.compose(endpoint0, gauge, "factorized-endpoint-K")
    if gauge_operator.base:
        raise AssertionError("factorized base endpoint lost the action gauge identity")

    solved = _solve_correction(gauge_operator.delta(()), pbw, gauge)
    correction = solved["correction"]
    endpoint_variation = _table_add(data["schur"].delta(()), correction)
    action_bach_target = _table_scale(endpoint_variation, -sp.Rational(1, 2))

    pairing = data["endpoint_pairing"]
    inverse = pairing.inv()
    correction_sharp = {
        word: (inverse * matrix.T * pairing).applyfunc(sp.expand)
        for word, matrix in correction.items()
    }
    cyclic_defect = _difference(correction_sharp, correction)
    if cyclic_defect:
        raise AssertionError("unique factorized endpoint correction is not cyclic")
    if any(word for word in correction):
        raise AssertionError("unique factorized endpoint correction ceased to be algebraic")

    old_point = _deserialize_table(
        json.loads(OLD_SOLVE.read_text())["exact_data"]["unique_first_order_correction"]
    )
    return {
        "base_reconciliation": {
            "formula": "Q_factorized,0=-2 B_action-Schur_factorized,0",
            "correction": _table(base_correction),
            "historical_Q_base_defect": _table(_difference(base_correction, old_base)),
            "endpoint_plus_2_B_action_defect": _table(base_action_defect),
            "historical_post_normal_order_Q_authoritative": False,
        },
        "complete_first_order_solve": {
            "ansatz": "Qdot=Qdot_0+sum_a Qdot_a nabla_a",
            "total_unknowns": 405,
            "coefficient_map_shape": solved["coefficient_map_shape"],
            "coefficient_map_rank": solved["coefficient_map_rank"],
            "augmented_ranks": solved["augmented_ranks"],
            "free_parameter_counts": solved["free_parameter_counts"],
            "equation_key_count": solved["equation_key_count"],
            "unique_correction": _table(correction),
            "corrected_gauge_residual": _table(solved["residual"]),
            "historical_point_correction_defect": _table(_difference(correction, old_point)),
        },
        "factorized_endpoint_target": {
            "formula": "Bdot_parent_target=-(1/2)(Schurdot_factorized+Qdot_factorized)",
            "compressed_parent_endpoint_variation": _table(endpoint_variation),
            "action_bach_variation_target": _table(action_bach_target),
            "normalization_audit": "the parent endpoint is -2 times the action-normalized Bach Hessian; the two tables are serialized separately",
            "Qdot_is_order_zero": True,
            "Qdot_fibre_adjoint_defect": _table(cyclic_defect),
            "endpoint_factorized_cyclic": True,
            "endpoint_gauge_closed": True,
        },
        "disposition": {
            "unique_factorized_endpoint_completion": True,
            "action_base_reconciled": True,
            "action_third_variation_independently_derived": False,
            "rank_310_first_variation_SDR": False,
            "transverse_causal_transfer": False,
        },
    }


def build() -> dict[str, Any]:
    refs = {}
    for key, path, expected in (
        ("factorized_Hom_schur", SCHUR_CERT, "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1"),
        ("upper_relative_saddle", UPPER_CERT, "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1"),
        ("superseded_point_solve", OLD_SOLVE, "NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise AssertionError(f"dependency drifted: {key}")
        refs[key] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": expected,
            "sha256": _sha(path),
        }
    data = exact_data()
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, SCHUR_PRODUCER, UPPER_PRODUCER)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-factorized-endpoint-completion-v1",
        "schema_version": "1.1.0",
        "result_id": "NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1",
        "result_state": "UNIQUE_CYCLIC_FACTORIZED_ENDPOINT_AND_SCALED_ACTION_TARGET_EXACT_ACTION_COMPARISON_OPEN",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "exact_data": data,
        "exact_checks": {
            "base_action_endpoint_exact": data["base_reconciliation"]["endpoint_plus_2_B_action_defect"]["nonzero_coefficients"] == 0,
            "complete_ansatz_full_rank": data["complete_first_order_solve"]["coefficient_map_rank"] == 45,
            "all_rows_unique": data["complete_first_order_solve"]["free_parameter_counts"] == [0] * 9,
            "gauge_residual_zero": data["complete_first_order_solve"]["corrected_gauge_residual"]["nonzero_coefficients"] == 0,
            "correction_is_algebraic": data["factorized_endpoint_target"]["Qdot_is_order_zero"],
            "correction_is_cyclic": data["factorized_endpoint_target"]["Qdot_fibre_adjoint_defect"]["nonzero_coefficients"] == 0,
            "parent_and_action_targets_serialized_separately": data["factorized_endpoint_target"]["compressed_parent_endpoint_variation"]["sha256"] != data["factorized_endpoint_target"]["action_bach_variation_target"]["sha256"],
            "action_third_variation_not_overclaimed": not data["disposition"]["action_third_variation_independently_derived"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_first_variation_SDR"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION": True,
            "TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_INDEPENDENT_ACTION_THIRD_VARIATION_COMPARISON",
        "claim_boundary": "This exact complete first-order solve reconciles the authoritative factorized Hom-adjoint Schur operator with the action-derived base Bach endpoint and derives the unique cyclic transverse lower-order completion. The solution has fifteen algebraic coefficients and zero gauge/cyclic defects. The certificate now distinguishes the compressed parent endpoint variation from the action-normalized Bach target by the required factor -1/2. It is the exact target for, not a substitute for, an independent action-leading comparison. The action comparison, all-row rank-310 SDR and transverse causal transfer remain false.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in sources},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_factorized_endpoint_completion --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_factorized_endpoint_completion.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_factorized_endpoint_completion",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-factorized-endpoint-completion-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    solve = data["complete_first_order_solve"]
    return rf"""# Transverse factorized endpoint completion

The authoritative factorized Hom adjoint changes the fifteen-term base
endpoint completion.  Reconciliation with the independently action-derived
Nariai endpoint gives

\[
Q_{{\mathrm{{fact}},0}}=-2B_{{\mathrm{{action}}}}-
L_1^\sharp M_{{\rm parent}}L_1.
\]

The complete order-at-most-one transverse ansatz has
`{solve['total_unknowns']}` unknowns.  Its common coefficient map has shape
`{solve['coefficient_map_shape']}`, rank `{solve['coefficient_map_rank']}`,
and every augmented row has the same rank with no free parameter.  The unique
solution collapses to
`{solve['unique_correction']['nonzero_coefficients']}` algebraic coefficients,
has zero gauge residual, and is fibre-self-adjoint.

The serialized parent endpoint and action-normalized Bach target are now
distinct fields:

\[
\dot B_{{\rm target}}=-\frac12
  (\dot{{\rm Schur}}+\dot Q_{{\rm fact}}).
\]

This repairs the previous ambiguous `endpoint_variation` field, which stored
the unscaled parent endpoint despite displaying the scaled formula.

This supplies the exact parent-forced target for the action calculation.  It
does not replace the independent third variation of the Weyl-squared action,
and therefore does not yet promote the transverse rank-310 SDR or causal
transfer.
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
        raise AssertionError("factorized endpoint artifact is stale")
    print("NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1: PASS")


if __name__ == "__main__":
    main()
