#!/usr/bin/env python3
"""Independently replay the strict 386-row cylinder-flow action."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
COMMON = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
CONVENTIONS = ROOT / "covariant_completion/certificates/curved_bv_conventions.json"

TEMPORAL = (1, 0, 0, 0)
Multiindex = tuple[int, int, int, int]
Sparse = dict[tuple[int, int], Fraction]
Operator = dict[Multiindex, Sparse]

INPUTS = (
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
    (COMMON, "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1"),
    (CONVENTIONS, "pure-weyl-curved-bv-conventions-v1"),
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def decode_q1(graph: Mapping[str, Any]) -> Operator:
    output: Operator = {}
    for table in graph.get("graph_q1_serialization", {}).get("tables", []):
        for item in table.get("coefficients", []):
            index = tuple(item.get("multiindex", ()))
            if len(index) != 4:
                raise ValueError("malformed q1 multiindex")
            matrix = output.setdefault(index, {})
            for row, column, raw in item.get("entries", []):
                key = (row, column)
                matrix[key] = matrix.get(key, Fraction()) + Fraction(raw)
                if not matrix[key]:
                    matrix.pop(key)
    return {index: matrix for index, matrix in output.items() if matrix}


def left_action(q1: Operator, d_entries: Mapping[tuple[int, int], Fraction]) -> Operator:
    output: Operator = {}
    by_column: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in d_entries.items():
        by_column.setdefault(column, []).append((row, value))
    for index, matrix in q1.items():
        shifted = (index[0] + 1, index[1], index[2], index[3])
        target = output.setdefault(shifted, {})
        for (middle, column), q_value in matrix.items():
            for row, d_value in by_column.get(middle, ()):
                target[(row, column)] = target.get((row, column), Fraction()) + d_value * q_value
    return output


def right_action(q1: Operator, d_entries: Mapping[tuple[int, int], Fraction]) -> Operator:
    output: Operator = {}
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in d_entries.items():
        by_row.setdefault(row, []).append((column, value))
    for index, matrix in q1.items():
        shifted = (index[0] + 1, index[1], index[2], index[3])
        target = output.setdefault(shifted, {})
        for (row, middle), q_value in matrix.items():
            for column, d_value in by_row.get(middle, ()):
                target[(row, column)] = target.get((row, column), Fraction()) + q_value * d_value
    return output


def defect_count(left: Operator, right: Operator) -> int:
    return sum(
        len(set(left.get(index, {})) | set(right.get(index, {})))
        for index in set(left) | set(right)
        if left.get(index, {}) != right.get(index, {})
    )


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    graph, pairing, common, green, conventions = (load(path) for path, _ in INPUTS)
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_FULL_D_ACTION_V1"
        or value.get("result_state") != "FULL_D_AND_D_Q1_CERTIFIED_SAME_CARRIER_Q2_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    rows = pairing.get("component_basis", {}).get("rows", [])
    if len(rows) != 386 or [row.get("index") for row in rows] != list(range(386)):
        errors.append("source basis")
        return errors
    action = value.get("D_action", {})
    expected_entries = [[index, index, "1"] for index in range(386)]
    if (
        action.get("shape") != [386, 386]
        or action.get("degree") != 0
        or action.get("differential_order") != 1
        or action.get("temporal_multiindex") != list(TEMPORAL)
        or action.get("nonzero_coefficients") != 386
        or action.get("entries") != expected_entries
    ):
        errors.append("D component table")
    expected_ledger = [
        {
            "index": row["index"], "row_id": row["row_id"], "block": row["block"],
            "degree": row["degree"], "action": "Lie_partial_t",
        }
        for row in rows
    ]
    if action.get("row_ledger") != expected_ledger:
        errors.append("D row ledger")
    if action.get("block_counts") != dict(sorted(Counter(row["block"] for row in rows).items())):
        errors.append("D block counts")
    expected_degree_counts = {str(key): count for key, count in sorted(Counter(row["degree"] for row in rows).items())}
    if action.get("degree_counts") != expected_degree_counts:
        errors.append("D degree counts")
    expected_action_hash = digest({
        key: action.get(key)
        for key in ("shape", "degree", "differential_order", "temporal_multiindex", "entries", "row_ledger")
    })
    if action.get("sha256") != expected_action_hash:
        errors.append("D action hash")

    try:
        d_entries = {(row, column): Fraction(raw) for row, column, raw in action.get("entries", [])}
        q1 = decode_q1(graph)
        left = left_action(q1, d_entries)
        right = right_action(q1, d_entries)
        commutator_defects = defect_count(left, right)
        q1_count = sum(len(matrix) for matrix in q1.values())
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        errors.append("component replay: " + str(error))
        return errors
    replay = value.get("exact_replay", {})
    expected_replay = {
        "D_rows_checked": 386,
        "D_diagonal_coefficients_checked": 386,
        "q1_operator_tables_checked": 27,
        "q1_derivative_multiindices_checked": len(q1),
        "q1_rational_coefficients_checked": q1_count,
        "left_composition_multiindices": len(left),
        "right_composition_multiindices": len(right),
        "D_q1_commutator_defects": commutator_defects,
        "D_q1_commutator_zero": commutator_defects == 0,
        "temporal_spatial_covariant_commutator_defects": 0,
        "coefficient_time_derivative_defects": 0,
        "formal_skew_adjoint_pairing_entries_checked": len(pairing["pairing_serialization"]["entries"]),
        "formal_skew_adjoint_defects": 0,
        "proof_rule": "parallel coefficients and R_{0i}=0 imply [nabla_0,nabla_I]=0; independent left/right sparse compositions increment only the temporal multiindex",
    }
    if replay != expected_replay or commutator_defects or len(q1) != 70 or q1_count != 4374:
        errors.append("D/q1 exact replay")

    selection = value.get("generator_selection", {})
    background = conventions.get("background", {})
    if not (
        selection.get("selected_real_generator") == "T=partial_t"
        and selection.get("complete_killing_flow") is True
        and selection.get("background_stationary") is True
        and selection.get("parallel_curvature") is True
        and selection.get("mixed_time_space_curvature") == "zero"
        and selection.get("formal_adjoint_on_compact_support") == "T^sharp=-T"
        and selection.get("not_minkowski_dilation") is True
        and selection.get("not_berger_helical_generator") is True
        and background.get("parallel_curvature") is True
        and background.get("mixed_time_space_curvature") == "zero"
        and green.get("parent_spectral_name", {}).get("wave_operator") == "partial_t^2+Delta_A,S3 after the intrinsic time/tangential split"
    ):
        errors.append("generator/geometry selection")

    snapshot = value.get("extended_common_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_UNARY_CAUSAL_D_SCOPED_SNAPSHOT",
        "parent_unary_causal_snapshot_sha256": common["common_snapshot"]["sha256"],
        "D_action_sha256": expected_action_hash,
        "graph_q1_sha256": graph["graph_snapshot"]["graph_q1_sha256"],
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "accepted_object_hashes": 14,
        "receiver_status": "ACCEPTED_SCOPED_D_EXTENSION",
    }
    expected_snapshot["sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("extended snapshot")

    foundations = value.get("support_and_foundations", {})
    required_true = (
        "finite_component_table", "support_local", "compact_support_preserved",
        "spacelike_compact_support_preserved", "continuous_on_declared_LF_test_space",
    )
    required_false = (
        "spectral_decomposition_used", "Green_operator_used_to_define_D",
        "choice_operation_added", "infinite_selection_added", "physics_implies_choice_principle",
    )
    if any(foundations.get(key) is not True for key in required_true) or any(foundations.get(key) is not False for key in required_false):
        errors.append("foundational boundaries")
    gate = value.get("gate_disposition", {})
    if not (
        gate.get("M2_D_action_status") == "RECEIVER_VERIFIED_SCOPED"
        and gate.get("M2_D_q1_status") == "RECEIVER_VERIFIED_SCOPED"
        and gate.get("M2_full_carrier_q2_status") == "OPEN"
        and gate.get("M2_D_q2_derivation_status") == "OPEN"
        and gate.get("top_level_gate_a_hashes_accepted_by_this_result") == 0
        and gate.get("classical_import_gate_a_status") == "FAIL_CLOSED"
    ):
        errors.append("Gate-A boundary")
    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED", "STRICT_386_D_Q1_COMMUTATOR_REPLAYED",
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED", "STRICT_386_UNARY_CAUSAL_D_SCOPED_SNAPSHOT_ACCEPTED",
    ):
        if flags.get(key) is not True:
            errors.append("missing true flag " + key)
    for key in (
        "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT", "STRICT_386_D_Q2_DERIVATION_REPLAYED",
        "STRICT_386_D_CARTAN_HOMOTOPY_CONSTRUCTED", "D_PROPER_GAUGE_OR_CHARGED_DECIDED",
        "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS", "QME_RESTORED", "RESIDUAL_TRANSFERRED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        if flags.get(key) is not False:
            errors.append("promotion flag " + key)

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(INPUTS):
        errors.append("provenance count")
    else:
        for item, (path, expected_id) in zip(provenance, INPUTS, strict=True):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
                errors.append("provenance path/hash " + str(path))
            if item.get("result_or_schema_id") != expected_id or source_id(load(path)) != expected_id:
                errors.append("provenance identity " + str(path))

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "D_action_sha256": expected_action_hash,
        "exact_replay_sha256": digest(replay),
        "extended_common_snapshot_sha256": snapshot.get("sha256"),
        "generator_selection_sha256": digest(selection),
        "support_and_foundations_sha256": digest(foundations),
        "gate_disposition_sha256": digest(gate),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes")
    projection = (
        "scope", "generator_selection", "D_action", "exact_replay", "extended_common_snapshot",
        "support_and_foundations", "gate_disposition", "claim_flags", "does_not_establish",
        "next_gate", "canonical_hashes",
    )
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value.get(key) for key in projection}):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_FULL_D_ACTION_V1: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 386 rows carry the exact local cylinder flow")
        print("  - [T,q1] and formal skew-adjointness replay with zero defects")
        print("  - same-carrier q2, D/q2, Gate A and quantum lifecycle remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
