#!/usr/bin/env python3
"""Independent geometric replay of the order-two obstruction sensitivity."""

from __future__ import annotations

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
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-obstruction-sensitivity-v1.schema.json"
Q1 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json"
WORDS2 = list(combinations_with_replacement(range(4), 2))
WORD_INDEX = {word: index for index, word in enumerate(WORDS2)}
FORMS3 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def _load(path: Path):
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _base(expression: sp.Expr) -> sp.Rational:
    return sp.Rational(sp.simplify(expression.subs(BASE_POINT)))


def _adjoint_j3() -> sp.Matrix:
    result = sp.zeros(5)
    result[2, 1] = -1
    result[1, 2] = 1
    return result


def _vector_derivative(generator: str) -> sp.Matrix:
    vectors = stabilizer_vectors()
    return sp.Matrix(
        4,
        4,
        lambda output, incoming: _base(
            sp.diff(vectors[generator][output], COORDINATES[incoming])
        ),
    )


def _form_action(generator: str, derivative_axis: int | None = None) -> sp.Matrix:
    vector = stabilizer_vectors()[generator]
    result = sp.zeros(4)
    for incoming, indices in enumerate(FORMS3):
        for position, index in enumerate(indices):
            for replacement in range(4):
                coefficient = sp.diff(vector[replacement], COORDINATES[index])
                if derivative_axis is not None:
                    coefficient = sp.diff(coefficient, COORDINATES[derivative_axis])
                coefficient = _base(coefficient)
                if not coefficient:
                    continue
                replaced = list(indices)
                replaced[position] = replacement
                if len(set(replaced)) != 3:
                    continue
                inversions = sum(
                    replaced[left] > replaced[right]
                    for left in range(3)
                    for right in range(left + 1, 3)
                )
                result[FORMS3.index(tuple(sorted(replaced))), incoming] += (
                    (-1) ** inversions * coefficient
                )
    return result


def _source_action(generator: str, derivative_axis: int | None = None) -> sp.Matrix:
    generator_part = (
        sp.kronecker_product(_adjoint_j3(), sp.eye(4))
        if generator == "J_3" and derivative_axis is None
        else sp.zeros(20)
    )
    return generator_part + sp.kronecker_product(
        sp.eye(5), _form_action(generator, derivative_axis)
    )


def _target_action_j3() -> sp.Matrix:
    result = sp.zeros(14)
    for output, incoming, word, profile in density_dual_action(
        stabilizer_action(stabilizer_vectors()["J_3"])
    ):
        if not word:
            result[output, incoming] += sp.Rational(profile.get((), 0))
    return result


def _target_q1_theta_symbol() -> sp.Matrix:
    content = _load(Q1)["content"]
    profiles = {
        item["index"]: {
            tuple(jet["word"]): sp.Rational(jet["coefficient"])
            for jet in item["coefficient_jets"]
        }
        for item in content["coefficient_profiles"]
    }
    result = sp.zeros(6, 14)
    for term in content["terms"]:
        incoming = term["inputs"][0]
        if (
            34 <= term["output_row"] < 40
            and 20 <= incoming["row"] < 34
            and incoming["word"] == [2]
        ):
            value = profiles[term["coefficient_profile"]].get((), 0)
            if value != sp.Rational(term["coefficient"]):
                raise AssertionError("q1 coefficient/profile mismatch")
            result[term["output_row"] - 34, incoming["row"] - 20] += value
    return result


def _sym2_action() -> sp.Matrix:
    vector = _vector_derivative("J_3")
    result = sp.zeros(10)
    for incoming, (left, right) in enumerate(WORDS2):
        for replacement in range(4):
            result[WORD_INDEX[tuple(sorted((replacement, right)))], incoming] += (
                vector[replacement, left]
            )
            result[WORD_INDEX[tuple(sorted((left, replacement)))], incoming] += (
                vector[replacement, right]
            )
    return result


def _symbol(records) -> list[sp.Matrix]:
    output = [sp.zeros(14, 20) for _ in WORDS2]
    for record in records:
        output[WORD_INDEX[tuple(record["word"])]][
            record["A1_output_local"], record["P3_input_local"]
        ] += sp.Rational(record["coefficient"])
    return output


def _invariance(symbol: list[sp.Matrix]) -> int:
    target = _target_action_j3()
    source = _source_action("J_3")
    derivative = _sym2_action()
    residual = [
        target * symbol[word]
        - symbol[word] * source
        - sum(
            (
                derivative[word, incoming] * symbol[incoming]
                for incoming in range(10)
            ),
            sp.zeros(14, 20),
        )
        for word in range(10)
    ]
    return sum(len(matrix.todok()) for matrix in residual)


def _sensitivity(symbol: list[sp.Matrix]) -> sp.Rational:
    vector = stabilizer_vectors()["J_2"]
    source_derivatives = [_source_action("J_2", axis) for axis in range(4)]
    first = [sp.zeros(14, 20), sp.zeros(14, 20)]
    for word_index, (left, right) in enumerate(WORDS2):
        coefficient = symbol[word_index]
        for derivative_index in range(2):
            second_vector = _base(
                sp.diff(
                    vector[derivative_index],
                    COORDINATES[left],
                    COORDINATES[right],
                )
            )
            if second_vector:
                first[derivative_index] += second_vector * coefficient
            if right == derivative_index:
                first[derivative_index] += coefficient * source_derivatives[left]
            if left == derivative_index:
                first[derivative_index] += coefficient * source_derivatives[right]
    q1_theta = _target_q1_theta_symbol()
    return sp.Rational(
        -(q1_theta * first[0])[1, 2] - (q1_theta * first[1])[0, 2]
    )


def main() -> None:
    certificate = _load(CERT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for artifact in certificate["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {artifact['path']}")
    quotient = certificate["obstruction_quotient"]
    if (
        quotient["dimension"] != 1
        or quotient["source_certificate_augmented_rank"]
        - quotient["source_certificate_rank"]
        != 1
    ):
        raise AssertionError("obstruction quotient census failed")
    if certificate["order_two_symbol_space"]["homogeneous_invariant_dimension"] != 626:
        raise AssertionError("order-two invariant census failed")

    replay = []
    for candidate in certificate["induced_sensitivity"][
        "explicit_invariant_candidates"
    ]:
        symbol = _symbol(candidate["records"])
        residual = _invariance(symbol)
        value = _sensitivity(symbol)
        if residual != candidate["isotropy_residual_nonzero_entries"]:
            raise AssertionError("candidate isotropy replay failed")
        if str(value) != candidate["normalized_obstruction_sensitivity"]:
            raise AssertionError("candidate sensitivity replay failed")
        replay.append([candidate["id"], residual, str(value)])
    if {item[2] for item in replay} != {"-1", "1"}:
        raise AssertionError("nonzero quotient image was not independently replayed")
    print(
        json.dumps(
            {
                "status": "PASS",
                "obstruction_quotient_dimension": 1,
                "order_two_invariant_dimension": 626,
                "candidate_replay": replay,
                "sensitivity_rank": 1,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
