#!/usr/bin/env python3
"""Independently replay the strict 386-row canonical shear certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
BRIDGE = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
LOCAL_SDR = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
ENDPOINT = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
SUBSTITUTION = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"

ZERO = (0, 0, 0, 0)
Multiindex = tuple[int, int, int, int]
Matrix = list[list[Fraction]]
Table = dict[Multiindex, Matrix]
Sparse = dict[tuple[int, int], Fraction]
Operator = dict[Multiindex, Sparse]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shape mismatch")
    return [
        [
            sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction())
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def scale(matrix: Matrix, coefficient: int | Fraction) -> Matrix:
    coefficient = Fraction(coefficient)
    return [[coefficient * entry for entry in row] for row in matrix]


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if not size or any(len(row) != size for row in matrix):
        raise ValueError("non-square inverse")
    work = [row[:] + identity(size)[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [
                    entry - coefficient * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[column], strict=True)
                ]
    return [row[size:] for row in work]


def decode_matrix(value: Sequence[Sequence[object]]) -> Matrix:
    return [[Fraction(str(entry)) for entry in row] for row in value]


def decode_source_table(value: Mapping[str, Any]) -> Table:
    rows, columns = value["shape"]
    output: Table = {}
    for item in value["coefficients"]:
        matrix = zeros(rows, columns)
        for row, column, raw in item["entries"]:
            matrix[row][column] = Fraction(raw)
        output[tuple(item["multiindex"])] = matrix
    return output


def right(table: Table, matrix: Matrix) -> Table:
    return {multiindex: multiply(coefficient, matrix) for multiindex, coefficient in table.items()}


def compose(left: Table, right_table: Table) -> Table:
    output: Table = {}
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right_table.items():
            product = multiply(left_matrix, right_matrix)
            nonzero = any(entry for row in product for entry in row)
            if nonzero and sum(left_index) and sum(right_index):
                raise ValueError("uncertified derivative/derivative composition")
            multiindex = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            if multiindex not in output:
                output[multiindex] = product
            else:
                output[multiindex] = [
                    [old + new for old, new in zip(old_row, new_row, strict=True)]
                    for old_row, new_row in zip(output[multiindex], product, strict=True)
                ]
    return output


def table_scale(table: Table, coefficient: int) -> Table:
    return {multiindex: scale(matrix, coefficient) for multiindex, matrix in table.items()}


def sympy_table_hash(table: Table, padded_columns: int | None = None) -> str:
    parts = []
    for multiindex, matrix in sorted(table.items()):
        if padded_columns is not None:
            matrix = [row + [Fraction()] * (padded_columns - len(row)) for row in matrix]
        dense = sp.Matrix([[sp.Rational(value.numerator, value.denominator) for value in row] for row in matrix])
        parts.append(f"{multiindex}:" + sp.srepr(sp.ImmutableDenseMatrix(dense)))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def sympy_sparse_hash(matrix: Matrix) -> str:
    value = sp.Matrix([[sp.Rational(entry.numerator, entry.denominator) for entry in row] for row in matrix])
    return hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(value)).encode()).hexdigest()


def blocks(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


def pairing_block(pairing: Mapping[str, Any], left: Sequence[int], right_indices: Sequence[int]) -> Matrix:
    entries = {
        (item["left_index"], item["right_index"]): Fraction(item["coefficient"])
        for item in pairing["pairing_serialization"]["entries"]
    }
    return [[entries.get((row, column), Fraction()) for column in right_indices] for row in left]


def partner(table: Table, omega_source: Matrix, omega_target: Matrix) -> Table:
    omega_inverse = inverse(omega_source)
    return {
        multiindex: scale(
            multiply(
                multiply(
                    omega_inverse,
                    scale(transpose(matrix), -1 if sum(multiindex) % 2 else 1),
                ),
                omega_target,
            ),
            -1,
        )
        for multiindex, matrix in table.items()
    }


def expected_sparse(table: Table, source: Sequence[int], target: Sequence[int]) -> Operator:
    return {
        multiindex: {
            (target[row], source[column]): value
            for row in range(len(target))
            for column in range(len(source))
            if (value := matrix[row][column])
        }
        for multiindex, matrix in table.items()
    }


def decode_result_table(value: Mapping[str, Any]) -> Operator:
    output: Operator = {}
    for item in value.get("coefficients", []):
        matrix: Sparse = {}
        for target, source, raw in item.get("entries", []):
            key = (target, source)
            coefficient = Fraction(raw)
            if key in matrix or not coefficient:
                raise ValueError("duplicate or zero component coefficient")
            matrix[key] = coefficient
        multiindex = tuple(item.get("multiindex", ()))
        if len(multiindex) != 4 or multiindex in output:
            raise ValueError("duplicate or malformed multiindex")
        output[multiindex] = matrix
    return output


def sparse_multiply(left: Sparse, right: Sparse) -> Sparse:
    middle_rows: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        middle_rows.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in middle_rows.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def assemble(tables: Sequence[Mapping[str, Any]], coefficient: int = 1) -> Operator:
    output: Operator = {ZERO: {(index, index): Fraction(1) for index in range(386)}}
    for table in tables:
        for multiindex, matrix in decode_result_table(table).items():
            target = output.setdefault(multiindex, {})
            for key, value in matrix.items():
                target[key] = target.get(key, Fraction()) + coefficient * value
                if not target[key]:
                    target.pop(key)
    return output


def operator_product(left: Operator, right_operator: Operator) -> tuple[Operator, int]:
    output: Operator = {}
    forbidden = 0
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right_operator.items():
            product = sparse_multiply(left_matrix, right_matrix)
            if not product:
                continue
            if sum(left_index) and sum(right_index):
                forbidden += len(product)
                continue
            multiindex = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            target = output.setdefault(multiindex, {})
            for key, value in product.items():
                target[key] = target.get(key, Fraction()) + value
                if not target[key]:
                    target.pop(key)
    return {key: value for key, value in output.items() if value}, forbidden


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    pairing, bridge, q1, local_sdr, endpoint, substitution = (
        load(path) for path in (PAIRING, BRIDGE, Q1, LOCAL_SDR, ENDPOINT, SUBSTITUTION)
    )
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    source = endpoint["graph_inclusion_primal"]
    projection = endpoint["base_projection"]
    try:
        t_core = decode_source_table(source["T_core"])
        a_core = decode_source_table(source["A_core"])
        b_core = decode_source_table(source["B_core"])
        p_e = decode_source_table(projection["p_E"])
        p_i = decode_source_table(projection["p_I"])
        source_table_hashes = {
            "T_core": sympy_table_hash(t_core),
            "A_core": sympy_table_hash(a_core),
            "B_core": sympy_table_hash(b_core),
            "p_E": sympy_table_hash(p_e),
            "p_I": sympy_table_hash(p_i),
        }
        for name, item in (
            ("T_core", source["T_core"]), ("A_core", source["A_core"]),
            ("B_core", source["B_core"]), ("p_E", projection["p_E"]),
            ("p_I", projection["p_I"]),
        ):
            if source_table_hashes[name] != item["sha256"]:
                errors.append("source table hash " + name)
        a_aux = compose(a_core, p_e)
        b_aux = compose(b_core, p_i)
        raw_hashes = {
            "T_state": sympy_table_hash(t_core, 24),
            "A_equation": sympy_table_hash(a_aux),
            "B_identity": sympy_sparse_hash(b_aux[ZERO]),
        }
    except (KeyError, ValueError, TypeError) as error:
        errors.append("source reconstruction: " + str(error))
        return errors
    expected_raw = {name: substitution["coefficient_tables"][name]["sha256"] for name in raw_hashes}
    if raw_hashes != expected_raw:
        errors.append("raw T/A/B authority hash")

    # Recompute the Gate bridge from the endpoint pairings instead of using
    # the matrices copied into the result.
    j_flat = endpoint["pairings"]["J_met"]
    y_flat = endpoint["pairings"]["Y_met"]
    j_met = decode_matrix([j_flat[10 * row:10 * row + 10] for row in range(10)])
    y_met = decode_matrix([y_flat[5 * row:5 * row + 5] for row in range(5)])
    weights = [[Fraction((1 if row == column and row in (0, 4, 7, 9) else 2 if row == column else 0)) for column in range(10)] for row in range(10)]
    a_g = [[Fraction((-1 if row == 0 else 2 if row == 4 else 1) if row == column else 0) for column in range(5)] for row in range(5)]
    computed_bridge = {
        "A_G": a_g,
        "A_M": identity(10),
        "A_E": multiply(inverse(j_met), weights),
        "A_I": inverse(multiply(transpose(a_g), y_met)),
        "W_M": weights,
        "W_G": identity(5),
    }
    serialized_bridge = {name: decode_matrix(matrix) for name, matrix in bridge["basis_bridge"]["matrices"].items()}
    if computed_bridge != serialized_bridge:
        errors.append("independent Gate bridge")

    primal = {
        "T": right(t_core, computed_bridge["A_M"]),
        "A": right(a_core, computed_bridge["A_E"]),
        "B": right(b_core, computed_bridge["A_I"]),
    }
    by_block = blocks(pairing)
    specs = {
        "T": ("ENDPOINT_M", "CONE_X_U", "ENDPOINT_E", "CONE_X_U_SHARP"),
        "A": ("ENDPOINT_E", "CONE_X_EQ", "ENDPOINT_M", "CONE_X_EQ_SHARP"),
        "B": ("ENDPOINT_I", "CONE_X_ID", "ENDPOINT_G", "CONE_X_ID_SHARP"),
    }
    partners: dict[str, Table] = {}
    expected: dict[str, tuple[str, str, Table]] = {}
    canonical_defects = 0
    for name, (source_block, target_block, source_partner, target_partner) in specs.items():
        omega_source = pairing_block(pairing, by_block[source_block], by_block[source_partner])
        omega_target = pairing_block(pairing, by_block[target_block], by_block[target_partner])
        partners[name] = partner(primal[name], omega_source, omega_target)
        expected[f"{name}_PRIMAL"] = (source_block, target_block, primal[name])
        expected[f"{name}_FORCED_PARTNER"] = (target_partner, source_partner, partners[name])
        for multiindex, matrix in primal[name].items():
            defect = [
                [a + b for a, b in zip(left_row, right_row, strict=True)]
                for left_row, right_row in zip(
                    multiply(omega_source, partners[name][multiindex]),
                    multiply(scale(transpose(matrix), -1 if sum(multiindex) % 2 else 1), omega_target),
                    strict=True,
                )
            ]
            canonical_defects += sum(bool(entry) for row in defect for entry in row)
    forward_cross = compose(primal["A"], partners["T"])
    inverse_cross = compose(primal["T"], partners["A"])
    expected["FORWARD_CROSS_A_TSHARP"] = ("CONE_X_U_SHARP", "CONE_X_EQ", forward_cross)
    expected["INVERSE_CROSS_T_ASHARP"] = ("CONE_X_EQ_SHARP", "CONE_X_U", inverse_cross)
    for name in ("T", "A", "B"):
        source_block, target_block, _, _ = specs[name]
        expected[f"INVERSE_{name}_PRIMAL"] = (source_block, target_block, table_scale(primal[name], -1))
        _, _, source_partner, target_partner = specs[name]
        expected[f"INVERSE_{name}_FORCED_PARTNER"] = (target_partner, source_partner, table_scale(partners[name], -1))

    transform = value.get("canonical_transform", {})
    elementary = transform.get("elementary_shears", [])
    exact_identity = {ZERO: {(index, index): Fraction(1) for index in range(386)}}
    if [item.get("element_id") for item in elementary] != ["S_T", "S_A", "S_B"]:
        errors.append("elementary circuit inventory")
    result_tables = []
    for element in elementary:
        element_tables = (element.get("primal_table", {}), element.get("forced_partner_table", {}))
        result_tables.extend(element_tables)
        try:
            element_forward = assemble(element_tables)
            element_inverse = assemble(element_tables, -1)
            element_left, element_left_forbidden = operator_product(element_inverse, element_forward)
            element_right, element_right_forbidden = operator_product(element_forward, element_inverse)
        except (ValueError, TypeError) as error:
            errors.append(f"elementary replay: {error}")
            element_left, element_right = {}, {}
            element_left_forbidden = element_right_forbidden = 1
        if (
            element.get("nilpotent_off_diagonal_square") is not True
            or element.get("exact_inverse_defects") != 0
            or element.get("forbidden_derivative_derivative_products") != 0
            or element.get("BV_canonicality_defects") != 0
            or element_left != exact_identity
            or element_right != exact_identity
            or element_left_forbidden
            or element_right_forbidden
        ):
            errors.append("elementary replay metadata")
    forward_tables = transform.get("forward", {}).get("tables", [])
    inverse_tables = transform.get("inverse", {}).get("tables", [])
    result_tables.extend(forward_tables[-1:] + inverse_tables)
    seen_ids: set[str] = set()
    rows = pairing["component_basis"]["rows"]
    for item in result_tables:
        table_id = item.get("table_id")
        if table_id in seen_ids:
            continue
        seen_ids.add(table_id)
        if table_id not in expected:
            errors.append("unexpected table " + str(table_id))
            continue
        source_block, target_block, expected_table = expected[table_id]
        source_indices, target_indices = by_block[source_block], by_block[target_block]
        try:
            actual = decode_result_table(item)
        except (ValueError, TypeError) as error:
            errors.append(f"{table_id} decoding: {error}")
            continue
        if actual != expected_sparse(expected_table, source_indices, target_indices):
            errors.append(table_id + " coefficients")
        coefficient_rows = item.get("coefficients", [])
        if (
            item.get("source_block") != source_block
            or item.get("target_block") != target_block
            or item.get("source_global_indices") != source_indices
            or item.get("target_global_indices") != target_indices
            or item.get("shape") != [len(target_indices), len(source_indices)]
            or item.get("coefficient_multiindices") != len(expected_table)
            or item.get("maximum_order") != max(sum(index) for index in expected_table)
            or item.get("nonzero_coefficients") != sum(len(matrix) for matrix in actual.values())
            or item.get("sha256") != digest(coefficient_rows)
        ):
            errors.append(table_id + " metadata/hash")
        for coefficient in coefficient_rows:
            for target, source_index, _ in coefficient.get("entries", []):
                if rows[target]["degree"] != rows[source_index]["degree"]:
                    errors.append(table_id + " degree")
                    break
    if seen_ids != set(expected):
        errors.append("flat table inventory")
    if not elementary or not forward_tables:
        errors.append("forward table ordering")
    else:
        expected_forward = [
            elementary[0]["primal_table"],
            elementary[0]["forced_partner_table"],
            elementary[1]["primal_table"],
            elementary[1]["forced_partner_table"],
            elementary[2]["primal_table"],
            elementary[2]["forced_partner_table"],
            forward_tables[-1],
        ]
        if forward_tables != expected_forward:
            errors.append("forward table ordering")
    if transform.get("ordered_elementary_forward_circuit") != ["S_T", "S_A", "S_B"] or transform.get("ordered_elementary_inverse_circuit") != ["S_B^-1", "S_A^-1", "S_T^-1"]:
        errors.append("circuit order")
    if transform.get("forward", {}).get("sha256") != digest(forward_tables) or transform.get("inverse", {}).get("sha256") != digest(inverse_tables):
        errors.append("transform table digest")

    try:
        forward_operator = assemble(forward_tables)
        inverse_operator = assemble(inverse_tables)
        left, left_forbidden = operator_product(inverse_operator, forward_operator)
        right_product, right_forbidden = operator_product(forward_operator, inverse_operator)
    except (ValueError, TypeError) as error:
        errors.append("operator replay: " + str(error))
        left, right_product, left_forbidden, right_forbidden = {}, {}, 1, 1
    if left != exact_identity or right_product != exact_identity or left_forbidden or right_forbidden:
        errors.append("full inverse replay")

    replay = value.get("exact_replay", {})
    if (
        replay.get("raw_T_A_B_sha256") != raw_hashes
        or replay.get("expected_substitution_sha256") != expected_raw
        or replay.get("raw_T_A_B_hash_defects") != 0
        or replay.get("generalized_auxiliary_attachment_nonzero_coefficients") != 0
        or replay.get("elementary_BV_canonicality_defects") != canonical_defects
        or replay.get("full_left_inverse_defects") != 0
        or replay.get("full_right_inverse_defects") != 0
        or replay.get("forbidden_derivative_derivative_products_in_inverse_replay") != 0
        or replay.get("degree_zero_defects") != 0
        or replay.get("forward_cross_terms") != 1
        or replay.get("inverse_cross_terms") != 1
        or replay.get("cross_term_PBW_commutator_required") is not False
        or replay.get("full_BV_canonicality") is not True
    ):
        errors.append("exact replay projection")

    snapshot = value.get("canonical_shear_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "split_local_sdr_snapshot_sha256": local_sdr["local_sdr_snapshot"]["snapshot_sha256"],
        "forward_sha256": transform.get("forward", {}).get("sha256"),
        "inverse_sha256": transform.get("inverse", {}).get("sha256"),
    }
    expected_snapshot["snapshot_sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("snapshot binding")

    support = value.get("support_and_foundations", {})
    if support.get("maximum_differential_order") != 3 or support.get("support_local") is not True or support.get("Green_operator_used") is not False or support.get("finite_exact_upper_bound") != "PRA" or support.get("choice_operation_added") is not False:
        errors.append("support/foundational boundary")
    gate = value.get("gate_disposition", {})
    if gate.get("canonical_shear_snapshot_bound") is not True or gate.get("graph_coordinate_q1_component_replay_complete") is not False or gate.get("graph_coordinate_sdr_component_replay_complete") is not False or gate.get("represented_advanced_retarded_actions_bound") is not False or gate.get("one_common_gate_a_snapshot_accepted") is not False or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED", "STRICT_386_CANONICAL_SHEAR_INVERSE_REPLAYED", "STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED", "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED", "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED", "CLASSICAL_IMPORT_GATE_PASSED", "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    reconciliation = value.get("source_coordinate_reconciliation", {})
    if reconciliation.get("raw_hashes") != raw_hashes or reconciliation.get("authoritative_hashes") != expected_raw or reconciliation.get("hash_defects") != 0 or reconciliation.get("Gate_transport", {}).get("bridge_matrix_sha256") != digest(bridge["basis_bridge"]["matrices"]):
        errors.append("source reconciliation projection")
    canonical = value.get("canonical_hashes", {})
    expected_canonical = {
        "source_coordinate_reconciliation_sha256": digest(reconciliation),
        "canonical_transform_sha256": digest(transform),
        "exact_replay_sha256": digest(replay),
        "canonical_shear_snapshot_sha256": snapshot.get("snapshot_sha256"),
    }
    if canonical != expected_canonical:
        errors.append("canonical hashes")
    projection_keys = (
        "scope", "source_coordinate_reconciliation", "canonical_transform", "exact_replay",
        "canonical_shear_snapshot", "support_and_foundations", "gate_disposition", "claim_flags",
        "does_not_establish", "next_gate", "canonical_hashes",
    )
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value[key] for key in projection_keys}):
        errors.append("canonical digest")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append("provenance " + item.get("path", ""))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
