#!/usr/bin/env python3
"""Separate formal K sensitivity from action-derived transverse admissibility."""

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
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import _pbw_layers


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JET_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
L0_INPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-k-sensitivity-admissibility.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-k-sensitivity-admissibility-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_k_sensitivity_admissibility.py"
TESTS = HERE / "tests/test_nariai_transverse_k_sensitivity_admissibility.py"
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


def _rigid_inverse(pbw, l0, first_bgg):
    responses = []
    for column in range(15):
        correction = {(): sp.zeros(1, 15)}
        correction[()][0, column] = 1
        responses.append(pbw.compose(correction, l0))
    for word in WORDS:
        for column in range(9):
            correction = {word: sp.zeros(1, 9)}
            correction[word][0, column] = 1
            responses.append(_scale(pbw.compose(correction, first_bgg), -1))
    keys = sorted(
        {(word, column) for response in responses for word, matrix in response.items() for column in range(matrix.cols)},
        key=lambda item: (len(item[0]), item[0], item[1]),
    )
    matrix = sp.Matrix([[response.get(word, sp.zeros(1, 4))[0, column] for response in responses] for word, column in keys])
    return matrix.inv(), keys


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    jet = json.loads(JET_INPUT.read_text())
    obstruction = json.loads(L0_INPUT.read_text())
    first_bgg_variation = jet["exact_data"]["operator_variations"]["first_BGG"]
    if first_bgg_variation["nonzero_coefficients"] != 0:
        raise AssertionError("authoritative transverse first-BGG variation ceased to vanish")

    base = fixture()
    layers = _pbw_layers()
    h0, h1, c0 = layers["H0"].base, layers["H1"].base, layers["C0"].base
    l0, l1 = base["corrected_l0"], base["corrected_l1"]
    first_bgg = h0.compose(base["k_p0"], l0)
    inverse, constraint_keys = _rigid_inverse(h0, l0, first_bgg)
    witness_terms = obstruction["exact_data"]["normalized_left_null_witness"]["terms"]

    def witness(operator):
        return sp.expand(sum(
            sp.sympify(term["coefficient"])
            * operator.get(tuple(term["word"]), sp.zeros(60, 15))[term["output_row"], term["input_column"]]
            for term in witness_terms
        ))

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
                    target = sp.Matrix([
                        source.get(key_word, sp.zeros(60, 4))[row, column]
                        for key_word, column in constraint_keys
                    ])
                    solution = inverse * target
                    delta_d[row, :] = solution[:15, :].T
                    for word_index, basis_word in enumerate(WORDS):
                        delta_l1[basis_word][row, :] = solution[
                            15 + 9 * word_index : 15 + 9 * (word_index + 1), :
                        ].T
                delta_l1 = _clean(delta_l1)
                delta_k_p0 = h0.compose(delta_k, {(): base["projection0"]})
                response = _add(
                    c0.compose(base["middle"]["yang_mills_middle"], {(): delta_d}),
                    _scale(c0.compose(h1.compose(base["middle"]["yang_mills_middle"], delta_l1), base["k_p0"]), -1),
                    _scale(c0.compose(base["phi"], delta_k_p0), -1),
                )
                sensitivities.append(witness(response))
                basis.append({"word": list(word), "output_row": output_row, "input_column": input_column})
    sensitivity_map = sp.Matrix([sensitivities])
    nonzero = [
        {**basis[index], "value": str(value)}
        for index, value in enumerate(sensitivities) if value != 0
    ]
    if sensitivity_map.rank() != 1 or len(nonzero) != 23:
        raise AssertionError("formal K-sensitivity count drifted")
    if any(item["word"] == [] for item in nonzero):
        raise AssertionError("zeroth-order K sensitivity unexpectedly appeared")

    return {
        "formal_screen": {
            "ansatz": "arbitrary local delta_K of differential order at most one, with uniquely induced delta_d_aut and delta_L1 preserving the first square",
            "basis": basis,
            "basis_dimension": len(basis),
            "sensitivity_map": _sparse(sensitivity_map),
            "nonzero_directions": nonzero,
            "nonzero_direction_count": len(nonzero),
            "all_nonzero_directions_first_order": all(item["word"] != [] for item in nonzero),
        },
        "action_derived_admissibility": {
            "source_path": "exact_data.operator_variations.first_BGG",
            "authoritative_delta_K_nonzero_coefficients": first_bgg_variation["nonzero_coefficients"],
            "authoritative_delta_K_orders": first_bgg_variation["orders"],
            "formal_sensitive_direction_admissible": False,
        },
        "interpretation": {
            "obstruction_formally_K_sensitive": True,
            "repair_within_action_derived_target_complex": False,
            "complete_coupled_SDR_obstructed": False,
            "required_next_ansatz": "neighbouring equation/constraint/cotangent rows or a homotopy-coherent equation cone, without changing the action-derived metric gauge generator",
        },
    }


