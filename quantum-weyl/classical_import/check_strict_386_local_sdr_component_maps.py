#!/usr/bin/env python3
"""Independently replay the strict 386-row split local SDR certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
AUXILIARY = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
ZERO = (0, 0, 0, 0)
Sparse = dict[tuple[int, int], Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [values[:] + [Fraction(index == column) for column in range(size)] for index, values in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular doublet block")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * source for entry, source in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in by_row.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def add(left: Sparse, right: Sparse, coefficient: int = 1) -> Sparse:
    output = dict(left)
    for key, value in right.items():
        output[key] = output.get(key, Fraction()) + coefficient * value
    return {key: value for key, value in output.items() if value}


def decode(item: Mapping[str, Any]) -> Sparse:
    output: Sparse = {}
    for entry in item.get("entries", []):
        key = (entry.get("target"), entry.get("source"))
        try:
            value = Fraction(entry.get("coefficient"))
        except (TypeError, ValueError, ZeroDivisionError):
            raise ValueError("non-rational map entry") from None
        if key in output or not value:
            raise ValueError("duplicate or zero map entry")
        output[key] = value
    return output


def q_tables(q1: Mapping[str, Any]) -> dict[tuple[int, int, int, int], Sparse]:
    output: dict[tuple[int, int, int, int], Sparse] = {}
    for table in q1["q1_serialization"]["tables"]:
        for coefficient in table["coefficients"]:
            matrix = output.setdefault(tuple(coefficient["multiindex"]), {})
            for target, source, raw in coefficient["entries"]:
                if (target, source) in matrix:
                    raise ValueError("overlapping q1 entry")
                matrix[target, source] = Fraction(raw)
    return output


def expected_h(q1: Mapping[str, Any], pairing: Mapping[str, Any]) -> Sparse:
    q0 = q_tables(q1)[ZERO]
    output: Sparse = {}
    for source_start, target_start, size in ((30, 44, 4), (34, 48, 10), (58, 62, 4)):
        block = [[q0.get((target_start + row, source_start + column), Fraction()) for column in range(size)] for row in range(size)]
        for target_local, row in enumerate(inverse(block)):
            for source_local, value in enumerate(row):
                if value:
                    output[source_start + target_local, target_start + source_local] = value
    blocks: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        blocks.setdefault(row["block"], []).append(row["index"])
    for source_block, target_block in (
        ("CONE_Y_U", "CONE_X_U"),
        ("CONE_Y_EQ", "CONE_X_EQ"),
        ("CONE_Y_ID", "CONE_X_ID"),
        ("CONE_X_U_SHARP", "CONE_Y_U_SHARP"),
        ("CONE_X_EQ_SHARP", "CONE_Y_EQ_SHARP"),
        ("CONE_X_ID_SHARP", "CONE_Y_ID_SHARP"),
    ):
        for source, target in zip(blocks[source_block], blocks[target_block], strict=True):
            output[target, source] = Fraction(1)
    return output


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    q1, pairing = load(Q1), load(PAIRING)
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    rows = pairing["component_basis"]["rows"]
    maps = value.get("component_maps", {})
    expected_meta = {
        "H_alg": ([386, 386], -1, 190),
        "P_alg": ([386, 386], 0, 356),
        "P_end": ([386, 386], 0, 30),
        "i_end": ([386, 30], 0, 30),
        "p_end": ([30, 386], 0, 30),
    }
    if set(maps) != set(expected_meta):
        errors.append("map inventory")
    decoded: dict[str, Sparse] = {}
    for name, (shape, degree, count) in expected_meta.items():
        item = maps.get(name, {})
        try:
            decoded[name] = decode(item)
        except ValueError as error:
            errors.append(f"{name} decoding: {error}")
            decoded[name] = {}
        if item.get("map_id") != name or item.get("shape") != shape or item.get("degree") != degree or item.get("nonzero_entries") != count or len(item.get("entries", [])) != count:
            errors.append(name + " metadata")
        if item.get("sha256") != digest({"shape": shape, "degree": degree, "entries": item.get("entries", [])}):
            errors.append(name + " digest")
        for entry in item.get("entries", []):
            target, source = entry.get("target"), entry.get("source")
            if not isinstance(target, int) or not isinstance(source, int) or target < 0 or source < 0 or target >= shape[0] or source >= shape[1]:
                errors.append(name + " index")
                break
            target_global = target
            source_global = source
            if name == "i_end":
                source_global = source
            elif name == "p_end":
                target_global = target
            if entry.get("target_id") != rows[target_global]["row_id"] or entry.get("source_id") != rows[source_global]["row_id"]:
                errors.append(name + " row identity")
                break

    try:
        independent_h = expected_h(q1, pairing)
    except (KeyError, ValueError, TypeError) as error:
        errors.append("independent H reconstruction: " + str(error))
        independent_h = {}
    if decoded.get("H_alg") != independent_h:
        errors.append("H_alg coefficient reconstruction")
    expected_p_alg = {(index, index): Fraction(1) for index in range(30, 386)}
    expected_p_end = {(index, index): Fraction(1) for index in range(30)}
    expected_endpoint = {(index, index): Fraction(1) for index in range(30)}
    if decoded.get("P_alg") != expected_p_alg or decoded.get("P_end") != expected_p_end:
        errors.append("projector coefficients")
    if decoded.get("i_end") != expected_endpoint or decoded.get("p_end") != expected_endpoint:
        errors.append("endpoint inclusion/projection coefficients")

    q_by_multiindex = q_tables(q1)
    h = decoded.get("H_alg", {})
    homotopy_defects = 0
    for multiindex, matrix in q_by_multiindex.items():
        expected = expected_p_alg if multiindex == ZERO else {}
        homotopy_defects += len(add(add(multiply(matrix, h), multiply(h, matrix)), expected, -1))
    cross = sum((target < 30) != (source < 30) for matrix in q_by_multiindex.values() for target, source in matrix)
    if homotopy_defects:
        errors.append("qH+Hq replay")
    if multiply(h, h) or multiply(h, expected_p_end) or multiply(expected_p_end, h):
        errors.append("normalized H side conditions")
    if add(expected_p_alg, expected_p_end) != {(index, index): Fraction(1) for index in range(386)} or multiply(expected_p_alg, expected_p_end):
        errors.append("complementary projector replay")

    omega = {(entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"]) for entry in pairing["pairing_serialization"]["entries"]}
    h_transpose = {(column, row): coefficient for (row, column), coefficient in h.items()}
    omega_h = multiply(omega, h)
    d_omega_h = {(row, column): (-1 if rows[row]["degree"] % 2 else 1) * coefficient for (row, column), coefficient in omega_h.items()}
    cyclic_defects = len(add(multiply(h_transpose, omega), d_omega_h, -1))
    replay = value.get("exact_replay", {})
    expected_true = (
        "qH_plus_Hq_equals_P_alg", "p_end_i_end_identity", "i_end_p_end_equals_P_end",
        "q_i_end_equals_i_end_q_endpoint", "p_end_q_equals_q_endpoint_p_end",
        "P_alg_plus_P_end_identity", "P_alg_P_end_zero", "projectors_idempotent",
        "projectors_commute_with_q", "H_alg_squared_zero", "H_alg_i_end_zero",
        "p_end_H_alg_zero", "H_alg_P_end_and_P_end_H_alg_zero",
    )
    if any(replay.get(key) is not True for key in expected_true) or replay.get("qH_plus_Hq_defects") != homotopy_defects or replay.get("derivative_multiindices_checked") != len(q_by_multiindex) or replay.get("H_alg_cyclicity_defects") != cyclic_defects or replay.get("cross_endpoint_complement_q_entries") != cross:
        errors.append("exact replay projection")
    if cyclic_defects or cross:
        errors.append("cyclicity or endpoint split replay")

    snapshot = value.get("local_sdr_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_SPLIT_LOCAL_SDR_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "map_sha256": {name: maps.get(name, {}).get("sha256") for name in maps},
    }
    expected_snapshot["snapshot_sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("local SDR snapshot binding")

    boundary = value.get("coordinate_transport_boundary", {})
    if boundary.get("split_SDR_complete") is not True or boundary.get("T_A_B_canonical_shear_serialized") is not False or boundary.get("unshifted_curvature_graph_SDR_snapshot_complete") is not False:
        errors.append("coordinate/shear boundary")
    support = value.get("support_and_foundations", {})
    if support.get("maximum_differential_order") != 0 or support.get("support_local") is not True or support.get("finite_exact_upper_bound") != "PRA" or support.get("choice_operation_added") is not False or support.get("analytic_green_theorem_used") is not False:
        errors.append("support/foundational boundary")
    gate = value.get("gate_disposition", {})
    if gate.get("split_local_sdr_snapshot_bound") is not True or gate.get("canonical_shear_snapshot_bound") is not False or gate.get("represented_advanced_retarded_actions_bound") is not False or gate.get("one_common_gate_a_snapshot_accepted") is not False or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_SPLIT_LOCAL_SDR_COMPONENT_MAPS_SERIALIZED", "STRICT_386_LOCAL_SDR_IDENTITIES_REPLAYED", "STRICT_386_LOCAL_SDR_CYCLICITY_REPLAYED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED", "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED", "CLASSICAL_IMPORT_GATE_PASSED", "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    canonical = value.get("canonical_hashes", {})
    if canonical != {"component_maps_sha256": digest(maps), "exact_replay_sha256": digest(replay), "local_sdr_snapshot_sha256": snapshot.get("snapshot_sha256")}:
        errors.append("canonical hashes")
    projection = {key: value[key] for key in ("scope", "component_maps", "exact_replay", "local_sdr_snapshot", "coordinate_transport_boundary", "support_and_foundations", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    if value.get("independent_checker", {}).get("expected_digest") != digest(projection):
        errors.append("canonical digest")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append("provenance " + item.get("path", ""))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 190-entry H_alg and endpoint i/p replay on all 70 unary multiindices")
        print("  - exact cyclicity and normalized SDR side conditions: zero defects")
        print("  - canonical shear, represented Green actions and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
