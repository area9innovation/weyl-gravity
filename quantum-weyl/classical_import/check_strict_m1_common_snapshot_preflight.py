#!/usr/bin/env python3
"""Independent receiver for the M1 common-snapshot preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"

AUTHORITIES = {
    "bootstrap": HERE / "snapshots/bootstrap-v1.json",
    "gate_v25": HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json",
    "component_pairing": HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
    "full_q1": HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json",
    "common_endpoint": HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json",
    "source_q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "source_q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "D_action": HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    "dfinite": HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json",
    "m3r": HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json",
    "m3rc_a": HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json",
    "m3rc_b": HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json",
    "m4r": HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json",
    "zero_modes": HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
    "centered": HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json",
}

REQUIRED_ROW_FIELDS = {
    "ghost_number", "antifield_number", "form_degree", "Grassmann_parity",
    "mass_dimension", "Weyl_weight", "compact_degree", "derivative_order_bound",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1", "result identity drift")
    require(value.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"], "dependency tags drift")
    pins = {item.get("role"): item for item in value.get("provenance", {}).get("inputs", [])}
    require(set(pins) == set(AUTHORITIES), "authority role ledger drift")
    for role, path in AUTHORITIES.items():
        pin = pins.get(role, {})
        require(pin.get("path") == str(path.relative_to(ROOT)), f"authority path drift: {role}")
        require(pin.get("sha256") == sha(path), f"authority hash drift: {role}")

    sources = {name: load(path) for name, path in AUTHORITIES.items()}
    gate = sources["gate_v25"]
    require(gate.get("result_id") == "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION", "Gate V25 identity drift")
    require(gate.get("gate_disposition", {}).get("gate_a_status") == "FAIL_CLOSED", "Gate V25 promoted")
    require([item.get("id") for item in gate.get("minimal_missing_bundle", [])] == ["M1_COMMON_STRICT_SNAPSHOT"], "Gate V25 M1 frontier drift")

    rows = sources["component_pairing"].get("component_basis", {}).get("rows", [])
    present = {key for row in rows for key in row}
    missing = sorted(REQUIRED_ROW_FIELDS - present)
    ledger = value.get("local_row_ledger_audit", {})
    require(len(rows) == ledger.get("rows") == 386, "local row count drift")
    require(ledger.get("serialized_fields") == sorted(present), "serialized row-field audit drift")
    require(ledger.get("required_explicit_fields") == [
        "ghost_number", "antifield_number", "form_degree", "Grassmann_parity",
        "mass_dimension", "Weyl_weight", "compact_degree", "derivative_order_bound",
    ], "required row-field contract drift")
    require(ledger.get("missing_explicit_fields") == [
        field for field in ledger.get("required_explicit_fields", []) if field in set(missing)
    ], "missing row-field audit drift")
    require(bool(missing) and ledger.get("all_rows_have_required_explicit_fields") is False, "full row ledger falsely closed")

    carriers = {row.get("id"): row for row in value.get("carrier_inventory", [])}
    expected_dimensions = {
        "LOCAL_GRAPH_BV_386": 386,
        "LOCAL_ENDPOINT_30": 30,
        "REPRESENTED_ENDPOINT_DFINITE_4080": sources["m3r"]["comparison"]["source"]["total_dimension"],
        "DFINITE_COMPARISON_4490": sources["dfinite"]["global_direct_sum"]["full_dimension"],
        "FORMAL_COTANGENT_COMPARISON_8980": sources["m3rc_a"]["formal_cotangent_completion"]["full_dimension"],
        "ACTION_RESIDUAL_940": sources["m4r"]["typed_carrier"]["total_residual_coordinates"],
        "ZERO_MODE_15_PLUS_15": 30,
        "CENTERED_C3_C4_C5": 12343,
    }
    require({key: carriers.get(key, {}).get("dimension") for key in expected_dimensions} == expected_dimensions, "carrier census drift")
    require(carriers.get("FORMAL_COTANGENT_COMPARISON_8980", {}).get("status") == "NOT_AUTHORITATIVE_FULL_BV_SOURCE", "formal source authority promoted")
    decision = value.get("authoritative_source_decision", {})
    require(decision.get("local_source") == "LOCAL_GRAPH_BV_386" and decision.get("snapshot_shape") == "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE", "authoritative source decision drift")
    require(decision.get("formal_8980_source_authoritative") is False and decision.get("action_residual_940_is_target_not_local_source") is True, "source/target category firewall drift")

    edges = {row.get("id"): row for row in value.get("cross_category_edges", [])}
    expected_edges = {
        "M3L_LOCAL_ENDPOINT_SDR": ("LOCAL_GRAPH_BV_386", "LOCAL_ENDPOINT_30", "EXACT_SUPPORT_LOCAL_COMPLETE"),
        "FINITE_HARMONIC_REALIZATION": ("LOCAL_ENDPOINT_30", "REPRESENTED_ENDPOINT_DFINITE_4080", "EXACT_GLOBAL_REPRESENTATION_FUNCTOR_NOT_POSITION_LOCAL"),
        "M3R_ANALYSIS_SYNTHESIS": ("REPRESENTED_ENDPOINT_DFINITE_4080", "ACTION_RESIDUAL_940", "PRIMAL_470_STAGE_COMPLETE_DUAL_STAGE_ACTION_IDENTIFIED"),
        "M3RCA_FORMAL_COTANGENT_SDR": ("FORMAL_COTANGENT_COMPARISON_8980", "ACTION_RESIDUAL_940", "EXACT_COMPARISON_ONLY_NOT_AUTHORITATIVE_SOURCE"),
        "M3RCB_COMPACT_SOURCE_DUAL": ("REPRESENTED_ENDPOINT_DFINITE_4080", "ACTION_RESIDUAL_940", "EXACT_ON_REPRESENTED_ACTION_DUAL"),
        "M4R_FORMAL_CYCLIC_CONTRACTION": ("FORMAL_COTANGENT_COMPARISON_8980", "ACTION_RESIDUAL_940", "EXACT_COMPARISON_ONLY"),
        "M1B_ACTUAL_REPRESENTED_COMPOSITE_CONTRACTION": ("LOCAL_GRAPH_BV_386", "ACTION_RESIDUAL_940", "MISSING_SERIALIZED_TYPED_COMPOSITE"),
    }
    require(
        {key: (edges.get(key, {}).get("source"), edges.get(key, {}).get("target"), edges.get(key, {}).get("status")) for key in expected_edges}
        == expected_edges and len(edges) == len(expected_edges),
        "typed edge inventory drift",
    )

    exports = value.get("export_inventory", [])
    gate_ids = [item.get("export_id") for item in gate.get("export_reconciliation", [])]
    require([item.get("export_id") for item in exports] == gate_ids and len(exports) == 20, "twenty-export order/census drift")
    status_counts: dict[str, int] = {}
    for item in exports:
        status_counts[item.get("m1_preflight_status", "")] = status_counts.get(item.get("m1_preflight_status", ""), 0) + 1
    require(status_counts == {
        "MISSING_FULL_TYPED_ROW_LEDGER": 2,
        "TYPED_STAGES_READY_COMPOSITE_MAP_MISSING": 3,
        "LOCAL_AND_RESIDUAL_FORMS_READY_COMMON_COMPOSITE_MISSING": 1,
        "COMMON_OBJECT_READY_FOR_BINDING": 14,
    }, "M1 export blocker partition drift")

    hashes = value.get("hash_inventory", [])
    require([item.get("hash_id") for item in hashes] == [
        "field_dictionary_hash", "differential_hash", "q2_hash", "D_action_hash",
        "zero_mode_basis_hash", "pairing_hash", "representative_hash",
    ], "seven-hash order/census drift")
    require(sum("BLOCKED" in item.get("status", "") for item in hashes) == 3, "blocked hash census drift")
    require(sum("READY" in item.get("status", "") and "BLOCKED" not in item.get("status", "") for item in hashes) == 4, "ready hash-object census drift")
    require(len(value.get("freeze_check_inventory", [])) == 10 and all(item.get("common_snapshot_replay_status") == "WAITING_FOR_M1C_AFTER_M1A_M1B" for item in value.get("freeze_check_inventory", [])), "ten-check M1 replay firewall drift")
    require(value.get("counts") == {
        "exports_total": 20,
        "exports_common_object_ready": 14,
        "exports_blocked_full_typed_ledger": 2,
        "exports_blocked_composite_contraction": 4,
        "hashes_total": 7,
        "hash_objects_ready_await_binding": 4,
        "hashes_blocked_before_binding": 3,
        "freeze_checks_total": 10,
        "freeze_checks_common_snapshot_replayed": 0,
    }, "summary census drift")

    packages = value.get("m1_work_packages", [])
    require([item.get("id") for item in packages] == [
        "M1A_FULL_TYPED_CARRIER_LEDGER",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION",
        "M1C_COMMON_MANIFEST_REPLAY",
    ], "M1 package ordering drift")
    require([item.get("status") for item in packages] == ["OPEN", "OPEN_AFTER_M1A", "OPEN_AFTER_M1A_M1B"], "M1 package lifecycle drift")

    flags = value.get("claim_flags", {})
    for key in ("M1_PREFLIGHT_COMPLETE", "M1_TYPED_DIAGRAM_REQUIRED"):
        require(flags.get(key) is True, f"positive preflight flag missing: {key}")
    for key in (
        "M1_IS_CLERICAL_HASH_BUNDLE", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")

    keys = (
        "authoritative_source_decision", "carrier_inventory", "cross_category_edges",
        "local_row_ledger_audit", "export_inventory", "hash_inventory",
        "freeze_check_inventory", "counts", "m1_work_packages", "claim_flags",
    )
    require(value.get("independent_checker", {}).get("expected_digest") == digest({key: value[key] for key in keys}), "canonical preflight digest drift")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - 14 of 20 exports are object-ready; two ledger and four composite exports remain")
        print("  - four of seven hash objects are ready; three remain blocked before common binding")
        print("  - M1 splits into M1A typed ledger, M1B actual composite contraction and M1C final replay")
        print("  - Gate A, Hadamard and QME remain fail closed")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
