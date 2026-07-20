#!/usr/bin/env python3
"""Prove that cubic coefficient descent cannot remove the order-two obstruction."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
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
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-three-descent-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-three-descent-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_three_descent_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_three_descent_obstruction.py"
DEPENDENCIES = {
    "order_two_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
}
TRANSITIVE = ["H", "P_x", "J_2", "J_1"]
FORMS3 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
WORDS3 = list(combinations_with_replacement(range(4), 3))
TOP_ROWS = [
    ((0, 2, 2), 1, 2, sp.Rational(-1)),
    ((1, 2, 2), 0, 2, sp.Rational(-1)),
    ((2, 2, 2), 0, 1, sp.Rational(-1, 2)),
    ((2, 2, 3), 0, 0, sp.Rational(1, 2)),
]


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


def _base(expression: sp.Expr) -> sp.Rational:
    return sp.Rational(sp.simplify(expression.subs(BASE_POINT)))


def _fraction(value: sp.Expr) -> str:
    rational = sp.Rational(value)
    return str(int(rational.p)) if rational.q == 1 else f"{int(rational.p)}/{int(rational.q)}"


def _third_vector_jets() -> list[dict[str, Any]]:
    records = []
    vectors = stabilizer_vectors()
    for generator in TRANSITIVE:
        for output in range(4):
            for word in WORDS3:
                expression = vectors[generator][output]
                for axis in word:
                    expression = sp.diff(expression, COORDINATES[axis])
                value = _base(expression)
                if value:
                    records.append(
                        {
                            "generator": generator,
                            "output": output,
                            "word": list(word),
                            "coefficient": _fraction(value),
                        }
                    )
    return records


def _form_action_second(
    generator: str, left_derivative: int, right_derivative: int
) -> sp.Matrix:
    vector = stabilizer_vectors()[generator]
    result = sp.zeros(4)
    for incoming, indices in enumerate(FORMS3):
        for position, index in enumerate(indices):
            for replacement in range(4):
                coefficient = sp.diff(
                    vector[replacement],
                    COORDINATES[index],
                    COORDINATES[left_derivative],
                    COORDINATES[right_derivative],
                )
                coefficient = _base(coefficient)
                if not coefficient:
                    continue
                replaced = list(indices)
                replaced[position] = replacement
                if len(set(replaced)) != 3:
                    continue
                inversions = sum(
                    replaced[a] > replaced[b]
                    for a in range(3)
                    for b in range(a + 1, 3)
                )
                output = FORMS3.index(tuple(sorted(replaced)))
                result[output, incoming] += (-1) ** inversions * coefficient
    return result


def _source_second_jets() -> list[dict[str, Any]]:
    records = []
    for generator in TRANSITIVE:
        for left in range(4):
            for right in range(left, 4):
                matrix = sp.kronecker_product(
                    sp.eye(5), _form_action_second(generator, left, right)
                )
                for (output, incoming), value in matrix.todok().items():
                    if value:
                        records.append(
                            {
                                "generator": generator,
                                "word": [left, right],
                                "output": output,
                                "input": incoming,
                                "coefficient": _fraction(value),
                            }
                        )
    return records


def _cubic_direct_sensitivity_nonzero_entries() -> int:
    """Direct cubic-to-first-coefficient descent uses only the two jet families above."""

    if _third_vector_jets() or _source_second_jets():
        raise AssertionError("direct cubic descent no longer vanishes")
    return 0


def _matrix_records(matrix: sp.Matrix) -> list[list[Any]]:
    return [
        [row, column, _fraction(value)]
        for (row, column), value in sorted(matrix.todok().items())
        if value
    ]


def _effective_indirect_descent() -> dict[str, Any]:
    """Compute -y_2 D_3 on arbitrary raw cubic A1 coefficients."""

    target_zero, target_symbol = _target_q1()
    target_actions = {
        generator: _target_equation_action(generator) for generator in TRANSITIVE
    }
    source_actions = {
        generator: _source_action(generator) for generator in TRANSITIVE
    }
    vector_derivatives = {
        generator: _vector_derivative(generator) for generator in TRANSITIVE
    }
    if any(matrix.todok() for matrix in vector_derivatives.values()):
        raise AssertionError("transitive first stabilizer jets no longer vanish")

    word_functionals: dict[tuple[int, int, int], sp.Matrix] = {
        word: sp.zeros(14, 20) for word in WORDS3
    }
    for word, target_output, source_input, witness_coefficient in TOP_ROWS:
        for output in range(14):
            for incoming in range(20):
                value = target_zero[target_output, output] * (
                    1 if incoming == source_input else 0
                )
                for axis, generator in enumerate(TRANSITIVE):
                    left = -target_actions[generator]
                    value += (
                        (target_symbol[axis] * left)[target_output, output]
                        * (1 if incoming == source_input else 0)
                    )
                    value += (
                        target_symbol[axis][target_output, output]
                        * source_actions[generator][incoming, source_input]
                    )
                word_functionals[word][output, incoming] -= (
                    witness_coefficient * value
                )
    records = {
        ",".join(str(axis) for axis in word): _matrix_records(matrix)
        for word, matrix in word_functionals.items()
        if matrix.todok()
    }
    if records:
        raise AssertionError(f"effective cubic descent no longer vanishes: {records}")
    matrix_digest = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "raw_cubic_coefficient_count": len(WORDS3) * 14 * 20,
        "nonzero_entries": 0,
        "zero_matrix_records_sha256": matrix_digest,
    }


def _sym_weights(order: int) -> Counter[int]:
    weights = [0, 0, 1, -1]
    return Counter(
        sum(weights[index] for index in word)
        for word in combinations_with_replacement(range(4), order)
    )


def _hom_dimension(
    source: dict[int, int], target: dict[int, int], order: int
) -> int:
    derivative = _sym_weights(order)
    return sum(
        source_multiplicity
        * derivative_multiplicity
        * target.get(source_weight + derivative_weight, 0)
        for source_weight, source_multiplicity in source.items()
        for derivative_weight, derivative_multiplicity in derivative.items()
    )


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    old = dependencies["order_two_obstruction"]
    witness_rows = old["top_descent_system"]["rowspace_witness_rows"]
    serialized = [
        (tuple(record["word"]), record["output_local"], record["input_local"], sp.Rational(record["coefficient"]))
        for record in witness_rows
    ]
    if serialized != TOP_ROWS:
        raise AssertionError("order-two rowspace witness drifted")
    p3 = {0: 8, 1: 5, -1: 5, 2: 1, -2: 1}
    p4 = {0: 3, 1: 1, -1: 1}
    w1 = {0: 6, 1: 3, -1: 3, 2: 1, -2: 1}
    w2 = {0: 4, 1: 1, -1: 1}
    dimensions = [_hom_dimension(p3, w1, 3), _hom_dimension(p4, w2, 3)]
    if dimensions != [1108, 144]:
        raise AssertionError("cubic invariant census drifted")
    direct = _cubic_direct_sensitivity_nonzero_entries()
    indirect = _effective_indirect_descent()
    return {
        "schema": "pure-weyl-relative-order-three-descent-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "CUBIC_PROLONGATION_CANNOT_REMOVE_ORDER_TWO_OBSTRUCTION",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": old["scope"],
        "dependencies": {
            name: _artifact(path, dependencies[name])
            for name, path in DEPENDENCIES.items()
        },
        "cubic_symbol_space": {
            "A1_order_three_invariant_dimension": dimensions[0],
            "A2_order_three_invariant_dimension": dimensions[1],
            "raw_A1_coefficient_count": len(WORDS3) * 14 * 20,
            "canonical_derivative_words": len(WORDS3),
        },
        "direct_descent": {
            "third_stabilizer_vector_jets_nonzero": len(_third_vector_jets()),
            "second_source_action_jets_nonzero": len(_source_second_jets()),
            "direct_obstruction_sensitivity_nonzero_entries": direct,
        },
        "indirect_descent": {
            "identity": "L2=y2*M2 and M2*x2+D3*x3=0 imply L2*x2=-y2*D3*x3",
            "order_two_rowspace_witness": [
                {
                    "word": list(word),
                    "output_local": output,
                    "input_local": incoming,
                    "coefficient": _fraction(coefficient),
                }
                for word, output, incoming, coefficient in TOP_ROWS
            ],
            "effective_cubic_functional": indirect,
        },
        "combined_obstruction": {
            "direct_L3": "0",
            "indirect_minus_y2_D3": "0",
            "surviving_order_one_left_null_evaluation": old[
                "combined_obstruction"
            ]["order_one_left_null_evaluation"],
            "complete_order_three_chain_map_exists": False,
        },
        "classification": {
            "complete_endpoint_normalized_order_three_chain_map_obstructed": True,
            "all_finite_orders_obstructed": False,
            "order_four_chain_map_obstructed": False,
            "current_improvement_obstructed": False,
            "larger_carrier_obstructed": False,
            "f2_incidence_activated": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "PROVE_A_GENERAL_SPENCER_PROLONGATION_OBSTRUCTION_OR_CHANGE_THE_ENDPOINT_CURRENT_INCIDENCE_OR_RELATIVE_CARRIER",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_three_descent_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_three_descent_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_three_descent_obstruction",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem propagates the four-row order-two obstruction identity through one further differential order. All third stabilizer-vector jets and second source-action jets vanish at the base point, so direct cubic sensitivity is zero. More strongly, the effective indirect functional -y2 D3 vanishes coefficientwise on all 5,600 raw cubic A1 coefficients, before imposing isotropy or the cubic top equation. Hence no endpoint-normalized invariant chain map exists through differential order three. This does not prove an all-order obstruction, obstruct order four, decide another endpoint/current incidence or larger carrier, activate f2, or imply causal, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    return """# Order-three relative descent obstruction

The order-two defect is represented by a four-row top-symbol functional
`y2`.  At cubic order, both possible corrections vanish:

* all third jets of the transitive stabilizer vector fields and all second
  jets of their source-fibre actions vanish at the product base point, so
  direct cubic-to-first-jet sensitivity is zero;
* the effective indirect functional `-y2 D3` is the zero functional on all
  5,600 raw cubic `A1` coefficients, before isotropy or top descent.

Thus allowing cubic symbols cannot relax the quadratic top equation in a way
that changes the surviving normalized defect.  No endpoint-normalized
invariant chain map exists through differential order three.

The result is not an all-order no-go.  Order four, a different endpoint or
current incidence, and larger carriers remain open.

CLOSE-OUT: OBSTRUCTED — the exact cubic prolongation cannot remove the fixed endpoint-normalized defect
EVIDENCE: EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "all_finite_orders_obstructed",
        "order_four_chain_map_obstructed",
        "current_improvement_obstructed",
        "larger_carrier_obstructed",
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
        raise AssertionError("order-three descent outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
