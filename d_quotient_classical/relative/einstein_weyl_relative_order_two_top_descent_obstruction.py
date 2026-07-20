#!/usr/bin/env python3
"""Restrict order-two sensitivity to the legal top-descent kernel."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from functools import reduce
from itertools import combinations_with_replacement
from math import gcd
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.relative.einstein_weyl_relative_order_one_chain_obstruction import (
    _adjoint,
    _de_rham,
    _source_action,
    _target_equation_action,
    _target_identity_action,
    _target_q1,
)
from d_quotient_classical.relative.einstein_weyl_relative_order_two_obstruction_sensitivity import (
    WORDS2,
    _coordinate_sensitivity,
    _sym2_action,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-two-top-descent-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-top-descent-obstruction-v1.schema.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_order_two_top_descent_obstruction_v1/system.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-top-descent-system-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_two_top_descent_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_two_top_descent_obstruction.py"
DEPENDENCIES = {
    "order_one_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json",
    "unrestricted_sensitivity": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
}
WORDS3 = list(combinations_with_replacement(range(4), 3))


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


def _primitive_sparse(vector: dict[int, sp.Rational]) -> dict[int, sp.Rational]:
    if not vector:
        return {}
    common = 1
    for value in vector.values():
        common = sp.ilcm(common, sp.Rational(value).q)
    integers = {key: int(sp.Rational(value) * common) for key, value in vector.items()}
    divisor = reduce(gcd, (abs(value) for value in integers.values()), 0)
    if divisor:
        integers = {key: value // divisor for key, value in integers.items()}
    first = integers[min(integers)]
    if first < 0:
        integers = {key: -value for key, value in integers.items()}
    return {key: sp.Rational(value) for key, value in integers.items() if value}


def _invariant_basis(
    target: sp.Matrix, source: sp.Matrix, derivative: sp.Matrix
) -> list[dict[int, sp.Rational]]:
    """Kernel basis by tiny connected representation blocks."""

    word_count = derivative.rows
    target_rank = target.rows
    source_rank = source.rows
    dimension = word_count * target_rank * source_rank

    def index(word: int, output: int, incoming: int) -> int:
        return (word * target_rank + output) * source_rank + incoming

    rows: list[dict[int, sp.Rational]] = [{} for _ in range(dimension)]
    for word in range(word_count):
        for output in range(target_rank):
            for incoming in range(source_rank):
                row = rows[index(word, output, incoming)]
                for target_input in range(target_rank):
                    value = target[output, target_input]
                    if value:
                        raw = index(word, target_input, incoming)
                        row[raw] = row.get(raw, sp.S.Zero) + value
                for source_output in range(source_rank):
                    value = source[source_output, incoming]
                    if value:
                        raw = index(word, output, source_output)
                        row[raw] = row.get(raw, sp.S.Zero) - value
                for input_word in range(word_count):
                    value = derivative[word, input_word]
                    if value:
                        raw = index(input_word, output, incoming)
                        row[raw] = row.get(raw, sp.S.Zero) - value

    adjacency = [set() for _ in range(dimension)]
    for row in rows:
        variables = list(row)
        for variable in variables:
            adjacency[variable].update(variables)
    seen: set[int] = set()
    basis: list[dict[int, sp.Rational]] = []
    for seed in range(dimension):
        if seed in seen:
            continue
        stack = [seed]
        seen.add(seed)
        component = []
        while stack:
            variable = stack.pop()
            component.append(variable)
            for neighbour in adjacency[variable]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        component.sort()
        local_index = {variable: position for position, variable in enumerate(component)}
        relevant_rows = sorted(
            row_index
            for row_index, row in enumerate(rows)
            if any(variable in local_index for variable in row)
        )
        matrix = sp.SparseMatrix(
            len(relevant_rows),
            len(component),
            {
                (local_row, local_index[variable]): value
                for local_row, row_index in enumerate(relevant_rows)
                for variable, value in rows[row_index].items()
                if variable in local_index
            },
        )
        for vector in matrix.nullspace():
            basis.append(
                _primitive_sparse(
                    {
                        component[position]: sp.Rational(value)
                        for position, value in enumerate(vector)
                        if value
                    }
                )
            )
    return basis


def _basis_digest(basis: list[dict[int, sp.Rational]]) -> str:
    records = [
        [[index, _fraction(value)] for index, value in sorted(vector.items())]
        for vector in basis
    ]
    return hashlib.sha256(
        json.dumps(records, separators=(",", ":")).encode()
    ).hexdigest()


def _top_system() -> dict[str, Any]:
    derivative = _sym2_action()
    a1_basis = _invariant_basis(
        _target_equation_action("J_3"),
        _source_action("J_3"),
        derivative,
    )
    a2_basis = _invariant_basis(
        _target_identity_action("J_3"),
        _adjoint("J_3"),
        derivative,
    )
    if (len(a1_basis), len(a2_basis)) != (626, 86):
        raise AssertionError("order-two invariant basis census drifted")

    target_symbol = _target_q1()[1]
    de_rham = _de_rham()[0]
    columns: list[dict[tuple, sp.Rational]] = []
    sensitivity: list[sp.Rational] = []
    for vector in a1_basis:
        column: dict[tuple, sp.Rational] = defaultdict(lambda: sp.S.Zero)
        evaluation = sp.S.Zero
        for raw, coefficient in vector.items():
            incoming = raw % 20
            quotient = raw // 20
            output = quotient % 14
            word = WORDS2[quotient // 14]
            evaluation += coefficient * _coordinate_sensitivity(
                word, output, incoming
            )
            for axis in range(4):
                output_word = tuple(sorted(word + (axis,)))
                for target_output in range(6):
                    value = target_symbol[axis][target_output, output] * coefficient
                    if value:
                        column[(output_word, target_output, incoming)] += value
        columns.append({key: value for key, value in column.items() if value})
        sensitivity.append(sp.Rational(evaluation))
    for vector in a2_basis:
        column = defaultdict(lambda: sp.S.Zero)
        for raw, coefficient in vector.items():
            incoming = raw % 5
            quotient = raw // 5
            output = quotient % 6
            word = WORDS2[quotient // 6]
            for axis in range(4):
                output_word = tuple(sorted(word + (axis,)))
                for source_input in range(20):
                    value = -coefficient * de_rham[axis][incoming, source_input]
                    if value:
                        column[(output_word, output, source_input)] += value
        columns.append({key: value for key, value in column.items() if value})
        sensitivity.append(sp.S.Zero)

    keys = sorted({key for column in columns for key in column})
    row_index = {key: index for index, key in enumerate(keys)}
    entries = {
        (row_index[key], column_index): value
        for column_index, column in enumerate(columns)
        for key, value in column.items()
    }
    matrix = sp.SparseMatrix(len(keys), len(columns), entries)
    functional = sp.Matrix(1, len(columns), sensitivity)
    rank = matrix.rank()
    appended_rank = matrix.col_join(functional).rank()
    if (
        matrix.rows,
        matrix.cols,
        len(entries),
        rank,
        appended_rank,
    ) != (1056, 712, 2484, 516, 516):
        raise AssertionError(
            "top-descent system census drifted: "
            f"{matrix.rows}, {matrix.cols}, {len(entries)}, {rank}, {appended_rank}"
        )

    # Obtain an exact rowspace certificate using independent row/column pivots.
    row_pivots = matrix.T.rref()[1]
    independent_rows = list(row_pivots)
    row_basis = matrix[independent_rows, :]
    column_pivots = row_basis.rref()[1]
    square = row_basis[:, list(column_pivots)]
    rhs = functional[:, list(column_pivots)].T
    coefficients = square.T.inv() * rhs
    rowspace = sp.zeros(1, matrix.rows)
    for local, row in enumerate(independent_rows):
        rowspace[row] = coefficients[local]
    if rowspace * matrix != functional:
        raise AssertionError("rowspace certificate failed")

    records = [
        [row, column, _fraction(value)]
        for (row, column), value in sorted(entries.items())
    ]
    functional_records = [
        [column, _fraction(value)]
        for column, value in enumerate(functional)
        if value
    ]
    rowspace_records = [
        [row, _fraction(value)]
        for row, value in enumerate(rowspace)
        if value
    ]
    return {
        "a1_basis_digest": _basis_digest(a1_basis),
        "a2_basis_digest": _basis_digest(a2_basis),
        "keys": keys,
        "matrix": matrix,
        "functional": functional,
        "records": records,
        "functional_records": functional_records,
        "rowspace_records": rowspace_records,
        "rank": rank,
        "appended_rank": appended_rank,
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    data = _top_system()
    payload = {
        "schema": "pure-weyl-relative-order-two-top-descent-system-v1",
        "result_id": f"{RESULT_ID}_SYSTEM",
        "shape": [data["matrix"].rows, data["matrix"].cols],
        "row_layout": [
            {
                "row": row,
                "word": list(key[0]),
                "output_local": key[1],
                "input_local": key[2],
            }
            for row, key in enumerate(data["keys"])
        ],
        "matrix_coo": data["records"],
        "sensitivity_sparse": data["functional_records"],
        "rowspace_witness_sparse": data["rowspace_records"],
    }
    payload_bytes = _render(payload).encode()
    certificate = {
        "schema": "pure-weyl-relative-order-two-top-descent-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "LEGAL_ORDER_TWO_TOP_DESCENT_KERNEL_CANNOT_REMOVE_ORDER_ONE_OBSTRUCTION",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": dependencies["order_one_obstruction"]["scope"],
        "dependencies": {
            name: _artifact(path, dependencies[name])
            for name, path in DEPENDENCIES.items()
        },
        "invariant_bases": {
            "A1_order_two_dimension": 626,
            "A2_order_two_dimension": 86,
            "total_top_symbol_unknowns": 712,
            "primitive_sparse_basis_sha256": {
                "A1": data["a1_basis_digest"],
                "A2": data["a2_basis_digest"],
            },
        },
        "top_descent_system": {
            "equations": data["matrix"].rows,
            "unknowns": data["matrix"].cols,
            "nonzero_entries": len(data["records"]),
            "rank_over_Q": data["rank"],
            "kernel_dimension": data["matrix"].cols - data["rank"],
            "rank_with_sensitivity_row": data["appended_rank"],
            "sensitivity_vanishes_on_kernel": True,
            "rowspace_witness_nonzero_entries": len(data["rowspace_records"]),
            "rowspace_witness_rows": [
                {
                    "row": row,
                    "coefficient": coefficient,
                    "word": list(data["keys"][row][0]),
                    "output_local": data["keys"][row][1],
                    "input_local": data["keys"][row][2],
                }
                for row, coefficient in data["rowspace_records"]
            ],
        },
        "system_payload": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
            "matrix_coo_sha256": hashlib.sha256(
                json.dumps(data["records"], separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "combined_obstruction": {
            "order_one_left_null_evaluation": dependencies["order_one_obstruction"][
                "exact_linear_system"
            ]["left_null_witness"]["evaluation"],
            "top_symbol_rowspace_identity": "sensitivity = rowspace_witness * top_descent_matrix",
            "complete_order_two_chain_map_exists": False,
        },
        "classification": {
            "unrestricted_order_two_sensitivity_nonzero": True,
            "legal_top_descent_sensitivity_zero": True,
            "complete_endpoint_normalized_order_two_chain_map_obstructed": True,
            "all_finite_orders_obstructed": False,
            "order_three_chain_map_obstructed": False,
            "current_improvement_obstructed": False,
            "larger_carrier_obstructed": False,
            "f2_incidence_activated": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "SCREEN_ORDER_THREE_SENSITIVITY_OR_CHANGE_THE_ENDPOINT_CURRENT_INCIDENCE_OR_RELATIVE_CARRIER",
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
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_two_top_descent_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_two_top_descent_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_two_top_descent_obstruction",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem restricts the previously nonzero unrestricted order-two sensitivity to the legal top-descent kernel. The 1056-by-712 top system has rank 516 and a 196-dimensional kernel, but adjoining the obstruction sensitivity row leaves rank 516. The serialized rowspace witness proves that every legal order-two top symbol has zero obstruction sensitivity; combined with the normalized order-one left-null evaluation one, this obstructs the complete endpoint-normalized chain map through order two. It does not obstruct order three or higher, another endpoint/current incidence, a larger carrier, f2 in another legal incidence, or any causal, observable, particle or quantum claim.",
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
    top = value["top_descent_system"]
    return f"""# Order-two top-descent obstruction