def build() -> dict[str, Any]:
    exact = exact_data()
    return {
        "schema": "nariai-transverse-k-sensitivity-admissibility-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1",
        "result_state": "FORMAL_K_DIRECTIONS_HIT_OBSTRUCTION_BUT_ACTION_DERIVED_DELTA_K_IS_ZERO",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_first_BGG": {"path": str(JET_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", "sha256": _sha(JET_INPUT)},
            "normalized_L0_obstruction": {"path": str(L0_INPUT.relative_to(ROOT)), "result_id": "NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1", "sha256": _sha(L0_INPUT)},
        },
        "exact_data": exact,
        "exact_checks": {
            "formal_basis_complete": exact["formal_screen"]["basis_dimension"] == 180,
            "twenty_three_sensitive_directions": exact["formal_screen"]["nonzero_direction_count"] == 23,
            "sensitive_directions_first_order": exact["formal_screen"]["all_nonzero_directions_first_order"] is True,
            "action_derived_delta_K_zero": exact["action_derived_admissibility"]["authoritative_delta_K_nonzero_coefficients"] == 0,
            "formal_repair_rejected": exact["action_derived_admissibility"]["formal_sensitive_direction_admissible"] is False,
            "complete_SDR_not_overclaimed": exact["interpretation"]["complete_coupled_SDR_obstructed"] is False,
        },
        "flags": {
            "TRANSVERSE_FORMAL_K_SENSITIVITY_NONZERO": True,
            "TRANSVERSE_ACTION_DERIVED_K_CORRECTION_AVAILABLE": False,
            "TRANSVERSE_SHIFTED_CHAIN_REPAIRED": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_EQUATION_CONSTRAINT_COTANGENT_COUPLED_VARIATION",
        "claim_boundary": "The complete local order-at-most-one formal delta_K family has 180 basis directions. After uniquely preserving the first BGG square and including the induced delta(Kp0) term, exactly 23 first-order directions act nontrivially on the normalized five-term obstruction quotient. However, the authoritative action-derived transverse first-BGG variation is identically zero, so none of those formal directions is an admissible repair of the existing metric BV complex. This does not obstruct equation/constraint/cotangent or homotopy-coherent equation-cone corrections, the complete SDR, or causal transfer.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_k_sensitivity_admissibility --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_k_sensitivity_admissibility.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_k_sensitivity_admissibility",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-k-sensitivity-admissibility-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return f"""# Transverse Nariai K-sensitivity admissibility

The complete formal order-at-most-one `delta_K` screen has
`{data['formal_screen']['basis_dimension']}` directions.  Exactly
`{data['formal_screen']['nonzero_direction_count']}` first-order directions
act nontrivially on the normalized five-term obstruction quotient.

The authoritative action-derived transverse `first_BGG` variation nevertheless
has zero coefficients.  The sensitive directions therefore change the metric
gauge generator and are not admissible repairs of the existing BV complex.
Equation/constraint/cotangent and homotopy-coherent equation-cone corrections
remain open.
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
        raise AssertionError("K-sensitivity admissibility artifact is stale")
    print("NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1: PASS")


if __name__ == "__main__":
    main()
