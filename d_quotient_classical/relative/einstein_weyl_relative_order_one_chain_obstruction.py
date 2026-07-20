#!/usr/bin/env python3
"""Solve the complete endpoint-normalized invariant order-one chain system."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from math import gcd
import hashlib
import json
from pathlib import Path
from typing import Any

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
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-one-chain-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-one-chain-obstruction-v1.schema.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_order_one_chain_obstruction_v1/system.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-one-chain-system-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_one_chain_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_one_chain_obstruction.py"
DEPENDENCIES = {
    "ansatz": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1.json",
    "endpoint": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json",
    "order_zero": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
    "current_layout": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json",
}

GENERATORS = ["H", "P_x", "J_1", "J_2", "J_3"]
TRANSITIVE = ["H", "P_x", "J_2", "J_1"]
FORMS3 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
AXES = ["t", "x", "theta", "phi"]


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


def _fraction(value: sp.Rational) -> str:
    return str(int(value.p)) if value.q == 1 else f"{int(value.p)}/{int(value.q)}"


def _base(expression: sp.Expr) -> sp.Rational:
    return sp.Rational(sp.simplify(expression.subs(BASE_POINT)))


def _primitive(vector: sp.Matrix) -> sp.Matrix:
    values = [sp.Rational(value) for value in vector]
    common = 1
    for value in values:
        common = sp.ilcm(common, value.q)
    integers = [int(value * common) for value in values]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    if divisor:
        integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return sp.Matrix(integers)


def _basis_digest(basis: list[sp.Matrix]) -> str:
    records = [
        [[index, _fraction(sp.Rational(value))] for index, value in enumerate(vector) if value]
        for vector in basis
    ]
    return hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()


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
                output = FORMS3.index(tuple(sorted(replaced)))
                result[output, incoming] += (-1) ** inversions * coefficient
    return result


def _source_action(generator: str, derivative_axis: int | None = None) -> sp.Matrix:
    generator_part = (
        sp.kronecker_product(_adjoint(generator), sp.eye(4))
        if derivative_axis is None
        else sp.zeros(20)
    )
    return generator_part + sp.kronecker_product(
        sp.eye(5), _form_action(generator, derivative_axis)
    )


def _target_equation_action(generator: str) -> sp.Matrix:
    result = sp.zeros(14)
    for output, incoming, word, profile in density_dual_action(
        stabilizer_action(stabilizer_vectors()[generator])
    ):
        if not word:
            result[output, incoming] += sp.Rational(profile.get((), 0))
    return result


def _target_identity_action(generator: str) -> sp.Matrix:
    result = sp.zeros(6)
    result[:4, :4] = _vector_derivative(generator).T
    return result


def _invariance_matrix(
    target: sp.Matrix, source: sp.Matrix, *, derivative: bool
) -> sp.Matrix:
    base = (
        sp.kronecker_product(sp.eye(source.rows), target)
        - sp.kronecker_product(source.T, sp.eye(target.rows))
    )
    if not derivative:
        return base
    return (
        sp.kronecker_product(sp.eye(4), base)
        - sp.kronecker_product(
            _vector_derivative("J_3"), sp.eye(target.rows * source.rows)
        )
    )


def _invariant_bases() -> tuple[list[sp.Matrix], list[sp.Matrix], list[sp.Matrix]]:
    a10 = [
        _primitive(vector)
        for vector in _invariance_matrix(
            _target_equation_action("J_3"), _source_action("J_3"), derivative=False
        ).nullspace()
    ]
    a11 = [
        _primitive(vector)
        for vector in _invariance_matrix(
            _target_equation_action("J_3"), _source_action("J_3"), derivative=True
        ).nullspace()
    ]
    a21 = [
        _primitive(vector)
        for vector in _invariance_matrix(
            _target_identity_action("J_3"), _adjoint("J_3"), derivative=True
        ).nullspace()
    ]
    if [len(a10), len(a11), len(a21)] != [80, 284, 42]:
        raise AssertionError("invariant basis census drifted")
    return a10, a11, a21


def _unvec(vector: sp.Matrix, output: int, incoming: int) -> sp.Matrix:
    return sp.Matrix(output, incoming, lambda row, column: vector[column * output + row])


def _decode_a1(vector: sp.Matrix, derivative: bool) -> tuple[sp.Matrix, list[sp.Matrix]]:
    if not derivative:
        return _unvec(vector, 14, 20), [sp.zeros(14, 20) for _ in range(4)]
    return sp.zeros(14, 20), [
        _unvec(vector[axis * 280 : (axis + 1) * 280, :], 14, 20)
        for axis in range(4)
    ]


def _coefficient_derivatives(
    order_zero: sp.Matrix, symbol: list[sp.Matrix]
) -> tuple[list[sp.Matrix], list[list[sp.Matrix]]]:
    zero_derivatives = []
    symbol_derivatives = []
    for generator in TRANSITIVE:
        target = _target_equation_action(generator)
        source = _source_action(generator)
        source_derivatives = [_source_action(generator, axis) for axis in range(4)]
        vector_derivative = _vector_derivative(generator)
        symbol_derivatives.append(
            [
                -target * symbol[output]
                + symbol[output] * source
                + sum(
                    (
                        symbol[incoming] * vector_derivative[output, incoming]
                        for incoming in range(4)
                    ),
                    sp.zeros(14, 20),
                )
                for output in range(4)
            ]
        )
        zero_derivatives.append(
            -target * order_zero
            + order_zero * source
            + sum(
                (
                    symbol[axis] * source_derivatives[axis]
                    for axis in range(4)
                ),
                sp.zeros(14, 20),
            )
        )
    return zero_derivatives, symbol_derivatives


def _target_q1() -> tuple[sp.Matrix, list[sp.Matrix]]:
    content = _load(DEPENDENCIES["target_q1"])["content"]
    profiles = {
        item["index"]: {
            tuple(jet["word"]): sp.Rational(jet["coefficient"])
            for jet in item["coefficient_jets"]
        }
        for item in content["coefficient_profiles"]
    }
    order_zero = sp.zeros(6, 14)
    symbol = [sp.zeros(6, 14) for _ in range(4)]
    for term in content["terms"]:
        incoming = term["inputs"][0]
        if not (34 <= term["output_row"] < 40 and 20 <= incoming["row"] < 34):
            continue
        coefficient = profiles[term["coefficient_profile"]].get((), 0)
        if coefficient != sp.Rational(term["coefficient"]):
            raise AssertionError("q1 display coefficient/profile mismatch")
        word = incoming["word"]
        if not word:
            order_zero[term["output_row"] - 34, incoming["row"] - 20] += coefficient
        elif len(word) == 1:
            symbol[word[0]][term["output_row"] - 34, incoming["row"] - 20] += coefficient
        else:
            raise AssertionError("top target row is not first order")
    return order_zero, symbol


def _de_rham() -> tuple[list[sp.Matrix], list[dict], list[dict]]:
    layout = _load(DEPENDENCIES["current_layout"])
    p3 = sorted(
        (row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 3),
        key=lambda row: row["index"],
    )
    p4 = sorted(
        (row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 4),
        key=lambda row: row["index"],
    )
    p3_index = {row["index"]: index for index, row in enumerate(p3)}
    p4_index = {row["index"]: index for index, row in enumerate(p4)}
    axis_index = {axis: index for index, axis in enumerate(AXES)}
    symbol = [sp.zeros(5, 20) for _ in range(4)]
    for term in layout["unary_terms"]:
        if term["source_row"] in p3_index and term["target_row"] in p4_index:
            symbol[axis_index[term["derivative"]]][
                p4_index[term["target_row"]], p3_index[term["source_row"]]
            ] += sp.Rational(term["coefficient"])
    return symbol, p3, p4


def _fixed_endpoint() -> sp.Matrix:
    result = sp.zeros(6, 5)
    result[0, 0] = result[1, 1] = result[3, 2] = result[2, 3] = 1
    if _target_identity_action("J_3") * result != result * _adjoint("J_3"):
        raise AssertionError("fixed endpoint is not isotropy equivariant")
    return result


def _add_matrix(
    output: dict[tuple, sp.Rational], word: tuple[int, ...], matrix: sp.Matrix
) -> None:
    for (row, column), value in matrix.todok().items():
        if value:
            output[(tuple(sorted(word)), row, column)] += value


def _a1_column(
    vector: sp.Matrix,
    *,
    derivative: bool,
    target_zero: sp.Matrix,
    target_symbol: list[sp.Matrix],
) -> dict[tuple, sp.Rational]:
    order_zero, symbol = _decode_a1(vector, derivative)
    zero_derivatives, symbol_derivatives = _coefficient_derivatives(order_zero, symbol)
    result: dict[tuple, sp.Rational] = defaultdict(lambda: sp.S.Zero)
    for outer in range(4):
        for inner in range(4):
            _add_matrix(result, (outer, inner), target_symbol[outer] * symbol[inner])
    for axis in range(4):
        first = (
            sum(
                (
                    target_symbol[outer] * symbol_derivatives[outer][axis]
                    for outer in range(4)
                ),
                sp.zeros(6, 20),
            )
            + target_symbol[axis] * order_zero
            + target_zero * symbol[axis]
        )
        _add_matrix(result, (axis,), first)
    zero = (
        sum(
            (
                target_symbol[axis] * zero_derivatives[axis]
                for axis in range(4)
            ),
            sp.zeros(6, 20),
        )
        + target_zero * order_zero
    )
    _add_matrix(result, (), zero)
    return {key: value for key, value in result.items() if value}


def _system() -> dict[str, Any]:
    a10, a11, a21 = _invariant_bases()
    target_zero, target_symbol = _target_q1()
    de_rham, p3, _ = _de_rham()
    columns = [
        _a1_column(vector, derivative=False, target_zero=target_zero, target_symbol=target_symbol)
        for vector in a10
    ] + [
        _a1_column(vector, derivative=True, target_zero=target_zero, target_symbol=target_symbol)
        for vector in a11
    ]
    all_keys: set[tuple] = set()
    for vector in a21:
        symbol = [
            _unvec(vector[axis * 30 : (axis + 1) * 30, :], 6, 5)
            for axis in range(4)
        ]
        column: dict[tuple, sp.Rational] = defaultdict(lambda: sp.S.Zero)
        for left in range(4):
            for right in range(4):
                _add_matrix(column, (left, right), -symbol[left] * de_rham[right])
        cleaned = {key: value for key, value in column.items() if value}
        columns.append(cleaned)
    rhs: dict[tuple, sp.Rational] = defaultdict(lambda: sp.S.Zero)
    endpoint = _fixed_endpoint()
    for axis in range(4):
        _add_matrix(rhs, (axis,), endpoint * de_rham[axis])
    for column in columns:
        all_keys.update(column)
    all_keys.update(rhs)
    keys = sorted(all_keys)
    row_index = {key: index for index, key in enumerate(keys)}
    entries = {
        (row_index[key], column_index): value
        for column_index, column in enumerate(columns)
        for key, value in column.items()
        if value
    }
    rhs_vector = sp.zeros(len(keys), 1)
    for key, value in rhs.items():
        rhs_vector[row_index[key]] = value
    matrix = sp.SparseMatrix(len(keys), len(columns), entries)
    rank = matrix.rank()
    augmented_rank = matrix.row_join(rhs_vector).rank()
    if (matrix.rows, matrix.cols, rank, augmented_rank) != (822, 406, 398, 399):
        raise AssertionError(
            f"order-one system census drifted: "
            f"{matrix.rows}, {matrix.cols}, {rank}, {augmented_rank}"
        )

    # A two-row certificate is preferable to serializing a large nullspace:
    # find primitive-equal coefficient rows with incompatible right sides.
    groups: dict[tuple, list[tuple[int, int, sp.Rational]]] = defaultdict(list)
    for row in range(matrix.rows):
        values = [(column, matrix[row, column]) for column in range(matrix.cols) if matrix[row, column]]
        if not values:
            if rhs_vector[row]:
                groups[()].append((row, 1, rhs_vector[row]))
            continue
        denominators = [value.q for _, value in values]
        common = 1
        for denominator in denominators:
            common = sp.ilcm(common, denominator)
        integers = [int(value * common) for _, value in values]
        divisor = 0
        for value in integers:
            divisor = gcd(divisor, abs(value))
        integers = [value // divisor for value in integers]
        sign = 1 if next(value for value in integers if value) > 0 else -1
        signature = tuple((column, sign * value) for (column, _), value in zip(values, integers))
        scale = sp.Rational(sign * divisor, common)
        groups[signature].append((row, scale, rhs_vector[row]))
    witness = None
    for rows in groups.values():
        for left_index, (left, left_scale, left_rhs) in enumerate(rows):
            for right, right_scale, right_rhs in rows[left_index + 1 :]:
                evaluation = right_scale * left_rhs - left_scale * right_rhs
                if evaluation:
                    witness = {
                        "terms": [[left, _fraction(right_scale)], [right, _fraction(-left_scale)]],
                        "evaluation": _fraction(evaluation),
                    }
                    break
            if witness:
                break
        if witness:
            break
    if witness is None:
        raise AssertionError("short left-null witness disappeared")

    def row_record(index: int) -> dict[str, Any]:
        word, output, incoming = keys[index]
        return {
            "row": index,
            "word": list(word),
            "output_local": output,
            "output_row": output + 34,
            "output_row_id": ["c_0_star", "c_1_star", "c_2_star", "c_3_star", "lambda_cov_star", "sigma_W_star"][output],
            "input_local": incoming,
            "input_row": p3[incoming]["index"],
            "input_row_id": p3[incoming]["row_id"],
            "rhs": _fraction(sp.Rational(rhs_vector[index])),
        }
    witness["rows"] = [row_record(index) for index, _ in witness["terms"]]
    records = [
        [row, column, _fraction(sp.Rational(value))]
        for (row, column), value in sorted(entries.items())
    ]
    return {
        "basis_dimensions": [len(a10), len(a11), len(a21)],
        "basis_digests": [_basis_digest(a10), _basis_digest(a11), _basis_digest(a21)],
        "matrix": matrix,
        "rhs": rhs_vector,
        "records": records,
        "rank": rank,
        "augmented_rank": augmented_rank,
        "witness": witness,
        "rhs_records": [
            [row, _fraction(sp.Rational(value))]
            for row, value in enumerate(rhs_vector)
            if value
        ],
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    data = _system()
    payload = {
        "schema": "pure-weyl-relative-order-one-chain-system-v1",
        "result_id": f"{RESULT_ID}_SYSTEM",
        "shape": [data["matrix"].rows, data["matrix"].cols],
        "matrix_coo": data["records"],
        "rhs_sparse": data["rhs_records"],
    }
    payload_bytes = _render(payload).encode()
    certificate = {
        "schema": "pure-weyl-relative-order-one-chain-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_ENDPOINT_NORMALIZED_ORDER_ONE_CHAIN_MAP_OBSTRUCTED",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": values["ansatz"]["scope"],
        "dependencies": {
            name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()
        },
        "invariant_basis": {
            "A1_order_zero_dimension": data["basis_dimensions"][0],
            "A1_order_one_dimension": data["basis_dimensions"][1],
            "A2_order_one_dimension": data["basis_dimensions"][2],
            "total_unknowns": 406,
            "primitive_sparse_basis_sha256": {
                "A1_order_zero": data["basis_digests"][0],
                "A1_order_one": data["basis_digests"][1],
                "A2_order_one": data["basis_digests"][2],
            },
            "globalization": "isotropy-equivariant base tensors; first coefficient jets fixed by the four transitive stabilizer actions",
        },
        "system_payload": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
            "matrix_records": len(data["records"]),
            "rhs_records": len(data["rhs_records"]),
        },
        "exact_linear_system": {
            "equations": data["matrix"].rows,
            "unknowns": data["matrix"].cols,
            "nonzero_entries": len(data["records"]),
            "rank_over_Q": data["rank"],
            "nullity": data["matrix"].cols - data["rank"],
            "augmented_rank_over_Q": data["augmented_rank"],
            "consistent": False,
            "matrix_coo_sha256": hashlib.sha256(
                json.dumps(data["records"], separators=(",", ":")).encode()
            ).hexdigest(),
            "left_null_witness": data["witness"],
        },
        "classification": {
            "complete_endpoint_normalized_invariant_order_one_system_solved": True,
            "order_one_chain_map_exists": False,
            "order_one_chain_map_obstructed": True,
            "higher_order_chain_map_obstructed": False,
            "nonzero_f2_obstructed": False,
            "alternate_current_improvement_obstructed": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CLASSIFY_ORDER_TWO_OR_CHANGE_THE_RELATIVE_CURRENT_REPRESENTATIVE_OR_CARRIER_BEFORE_THE_FIFTEEN_ROW_F2_INCIDENCE",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (
                    Path(__file__).resolve(),
                    VERIFIER,
                    TESTS,
                    SCHEMA,
                    PAYLOAD_SCHEMA,
                )
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_one_chain_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_one_chain_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_one_chain_obstruction",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem exhausts the 406-parameter endpoint-normalized SO(2)-invariant differential ansatz with A1 and A2 through order one. After deleting identically zero coefficient rows, the 822-by-406 rational chain system has rank 398 and augmented rank 399; the serialized two-row left-null witness proves inconsistency. It does not obstruct order two or higher, nonzero f2, another current improvement, a larger relative carrier, causal data, observables, particles or quantum claims.",
    }
    return certificate, payload


def validate(value: dict[str, Any], payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(value)
    Draft202012Validator(payload_schema).validate(payload)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    witness = value["exact_linear_system"]["left_null_witness"]
    return f"""# Complete invariant order-one chain obstruction

