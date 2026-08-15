#!/usr/bin/env python3
"""Independent exact receiver for the strict 386 endpoint q1 bridge."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from math import factorial
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
WITNESS = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
UNIVERSAL = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
ENDPOINT_PAYLOAD = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
PAIRS = ((0,0),(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,2),(2,3),(3,3))
ZERO = (0,0,0,0)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(sorted((item for item in product(range(5), repeat=4) if sum(item) <= 4), key=lambda item: (sum(item), item)))


def zero(rows: int, columns: int):
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def eye(size: int):
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def diag(values: Sequence[int | Fraction]):
    return [[Fraction(value if row == column else 0) for column, value in enumerate(values)] for row in range(len(values))]


def trans(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def mul(left, right):
    return [[sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction()) for column in range(len(right[0]))] for row in range(len(left))]


def smul(value, matrix):
    return [[Fraction(value) * entry for entry in row] for row in matrix]


def inv(matrix):
    size = len(matrix)
    work = [row[:] + eye(size)[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular bridge matrix")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * pivot_entry for entry, pivot_entry in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def decode_endpoint(raw: Mapping[str, Any]):
    shape = raw["shape"]
    output = {}
    for item in raw["coefficients"]:
        matrix = zero(shape[0], shape[1])
        for row, column, coefficient in item["entries"]:
            matrix[row][column] = Fraction(coefficient)
        output[tuple(item["multiindex"])] = matrix
    return output


def encoded(table):
    return [
        {
            "multiindex": list(multiindex),
            "shape": [len(matrix), len(matrix[0])],
            "entries": [[row, column, str(matrix[row][column])] for row in range(len(matrix)) for column in range(len(matrix[0])) if matrix[row][column]],
        }
        for multiindex, matrix in sorted(table.items())
    ]


def table_digest(table):
    return digest(encoded(table))


def nonzero(table):
    return sum(bool(entry) for matrix in table.values() for row in matrix for entry in row)


def check(value: dict[str, Any] | None = None, witness: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    witness = json.loads(WITNESS.read_text()) if witness is None else witness
    q1 = json.loads(Q1.read_text())
    universal_result = json.loads(UNIVERSAL.read_text())
    universal = universal_result["universal_table"]
    endpoint = json.loads(ENDPOINT_PAYLOAD.read_text())
    errors: list[str] = []

    if value.get("result_id") != "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    scope = value.get("scope", {})
    if scope.get("gate_carrier_dimension") != 30 or scope.get("causal_full_dimension") != 386 or scope.get("maximum_q1_order") != 4:
        errors.append("scope dimensions/order")

    columns = witness.get("columns", [])
    expected_columns = [(component, multiindex) for multiindex in words() for component in range(10)]
    actual_columns = [(item.get("component"), tuple(item.get("multiindex", ()))) for item in columns]
    if witness.get("schema") != "strict-cylinder-coordinate-to-covariant-symmetric-four-jet-v1" or witness.get("universal_table_sha256") != digest(universal):
        errors.append("witness identity/source")
    if actual_columns != expected_columns or len(columns) != 700:
        errors.append("witness column closure/order")
    if witness.get("canonical_columns_sha256") != digest(columns):
        errors.append("witness digest")
    if witness.get("exhaustive_checks") != {"columns": 700, "triangular_equations": 490000, "construction_defects": 0, "arithmetic": "exact fractions"}:
        errors.append("witness exhaustive ledger")

    basis = universal["input_basis"]
    coefficient_dictionary = [Fraction(item) for item in universal["coefficient_dictionary"]]
    linear = [{int(basis_id): coefficient_dictionary[int(coefficient_id)] for basis_id, coefficient_id in row["linear_entries"]} for row in universal["rows"]]
    converted_bach = {multiindex: zero(10, 10) for multiindex in words()}
    coordinate_entry_count = 0
    for column_id, column in enumerate(columns):
        entries = column.get("coordinate_entries", [])
        coordinate_entry_count += len(entries)
        if column.get("column_id") != column_id:
            errors.append("witness column id")
            continue
        values = {}
        for basis_id, coefficient in entries:
            try:
                coefficient = Fraction(coefficient)
            except (ValueError, ZeroDivisionError):
                errors.append("witness non-rational coefficient")
                continue
            if basis_id in values or not 0 <= basis_id < 700 or not coefficient:
                errors.append("witness coordinate entry")
            values[basis_id] = coefficient
            if basis[basis_id]["order"] < sum(column["multiindex"]):
                errors.append("witness triangular order")
        diagonal_id = int(column["component"]) * 70 + words().index(tuple(column["multiindex"]))
        expected_diagonal = Fraction(1)
        for multiplicity in column["multiindex"]:
            expected_diagonal /= factorial(multiplicity)
        if values.get(diagonal_id) != expected_diagonal:
            errors.append("witness diagonal")
        multiindex = tuple(column["multiindex"])
        component = int(column["component"])
        for row, terms in enumerate(linear):
            converted_bach[multiindex][row][component] = sum((coefficient * values.get(basis_id, Fraction()) for basis_id, coefficient in terms.items()), Fraction())

    endpoint_q = endpoint["endpoint_Q"]
    k_endpoint = decode_endpoint(endpoint_q["K_met"])
    bach_endpoint = decode_endpoint(endpoint_q["Bach_bar"])
    c_endpoint = decode_endpoint(endpoint_q["C_met"])
    j = [list(map(Fraction, endpoint["pairings"]["J_met"][10 * row : 10 * row + 10])) for row in range(10)]
    y = [list(map(Fraction, endpoint["pairings"]["Y_met"][5 * row : 5 * row + 5])) for row in range(5)]
    w = diag([1 if left == right else 2 for left, right in PAIRS])
    ag = diag([-1, 1, 1, 1, 2])
    am = eye(10)
    ae = mul(inv(j), w)
    ai = inv(mul(trans(ag), y))

    ast = q1.get("local_q1_ast", {})
    components = {item.get("component_id"): item.get("coefficient") for item in ast.get("components", [])}
    if components != {"q1_h_c": 1, "q1_h_omega": 1, "q1_hstar_h": 1, "q1_cstar_hstar": 1, "q1_omegastar_hstar": 1}:
        errors.append("portable q1 AST components")
    r_gate = {multiindex: zero(10, 5) for multiindex in k_endpoint}
    metric = (-1, 1, 1, 1)
    for row, (left, right) in enumerate(PAIRS):
        if left == right:
            r_gate[ZERO][row][4] = Fraction(2 * metric[left])
    for axis in range(4):
        multiindex = tuple(int(index == axis) for index in range(4))
        for row, (left, right) in enumerate(PAIRS):
            for ghost in range(4):
                r_gate[multiindex][row][ghost] = Fraction(int(axis == left and ghost == right) * metric[right] + int(axis == right and ghost == left) * metric[left])
    n_gate = {multiindex: smul(-((-1) ** sum(multiindex)), mul(trans(matrix), w)) for multiindex, matrix in r_gate.items()}

    k_gate_from_endpoint = {multiindex: mul(matrix, ag) for multiindex, matrix in k_endpoint.items()}
    bach_gate_from_endpoint = {multiindex: mul(inv(ae), matrix) for multiindex, matrix in bach_endpoint.items()}
    n_gate_from_endpoint = {multiindex: mul(mul(inv(ai), smul(-1, matrix)), ae) for multiindex, matrix in c_endpoint.items()}
    defects = {
        "G_to_M": sum(r_gate[key] != k_gate_from_endpoint[key] for key in r_gate),
        "M_to_E": sum(converted_bach[key] != bach_gate_from_endpoint[key] for key in converted_bach),
        "E_to_I": sum(n_gate[key] != n_gate_from_endpoint[key] for key in n_gate),
    }
    if any(defects.values()):
        errors.append("q1 coefficient defects")

    common = {"G_to_M": encoded(r_gate), "M_to_E": encoded(converted_bach), "E_to_I": encoded(n_gate)}
    gate_hashes = {"G_to_M": table_digest(r_gate), "M_to_E": table_digest(converted_bach), "E_to_I": table_digest(n_gate)}
    endpoint_hashes = {"G_to_M": table_digest(k_gate_from_endpoint), "M_to_E": table_digest(bach_gate_from_endpoint), "E_to_I": table_digest(n_gate_from_endpoint)}
    identification = value.get("coefficientwise_identification", {})
    expected_identification = {
        "arrow_table_counts": {"G_to_M": 5, "M_to_E": 70, "E_to_I": 5, "total": 80},
        "gate_bach_input_columns": 700,
        "gate_bach_columns_matching": 700,
        "arrow_defect_counts": defects,
        "common_nonzero_coefficients": nonzero(r_gate) + nonzero(converted_bach) + nonzero(n_gate),
        "endpoint_coordinate_nonzero_coefficients": nonzero(k_endpoint) + nonzero(bach_endpoint) + nonzero(c_endpoint),
        "gate_arrow_sha256": gate_hashes,
        "endpoint_in_gate_coordinates_sha256": endpoint_hashes,
        "common_q1_sha256": digest(common),
        "same_operator_content_identified": True,
    }
    if identification != expected_identification:
        errors.append("coefficientwise identification ledger")

    field_pullback = mul(mul(trans(am), j), ae)
    original_ghost_pullback = mul(mul(trans(ag), y), ai)
    transported_ghost_pullback = smul(-1, original_ghost_pullback)
    pairing = value.get("pairing_disposition", {})
    expected_pairing_flags = {
        "field_pullback_equals_gate_canonical": field_pullback == w,
        "original_endpoint_ghost_pullback_equals_gate_canonical": original_ghost_pullback == eye(5),
        "simultaneously_transported_causal_ghost_pullback_equals_gate_canonical": transported_ghost_pullback == eye(5),
        "simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical": transported_ghost_pullback == smul(-1, eye(5)),
    }
    if {key: pairing.get(key) for key in expected_pairing_flags} != expected_pairing_flags or expected_pairing_flags != {"field_pullback_equals_gate_canonical": True, "original_endpoint_ghost_pullback_equals_gate_canonical": True, "simultaneously_transported_causal_ghost_pullback_equals_gate_canonical": False, "simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical": True}:
        errors.append("pairing sign firewall")

    flags = value.get("claim_flags", {})
    for key in ("UNIT_CYLINDER_30_ROW_ENDPOINT_Q1_COMMON_CONTENT_IDENTIFIED", "ALL_700_BACH_COLUMNS_MATCH", "TRANSPORTED_ENDPOINT_Q1_MATCHES_GATE_CANONICAL_Q1", "STRICT_386_CAUSAL_ENDPOINT_OPERATOR_LINKED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("SIMULTANEOUSLY_TRANSPORTED_CAUSAL_PAIRING_EQUALS_GATE_CANONICAL", "FULL_386_PAIRING_SERIALIZED_IN_GATE_CONVENTION", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0 or gate.get("scoped_common_minimal_q1_digest_established") is not True or gate.get("full_common_carrier_established") is not False:
        errors.append("Gate-A boundary")

    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    hashes = value.get("canonical_hashes", {})
    if hashes != {
        "basis_bridge_sha256": digest(value.get("basis_bridge")),
        "coefficientwise_identification_sha256": digest(identification),
        "pairing_disposition_sha256": digest(pairing),
    }:
        errors.append("canonical section hashes")
    digest_payload = {key: value[key] for key in ("scope", "ordered_gate_basis", "basis_bridge", "coefficientwise_identification", "pairing_disposition", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    if digest(digest_payload) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical result digest")
    return errors, {"columns": len(columns), "coordinate_entries": coordinate_entry_count, "tables": 80, "common_coefficients": expected_identification["common_nonzero_coefficients"]}


def main() -> int:
    errors, counts = check()
    print("STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['columns']}/700 Bach columns and {counts['tables']}/80 q1 tables match")
        print(f"  - common q1 has {counts['common_coefficients']} exact nonzero coefficients")
        print("  - paired causal transport differs from Gate canonical on the 5-row ghost/identity block")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
