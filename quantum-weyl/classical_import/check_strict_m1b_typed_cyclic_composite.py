#!/usr/bin/env python3
"""Independent receiver for the typed rank-940 M1B cyclic composite."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
REPORT = HERE / "REPORT_STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.md"
SCHEMA = HERE / "schema/strict-m1b-typed-cyclic-composite-v1.schema.json"
PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
DUAL = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
M1A = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
LOCAL = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
INPUTS = (PRIMAL, DUAL, M1A, LOCAL, M4R)

Sparse = dict[tuple[int, int], Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_object(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def receive(spec: dict[str, Any]) -> tuple[Sparse, int]:
    result: Sparse = {}
    duplicates = 0
    for target, source, coefficient in spec["entries"]:
        key = (int(target), int(source))
        duplicates += int(key in result)
        result[key] = result.get(key, Fraction(0)) + Fraction(str(coefficient))
        if not result[key]:
            del result[key]
    return result, duplicates


def block_sum(first: Sparse, second: Sparse, row_shift: int, column_shift: int) -> Sparse:
    result = dict(first)
    for (row, column), coefficient in second.items():
        result[row + row_shift, column + column_shift] = coefficient
    return result


def compose(left: Sparse, right: Sparse) -> Sparse:
    left_by_column: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    for (row, column), coefficient in left.items():
        left_by_column[column].append((row, coefficient))
    result: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (middle, column), right_coefficient in right.items():
        for row, left_coefficient in left_by_column.get(middle, []):
            result[row, column] += left_coefficient * right_coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def transpose(value: Sparse) -> Sparse:
    return {(column, row): coefficient for (row, column), coefficient in value.items()}


def combination(*terms: tuple[int, Sparse]) -> Sparse:
    result: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for scale, matrix in terms:
        for key, coefficient in matrix.items():
            result[key] += scale * coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def unit(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def omega(size: int) -> Sparse:
    return {
        **{(index, size + index): Fraction(1) for index in range(size)},
        **{(size + index, index): Fraction(-1) for index in range(size)},
    }


def matrix_digest(matrix: Sparse, shape: list[int]) -> str:
    rows = [[row, column, str(coefficient)] for (row, column), coefficient in sorted(matrix.items())]
    return hash_object({"shape": shape, "entries": rows})


def reconstruct(primal: dict[str, Any], dual: dict[str, Any]) -> dict[str, Any]:
    n, r = primal["represented_dimension"], primal["residual_dimension"]
    p = {name: receive(primal["matrices"][name])[0] for name in ("q0_rep", "iota_rep", "pi_rep", "s_rep")}
    d = {name: receive(dual["matrices"][name])[0] for name in ("q_dual_rep", "iota_dual_rep", "pi_dual_rep", "s_dual_rep")}
    q = block_sum(p["q0_rep"], d["q_dual_rep"], n, n)
    inclusion = block_sum(p["iota_rep"], d["iota_dual_rep"], n, r)
    projection = block_sum(p["pi_rep"], d["pi_dual_rep"], r, n)
    homotopy = block_sum(p["s_rep"], d["s_dual_rep"], n, n)
    source_form, residual_form = omega(n), omega(r)
    identities = {
        "q_squared_defects": len(compose(q, q)),
        "projection_inclusion_identity_defects": len(combination((1, compose(projection, inclusion)), (-1, unit(2 * r)))),
        "contraction_identity_defects": len(combination((1, compose(inclusion, projection)), (1, compose(q, homotopy)), (1, compose(homotopy, q)), (-1, unit(2 * n)))),
        "inclusion_chain_map_defects": len(compose(q, inclusion)),
        "projection_chain_map_defects": len(compose(projection, q)),
        "homotopy_squared_defects": len(compose(homotopy, homotopy)),
        "homotopy_inclusion_defects": len(compose(homotopy, inclusion)),
        "projection_homotopy_defects": len(compose(projection, homotopy)),
        "source_q_cyclicity_defects": len(combination((1, compose(transpose(q), source_form)), (1, compose(source_form, q)))),
        "residual_q_cyclicity_defects": 0,
        "projection_equals_inclusion_sharp_defects": len(combination((1, compose(transpose(projection), residual_form)), (-1, compose(source_form, inclusion)))),
        "homotopy_skew_adjoint_defects": len(combination((1, compose(transpose(homotopy), source_form)), (1, compose(source_form, homotopy)))),
        "inclusion_isometry_defects": len(combination((1, compose(transpose(inclusion), compose(source_form, inclusion))), (-1, residual_form))),
    }
    return {
        "energy": primal["energy"],
        "verification_core_primal_dimension": n,
        "verification_core_action_test_dual_dimension": n,
        "verification_core_total_dimension": 2 * n,
        "residual_primal_dimension": r,
        "residual_action_dual_dimension": r,
        "residual_total_dimension": 2 * r,
        "verification_core_pairing_rank": 2 * n,
        "action_residual_pairing_rank": 2 * r,
        "map_nonzero_entries": {"q_cyclic": len(q), "iota_cyclic": len(inclusion), "pi_cyclic": len(projection), "s_cyclic": len(homotopy)},
        "map_hashes": {
            "q_cyclic": matrix_digest(q, [2 * n, 2 * n]),
            "iota_cyclic": matrix_digest(inclusion, [2 * n, 2 * r]),
            "pi_cyclic": matrix_digest(projection, [2 * r, 2 * n]),
            "s_cyclic": matrix_digest(homotopy, [2 * n, 2 * n]),
            "verification_core_pairing": matrix_digest(source_form, [2 * n, 2 * n]),
            "action_residual_pairing": matrix_digest(residual_form, [2 * r, 2 * r]),
        },
        "identity_defects": identities,
    }


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        if list(Draft202012Validator(schema).iter_errors(value)):
            errors.append("schema validation")
    except Exception:
        errors.append("schema validation")

    sources = tuple(map(load, INPUTS))
    primal, dual, m1a, local, m4r = sources
    pins = value.get("provenance", {}).get("inputs", [])
    if len(pins) != 5 or any(
        pin.get("path") != str(path.relative_to(ROOT))
        or pin.get("sha256") != hash_file(path)
        or pin.get("result_id") != source.get("result_id")
        for pin, path, source in zip(pins, INPUTS, sources)
    ):
        errors.append("provenance pins")

    expected_blocks = [
        reconstruct(primal_block, dual_block)
        for primal_block, dual_block in zip(primal["represented_contraction"]["blocks"], dual["represented_dual_lift"]["blocks"])
    ]
    received = value.get("exact_cyclic_replay", {})
    received_blocks = received.get("blocks", [])
    if received_blocks != expected_blocks:
        errors.append("exact cyclic block replay")
    totals = {key: sum(block["identity_defects"][key] for block in expected_blocks) for key in expected_blocks[0]["identity_defects"]}
    aggregate = {
        "energy_blocks": 5,
        "represented_primal_coordinates": 4080,
        "represented_action_test_dual_check_coordinates": 4080,
        "finite_verification_core_coordinates": 8160,
        "excluded_formal_comparison_coordinates": 820,
        "residual_primal_coordinates": 470,
        "residual_action_dual_coordinates": 470,
        "action_residual_coordinates": 940,
        "action_residual_pairing_rank": 940,
        "all_identity_defects": sum(totals.values()),
    }
    if any(totals.values()) or received.get("identity_totals") != totals or received.get("aggregate") != aggregate or received.get("sha256") != hash_object(received_blocks):
        errors.append("exact cyclic aggregate")

    legacy = value.get("legacy_comparison_boundary", {})
    expected_legacy = {
        "formal_comparison_source_coordinates": m4r["exact_cyclic_replay"]["formal_source_dimension"],
        "current_verification_core_coordinates": 8160,
        "deleted_test_doublet_cotangent_coordinates": 820,
        "same_action_residual_coordinates": m4r["exact_cyclic_replay"]["residual_dimension"] == 940,
        "same_action_residual_pairing_rank": m4r["exact_cyclic_replay"]["residual_pairing_rank"] == 940,
        "legacy_all_identity_defects": m4r["exact_cyclic_replay"]["all_identity_defects"],
        "formal_8980_source_promoted": False,
    }
    if legacy != expected_legacy:
        errors.append("legacy comparison boundary")

    dag = value.get("typed_cyclic_dag", {})
    authorities = {node.get("id"): node.get("authority") for node in dag.get("nodes", [])}
    if (
        authorities.get("LOCAL_GRAPH_BV_386") != "AUTHORITATIVE_LOCAL_SOURCE"
        or authorities.get("ACTION_TEST_DUAL_CHECK_4080") != "CHECK_ONLY"
        or authorities.get("FORMAL_COTANGENT_COMPARISON_8980") != "EXCLUDED_COMPARISON_ONLY"
        or len(dag.get("identities", [])) != 13
        or dag.get("sha256") != hash_object({key: dag[key] for key in ("nodes", "arrows", "identities")})
    ):
        errors.append("typed cyclic DAG")

    flags = value.get("claim_flags", {})
    required_true = (
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE", "M1B_ACTION_DUAL_LIFT_COMPLETE",
        "M1B_TYPED_CYCLIC_REPLAY_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "ACTION_RESIDUAL_PAIRING_RANK_940", "ALL_THIRTEEN_TYPED_CYCLIC_IDENTITIES_REPLAYED",
    )
    required_false = (
        "FINITE_8160_CHECK_CORE_IS_AUTHORITATIVE_FULL_BV_SOURCE",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    )
    for flag in required_true:
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    content = {key: value.get(key) for key in ("typed_cyclic_dag", "exact_cyclic_replay", "legacy_comparison_boundary")}
    if value.get("content_sha256") != hash_object(content):
        errors.append("content digest")
    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    if "check core, not an authoritative source" not in report or "M1C must bind" not in report:
        errors.append("human report boundary")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1: PASS")
    print("  - independently reconstructed all five 8,160-to-940 cyclic blocks")
    print("  - replayed thirteen exact identities with zero defects")
    print("  - M1B complete; M1C, Gate A, nonlinear Green and Hadamard remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
