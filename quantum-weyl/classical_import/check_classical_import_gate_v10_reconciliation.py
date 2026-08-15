#!/usr/bin/env python3
"""Independently check Gate-A v10 and its scoped cubic-inventory promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
V9 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V9, CLASSICAL, RECEIVER))
    errors: list[str] = []
    if (
        value.get("result_id") != "CLASSICAL_IMPORT_GATE_V10_RECONCILIATION"
        or value.get("result_state") != "SEVEN_REQUIRED_CUBIC_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_HH_HV_GAUGE_COMPONENTS_OPEN_GATE_FAIL_CLOSED"
        or value.get("supersedes_for_current_status") != previous["result_id"]
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/predecessor/lifecycle/dependency")

    exports, checks = value.get("export_reconciliation", []), value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous["export_reconciliation"]] or len(exports) != 20:
        errors.append("export inventory")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous["freeze_check_reconciliation"]] or len(checks) != 10:
        errors.append("check inventory")
    q2 = next((row for row in exports if row.get("export_id") == "support_local_classical_bv_q2"), {})
    if classical["result_id"] not in q2.get("evidence", []) or receiver["result_id"] not in q2.get("evidence", []) or "72-coefficient" not in q2.get("established", ""):
        errors.append("q2 cubic-inventory projection")
    check_rows = {row.get("check_id"): row for row in checks}
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = check_rows.get(check_id, {})
        if receiver["result_id"] not in row.get("evidence", []) or "vv canonicality" not in row.get("boundary", ""):
            errors.append("freeze-check projection " + check_id)

    lift = receiver["vv_BV_cotangent_lift"]
    complete = receiver["inventory_completeness"]
    comparison = receiver["candidate_comparison"]
    resolution = value.get("m2_shifted_cubic_inventory_resolution", {})
    expected = {
        "status": "KNOWN_REQUIRED_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_FULL_LIFT_OPEN",
        "classical_evidence": classical["result_id"],
        "receiver_evidence": receiver["result_id"],
        "carrier_rows": 386,
        "known_required_cubic_block_families": 7,
        "component_complete_families": 2,
        "component_open_families": 5,
        "family_ids": [row["family_id"] for row in receiver["required_cubic_family_inventory"]],
        "h_f_hat_f_hat_source_coefficients": 72,
        "h_f_hat_f_hat_candidate_coefficients": 0,
        "vv_field_map_coefficients": 22,
        "vv_cotangent_partner_coefficients": 16,
        "vv_canonicality_slices": 4,
        "vv_canonicality_defects": 0,
        "quadratic_active_output_rows": 14,
        "quadratic_zero_output_rows": 372,
        "hh_hv_component_complete": False,
        "diffeomorphism_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "full_386_BV_cotangent_lift_serialized": False,
        "complete_source_q2_q3_pullback_replayed": False,
        "shift_alone_identifies_trivial_stabilization": False,
        "further_normalization_may_exist": True,
        "full_nonlinear_equivalence_obstructed": False,
    }
    if resolution != expected:
        errors.append("M2 shifted-cubic resolution")
    if lift.get("canonicality_defects") != 0 or complete.get("component_coefficient_open_families") != 5 or comparison.get("new_exact_source_candidate_component_defect_count") != 72:
        errors.append("receiver source projection")

    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0 or gate.get("claim_state") != "CLASSICAL_IMPORT_CUBIC_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_FULL_PULLBACK_OPEN":
        errors.append("Gate-A disposition")
    q2_hash = value.get("required_hash_disposition", {}).get("q2_hash", {})
    if q2_hash.get("accepted") is not None or q2_hash.get("candidate_scope") != "SEVEN_REQUIRED_FAMILIES_ENUMERATED_VV_LIFT_CANONICAL_FULL_SOURCE_PULLBACK_OPEN":
        errors.append("q2 hash disposition")
    m2 = next((item for item in value.get("minimal_missing_bundle", []) if item.get("id") == "M2_STRICT_Q2_D"), {})
    if "hh/hv" not in m2.get("object", "") or "Weyl/boost" not in m2.get("object", ""):
        errors.append("M2 next object")

    flags = value.get("claim_flags", {})
    positive = (
        "STRICT_386_KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED",
        "STRICT_386_SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_IMPORTED",
        "STRICT_386_VV_FIELD_MAP_COMPONENTS_IMPORTED",
        "STRICT_386_VV_COTANGENT_PARTNER_COMPONENTS_SERIALIZED",
        "STRICT_386_VV_BV_COTANGENT_LIFT_CANONICAL",
    )
    negative = (
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS",
        "STRICT_386_HH_HV_BV_COTANGENT_LIFT_COMPONENT_COMPLETE",
        "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE",
        "STRICT_386_FULL_BV_COTANGENT_LIFT_SERIALIZED",
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED",
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED",
        "STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED",
        "STRICT_386_NONLINEAR_EQUIVALENCE_OBSTRUCTED",
        "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
    )
    if any(flags.get(key) is not True for key in positive):
        errors.append("positive claim flags")
    if any(flags.get(key) is not False for key in negative):
        errors.append("claim firewall")

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3:
        errors.append("provenance count")
    else:
        for item, path, result_id in zip(provenance[-3:], (V9, CLASSICAL, RECEIVER), (previous["result_id"], classical["result_id"], receiver["result_id"])):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path) or item.get("result_or_artifact_id") != result_id:
                errors.append("direct provenance " + path.name)
    expected_drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            expected_drift.append((source["path"], source["sha256"], current))
    drift = value.get("transitive_provenance_drift", {})
    actual_drift = [(item.get("path"), item.get("historical_v9_sha256"), item.get("current_worktree_sha256")) for item in drift.get("entries", [])]
    if drift.get("files_checked") != len(previous["provenance"]["inputs"]) or drift.get("drifted_files") != len(expected_drift) or actual_drift != expected_drift:
        errors.append("transitive provenance drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V10_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
