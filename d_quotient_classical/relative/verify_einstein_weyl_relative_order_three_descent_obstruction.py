#!/usr/bin/env python3
"""Independent geometric replay of the cubic relative descent obstruction."""

from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.product_taylor_engine import BASE_POINT, COORDINATES
from d_quotient_classical.relative.einstein_weyl_relative_five_current_de_rham_q2 import (
    density_dual_action,
)
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    stabilizer_action,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-three-descent-obstruction-v1.schema.json"
Q1 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json"
TRANSITIVE = ["H", "P_x", "J_2", "J_1"]
GENERATORS = ["H", "P_x", "J_1", "J_2", "J_3"]
FORMS3 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def _load(path: Path):
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _base(expression: sp.Expr) -> sp.Rational:
    return sp.Rational(sp.simplify(expression.subs(BASE_POINT)))


def _adjoint(generator: str) -> sp.Matrix:
    result = sp.zeros(5)
    index = {name: position for position, name in enumerate(GENERATORS)}
    brackets = {
        ("J_1", "J_2"): ("J_3", -1),
        ("J_2", "J_1"): ("J_3", 1),
        ("J_2", "J_3"): ("J_1", -1),
        ("J_3", "J_2"): ("J_1", 1),
        ("J_3", "J_1"): ("J_2", -1),
        ("J_1", "J_3"): ("J_2", 1),
    }
    for incoming in GENERATORS:
        if (generator, incoming) in brackets:
            output, coefficient = brackets[(generator, incoming)]
            result[index[output], index[incoming]] = coefficient
    return result


def _form_action(generator: str, derivatives: tuple[int, ...] = ()) -> sp.Matrix:
    vector = stabilizer_vectors()[generator]
    result = sp.zeros(4)
    for incoming, indices in enumerate(FORMS3):
        for position, index in enumerate(indices):
            for replacement in range(4):
                coefficient = sp.diff(vector[replacement], COORDINATES[index])
                for derivative in derivatives:
                    coefficient = sp.diff(coefficient, COORDINATES[derivative])
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
                result[FORMS3.index(tuple(sorted(replaced))), incoming] += (
                    (-1) ** inversions * coefficient
                )
    return result


def _source_action(generator: str) -> sp.Matrix:
    return sp.kronecker_product(_adjoint(generator), sp.eye(4)) + sp.kronecker_product(
        sp.eye(5), _form_action(generator)
    )


def _target_action(generator: str) -> sp.Matrix:
    result = sp.zeros(14)
    for output, incoming, word, profile in density_dual_action(
        stabilizer_action(stabilizer_vectors()[generator])
    ):
        if not word:
            result[output, incoming] += sp.Rational(profile.get((), 0))
    return result


def _target_q1() -> tuple[sp.Matrix, list[sp.Matrix]]:
    content = _load(Q1)["content"]
    profiles = {
        item["index"]: {
            tuple(jet["word"]): sp.Rational(jet["coefficient"])
            for jet in item["coefficient_jets"]
        }
        for item in content["coefficient_profiles"]
    }
    zero = sp.zeros(6, 14)
    symbol = [sp.zeros(6, 14) for _ in range(4)]
    for term in content["terms"]:
        incoming = term["inputs"][0]
        if not (34 <= term["output_row"] < 40 and 20 <= incoming["row"] < 34):
            continue
        value = profiles[term["coefficient_profile"]].get((), 0)
        if value != sp.Rational(term["coefficient"]):
            raise AssertionError("q1 coefficient/profile mismatch")
        word = incoming["word"]
        if not word:
            zero[term["output_row"] - 34, incoming["row"] - 20] += value
        elif len(word) == 1:
            symbol[word[0]][term["output_row"] - 34, incoming["row"] - 20] += value
        else:
            raise AssertionError("top q1 row exceeds first order")
    return zero, symbol


def _hom_dimension(
    source: dict[int, int], target: dict[int, int], order: int
) -> int:
    derivative = Counter(
        sum((0, 0, 1, -1)[index] for index in word)
        for word in combinations_with_replacement(range(4), order)
    )
    return sum(
        source_multiplicity
        * derivative_multiplicity
        * target.get(source_weight + derivative_weight, 0)
        for source_weight, source_multiplicity in source.items()
        for derivative_weight, derivative_multiplicity in derivative.items()
    )


def main() -> None:
    certificate = _load(CERT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for artifact in certificate["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {artifact['path']}")

    p3 = {0: 8, 1: 5, -1: 5, 2: 1, -2: 1}
    p4 = {0: 3, 1: 1, -1: 1}
    w1 = {0: 6, 1: 3, -1: 3, 2: 1, -2: 1}
    w2 = {0: 4, 1: 1, -1: 1}
    dimensions = [_hom_dimension(p3, w1, 3), _hom_dimension(p4, w2, 3)]
    if dimensions != [1108, 144]:
        raise AssertionError("independent cubic character census failed")

    vectors = stabilizer_vectors()
    third_vector_nonzero = 0
    second_source_nonzero = 0
    for generator in TRANSITIVE:
        for output in range(4):
            for word in combinations_with_replacement(range(4), 3):
                expression = vectors[generator][output]
                for axis in word:
                    expression = sp.diff(expression, COORDINATES[axis])
                third_vector_nonzero += int(bool(_base(expression)))
        for left in range(4):
            for right in range(left, 4):
                second_source_nonzero += len(
                    _form_action(generator, (left, right)).todok()
                ) * 5
    if (third_vector_nonzero, second_source_nonzero) != (0, 0):
        raise AssertionError("direct cubic descent did not vanish")

    target_zero, target_symbol = _target_q1()
    target_actions = {generator: _target_action(generator) for generator in TRANSITIVE}
    source_actions = {generator: _source_action(generator) for generator in TRANSITIVE}
    for generator in TRANSITIVE:
        vector_derivative = sp.Matrix(
            4,
            4,
            lambda output, incoming: _base(
                sp.diff(vectors[generator][output], COORDINATES[incoming])
            ),
        )
        if vector_derivative.todok():
            raise AssertionError("transitive first jet unexpectedly nonzero")

    functionals: dict[tuple[int, ...], sp.Matrix] = {}
    for record in certificate["indirect_descent"]["order_two_rowspace_witness"]:
        word = tuple(record["word"])
        functionals.setdefault(word, sp.zeros(14, 20))
        target_output = record["output_local"]
        source_input = record["input_local"]
        witness = sp.Rational(record["coefficient"])
        for output in range(14):
            for incoming in range(20):
                value = target_zero[target_output, output] * (
                    incoming == source_input
                )
                for axis, generator in enumerate(TRANSITIVE):
                    value += (
                        (target_symbol[axis] * -target_actions[generator])[
                            target_output, output
                        ]
                        * (incoming == source_input)
                    )
                    value += (
                        target_symbol[axis][target_output, output]
                        * source_actions[generator][incoming, source_input]
                    )
                functionals[word][output, incoming] -= witness * value
    nonzero = sum(len(matrix.todok()) for matrix in functionals.values())
    if nonzero:
        raise AssertionError("independent effective cubic functional is nonzero")
    if (
        certificate["indirect_descent"]["effective_cubic_functional"][
            "nonzero_entries"
        ]
        != nonzero
    ):
        raise AssertionError("effective cubic functional census mismatch")
    print(
        json.dumps(
            {
                "status": "PASS",
                "invariant_dimensions": dimensions,
                "third_vector_jets_nonzero": third_vector_nonzero,
                "second_source_action_jets_nonzero": second_source_nonzero,
                "effective_cubic_functional_nonzero": nonzero,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
