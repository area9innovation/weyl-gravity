#!/usr/bin/env python3
"""Independent exact checker for the strict 386-component pairing table."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"

TENSOR_NAMES = ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33")
METRIC = (-1, 1, 1, 1)
CONE = (
    ("X_U", 26, 0), ("X_Eq", 40, 1), ("X_Id", 14, 2),
    ("Y_U", 26, 1), ("Y_Eq", 40, 2), ("Y_Id", 14, 3),
    ("X_Id_sharp", 14, -1), ("X_Eq_sharp", 40, 0), ("X_U_sharp", 26, 1),
    ("Y_Id_sharp", 14, -2), ("Y_Eq_sharp", 40, -1), ("Y_U_sharp", 26, 0),
)
CONE_PAIRS = (
    ("X_U", "X_U_sharp", 1), ("X_Eq", "X_Eq_sharp", -1),
    ("X_Id", "X_Id_sharp", -1), ("Y_U", "Y_U_sharp", -1),
    ("Y_Eq", "Y_Eq_sharp", -1), ("Y_Id", "Y_Id_sharp", 1),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def half_dewitt() -> list[list[Fraction]]:
    pairs = tuple((a, b) for a in range(4) for b in range(a, 4))
    tensors: list[list[list[int]]] = []
    for a, b in pairs:
        tensor = [[0] * 4 for _ in range(4)]
        tensor[a][b] = tensor[b][a] = 1
        tensors.append(tensor)
    traces = [sum(METRIC[a] * tensor[a][a] for a in range(4)) for tensor in tensors]
    result: list[list[Fraction]] = []
    for row, left in enumerate(tensors):
        values: list[Fraction] = []
        for column, right in enumerate(tensors):
            fibre = sum(METRIC[a] * METRIC[b] * left[a][b] * right[b][a] for a in range(4) for b in range(4))
            values.append(Fraction(fibre, 2) - Fraction(traces[row] * traces[column], 4))
        result.append(values)
    return result


def matrix_rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][column]
        work[rank] = [entry / divisor for entry in work[rank]]
        for row in range(len(work)):
            coefficient = work[row][column]
            if row != rank and coefficient:
                work[row] = [entry - coefficient * pivot_entry for entry, pivot_entry in zip(work[row], work[rank], strict=True)]
        rank += 1
    return rank


def expected_rows() -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    rows += [(name, -1, "ENDPOINT_G") for name in (*[f"c_{a}" for a in range(4)], "omega")]
    rows += [(f"h_{name}", 0, "ENDPOINT_M") for name in TENSOR_NAMES]
    rows += [(f"h_star_{name}", 1, "ENDPOINT_E") for name in TENSOR_NAMES]
    rows += [(name, 2, "ENDPOINT_I") for name in (*[f"c_star_{a}" for a in range(4)], "omega_star")]
    rows += [(f"eta_{a}", -1, "AUX_ETA") for a in range(4)]
    rows += [(f"f_hat_{name}", 0, "AUX_F_HAT") for name in TENSOR_NAMES]
    rows += [(f"v_{a}", 0, "AUX_V") for a in range(4)]
    rows += [(f"f_hat_star_{name}", 1, "AUX_F_HAT_STAR") for name in TENSOR_NAMES]
    rows += [(f"v_star_{a}", 1, "AUX_V_STAR") for a in range(4)]
    rows += [(f"eta_star_{a}", 2, "AUX_ETA_STAR") for a in range(4)]
    for block, dimension, degree in CONE:
        rows += [(f"{block}[{index}]", degree, "CONE_" + block.upper()) for index in range(dimension)]
    return rows


def expected_pairing(rows: list[tuple[str, int, str]]) -> dict[tuple[int, int], Fraction]:
    by_name = {name: index for index, (name, _, _) in enumerate(rows)}
    blocks: dict[str, list[int]] = {}
    for index, (_, _, block) in enumerate(rows):
        blocks.setdefault(block, []).append(index)
    expected: dict[tuple[int, int], Fraction] = {}
    cyclic = json.loads(CYCLIC.read_text())
    for item in cyclic["canonical_pairing"]["entries"]:
        expected[(by_name[item["left"]], by_name[item["right"]])] = Fraction(item["coefficient"])
    for local, coefficient in enumerate((1, -1, -1, -1)):
        left, right = blocks["AUX_ETA"][local], blocks["AUX_ETA_STAR"][local]
        expected[(left, right)], expected[(right, left)] = Fraction(coefficient), Fraction(-coefficient)
    for left_local, matrix_row in enumerate(half_dewitt()):
        for right_local, coefficient in enumerate(matrix_row):
            if coefficient:
                left, right = blocks["AUX_F_HAT"][left_local], blocks["AUX_F_HAT_STAR"][right_local]
                expected[(left, right)], expected[(right, left)] = coefficient, -coefficient
    for local, coefficient in enumerate(METRIC):
        left, right = blocks["AUX_V"][local], blocks["AUX_V_STAR"][local]
        expected[(left, right)], expected[(right, left)] = Fraction(coefficient), Fraction(-coefficient)
    for left_name, right_name, coefficient in CONE_PAIRS:
        for left, right in zip(blocks["CONE_" + left_name.upper()], blocks["CONE_" + right_name.upper()], strict=True):
            expected[(left, right)], expected[(right, left)] = Fraction(coefficient), Fraction(-coefficient)
    return expected


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    basis = value.get("component_basis", {})
    serialized_rows = basis.get("rows", [])
    expected = expected_rows()
    received = [(item.get("row_id"), item.get("degree"), item.get("block")) for item in serialized_rows]
    if received != expected or [item.get("index") for item in serialized_rows] != list(range(386)):
        errors.append("component row ordering")
    if len({item.get("row_id") for item in serialized_rows}) != 386:
        errors.append("component row uniqueness")
    if basis.get("dimension") != 386 or basis.get("algebraic_complement_dimension") != 356 or basis.get("algebraic_complement_split") != "356=36+320":
        errors.append("component dimension ledger")
    expected_degrees = {str(key): value for key, value in sorted(Counter(degree for _, degree, _ in expected).items())}
    if basis.get("degree_counts") != expected_degrees or expected_degrees != {"-2": 14, "-1": 63, "0": 116, "1": 116, "2": 63, "3": 14}:
        errors.append("degree ledger")

    pairing = value.get("pairing_serialization", {})
    actual_entries: dict[tuple[int, int], Fraction] = {}
    for item in pairing.get("entries", []):
        key = (item.get("left_index"), item.get("right_index"))
        if key in actual_entries:
            errors.append("duplicate pairing entry")
            break
        try:
            actual_entries[key] = Fraction(item.get("coefficient"))
        except (TypeError, ValueError, ZeroDivisionError):
            errors.append("invalid pairing coefficient")
            break
        if key[0] not in range(386) or key[1] not in range(386) or item.get("left") != expected[key[0]][0] or item.get("right") != expected[key[1]][0]:
            errors.append("pairing label/index mismatch")
            break
    expected_entries = expected_pairing(expected)
    if actual_entries != expected_entries:
        errors.append("exact pairing table")
    full_matrix = [[Fraction(0) for _ in expected] for _ in expected]
    for (left, right), coefficient in expected_entries.items():
        full_matrix[left][right] = coefficient
    independent_full_rank = matrix_rank(full_matrix)
    if len(expected_entries) != 410 or matrix_rank(half_dewitt()) != 10 or independent_full_rank != 386:
        errors.append("independent pairing count/rank")
    if pairing.get("rank") != independent_full_rank or pairing.get("nonzero_ordered_entry_count") != 410 or pairing.get("sector_nonzero_ordered_entry_counts") != {"endpoint": 30, "auxiliary_complement": 60, "mapping_cone_complement": 320}:
        errors.append("pairing rank/count ledger")
    if any(expected[left][1] + expected[right][1] != 1 or expected_entries.get((right, left)) != -coefficient for (left, right), coefficient in expected_entries.items()):
        errors.append("odd degree/skew identity")

    suspension = value.get("suspension_serialization", {})
    t = [-1 if block == "ENDPOINT_I" else 1 for _, _, block in expected]
    t_sharp = [-1 if block == "ENDPOINT_G" else 1 for _, _, block in expected]
    r = [left * right for left, right in zip(t_sharp, t, strict=True)]
    if suspension.get("T_diagonal") != t or suspension.get("T_sharp_gate_diagonal") != t_sharp or suspension.get("R_diagonal") != r:
        errors.append("suspension diagonal serialization")
    if any(t[left] != t_sharp[right] for left, right in expected_entries):
        errors.append("componentwise T adjoint relation")
    if (t.count(-1), t_sharp.count(-1), r.count(-1)) != (5, 5, 10) or suspension.get("R_negative") != 10:
        errors.append("suspension sign counts")

    terminology = value.get("terminology_reconciliation", {})
    if terminology.get("suspension_v1_value") != 54 or terminology.get("gate_coordinate_endpoint_pairing_nonzero_entries") != 30:
        errors.append("endpoint coordinate-count reconciliation")
    disposition = value.get("operator_adjoint_disposition", {})
    if disposition.get("projector_level_suspended_green_adjoint_replayed") is not True or disposition.get("every_component_operator_adjoint_replayed") is not False:
        errors.append("operator adjoint boundary")
    gate = value.get("gate_disposition", {})
    if gate != {"full_386_component_basis_serialized": True, "full_386_component_pairing_serialized": True, "one_common_operator_snapshot_hash_accepted": False, "classical_import_gate_a_status": "FAIL_CLOSED", "q2_d_same_carrier_established": False}:
        errors.append("Gate-A disposition")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_COMPONENT_BASIS_SERIALIZED", "STRICT_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION", "STRICT_386_COMPONENTWISE_T_ADJOINT_REPLAYED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED", "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    hashes = value.get("canonical_hashes", {})
    if hashes != {"component_basis_sha256": digest(basis), "pairing_serialization_sha256": digest(pairing), "suspension_serialization_sha256": digest(suspension)}:
        errors.append("canonical hashes")
    projection = {key: value[key] for key in ("scope", "terminology_reconciliation", "component_basis", "pairing_serialization", "suspension_serialization", "operator_adjoint_disposition", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    if digest(projection) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical result digest")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - 386 unique rows = 30 endpoint + 36 auxiliary + 320 cone/cotangent")
        print("  - exact rank-386 odd pairing has 410 ordered rational entries")
        print("  - T/T^sharp/R replay componentwise; full operator coefficient adjoints remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