The endpoint-normalized `SO(2)`-invariant ansatz has 406 exact coefficients:
80 order-zero and 284 order-one coefficients in `A1`, and 42 order-one
coefficients in `A2`.  Transitive equivariance fixes the required coefficient
jets.  After deleting identically zero coefficient rows, the complete rational
chain system has 822 equations, rank 398 and
augmented rank 399.  Its normalized two-row left-null witness evaluates to
`{witness['evaluation']}`, so no member of this family is a chain map.

This does not obstruct higher differential order, another current
representative, a larger carrier or any causal construction.  A nonzero
`f2` cannot be tested in this incidence until its unary chain map exists.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "order_one_chain_map_exists",
        "higher_order_chain_map_obstructed",
        "nonzero_f2_obstructed",
        "alternate_current_improvement_obstructed",
        "relative_q2_repaired",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant, {
                "schema": "pure-weyl-relative-order-one-chain-system-v1",
                "result_id": f"{RESULT_ID}_SYSTEM",
                "shape": [822, 406],
                "matrix_coo": [[0, 0, "1"]],
                "rhs_sparse": [[0, "1"]],
            })
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value, payload = build_outputs()
    validate(value, payload)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check and (
        OUTPUT.read_text() != _render(value)
        or PAYLOAD.read_text() != _render(payload)
        or REPORT.read_text() != _report(value)
    ):
        raise AssertionError("order-one chain obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
