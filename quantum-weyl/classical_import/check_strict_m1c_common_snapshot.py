#!/usr/bin/env python3
"""Independent common-byte receiver for the strict M1C classical snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1C_COMMON_SNAPSHOT_V1.md"
SCHEMA = HERE / "schema/strict-m1c-common-snapshot-v1.schema.json"
INPUTS = {
    "m1a": HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json",
    "graph_q1": HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    "source_q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "source_q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "D_action": HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    "zero_modes": HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
    "centered": HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json",
    "m1b_primal": HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json",
    "m1b_dual": HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json",
    "m1b_cyclic": HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json",
    "local_cyclic": HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json",
    "taub": ROOT / "bridge/certificates/taub_moment_map.json",
    "suspension": ROOT / "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json",
    "polarization": ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
    "nonminimal_contraction": ROOT / "field_bv_identification/gauge_fixed_equivalence/certificates/contraction.json",
    "nonminimal_pairs": ROOT / "field_bv_identification/gauge_fixed_equivalence/certificates/nonminimal_pairs.json",
}
CHECKERS = (
    "check_strict_m1a_immutable_typed_ledger.py",
    "check_strict_386_graph_q1_sdr_component_jets.py",
    "check_strict_386_source_q2_common_assembly.py",
    "check_strict_386_source_q3_common_assembly.py",
    "check_strict_386_full_d_action.py",
    "check_strict_residual_zero_mode_payload.py",
    "check_strict_centered_cohomology_payload.py",
    "check_strict_m1b_primal_composite_contraction.py",
    "check_strict_m1b_action_dual_lift.py",
    "check_strict_m1b_typed_cyclic_composite.py",
    "check_strict_386_local_cyclic_pairing_closure.py",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def expected_hashes(source: dict[str, dict[str, Any]]) -> tuple[dict[str, str], dict[str, Any]]:
    represented_q0_hash = object_hash([
        block["matrices"]["q0_rep"]["sha256"]
        for block in source["m1b_primal"]["represented_contraction"]["blocks"]
    ])
    differential = {
        "typed_field_dictionary_sha256": source["m1a"]["typed_field_dictionary"]["sha256"],
        "local_graph_q1_sha256": source["graph_q1"]["canonical_hashes"]["graph_q1_serialization_sha256"],
        "represented_q0_sha256": represented_q0_hash,
        "residual_q0_sha256": source["zero_modes"]["canonical_hashes"]["q_res_0_sha256"],
    }
    pairing = {
        "local_pairing_sha256": source["local_cyclic"]["pairing_replay"]["pairing_sha256"],
        "typed_cyclic_composite_sha256": source["m1b_cyclic"]["content_sha256"],
        "action_residual_pairing_rank": 940,
    }
    hashes = {
        "field_dictionary_hash": source["m1a"]["typed_field_dictionary"]["sha256"],
        "differential_hash": object_hash(differential),
        "q2_hash": source["source_q2"]["source_q2_snapshot"]["sha256"],
        "D_action_hash": source["D_action"]["canonical_hashes"]["D_action_sha256"],
        "zero_mode_basis_hash": source["zero_modes"]["canonical_hashes"]["zero_mode_basis_sha256"],
        "pairing_hash": object_hash(pairing),
        "representative_hash": source["centered"]["canonical_hashes"]["representatives_sha256"],
    }
    return hashes, {"differential_hash": differential, "pairing_hash": pairing}


def expected_check_defects(source: dict[str, dict[str, Any]]) -> dict[str, int]:
    cyclic = source["m1b_cyclic"]["exact_cyclic_replay"]["identity_totals"]
    return {
        "q0_squared_zero": 0,
        "q1_q2_arity_two_nilpotency": source["source_q2"]["q1_q2_replay"]["graph_386_q1_q2_defects"],
        "D_q1_commutator_zero": source["D_action"]["exact_replay"]["D_q1_commutator_defects"],
        "D_q2_derivation": source["source_q2"]["D_q2_replay"]["graph_D_q2_derivation_defects"],
        "q2_cyclic_compatibility": source["source_q2"]["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "pi_cl_iota_cl_identity": cyclic["projection_inclusion_identity_defects"],
        "classical_contraction_identity": cyclic["contraction_identity_defects"],
        "q0_iota_intertwining": cyclic["inclusion_chain_map_defects"],
        "pi_q0_intertwining": cyclic["projection_chain_map_defects"],
        "cyclic_compatibility": sum(value for key, value in cyclic.items() if "cyclic" in key or "sharp" in key or "skew" in key or "isometry" in key),
    }


def check(value: dict[str, Any], run_receivers: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        if list(Draft202012Validator(schema).iter_errors(value)):
            errors.append("schema validation")
    except Exception:
        errors.append("schema validation")

    source = {name: load(path) for name, path in INPUTS.items()}
    pins = value.get("artifact_pins", [])
    pins_by_id = {item.get("pin_id"): item for item in pins}
    if len(pins) != 16 or len(pins_by_id) != 16:
        errors.append("artifact pin census")
    for name, path in INPUTS.items():
        pin = pins_by_id.get(name, {})
        expected_id = source[name].get("result_id", source[name].get("schema", name))
        if pin.get("path") != str(path.relative_to(ROOT)) or pin.get("sha256") != file_hash(path) or pin.get("result_or_schema_id") != expected_id:
            errors.append("artifact pins")

    exports = value.get("export_bindings", [])
    expected_export_ids = {
        "field_ghost_antifield_dictionary", "field_gradings", "local_classical_bv_differential_q0",
        "support_local_classical_bv_q2", "local_D_action_on_bv_generators",
        "gauge_fixed_nonminimal_contractions", "trace_sector_contraction",
        "conformal_killing_zero_modes_15", "residual_representation_matrices", "so42_structure_constants",
        "classical_inclusion_iota_cl", "classical_projection_pi_cl", "classical_homotopy_s_cl",
        "cyclic_pairing", "taub_moment_map_normalization", "bfv_suspension_convention",
        "positive_frequency_state_ledger", "normalized_weyl_square_representatives",
        "centered_cohomology_bases_h3_h4_h5", "residual_differential_q_res_0",
    }
    if len(exports) != 20 or {item.get("export_id") for item in exports} != expected_export_ids:
        errors.append("export binding census")
    for item in exports:
        if item.get("status") != "BOUND_IN_COMMON_IMMUTABLE_MANIFEST" or not item.get("objects") or any(obj.get("pin_id") not in pins_by_id for obj in item.get("objects", [])):
            errors.append("export bindings")

    hashes, witnesses = expected_hashes(source)
    if value.get("accepted_top_level_hashes") != hashes or value.get("hash_composition_witnesses") != witnesses:
        errors.append("top-level hash binding")
    check_defects = expected_check_defects(source)
    replay = value.get("gate_a_replay", [])
    if len(replay) != 10 or {item.get("check_id") for item in replay} != set(check_defects):
        errors.append("Gate-A replay census")
    for item in replay:
        if item.get("status") != "PASS_ON_COMMON_BYTES" or item.get("defects") != check_defects.get(item.get("check_id")) or not item.get("pins") or any(pin_id not in pins_by_id for pin_id in item.get("pins", [])):
            errors.append("Gate-A replay payload")
    if any(check_defects.values()):
        errors.append("Gate-A replay mathematical defect")

    supplemental = value.get("supplemental_replay", [])
    if [item.get("check_id") for item in supplemental] != [
        "q3_arity_three_and_cyclicity", "residual_zero_mode_and_representation", "centered_H4_cohomology_and_representatives"
    ] or any(item.get("status") != "PASS_ON_COMMON_BYTES" or item.get("defects") != 0 or item.get("pin") not in pins_by_id for item in supplemental):
        errors.append("supplemental replay")

    carrier = value.get("carrier_manifest", {})
    if (
        carrier.get("typed_diagram_sha256") != source["m1a"]["diagram_freeze"]["sha256"]
        or carrier.get("authoritative_rows") != 17779
        or carrier.get("authoritative_carrier_objects") != 6
        or carrier.get("excluded_test_rows") != 410
        or carrier.get("excluded_formal_cotangent_rows") != 8980
        or carrier.get("distinct_categories_not_identified") is not True
    ):
        errors.append("carrier manifest")

    manifest_core = {
        "carrier_manifest": value.get("carrier_manifest"),
        "artifact_pins": value.get("artifact_pins"),
        "export_bindings": value.get("export_bindings"),
        "accepted_top_level_hashes": value.get("accepted_top_level_hashes"),
        "hash_composition_witnesses": value.get("hash_composition_witnesses"),
        "gate_a_replay": value.get("gate_a_replay"),
        "supplemental_replay": value.get("supplemental_replay"),
    }
    snapshot_hash = object_hash(manifest_core)
    if value.get("snapshot_sha256") != snapshot_hash or value.get("snapshot_id") != f"STRICT_PURE_WEYL_BV_SNAPSHOT_{snapshot_hash[:16]}":
        errors.append("immutable snapshot digest")

    receiver = value.get("receiver_replay", {})
    if receiver.get("independent_checkers") != list(CHECKERS) or receiver.get("all_required_checkers_passed") is not True or receiver.get("gate_checks_passed") != 10 or receiver.get("gate_checks_failed") != 0:
        errors.append("receiver ledger")
    if run_receivers:
        for checker in CHECKERS:
            completed = subprocess.run([sys.executable, str(HERE / checker)], cwd=ROOT, text=True, capture_output=True)
            if completed.returncode:
                errors.append(f"receiver failed {checker}")

    flags = value.get("claim_flags", {})
    required_true = (
        "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
        "ALL_20_EXPORTS_COMMON_BOUND", "ALL_7_TOP_LEVEL_HASHES_COMMON_BOUND",
        "ALL_10_GATE_A_CHECKS_COMMON_REPLAYED",
    )
    required_false = (
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX", "CLASSICAL_IMPORT_GATE_PASSED",
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
    content = {"snapshot_sha256": snapshot_hash, "receiver_replay": receiver, "claim_flags": flags}
    if value.get("content_sha256") != object_hash(content):
        errors.append("content digest")
    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    if "does not set the Gate-A-passed flag itself" not in report or "next scientific" not in report:
        errors.append("human report boundary")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT), run_receivers=True)
    if errors:
        print("STRICT_M1C_COMMON_SNAPSHOT_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1C_COMMON_SNAPSHOT_V1: PASS")
    print("  - independently verified 16 content pins and 20 export bindings")
    print("  - independently replayed all 10 Gate-A and 3 supplemental checks")
    print("  - immutable snapshot complete; Gate decision remains separate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
