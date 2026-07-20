#!/usr/bin/env python3
"""Test whether invariant order-two symbols can hit the order-one obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.product_taylor_engine import BASE_POINT, COORDINATES
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    stabilizer_vectors,
)
from d_quotient_classical.relative.einstein_weyl_relative_order_one_chain_obstruction import (
    _source_action,
    _target_equation_action,
    _target_q1,
    _vector_derivative,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-two-obstruction-sensitivity.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-obstruction-sensitivity-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_two_obstruction_sensitivity.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_two_obstruction_sensitivity.py"
DEPENDENCIES = {
    "order_one_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json",
    "invariant_ansatz": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
}

WORDS2 = list(combinations_with_replacement(range(4), 2))
WORD_INDEX = {word: index for index, word in enumerate(WORDS2)}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _fraction(value: sp.Expr) -> str:
    rational = sp.Rational(value)
    return str(int(rational.p)) if rational.q == 1 else f"{int(rational.p)}/{int(rational.q)}"


def _base(expression: sp.Expr) -> sp.Rational:
    return sp.Rational(sp.simplify(expression.subs(BASE_POINT)))


def _sym2_action() -> sp.Matrix:
    """Action of J_3 on canonical symmetric second derivative words."""

    vector_derivative = _vector_derivative("J_3")
    result = sp.zeros(len(WORDS2))
    for incoming, (left, right) in enumerate(WORDS2):
        for replacement in range(4):
            result[WORD_INDEX[tuple(sorted((replacement, right)))], incoming] += (
                vector_derivative[replacement, left]
            )
            result[WORD_INDEX[tuple(sorted((left, replacement)))], incoming] += (
                vector_derivative[replacement, right]
            )
    return result


def _empty_symbol() -> list[sp.Matrix]:
    return [sp.zeros(14, 20) for _ in WORDS2]


def _candidate(records: list[tuple[tuple[int, int], int, int, int]]) -> list[sp.Matrix]:
    symbol = _empty_symbol()
    for word, output, incoming, coefficient in records:
        symbol[WORD_INDEX[word]][output, incoming] += coefficient
    return symbol


def _isotropy_residual(symbol: list[sp.Matrix]) -> list[sp.Matrix]:
    target = _target_equation_action("J_3")
    source = _source_action("J_3")
    derivative = _sym2_action()
    return [
        target * symbol[word]
        - symbol[word] * source
        - sum(
            (
                derivative[word, incoming] * symbol[incoming]
                for incoming in range(len(WORDS2))
            ),
            sp.zeros(14, 20),
        )
        for word in range(len(WORDS2))
    ]


def _second_vector_derivative(
    generator: str, output: int, left: int, right: int
) -> sp.Rational:
    vector = stabilizer_vectors()[generator]
    return _base(
        sp.diff(
            vector[output],
            COORDINATES[left],
            COORDINATES[right],
        )
    )


@lru_cache(maxsize=None)
def _cached_source_action(generator: str, derivative_axis: int) -> sp.Matrix:
    return _source_action(generator, derivative_axis)


@lru_cache(maxsize=1)
def _cached_target_symbols() -> tuple[sp.Matrix, ...]:
    return tuple(_target_q1()[1])


def _first_symbol_jet_from_order_two(
    symbol: list[sp.Matrix], *, generator: str, derivative_index: int
) -> sp.Matrix:
    """Order-two contribution to X(a^derivative_index) in [L_X,A]=0."""

    result = sp.zeros(14, 20)
    for word_index, (left, right) in enumerate(WORDS2):
        coefficient = symbol[word_index]
        second_vector = _second_vector_derivative(
            generator, derivative_index, left, right
        )
        if second_vector:
            result += second_vector * coefficient
        if right == derivative_index:
            result += coefficient * _cached_source_action(generator, left)
        if left == derivative_index:
            result += coefficient * _cached_source_action(generator, right)
    return result


def _sensitivity(symbol: list[sp.Matrix]) -> sp.Rational:
    """Evaluate the normalized two-row left-null obstruction on an order-two symbol."""

    target_symbol = _cached_target_symbols()
    first_t = _first_symbol_jet_from_order_two(
        symbol, generator="J_2", derivative_index=0
    )
    first_x = _first_symbol_jet_from_order_two(
        symbol, generator="J_2", derivative_index=1
    )
    # The normalized witness is -row(c_1^*, d_t) - row(c_0^*, d_x).
    return sp.Rational(
        -(target_symbol[2] * first_t)[1, 2]
        - (target_symbol[2] * first_x)[0, 2]
    )


def _coordinate_sensitivity(
    word: tuple[int, int], output: int, incoming: int
) -> sp.Rational:
    """Evaluate one raw order-two coefficient without materializing a symbol."""

    left, right = word
    target_theta = _cached_target_symbols()[2]

    def component(derivative_index: int, target_output: int) -> sp.Rational:
        value = sp.S.Zero
        second_vector = _second_vector_derivative(
            "J_2", derivative_index, left, right
        )
        if incoming == 2:
            value += target_theta[target_output, output] * second_vector
        if right == derivative_index:
            value += (
                target_theta[target_output, output]
                * _cached_source_action("J_2", left)[incoming, 2]
            )
        if left == derivative_index:
            value += (
                target_theta[target_output, output]
                * _cached_source_action("J_2", right)[incoming, 2]
            )
        return sp.Rational(value)

    return sp.Rational(-component(0, 1) - component(1, 0))


def _raw_functional() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for word in WORDS2:
        for output in range(14):
            for incoming in range(20):
                value = _coordinate_sensitivity(word, output, incoming)
                if value:
                    records.append(
                        {
                            "word": list(word),
                            "A1_output_local": output,
                            "P3_input_local": incoming,
                            "coefficient": _fraction(value),
                        }
                    )
    if records != [
        {
            "word": [0, 2],
            "A1_output_local": 5,
            "P3_input_local": 2,
            "coefficient": "-1",
        },
        {
            "word": [1, 2],
            "A1_output_local": 2,
            "P3_input_local": 2,
            "coefficient": "1",
        },
    ]:
        raise AssertionError(f"order-two sensitivity functional drifted: {records}")
    return records


def _candidate_records() -> list[dict[str, Any]]:
    definitions = [
        (
            "time_plane_scalar",
            [
                ((0, 2), 5, 2, 1),
                ((0, 3), 6, 2, 1),
            ],
        ),
        (
            "space_plane_scalar",
            [
                ((1, 2), 2, 2, 1),
                ((1, 3), 3, 2, 1),
            ],
        ),
    ]
    output = []
    for identifier, records in definitions:
        symbol = _candidate(records)
        residual = _isotropy_residual(symbol)
        residual_entries = sum(len(matrix.todok()) for matrix in residual)
        value = _sensitivity(symbol)
        if residual_entries or not value:
            raise AssertionError(f"invalid sensitivity candidate {identifier}")
        output.append(
            {
                "id": identifier,
                "records": [
                    {
                        "word": list(word),
                        "A1_output_local": target,
                        "P3_input_local": source,
                        "coefficient": str(coefficient),
                    }
                    for word, target, source, coefficient in records
                ],
                "isotropy_residual_nonzero_entries": residual_entries,
                "normalized_obstruction_sensitivity": _fraction(value),
            }
        )
    if [item["normalized_obstruction_sensitivity"] for item in output] != ["-1", "1"]:
        raise AssertionError("normalized candidate sensitivities drifted")
    return output


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    obstruction = dependencies["order_one_obstruction"]["exact_linear_system"]
    if obstruction["augmented_rank_over_Q"] - obstruction["rank_over_Q"] != 1:
        raise AssertionError("order-one obstruction quotient is not one-dimensional")
    order_two_dimension = dependencies["invariant_ansatz"][
        "homogeneous_symbol_dimensions"
    ]["A1_exact_order_0_1_2"][2]
    if order_two_dimension != 626:
        raise AssertionError("A1 order-two invariant dimension drifted")
    raw = _raw_functional()
    candidates = _candidate_records()
    value = {
        "schema": "pure-weyl-relative-order-two-obstruction-sensitivity-v1",
        "result_id": RESULT_ID,
        "result_state": "ORDER_TWO_SYMBOLS_ACT_NONTRIVIALLY_ON_ORDER_ONE_OBSTRUCTION",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": dependencies["order_one_obstruction"]["scope"],
        "dependencies": {
            name: _artifact(path, dependencies[name])
            for name, path in DEPENDENCIES.items()
        },
        "obstruction_quotient": {
            "dimension": 1,
            "source_certificate_rank": obstruction["rank_over_Q"],
            "source_certificate_augmented_rank": obstruction["augmented_rank_over_Q"],
            "normalized_left_null_evaluation": obstruction["left_null_witness"][
                "evaluation"
            ],
            "witness_rows": obstruction["left_null_witness"]["rows"],
        },
        "order_two_symbol_space": {
            "bundle_map": "A1:P3(20)->W1(14)",
            "isotropy": "SO(2)",
            "homogeneous_invariant_dimension": order_two_dimension,
            "canonical_derivative_words": [list(word) for word in WORDS2],
        },
        "induced_sensitivity": {
            "derivation": "second jets of the transitive stabilizer J_2 feed the first coefficient jet of A1; q1_W then reaches the normalized two-row obstruction",
            "raw_nonzero_coordinates": raw,
            "explicit_invariant_candidates": candidates,
            "rank_to_obstruction_quotient": 1,
            "surjective": True,
        },
        "classification": {
            "order_two_symbol_can_change_order_one_obstruction": True,
            "full_order_two_solve_authorized": True,
            "order_two_chain_map_exists": False,
            "order_two_chain_map_obstructed": False,
            "all_finite_orders_obstructed": False,
            "current_improvement_obstructed": False,
            "carrier_enlargement_required": False,
            "f2_incidence_activated": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "SOLVE_THE_COMPLETE_ENDPOINT_NORMALIZED_INVARIANT_ORDER_TWO_CHAIN_SYSTEM_BEFORE_ACTIVATING_F2",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_two_obstruction_sensitivity --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_two_obstruction_sensitivity",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_two_obstruction_sensitivity",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC sensitivity theorem proves that the complete 626-dimensional invariant A1 order-two symbol space is not annihilated by the one-dimensional order-one obstruction quotient: two explicit isotropy-invariant symbols evaluate to -1 and +1. It authorizes, but does not solve, the full order-two chain system. It does not establish an order-two chain map, activate f2, require a carrier enlargement, decide current improvements, or imply any causal, observable, particle or quantum claim.",
    }
    return value


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    return """# Order-two sensitivity of the relative chain obstruction

The complete endpoint-normalized order-one system has a one-dimensional
obstruction quotient.  The order-two `A1:P3->W1` invariant symbol space has
dimension 626.  Second jets of the transitive stabilizer `J_2` feed these
symbols into the first coefficient jet that appears in the two-row witness.

The induced functional has only two raw nonzero coordinates.  Two explicit
`SO(2)`-invariant symbols evaluate to `-1` and `+1`, respectively.  Therefore
the order-two sensitivity map onto the obstruction quotient has rank one:
the previous obstruction is not rigid under the next differential order.

This is a screening theorem, not an existence theorem.  The complete
order-two chain system must now be solved before the fifteen-row `f2`
incidence is activated.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "order_two_chain_map_exists",
        "order_two_chain_map_obstructed",
        "all_finite_orders_obstructed",
        "current_improvement_obstructed",
        "carrier_enlargement_required",
        "f2_incidence_activated",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check and (
        OUTPUT.read_text() != _render(value)
        or REPORT.read_text() != _report(value)
    ):
        raise AssertionError("order-two sensitivity outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
