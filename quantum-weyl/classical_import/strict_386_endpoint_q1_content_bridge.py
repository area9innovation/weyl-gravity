#!/usr/bin/env python3
"""Exact standard-library kernel for the strict 30-row endpoint q1 bridge.

The expensive rail constructs the triangular coordinate-to-covariant jet
change of basis at the unit-cylinder frame.  The fast rail treats that table
as a proof witness, composes it with the independently produced 700-column
Gate-side Bach table, and compares all three unary arrows with the exact
causal endpoint payload.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import permutations, product
import json
from math import factorial
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


DIMENSION = 4
PAIRS = (
    (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
    (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
)
ZERO = (0, 0, 0, 0)
Matrix = list[list[Fraction]]
Table = dict[tuple[int, int, int, int], Matrix]


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def words_through(order: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        sorted(
            (word for word in product(range(order + 1), repeat=4) if sum(word) <= order),
            key=lambda word: (sum(word), word),
        )
    )


def zero_matrix(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(rank: int) -> Matrix:
    return [
        [Fraction(int(row == column)) for column in range(rank)]
        for row in range(rank)
    ]


def diagonal(entries: Sequence[Fraction | int]) -> Matrix:
    return [
        [Fraction(value if row == column else 0) for column, value in enumerate(entries)]
        for row in range(len(entries))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix product shape mismatch")
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def scale(value: Fraction | int, matrix: Matrix) -> Matrix:
    value = Fraction(value)
    return [[value * entry for entry in row] for row in matrix]


def inverse(matrix: Matrix) -> Matrix:
    rank = len(matrix)
    if rank == 0 or any(len(row) != rank for row in matrix):
        raise ValueError("inverse requires a square matrix")
    augmented = [row[:] + identity(rank)[index] for index, row in enumerate(matrix)]
    for column in range(rank):
        pivot = next(
            (row for row in range(column, rank) if augmented[row][column]), None
        )
        if pivot is None:
            raise ValueError("singular matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [entry / divisor for entry in augmented[column]]
        for row in range(rank):
            if row == column or not augmented[row][column]:
                continue
            coefficient = augmented[row][column]
            augmented[row] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return [row[rank:] for row in augmented]


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [entry / divisor for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            coefficient = work[row][column]
            work[row] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(
                    work[row], work[pivot_row], strict=True
                )
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def encode_matrix(matrix: Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def decode_matrix(value: Sequence[Sequence[object]]) -> Matrix:
    return [[Fraction(str(entry)) for entry in row] for row in value]


def encode_table(table: Table) -> list[dict[str, object]]:
    return [
        {
            "multiindex": list(multiindex),
            "shape": [len(matrix), len(matrix[0])],
            "entries": [
                [row, column, str(matrix[row][column])]
                for row in range(len(matrix))
                for column in range(len(matrix[0]))
                if matrix[row][column]
            ],
        }
        for multiindex, matrix in sorted(table.items())
    ]


def decode_table(value: Mapping[str, object]) -> Table:
    shape = value.get("shape")
    coefficients = value.get("coefficients")
    if not (
        isinstance(shape, list)
        and len(shape) == 2
        and all(isinstance(item, int) for item in shape)
        and isinstance(coefficients, list)
    ):
        raise ValueError("malformed endpoint table")
    output: Table = {}
    for item in coefficients:
        if not isinstance(item, Mapping):
            raise ValueError("malformed endpoint coefficient")
        multiindex = tuple(item.get("multiindex", ()))
        entries = item.get("entries")
        if len(multiindex) != 4 or not isinstance(entries, list):
            raise ValueError("malformed endpoint coefficient row")
        matrix = zero_matrix(shape[0], shape[1])
        for row, column, coefficient in entries:
            matrix[int(row)][int(column)] = Fraction(str(coefficient))
        output[multiindex] = matrix
    return output


def table_nonzero_count(table: Table) -> int:
    return sum(bool(entry) for matrix in table.values() for row in matrix for entry in row)


def table_digest(table: Table) -> str:
    return digest(encode_table(table))


def endpoint_data(payload: Mapping[str, object]) -> tuple[Table, Table, Table, Matrix, Matrix]:
    endpoint_q = payload.get("endpoint_Q")
    pairings = payload.get("pairings")
    if not isinstance(endpoint_q, Mapping) or not isinstance(pairings, Mapping):
        raise ValueError("endpoint payload is incomplete")
    k = decode_table(endpoint_q["K_met"])
    bach = decode_table(endpoint_q["Bach_bar"])
    companion = decode_table(endpoint_q["C_met"])
    field = decode_matrix(
        [pairings["J_met"][10 * row : 10 * row + 10] for row in range(10)]
    )
    ghost = decode_matrix(
        [pairings["Y_met"][5 * row : 5 * row + 5] for row in range(5)]
    )
    return k, bach, companion, field, ghost


def bridge_maps(field_pairing: Matrix, ghost_pairing: Matrix) -> dict[str, Matrix]:
    component_weights = diagonal([1 if left == right else 2 for left, right in PAIRS])
    gate_to_endpoint_ghost = diagonal([-1, 1, 1, 1, 2])
    gate_to_endpoint_field = identity(10)
    gate_to_endpoint_equation = multiply(inverse(field_pairing), component_weights)
    gate_to_endpoint_identity = inverse(
        multiply(transpose(gate_to_endpoint_ghost), ghost_pairing)
    )
    return {
        "A_G": gate_to_endpoint_ghost,
        "A_M": gate_to_endpoint_field,
        "A_E": gate_to_endpoint_equation,
        "A_I": gate_to_endpoint_identity,
        "W_M": component_weights,
        "W_G": identity(5),
    }


def gate_r_tables(q1: Mapping[str, object], endpoint_keys: Iterable[tuple[int, int, int, int]]) -> Table:
    ast = q1.get("local_q1_ast")
    if not isinstance(ast, Mapping):
        raise ValueError("portable q1 AST missing")
    components = {item.get("component_id"): item for item in ast.get("components", [])}
    if set(components) != {
        "q1_h_c", "q1_h_omega", "q1_hstar_h",
        "q1_cstar_hstar", "q1_omegastar_hstar",
    } or any(item.get("coefficient") != 1 for item in components.values()):
        raise ValueError("portable q1 component ledger drift")
    nodes = {item.get("node_id"): item for item in ast.get("nodes", [])}
    if nodes.get("R_weyl", {}).get("parameters", {}).get("formula") != "2 omega gbar_ab":
        raise ValueError("portable Weyl normalization drift")
    if "L_c gbar" not in nodes.get("R_diff", {}).get("parameters", {}).get("formula", ""):
        raise ValueError("portable Diff formula drift")

    table = {multiindex: zero_matrix(10, 5) for multiindex in endpoint_keys}
    metric = (-1, 1, 1, 1)
    for row, (left, right) in enumerate(PAIRS):
        if left == right:
            table[ZERO][row][4] = Fraction(2 * metric[left])
    for axis in range(4):
        multiindex = tuple(int(index == axis) for index in range(4))
        for row, (left, right) in enumerate(PAIRS):
            for ghost in range(4):
                table[multiindex][row][ghost] = Fraction(
                    int(axis == left and ghost == right) * metric[right]
                    + int(axis == right and ghost == left) * metric[left]
                )
    return table


def translated_gate_n_tables(r_tables: Table, component_weights: Matrix) -> Table:
    """Return the canonical translated Noether row ``-R^sharp``."""

    return {
        multiindex: scale(
            -((-1) ** sum(multiindex)),
            multiply(transpose(matrix), component_weights),
        )
        for multiindex, matrix in r_tables.items()
    }


def decode_universal_linear(
    universal: Mapping[str, object],
) -> tuple[list[dict[str, object]], list[dict[int, Fraction]]]:
    basis = universal.get("input_basis")
    raw_dictionary = universal.get("coefficient_dictionary")
    rows = universal.get("rows")
    if not isinstance(basis, list) or not isinstance(raw_dictionary, list) or not isinstance(rows, list):
        raise ValueError("universal Gate Bach table malformed")
    coefficients = [Fraction(str(value)) for value in raw_dictionary]
    linear = [
        {
            int(basis_id): coefficients[int(coefficient_id)]
            for basis_id, coefficient_id in row.get("linear_entries", [])
        }
        for row in rows
    ]
    if len(basis) != 700 or len(linear) != 10:
        raise ValueError("universal Gate Bach dimensions drift")
    return basis, linear


def validate_witness(
    witness: Mapping[str, object], universal: Mapping[str, object]
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    if witness.get("schema") != "strict-cylinder-coordinate-to-covariant-symmetric-four-jet-v1":
        errors.append("witness schema")
    if witness.get("universal_table_sha256") != digest(universal):
        errors.append("witness universal-table hash")
    columns = witness.get("columns")
    expected = [(component, multiindex) for multiindex in words_through(4) for component in range(10)]
    actual: list[tuple[int, tuple[int, ...]]] = []
    if not isinstance(columns, list):
        errors.append("witness columns")
        columns = []
    for index, column in enumerate(columns):
        if not isinstance(column, Mapping):
            errors.append("malformed witness column")
            continue
        component = column.get("component")
        multiindex = tuple(column.get("multiindex", ()))
        actual.append((component, multiindex))
        entries = column.get("coordinate_entries")
        if column.get("column_id") != index or not isinstance(entries, list):
            errors.append("witness column identity")
            continue
        seen: set[int] = set()
        for basis_id, raw in entries:
            try:
                coefficient = Fraction(str(raw))
            except (ValueError, ZeroDivisionError):
                errors.append("non-rational witness coefficient")
                continue
            if not 0 <= basis_id < 700 or basis_id in seen or not coefficient:
                errors.append("witness entry identity")
            seen.add(basis_id)
            source_order = universal["input_basis"][basis_id]["order"]
            if source_order < sum(multiindex):
                errors.append("witness violates upper triangularity")
        diagonal_basis = component * 70 + words_through(4).index(multiindex)
        expected_diagonal = Fraction(1)
        for multiplicity in multiindex:
            expected_diagonal /= factorial(multiplicity)
        diagonal_values = {
            basis_id: Fraction(str(raw)) for basis_id, raw in entries
        }
        if diagonal_values.get(diagonal_basis) != expected_diagonal:
            errors.append("witness diagonal normalization")
    if actual != expected:
        errors.append("witness column order")
    checks = witness.get("exhaustive_checks", {})
    if checks != {
        "columns": 700,
        "triangular_equations": 490000,
        "construction_defects": 0,
        "arithmetic": "exact fractions",
    }:
        errors.append("witness exhaustive-check ledger")
    if witness.get("canonical_columns_sha256") != digest(columns):
        errors.append("witness column digest")
    return errors, {
        "columns": len(columns),
        "coordinate_entries": sum(len(item.get("coordinate_entries", [])) for item in columns if isinstance(item, Mapping)),
    }


def covariantized_gate_bach(
    witness: Mapping[str, object], universal: Mapping[str, object]
) -> Table:
    basis, linear = decode_universal_linear(universal)
    if witness.get("universal_table_sha256") != digest(universal):
        raise ValueError("witness/universal mismatch")
    output = {multiindex: zero_matrix(10, 10) for multiindex in words_through(4)}
    for column in witness["columns"]:
        component = int(column["component"])
        multiindex = tuple(column["multiindex"])
        values = {
            int(basis_id): Fraction(str(coefficient))
            for basis_id, coefficient in column["coordinate_entries"]
        }
        for row, terms in enumerate(linear):
            output[multiindex][row][component] = sum(
                (coefficient * values.get(basis_id, Fraction(0)) for basis_id, coefficient in terms.items()),
                Fraction(0),
            )
    return output


def compare(
    *,
    q1: Mapping[str, object],
    universal: Mapping[str, object],
    witness: Mapping[str, object],
    endpoint_payload: Mapping[str, object],
) -> tuple[list[str], dict[str, Any]]:
    errors, witness_counts = validate_witness(witness, universal)
    k_endpoint, bach_endpoint, c_endpoint, field_pairing, ghost_pairing = endpoint_data(endpoint_payload)
    maps = bridge_maps(field_pairing, ghost_pairing)
    r_gate = gate_r_tables(q1, k_endpoint)
    bach_gate = covariantized_gate_bach(witness, universal)
    n_gate = translated_gate_n_tables(r_gate, maps["W_M"])

    k_from_endpoint = {
        multiindex: multiply(matrix, maps["A_G"])
        for multiindex, matrix in k_endpoint.items()
    }
    bach_from_endpoint = {
        multiindex: multiply(inverse(maps["A_E"]), matrix)
        for multiindex, matrix in bach_endpoint.items()
    }
    transported_c_endpoint = {
        multiindex: scale(-1, matrix) for multiindex, matrix in c_endpoint.items()
    }
    n_from_endpoint = {
        multiindex: multiply(
            multiply(inverse(maps["A_I"]), matrix), maps["A_E"]
        )
        for multiindex, matrix in transported_c_endpoint.items()
    }

    arrow_defects = {
        "G_to_M": sum(k_from_endpoint[key] != r_gate[key] for key in r_gate),
        "M_to_E": sum(bach_from_endpoint[key] != bach_gate[key] for key in bach_gate),
        "E_to_I": sum(n_from_endpoint[key] != n_gate[key] for key in n_gate),
    }
    if any(arrow_defects.values()):
        errors.append("coefficientwise q1 arrow mismatch")

    field_pullback = multiply(
        multiply(transpose(maps["A_M"]), field_pairing), maps["A_E"]
    )
    original_ghost_pullback = multiply(
        multiply(transpose(maps["A_G"]), ghost_pairing), maps["A_I"]
    )
    transported_ghost_pullback = scale(-1, original_ghost_pullback)
    if field_pullback != maps["W_M"] or original_ghost_pullback != maps["W_G"]:
        errors.append("untransported numeric pairing pullback")
    if transported_ghost_pullback != scale(-1, maps["W_G"]):
        errors.append("transported pairing sign ledger")

    common = {
        "G_to_M": encode_table(r_gate),
        "M_to_E": encode_table(bach_gate),
        "E_to_I": encode_table(n_gate),
    }
    counts = {
        "witness_columns": witness_counts["columns"],
        "witness_coordinate_entries": witness_counts["coordinate_entries"],
        "arrow_multiindex_tables": len(r_gate) + len(bach_gate) + len(n_gate),
        "common_nonzero_coefficients": (
            table_nonzero_count(r_gate)
            + table_nonzero_count(bach_gate)
            + table_nonzero_count(n_gate)
        ),
        "endpoint_nonzero_coefficients": (
            table_nonzero_count(k_endpoint)
            + table_nonzero_count(bach_endpoint)
            + table_nonzero_count(c_endpoint)
        ),
    }
    return errors, {
        "maps": {key: encode_matrix(value) for key, value in maps.items()},
        "arrow_defects": arrow_defects,
        "counts": counts,
        "common_q1_sha256": digest(common),
        "gate_arrow_sha256": {
            "G_to_M": table_digest(r_gate),
            "M_to_E": table_digest(bach_gate),
            "E_to_I": table_digest(n_gate),
        },
        "endpoint_in_gate_coordinates_sha256": {
            "G_to_M": table_digest(k_from_endpoint),
            "M_to_E": table_digest(bach_from_endpoint),
            "E_to_I": table_digest(n_from_endpoint),
        },
        "pairing": {
            "field_pullback_equals_gate_canonical": field_pullback == maps["W_M"],
            "original_endpoint_ghost_pullback_equals_gate_canonical": original_ghost_pullback == maps["W_G"],
            "simultaneously_transported_causal_ghost_pullback_equals_gate_canonical": transported_ghost_pullback == maps["W_G"],
            "simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical": transported_ghost_pullback == scale(-1, maps["W_G"]),
        },
    }


def _derivative_words(multiindex: tuple[int, int, int, int]) -> tuple[tuple[int, ...], ...]:
    word = tuple(
        axis for axis, multiplicity in enumerate(multiindex) for _ in range(multiplicity)
    )
    return tuple(sorted(set(permutations(word))))


def build_exhaustive_witness(universal: Mapping[str, object]) -> dict[str, object]:
    """Construct the 700-column exact triangular witness (Tier 2, minutes)."""

    try:
        from . import cylinder_polarized_bach_evaluator as point
    except ImportError:
        import cylinder_polarized_bach_evaluator as point

    basis, _ = decode_universal_linear(universal)
    basis_index = {
        (int(item["component"]), tuple(item["word"])): int(item["index"])
        for item in basis
    }
    background = point.cylinder_background(5)
    connection = point._connection(background, point.inverse_matrix(background))

    def covariant_derivatives(tensor: dict[tuple[int, ...], Any], order: int):
        current = tensor
        tensor_rank = 2
        for _ in range(order):
            output = {}
            for axis in range(4):
                for indices in product(range(4), repeat=tensor_rank):
                    value = current[indices].derivative(axis)
                    for position, old_index in enumerate(indices):
                        value = value - point.sum_jets(
                            (
                                connection[(replacement, axis, old_index)]
                                * current[
                                    indices[:position]
                                    + (replacement,)
                                    + indices[position + 1 :]
                                ]
                                for replacement in range(4)
                            ),
                            order=value.order,
                        )
                    output[(axis,) + indices] = value
            current = output
            tensor_rank += 1
        return current

    def symmetrized_value(derivatives, pair, multiindex):
        if not sum(multiindex):
            return derivatives[pair].constant_term
        words = _derivative_words(multiindex)
        return sum(
            (derivatives[word + pair].constant_term for word in words),
            Fraction(0),
        ) / len(words)

    columns = []
    equation_count = 0
    for multiindex in words_through(4):
        for component, selected_pair in enumerate(PAIRS):
            tensor = {
                (left, right): point.Jet.zero(4)
                for left, right in product(range(4), repeat=2)
            }
            for order in range(5):
                derivatives = tensor if order == 0 else covariant_derivatives(tensor, order)
                corrections = []
                for candidate in (
                    item for item in product(range(order + 1), repeat=4) if sum(item) == order
                ):
                    for pair in PAIRS:
                        desired = Fraction(int(pair == selected_pair and candidate == multiindex))
                        correction = desired - symmetrized_value(
                            derivatives, pair, candidate
                        )
                        equation_count += 1
                        if correction:
                            corrections.append((pair, candidate, correction))
                for pair, candidate, correction in corrections:
                    coefficient = correction
                    for multiplicity in candidate:
                        coefficient /= factorial(multiplicity)
                    jet = point.Jet.coordinate_series(4, {candidate: coefficient})
                    tensor[pair] = tensor[pair] + jet
                    if pair[0] != pair[1]:
                        reverse = (pair[1], pair[0])
                        tensor[reverse] = tensor[reverse] + jet
            entries = []
            for input_component, pair in enumerate(PAIRS):
                for a_degree, b_degree, word, coefficient in tensor[pair].terms:
                    if (a_degree, b_degree) != (0, 0):
                        raise AssertionError("parameter-dependent coordinate witness")
                    basis_id = basis_index[(input_component, tuple(word))]
                    entries.append([basis_id, str(coefficient)])
            entries.sort(key=lambda item: item[0])
            columns.append(
                {
                    "column_id": len(columns),
                    "component": component,
                    "component_pair": list(selected_pair),
                    "multiindex": list(multiindex),
                    "coordinate_entries": entries,
                }
            )
    if equation_count != 490000:
        raise AssertionError(f"triangular equation count drift: {equation_count}")
    witness = {
        "schema": "strict-cylinder-coordinate-to-covariant-symmetric-four-jet-v1",
        "background": "unit conformal cylinder at the homogeneous equatorial coordinate frame",
        "map": "normalized coordinate Taylor coefficients to symmetrized covariant four-jets",
        "coefficient_field": "Q",
        "triangular_by_total_derivative_order": True,
        "universal_table_sha256": digest(universal),
        "columns": columns,
        "exhaustive_checks": {
            "columns": 700,
            "triangular_equations": equation_count,
            "construction_defects": 0,
            "arithmetic": "exact fractions",
        },
        "canonical_columns_sha256": digest(columns),
    }
    errors, _ = validate_witness(witness, universal)
    if errors:
        raise AssertionError("; ".join(errors))
    return witness
