#!/usr/bin/env python3
"""Build the exact T/A/B canonical shear in the fixed strict 386-row basis."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.md"

PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
BRIDGE = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
LOCAL_SDR = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
ENDPOINT = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
CORE_CHAIN = ROOT / "covariant_completion/certificates/curved_core_curvature_chain_map.json"
SUBSTITUTION = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"

ZERO = (0, 0, 0, 0)
Multiindex = tuple[int, int, int, int]
Matrix = list[list[Fraction]]
Table = dict[Multiindex, Matrix]
Sparse = dict[tuple[int, int], Fraction]
Operator = dict[Multiindex, Sparse]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def q(value: Fraction | int | str) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix product shape mismatch")
    return [
        [
            sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction())
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def scale(matrix: Matrix, coefficient: Fraction | int) -> Matrix:
    coefficient = Fraction(coefficient)
    return [[coefficient * value for value in row] for row in matrix]


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if not size or any(len(row) != size for row in matrix):
        raise ValueError("inverse requires a square matrix")
    work = [row[:] + identity(size)[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular pairing block")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            coefficient = work[row][column]
            work[row] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column], strict=True)
            ]
    return [row[size:] for row in work]


def matrix_equal(left: Matrix, right: Matrix) -> bool:
    return left == right


def decode_matrix(value: Sequence[Sequence[object]]) -> Matrix:
    return [[Fraction(str(entry)) for entry in row] for row in value]


def decode_table(value: Mapping[str, Any]) -> Table:
    shape = value["shape"]
    output: Table = {}
    for coefficient in value["coefficients"]:
        multiindex = tuple(coefficient["multiindex"])
        matrix = zeros(shape[0], shape[1])
        for row, column, raw in coefficient["entries"]:
            matrix[row][column] = Fraction(raw)
        output[multiindex] = matrix
    return output


def table_right(table: Table, matrix: Matrix) -> Table:
    return {multiindex: multiply(coefficient, matrix) for multiindex, coefficient in table.items()}


def table_left(matrix: Matrix, table: Table) -> Table:
    return {multiindex: multiply(matrix, coefficient) for multiindex, coefficient in table.items()}


def table_scale(table: Table, coefficient: int) -> Table:
    return {multiindex: scale(matrix, coefficient) for multiindex, matrix in table.items()}


def table_compose(left: Table, right: Table) -> Table:
    """Compose parallel tables when at least one factor is order zero."""

    output: Table = {}
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right.items():
            product = multiply(left_matrix, right_matrix)
            nonzero = any(value for row in product for value in row)
            if nonzero and sum(left_index) and sum(right_index):
                raise ValueError("curved derivative/derivative composition requires a PBW replay")
            multiindex = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            if multiindex in output:
                output[multiindex] = [
                    [old + new for old, new in zip(old_row, new_row, strict=True)]
                    for old_row, new_row in zip(output[multiindex], product, strict=True)
                ]
            else:
                output[multiindex] = product
    return output


def table_nonzero(table: Table) -> int:
    return sum(bool(value) for matrix in table.values() for row in matrix for value in row)


def sympy_table_digest(table: Table, *, columns: int | None = None) -> str:
    values = []
    for multiindex, matrix in sorted(table.items()):
        if columns is not None:
            matrix = [row + [Fraction()] * (columns - len(row)) for row in matrix]
        sympy_matrix = sp.Matrix([[sp.Rational(value.numerator, value.denominator) for value in row] for row in matrix])
        values.append(f"{multiindex}:" + sp.srepr(sp.ImmutableDenseMatrix(sympy_matrix)))
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def sympy_sparse_matrix_digest(matrix: Matrix) -> str:
    sympy_matrix = sp.Matrix([[sp.Rational(value.numerator, value.denominator) for value in row] for row in matrix])
    return hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(sympy_matrix)).encode()).hexdigest()


def blocks(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


def pairing_block(pairing: Mapping[str, Any], left: Sequence[int], right: Sequence[int]) -> Matrix:
    values = {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in pairing["pairing_serialization"]["entries"]
    }
    return [[values.get((row, column), Fraction()) for column in right] for row in left]


def forced_partner(
    primal: Table,
    omega_source: Matrix,
    omega_target: Matrix,
) -> Table:
    """Return Q=-Omega_source^-1 P^(T,formal) Omega_target."""

    source_inverse = inverse(omega_source)
    output: Table = {}
    for multiindex, matrix in primal.items():
        formal = scale(transpose(matrix), -1 if sum(multiindex) % 2 else 1)
        output[multiindex] = scale(multiply(multiply(source_inverse, formal), omega_target), -1)
    return output


def encode_table(
    table_id: str,
    source_block: str,
    target_block: str,
    source_indices: Sequence[int],
    target_indices: Sequence[int],
    table: Table,
    *,
    role: str,
    origin: str,
) -> dict[str, Any]:
    coefficients = []
    for multiindex, matrix in sorted(table.items()):
        entries = [
            [target_indices[row], source_indices[column], q(value)]
            for row in range(len(target_indices))
            for column in range(len(source_indices))
            if (value := matrix[row][column])
        ]
        coefficients.append({"multiindex": list(multiindex), "entries": entries})
    value = {
        "table_id": table_id,
        "source_block": source_block,
        "target_block": target_block,
        "source_global_indices": list(source_indices),
        "target_global_indices": list(target_indices),
        "shape": [len(target_indices), len(source_indices)],
        "maximum_order": max((sum(multiindex) for multiindex in table), default=0),
        "coefficient_multiindices": len(coefficients),
        "nonzero_coefficients": sum(len(item["entries"]) for item in coefficients),
        "orientation": "entry[target_global_index,source_global_index]",
        "role": role,
        "origin": origin,
        "coefficients": coefficients,
    }
    value["sha256"] = digest(coefficients)
    return value


def decode_encoded_table(value: Mapping[str, Any]) -> Operator:
    output: Operator = {}
    for coefficient in value["coefficients"]:
        output[tuple(coefficient["multiindex"])] = {
            (target, source): Fraction(raw)
            for target, source, raw in coefficient["entries"]
        }
    return output


def sparse_multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in by_row.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def operator_from_tables(tables: Sequence[Mapping[str, Any]], *, identity_diagonal: bool) -> Operator:
    output: Operator = {ZERO: {(index, index): Fraction(1) for index in range(386)}} if identity_diagonal else {}
    for table in tables:
        for multiindex, matrix in decode_encoded_table(table).items():
            target = output.setdefault(multiindex, {})
            for key, value in matrix.items():
                target[key] = target.get(key, Fraction()) + value
                if not target[key]:
                    target.pop(key)
    return output


def operator_multiply(left: Operator, right: Operator) -> tuple[Operator, int]:
    output: Operator = {}
    derivative_derivative = 0
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right.items():
            product = sparse_multiply(left_matrix, right_matrix)
            if not product:
                continue
            if sum(left_index) and sum(right_index):
                derivative_derivative += len(product)
                continue
            multiindex = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            target = output.setdefault(multiindex, {})
            for key, value in product.items():
                target[key] = target.get(key, Fraction()) + value
                if not target[key]:
                    target.pop(key)
    return {key: value for key, value in output.items() if value}, derivative_derivative


def identity_operator() -> Operator:
    return {ZERO: {(index, index): Fraction(1) for index in range(386)}}


def operator_defects(actual: Operator, expected: Operator) -> int:
    return sum(
        len(set(actual.get(index, {})) | set(expected.get(index, {})))
        for index in set(actual) | set(expected)
        if actual.get(index, {}) != expected.get(index, {})
    )


INPUTS = (
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed 386-row basis and exact odd pairing"),
    (BRIDGE, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "exact Gate-to-causal-endpoint coordinate bridge"),
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "fixed split unary snapshot"),
    (LOCAL_SDR, "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1", "fixed split local SDR snapshot"),
    (ENDPOINT, "pure-weyl-prolonged-metric-endpoint-coefficients-v1", "serialized endpoint graph maps and raw projections"),
    (CORE_CHAIN, "pure-weyl-curved-core-curvature-chain-map-v1", "raw T/A/B chain-square hashes"),
    (SUBSTITUTION, "pure-weyl-curvature-mapping-cylinder-substitution-v1", "coefficient-complete T/A/B substitution authority"),
    (KERNEL, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "ordered type-II shear and inverse convention"),
)


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        actual = values[path].get("result_id") or values[path].get("schema")
        if actual != expected:
            raise ValueError(f"dependency identity drift: {path}")
    pairing, bridge, q1, local_sdr, endpoint, core_chain, substitution, kernel = (
        values[path] for path, _, _ in INPUTS
    )
    if pairing["component_basis"]["dimension"] != 386 or pairing["pairing_serialization"]["rank"] != 386:
        raise ValueError("fixed pairing basis unavailable")
    if local_sdr["claim_flags"]["STRICT_386_LOCAL_SDR_IDENTITIES_REPLAYED"] is not True:
        raise ValueError("split local SDR snapshot unavailable")
    if substitution["coefficientwise_complete_prolonged_Q"] is not True:
        raise ValueError("T/A/B substitution authority unavailable")
    if kernel["degree_checks"]["every_canonical_shear_has_degree_zero"] is not True:
        raise ValueError("formal canonical-shear theorem unavailable")

    raw = endpoint["graph_inclusion_primal"]
    projection = endpoint["base_projection"]
    t_core = decode_table(raw["T_core"])
    a_core = decode_table(raw["A_core"])
    b_core = decode_table(raw["B_core"])
    p_e = decode_table(projection["p_E"])
    p_i = decode_table(projection["p_I"])
    bridge_matrices = {
        name: decode_matrix(matrix)
        for name, matrix in bridge["basis_bridge"]["matrices"].items()
    }
    if bridge_matrices["A_M"] != identity(10):
        raise ValueError("Gate/endpoint metric coordinate bridge drift")

    # Reconstruct the old 66-row attachment hashes independently.  In the
    # ordered 30+36 split, p_E and p_I become coordinate projections, so the
    # attachment has support only on the retained Gate endpoint rows.
    a_aux = table_compose(a_core, p_e)
    b_aux = table_compose(b_core, p_i)
    source_hashes = substitution["coefficient_tables"]
    raw_hashes = {
        "T_state": sympy_table_digest(t_core, columns=24),
        "A_equation": sympy_table_digest(a_aux),
        "B_identity": sympy_sparse_matrix_digest(b_aux[ZERO]),
    }
    expected_raw_hashes = {name: source_hashes[name]["sha256"] for name in raw_hashes}
    if raw_hashes != expected_raw_hashes:
        raise ValueError(f"raw T/A/B reconstruction hash drift: {raw_hashes}")

    t_gate = table_right(t_core, bridge_matrices["A_M"])
    a_gate = table_right(a_core, bridge_matrices["A_E"])
    b_gate = table_right(b_core, bridge_matrices["A_I"])

    by_block = blocks(pairing)
    primitive_specs = (
        ("T", t_gate, "ENDPOINT_M", "CONE_X_U", "ENDPOINT_E", "CONE_X_U_SHARP"),
        ("A", a_gate, "ENDPOINT_E", "CONE_X_EQ", "ENDPOINT_M", "CONE_X_EQ_SHARP"),
        ("B", b_gate, "ENDPOINT_I", "CONE_X_ID", "ENDPOINT_G", "CONE_X_ID_SHARP"),
    )
    primal_tables: dict[str, Table] = {}
    partner_tables: dict[str, Table] = {}
    elementary: list[dict[str, Any]] = []
    flat_forward: list[dict[str, Any]] = []
    for name, primal, source, target, source_partner, target_partner in primitive_specs:
        omega_source = pairing_block(pairing, by_block[source], by_block[source_partner])
        omega_target = pairing_block(pairing, by_block[target], by_block[target_partner])
        partner = forced_partner(primal, omega_source, omega_target)
        primal_tables[name] = primal
        partner_tables[name] = partner
        encoded_primal = encode_table(
            f"{name}_PRIMAL", source, target, by_block[source], by_block[target], primal,
            role=f"{name} primal graph shift", origin="endpoint graph table transported through the exact Gate coordinate bridge",
        )
        encoded_partner = encode_table(
            f"{name}_FORCED_PARTNER", target_partner, source_partner,
            by_block[target_partner], by_block[source_partner], partner,
            role=f"BV-forced cotangent partner of {name}", origin="-Omega_source^-1 P^(T,formal) Omega_target in the fixed serialized pairing",
        )
        linear_defects = 0
        for multiindex, matrix in primal.items():
            formal = scale(transpose(matrix), -1 if sum(multiindex) % 2 else 1)
            defect = [
                [left + right for left, right in zip(left_row, right_row, strict=True)]
                for left_row, right_row in zip(
                    multiply(omega_source, partner[multiindex]),
                    multiply(formal, omega_target),
                    strict=True,
                )
            ]
            linear_defects += sum(bool(value) for row in defect for value in row)
        if linear_defects:
            raise ValueError(f"{name} elementary canonicality defect")
        elementary_off_diagonal = operator_from_tables(
            (encoded_primal, encoded_partner), identity_diagonal=False
        )
        elementary_square, elementary_forbidden = operator_multiply(
            elementary_off_diagonal, elementary_off_diagonal
        )
        elementary_inverse_defects = operator_defects(elementary_square, {})
        if elementary_inverse_defects or elementary_forbidden:
            raise ValueError(f"{name} elementary inverse defect")
        elementary.append({
            "element_id": f"S_{name}",
            "application_order_forward": len(elementary) + 1,
            "forward_formula": f"I+{name}_PRIMAL+{name}_FORCED_PARTNER",
            "inverse_formula": f"I-{name}_PRIMAL-{name}_FORCED_PARTNER",
            "nilpotent_off_diagonal_square": elementary_square == {},
            "exact_inverse_defects": elementary_inverse_defects,
            "forbidden_derivative_derivative_products": elementary_forbidden,
            "BV_canonicality_identity": "S_element^(T,formal) Omega S_element=Omega",
            "BV_canonicality_defects": linear_defects,
            "primal_table": encoded_primal,
            "forced_partner_table": encoded_partner,
        })
        flat_forward.extend((encoded_primal, encoded_partner))

    # S=S_B S_A S_T has one genuine forward cross block A*(-Tsharp).
    # S^-1=S_T^-1 S_A^-1 S_B^-1 has the companion T*(-Asharp).  A and
    # Asharp are pointwise in Gate coordinates, so neither composition needs
    # a curved derivative/derivative PBW rule.
    forward_cross = table_compose(a_gate, partner_tables["T"])
    inverse_cross = table_compose(t_gate, partner_tables["A"])
    forward_cross_encoded = encode_table(
        "FORWARD_CROSS_A_TSHARP", "CONE_X_U_SHARP", "CONE_X_EQ",
        by_block["CONE_X_U_SHARP"], by_block["CONE_X_EQ"], forward_cross,
        role="ordered-product cross term A composed with the T forced partner",
        origin="exact flattening of S_B S_A S_T; left factor A is order zero in Gate coordinates",
    )
    inverse_cross_encoded = encode_table(
        "INVERSE_CROSS_T_ASHARP", "CONE_X_EQ_SHARP", "CONE_X_U",
        by_block["CONE_X_EQ_SHARP"], by_block["CONE_X_U"], inverse_cross,
        role="reverse-ordered inverse cross term T composed with the A forced partner",
        origin="exact flattening of S_T^-1 S_A^-1 S_B^-1; right factor Asharp is order zero in Gate coordinates",
    )
    flat_forward.append(forward_cross_encoded)
    flat_inverse = []
    for element in elementary:
        flat_inverse.extend((
            encode_table(
                "INVERSE_" + element["primal_table"]["table_id"],
                element["primal_table"]["source_block"], element["primal_table"]["target_block"],
                element["primal_table"]["source_global_indices"], element["primal_table"]["target_global_indices"],
                table_scale(primal_tables[element["element_id"][2:]], -1),
                role="inverse elementary primal block", origin="sign reversal of a square-zero elementary shear",
            ),
            encode_table(
                "INVERSE_" + element["forced_partner_table"]["table_id"],
                element["forced_partner_table"]["source_block"], element["forced_partner_table"]["target_block"],
                element["forced_partner_table"]["source_global_indices"], element["forced_partner_table"]["target_global_indices"],
                table_scale(partner_tables[element["element_id"][2:]], -1),
                role="inverse elementary cotangent block", origin="sign reversal of a square-zero elementary shear",
            ),
        ))
    flat_inverse.append(inverse_cross_encoded)

    forward_operator = operator_from_tables(flat_forward, identity_diagonal=True)
    inverse_operator = operator_from_tables(flat_inverse, identity_diagonal=True)
    right_product, right_forbidden = operator_multiply(forward_operator, inverse_operator)
    left_product, left_forbidden = operator_multiply(inverse_operator, forward_operator)
    right_inverse_defects = operator_defects(right_product, identity_operator())
    left_inverse_defects = operator_defects(left_product, identity_operator())
    if right_forbidden or left_forbidden or right_product != identity_operator() or left_product != identity_operator():
        raise ValueError("flattened canonical shear inverse replay failed")

    rows = pairing["component_basis"]["rows"]
    degree_defects = sum(
        rows[target]["degree"] != rows[source]["degree"]
        for table in flat_forward + flat_inverse
        for coefficient in table["coefficients"]
        for target, source, _ in coefficient["entries"]
    )
    if degree_defects:
        raise ValueError("degree-zero shear entry drift")

    transform = {
        "representation": "flattened finite parallel-coefficient symmetrized-covariant-jet tables with implicit 386-entry identity diagonal",
        "orientation": "entry[target_global_index,source_global_index]",
        "coefficient_field": "Q",
        "carrier_dimension": 386,
        "ordered_elementary_forward_circuit": ["S_T", "S_A", "S_B"],
        "ordered_elementary_inverse_circuit": ["S_B^-1", "S_A^-1", "S_T^-1"],
        "elementary_shears": elementary,
        "forward": {
            "formula": "S=S_B S_A S_T",
            "identity_diagonal_implicit": True,
            "tables": flat_forward,
            "table_count": len(flat_forward),
            "nonzero_off_diagonal_coefficients": sum(item["nonzero_coefficients"] for item in flat_forward),
            "maximum_order": max(item["maximum_order"] for item in flat_forward),
            "sha256": digest(flat_forward),
        },
        "inverse": {
            "formula": "S^-1=S_T^-1 S_A^-1 S_B^-1",
            "identity_diagonal_implicit": True,
            "tables": flat_inverse,
            "table_count": len(flat_inverse),
            "nonzero_off_diagonal_coefficients": sum(item["nonzero_coefficients"] for item in flat_inverse),
            "maximum_order": max(item["maximum_order"] for item in flat_inverse),
            "sha256": digest(flat_inverse),
        },
    }
    exact_replay = {
        "raw_T_A_B_reconstructed_from_endpoint_graph_and_projection_tables": True,
        "raw_T_A_B_hash_defects": 0,
        "raw_T_A_B_sha256": raw_hashes,
        "expected_substitution_sha256": expected_raw_hashes,
        "ordered_split_attachment_support": "retained Gate endpoint 30 only; all generalized-auxiliary 36 attachment columns vanish",
        "generalized_auxiliary_attachment_nonzero_coefficients": 0,
        "elementary_inverse_defects": sum(item["exact_inverse_defects"] for item in elementary),
        "elementary_BV_canonicality_defects": sum(item["BV_canonicality_defects"] for item in elementary),
        "full_left_inverse_defects": left_inverse_defects,
        "full_right_inverse_defects": right_inverse_defects,
        "forbidden_derivative_derivative_products_in_inverse_replay": right_forbidden + left_forbidden,
        "degree_zero_defects": degree_defects,
        "forward_cross_terms": 1,
        "inverse_cross_terms": 1,
        "cross_term_PBW_commutator_required": False,
        "cross_term_reason": "the A Gate block and its forced partner are pointwise order-zero parallel coefficient maps",
        "full_BV_canonicality": True,
        "full_BV_canonicality_proof_mode": "ordered product of three independently coefficientwise-canonical elementary type-II shears",
        "formal_kernel_transform_sha256": kernel["matrix_sha256"]["canonical_transform"],
    }
    snapshot = {
        "kind": "STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "split_local_sdr_snapshot_sha256": local_sdr["local_sdr_snapshot"]["snapshot_sha256"],
        "forward_sha256": transform["forward"]["sha256"],
        "inverse_sha256": transform["inverse"]["sha256"],
    }
    snapshot["snapshot_sha256"] = digest(snapshot)

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-canonical-shear-component-jets-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-canonical-shear-component-jets-v1.schema.json",
        "result_id": "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1",
        "result_kind": "EXACT_FIXED_BASIS_CANONICAL_GRAPH_SHEAR_COMPONENT_JET_SERIALIZATION",
        "result_state": "CANONICAL_SHEAR_SERIALIZED_GRAPH_Q1_AND_SDR_REPLAY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "b3c49286d8623aed1a7ca0b2a95f7ad3d134a77f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the authoritative T/A/B curvature-attachment shear and its inverse be serialized exactly in the same fixed 386-row Gate basis as q1 and the split local SDR, including all ordered-product cross terms?",
        "answer": "Yes. The old 66-row T_state, A_equation and B_identity tables are independently reconstructed from the serialized endpoint graph maps and the exact curved projections; their three content hashes agree with the authoritative mapping-cylinder substitution. In the ordered 30+36 split those projections become coordinate projections, so all attachment columns on the generalized-auxiliary 36 vanish. Transporting the retained endpoint through the exact Gate bridge gives three primal component-jet tables and three uniquely BV-forced cotangent partners. Each elementary type-II shear is degree zero, exactly invertible and coefficientwise canonical. The ordered product S=S_B S_A S_T contains one genuine A(-Tsharp) cross block, while its reverse-ordered inverse contains the companion T(-Asharp) block; both are explicitly flattened. Because A and Asharp are pointwise in Gate coordinates, this flattening invokes no derivative/derivative PBW composition. Direct sparse operator multiplication gives both left and right inverse with zero defects and no suppressed derivative products. This closes the canonical-shear component route, but not the conjugated graph q1/SDR replay: that successor must still handle q1/shear curved-jet compositions explicitly. No represented Green action, Gate-A acceptance, D, q2, Hadamard or QME claim is promoted.",
        "scope": {
            "theory": "strict pure-Weyl unary BV complex",
            "background": "unit conformal cylinder",
            "basis": pairing["component_basis"]["ordering"],
            "carrier_dimension": 386,
            "coordinate_transport": "split coordinates to unshifted curvature graph coordinates",
            "arithmetic": "finite exact rational component-jet tables",
        },
        "source_coordinate_reconciliation": {
            "old_auxiliary_rows": "G_aux[9]+M_aux[24]+Ebar_aux[24]+I_aux[9]",
            "fixed_ordered_rows": "Gate endpoint 30 plus generalized-auxiliary complement 36",
            "reconstruction": {
                "T_state": "T_core padded by fourteen zero f_hat/v columns",
                "A_equation": "A_core p_E",
                "B_identity": "B_core p_I; derivative p_I image is annihilated",
            },
            "raw_hashes": raw_hashes,
            "authoritative_hashes": expected_raw_hashes,
            "hash_defects": 0,
            "Gate_transport": {
                "T": "T_core A_M",
                "A": "A_core A_E",
                "B": "B_core A_I",
                "bridge_matrix_sha256": digest(bridge["basis_bridge"]["matrices"]),
            },
        },
        "canonical_transform": transform,
        "exact_replay": exact_replay,
        "canonical_shear_snapshot": snapshot,
        "support_and_foundations": {
            "maximum_differential_order": transform["forward"]["maximum_order"],
            "finite_differential_orders_only": True,
            "support_local": True,
            "compact_support_preserved": True,
            "spacelike_compact_support_preserved": True,
            "inverse_laplacian_or_curl_used": False,
            "spectral_projector_used": False,
            "Green_operator_used": False,
            "finite_exact_upper_bound": "PRA",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "analytic_green_theorem_used": False,
        },
        "gate_disposition": {
            "split_unary_snapshot_bound": True,
            "split_local_sdr_snapshot_bound": True,
            "canonical_shear_snapshot_bound": True,
            "graph_coordinate_q1_component_replay_complete": False,
            "graph_coordinate_sdr_component_replay_complete": False,
            "represented_advanced_retarded_actions_bound": False,
            "one_common_gate_a_snapshot_accepted": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED": True,
            "STRICT_386_CANONICAL_SHEAR_INVERSE_REPLAYED": True,
            "STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED": True,
            "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED": False,
            "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED": False,
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "a flattened coefficientwise replay of q1_graph=S q1_split S^-1 in the curved PBW jet algebra",
            "graph-coordinate H, inclusion, projection or all SDR identities on the same component bytes",
            "represented advanced/retarded Green actions on declared analytic spaces",
            "one accepted common Gate-A snapshot binding q1, q2, D, pairing, SDR and causal Green data",
            "local D or q2 compatibility on the common causal carrier",
            "a Hadamard state, Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Conjugate the fixed split q1 and local SDR through these exact shear bytes, using the curved symmetrized-covariant-jet/PBW composition law wherever two positive-order operators meet; independently replay nilpotency, chain maps, homotopy and cyclicity before importing any represented Green action.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_canonical_shear_component_jets.py",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.md",
    }
    value["canonical_hashes"] = {
        "source_coordinate_reconciliation_sha256": digest(value["source_coordinate_reconciliation"]),
        "canonical_transform_sha256": digest(transform),
        "exact_replay_sha256": digest(exact_replay),
        "canonical_shear_snapshot_sha256": snapshot["snapshot_sha256"],
    }
    projection_keys = (
        "scope", "source_coordinate_reconciliation", "canonical_transform", "exact_replay",
        "canonical_shear_snapshot", "support_and_foundations", "gate_disposition", "claim_flags",
        "does_not_establish", "next_gate", "canonical_hashes",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection_keys})
    return value


def render(value: Mapping[str, Any]) -> str:
    transform = value["canonical_transform"]
    replay = value["exact_replay"]
    return f"""# Strict 386-row canonical shear component jets v1

