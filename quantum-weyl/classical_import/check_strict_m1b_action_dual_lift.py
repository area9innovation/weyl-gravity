#!/usr/bin/env python3
"""Independent receiver for the strict M1B action-derived dual lift."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1B_ACTION_DUAL_LIFT_V1.md"
SCHEMA = HERE / "schema/strict-m1b-action-dual-lift-v1.schema.json"
PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
M1A = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
CROSSWALK = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
ACTION = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
LOCAL = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
INPUTS = (PRIMAL, M1A, CROSSWALK, ACTION, LOCAL, M4R)

Sparse = dict[tuple[int, int], Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def decode(spec: dict[str, Any]) -> tuple[Sparse, int]:
    value: Sparse = {}
    duplicates = 0
    for row, column, coefficient in spec["entries"]:
        key = (int(row), int(column))
        duplicates += int(key in value)
        value[key] = value.get(key, Fraction(0)) + Fraction(str(coefficient))
        if not value[key]:
            del value[key]
    return value, duplicates


def transpose(value: Sparse, sign: int = 1) -> Sparse:
    return {(column, row): sign * coefficient for (row, column), coefficient in value.items()}


def compose(left: Sparse, right: Sparse) -> Sparse:
    lookup: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        lookup.setdefault(row, []).append((column, coefficient))
    result: Sparse = {}
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in lookup.get(middle, []):
            key = (row, column)
            result[key] = result.get(key, Fraction(0)) + left_coefficient * right_coefficient
            if not result[key]:
                del result[key]
    return result


def combine(*terms: tuple[int, Sparse]) -> Sparse:
    result: Sparse = {}
    for scale, matrix in terms:
        for key, coefficient in matrix.items():
            result[key] = result.get(key, Fraction(0)) + scale * coefficient
            if not result[key]:
                del result[key]
    return result


def unit(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def defects(q: Sparse, inclusion: Sparse, projection: Sparse, homotopy: Sparse, n: int, r: int) -> dict[str, int]:
    return {
        "q_dual_squared_defects": len(compose(q, q)),
        "pi_dual_iota_dual_defects": len(combine((1, compose(projection, inclusion)), (-1, unit(r)))),
        "dual_contraction_defects": len(combine((1, compose(inclusion, projection)), (-1, unit(n)), (1, compose(q, homotopy)), (1, compose(homotopy, q)))),
        "q_dual_iota_dual_defects": len(compose(q, inclusion)),
        "pi_dual_q_dual_defects": len(compose(projection, q)),
        "s_dual_squared_defects": len(compose(homotopy, homotopy)),
        "s_dual_iota_dual_defects": len(compose(homotopy, inclusion)),
        "pi_dual_s_dual_defects": len(compose(projection, homotopy)),
    }


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        failures = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.path))
        if failures:
            errors.append("schema validation")
    except Exception:
        errors.append("schema validation")

    sources = tuple(map(load, INPUTS))
    primal, m1a, crosswalk, action, local, m4r = sources
    pins = value.get("provenance", {}).get("inputs", [])
    if len(pins) != len(INPUTS) or any(
        pin.get("path") != str(path.relative_to(ROOT))
        or pin.get("sha256") != file_hash(path)
        or pin.get("result_id") != source.get("result_id")
        for pin, path, source in zip(pins, INPUTS, sources)
    ):
        errors.append("provenance pins")

    received_blocks = value.get("represented_dual_lift", {}).get("blocks", [])
    primal_blocks = primal["represented_contraction"]["blocks"]
    aggregate = {
        "represented_action_test_coordinates": 0,
        "action_residual_dual_coordinates": 0,
        "q_dual_nonzero_entries": 0,
        "iota_dual_nonzero_entries": 0,
        "pi_dual_nonzero_entries": 0,
        "s_dual_nonzero_entries": 0,
    }
    totals: dict[str, int] = {}
    block_errors = 0
    if len(received_blocks) != 5:
        block_errors += 1
    for source, received in zip(primal_blocks, received_blocks):
        n, r = source["represented_dimension"], source["residual_dimension"]
        primal_matrices = {name: decode(source["matrices"][name])[0] for name in ("q0_rep", "iota_rep", "pi_rep", "s_rep")}
        expected = {
            "q_dual_rep": transpose(primal_matrices["q0_rep"], -1),
            "iota_dual_rep": transpose(primal_matrices["pi_rep"]),
            "pi_dual_rep": transpose(primal_matrices["iota_rep"]),
            "s_dual_rep": transpose(primal_matrices["s_rep"], -1),
        }
        received_matrices: dict[str, Sparse] = {}
        for name, expected_matrix in expected.items():
            spec = received.get("matrices", {}).get(name, {})
            try:
                decoded, duplicates = decode(spec)
            except Exception:
                block_errors += 1
                continue
            expected_shape = [n, r] if name == "iota_dual_rep" else [r, n] if name == "pi_dual_rep" else [n, n]
            encoded = [[row, column, str(coefficient)] for (row, column), coefficient in sorted(decoded.items())]
            expected_hash = object_hash({"shape": expected_shape, "entries": encoded})
            if decoded != expected_matrix or duplicates or spec.get("shape") != expected_shape or spec.get("nonzero_entries") != len(decoded) or spec.get("sha256") != expected_hash:
                block_errors += 1
            received_matrices[name] = decoded
        if len(received_matrices) != 4:
            continue
        replay = defects(received_matrices["q_dual_rep"], received_matrices["iota_dual_rep"], received_matrices["pi_dual_rep"], received_matrices["s_dual_rep"], n, r)
        if received.get("energy") != source["energy"] or received.get("exact_replay") != replay or any(replay.values()):
            block_errors += 1
        expected_dual_basis = [f"dual[1]({label})" for label in source["residual_basis"]]
        if received.get("action_residual_dual_basis") != expected_dual_basis:
            block_errors += 1
        for key, count in replay.items():
            totals[key] = totals.get(key, 0) + count
        aggregate["represented_action_test_coordinates"] += n
        aggregate["action_residual_dual_coordinates"] += r
        aggregate["q_dual_nonzero_entries"] += len(expected["q_dual_rep"])
        aggregate["iota_dual_nonzero_entries"] += len(expected["iota_dual_rep"])
        aggregate["pi_dual_nonzero_entries"] += len(expected["pi_dual_rep"])
        aggregate["s_dual_nonzero_entries"] += len(expected["s_dual_rep"])
    lift = value.get("represented_dual_lift", {})
    if block_errors or lift.get("aggregate") != aggregate or lift.get("exact_replay") != totals or lift.get("sha256") != object_hash(received_blocks):
        errors.append("represented dual block payload")

    action_rows = crosswalk["action_residual_dual_rows"]
    dictionary = action["action_pairing_identification"]["dual_dictionary"]
    received_actions = value.get("action_residual_coordinate_actions", [])
    crosswalk_errors = 0
    if not (len(action_rows) == len(dictionary) == len(received_actions) == 470):
        crosswalk_errors += 1
    for index, (row, source, received) in enumerate(zip(action_rows, dictionary, received_actions)):
        if (
            row["pair_index"] != index
            or row["residual_label"] != source["formal_dual_label"]
            or row["compact_source_representative"] != source["compact_source_representative"]
            or not row["compact_source_support"]
            or received.get("pair_index") != index
            or received.get("dual_label") != row["residual_label"]
            or received.get("compact_source_representative") != row["compact_source_representative"]
            or received.get("inclusion_rule") != "iota_dual_comp=pi_comp^sharp"
            or received.get("projection_rule") != "pi_dual_comp=iota_comp^sharp"
        ):
            crosswalk_errors += 1
    if crosswalk_errors:
        errors.append("action residual crosswalk")

    bridge = value.get("action_pairing_bridge", {})
    expected_bridge = {
        "local_action_pairing_rank": local["pairing_replay"]["exact_rational_rank"],
        "local_action_pairing_rows": local["pairing_replay"]["carrier_rows"],
        "residual_action_pairing_rank": action["action_pairing_identification"]["phase_pairing_rank"],
        "compact_source_dual_classes": len(dictionary),
        "compact_source_support_defects": 0,
        "action_pairing_identification_defects": action["action_pairing_identification"]["pairing_identification_defects"],
        "m1a_action_dual_crosswalk_defects": 0,
        "adjoint_uniqueness_defects": 0,
        "full_4080_algebraic_dual_identified_with_compact_sources": False,
        "verification_core_is_authoritative_full_bv_source": False,
    }
    if bridge != expected_bridge:
        errors.append("action pairing bridge")

    dag = value.get("typed_adjoint_dag", {})
    node_categories = {node.get("id"): (node.get("category"), node.get("authority")) for node in dag.get("nodes", [])}
    formula = dag.get("formula", {})
    if (
        node_categories.get("REPRESENTED_ACTION_TEST_DUAL_CHECK") != ("FINITE_ALGEBRAIC_DUAL_VERIFICATION_CORE", "CHECK_ONLY_NOT_A_NEW_SOURCE_CARRIER")
        or node_categories.get("COMPACT_SOURCE_ACTION_DUAL_RESIDUAL") != ("COMPACT_SOURCE_ACTION_DUAL", "AUTHORITATIVE_REPRESENTED_ACTION_DUAL")
        or formula.get("q_dual") != "q_dual_comp=-q_comp^sharp"
        or formula.get("inclusion") != "iota_dual_comp=pi_comp^sharp"
        or formula.get("projection") != "pi_dual_comp=iota_comp^sharp"
        or formula.get("homotopy") != "s_dual_comp=-s_comp^sharp"
        or dag.get("sha256") != object_hash({key: dag[key] for key in ("nodes", "arrows", "formula")})
    ):
        errors.append("typed adjoint DAG")

    flags = value.get("claim_flags", {})
    required_true = (
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE", "M1B_ACTION_DUAL_LIFT_COMPLETE",
        "ALL_470_RESIDUAL_DUALS_ACTION_DERIVED_COMPACT_SOURCE",
        "ACTION_DUAL_MAPS_FORCED_BY_LOCAL_AND_RESIDUAL_PAIRINGS",
    )
    required_false = (
        "FULL_4080_ALGEBRAIC_DUAL_COMPACT_SOURCE_IDENTIFIED",
        "FINITE_8160_CHECK_CORE_IS_AUTHORITATIVE_FULL_BV_SOURCE",
        "M1B_TYPED_CYCLIC_REPLAY_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    )
    for flag in required_true:
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")

    content = {key: value.get(key) for key in ("typed_adjoint_dag", "represented_dual_lift", "action_residual_coordinate_actions", "action_pairing_bridge")}
    if value.get("content_sha256") != object_hash(content):
        errors.append("content digest")
    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    if "verification device, not a new" not in report or "rank-940 typed cyclic replay remains" not in report:
        errors.append("human report boundary")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("STRICT_M1B_ACTION_DUAL_LIFT_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1B_ACTION_DUAL_LIFT_V1: PASS")
    print("  - independently reconstructed five forced action-adjoint blocks")
    print("  - independently crosswalked all 470 compact-source residual duals")
    print("  - cyclic replay, M1C, Gate A and Hadamard remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