The unrestricted invariant order-two `A1` symbol space can reach the old
one-dimensional obstruction quotient, but a legal order-two chain map must
also satisfy its highest-order equation.  The complete invariant top-symbol
system has `{top['equations']} x {top['unknowns']}` entries, rank
`{top['rank_over_Q']}`, and kernel dimension `{top['kernel_dimension']}`.

Appending the obstruction-sensitivity row does not increase the rank.  An
exact serialized rowspace witness proves that the sensitivity vanishes on the
entire legal top-descent kernel.  Therefore the normalized order-one
left-null defect survives, and no endpoint-normalized invariant chain map
exists through differential order two.

This does not obstruct order three, a changed endpoint/current incidence, a
larger relative carrier, or any causal or quantum construction.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "all_finite_orders_obstructed",
        "order_three_chain_map_obstructed",
        "current_improvement_obstructed",
        "larger_carrier_obstructed",
        "f2_incidence_activated",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(
                mutant,
                {
                    "schema": "pure-weyl-relative-order-two-top-descent-system-v1",
                    "result_id": f"{RESULT_ID}_SYSTEM",
                    "shape": [1056, 712],
                    "row_layout": [
                        {"row": 0, "word": [0, 0, 0], "output_local": 0, "input_local": 0}
                    ],
                    "matrix_coo": [[0, 0, "1"]],
                    "sensitivity_sparse": [[0, "1"]],
                    "rowspace_witness_sparse": [[0, "1"]],
                },
            )
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
        PAYLOAD.read_text() != _render(payload)
        or OUTPUT.read_text() != _render(value)
        or REPORT.read_text() != _report(value)
    ):
        raise AssertionError("order-two top-descent outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