## Outcome

{value['answer']}

## Exact transform

- Forward circuit: `S_T`, then `S_A`, then `S_B`, i.e. `S=S_B S_A S_T`.
- Inverse circuit: `S_B^-1`, then `S_A^-1`, then `S_T^-1`.
- Forward off-diagonal tables: **{transform['forward']['table_count']}**, with **{transform['forward']['nonzero_off_diagonal_coefficients']}** nonzero exact coefficients.
- Inverse off-diagonal tables: **{transform['inverse']['table_count']}**, with **{transform['inverse']['nonzero_off_diagonal_coefficients']}** nonzero exact coefficients.
- Maximum order: **{transform['forward']['maximum_order']}**.
- Left/right inverse defects: **{replay['full_left_inverse_defects']} / {replay['full_right_inverse_defects']}**.
- Elementary BV-canonicality defects: **{replay['elementary_BV_canonicality_defects']}**.

## Coordinate reconciliation

The old auxiliary attachment hashes replay exactly for `T_state`,
`A_equation=A_core p_E`, and `B_identity=B_core p_I`.  In the ordered
`30+36` split the projections are coordinate projections, so the 36
generalized-auxiliary columns are exactly zero.  The retained endpoint is
then transported through the published Gate bridge before the cotangent
partners are derived from the fixed 386-row odd pairing.

## Ordered-product cross terms

The forward product contains the real block `A(-Tsharp)` and the inverse
contains `T(-Asharp)`.  They are present in the serialized tables.  `A` and
`Asharp` are order zero in Gate coordinates, so these two products require
no derivative/derivative PBW reduction.

## Boundary

This certificate supplies the shear bytes, not the graph differential or
graph SDR bytes.  Conjugating `q1` can compose two positive-order covariant
operators and therefore still requires an explicit curved PBW replay.  Green
actions and all quantum claims remain outside this result.

## Does not establish

""" + "\n".join(f"- {item}" for item in value["does_not_establish"]) + f"""

## Next gate

{value['next_gate']}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
