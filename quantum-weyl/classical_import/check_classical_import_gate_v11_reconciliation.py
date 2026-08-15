#!/usr/bin/env python3
"""Independently check Gate-A v11 and its quadratic-lift promotion boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
V10 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m2_hh_hv_cotangent_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V10, CLASSICAL, RECEIVER))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V11_RECONCILIATION" or value.get("supersedes_for_current_status") != previous["result_id"] or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("identity/predecessor/lifecycle/dependency")
    exports, checks = value.get("export_reconciliation", []), value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous["export_reconciliation"]] or len(exports) != 20:
        errors.append("export inventory")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous["freeze_check_reconciliation"]] or len(checks) != 10:
        errors.append("check inventory")
    q2 = next((row for row in exports if row.get("export_id") == "support_local_classical_bv_q2"), {})
    if classical["result_id"] not in q2.get("evidence", []) or receiver["result_id"] not in q2.get("evidence", []) or "complete quadratic" not in q2.get("boundary", ""):
        errors.append("q2 quadratic-lift projection")
    lift = receiver["quadratic_BV_cotangent_lift"]
    counts = lift["cotangent_component_counts_after_collection"]
    resolution = value.get("m2_hh_hv_cotangent_resolution", {})
    expected = {
        "status": "CURVED_HH_HV_FIELD_AND_COTANGENT_COMPONENT_JETS_EXACT",
        "classical_evidence": classical["result_id"], "receiver_evidence": receiver["result_id"], "carrier_rows": 386,
        "hh_field_coefficients": 1392, "hv_field_coefficients": 76, "vv_field_coefficients": 22,
        "hh_to_h_star_coefficients": counts["hh_to_h_star"], "hv_to_h_star_coefficients": counts["hv_to_h_star"], "hv_to_v_star_coefficients": counts["hv_to_v_star"], "vv_to_v_star_coefficients": counts["vv_to_v_star"], "combined_cotangent_coefficients": counts["combined"],
        "metric_variation_slices_declared": 150, "vector_variation_slices": 4, "formal_adjoint_defects": 0,
        "full_quadratic_BV_cotangent_lift_serialized": True, "full_source_q2_q3_pullback_replayed": False,
    }
    if resolution != expected:
        errors.append("hh/hv cotangent resolution")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0 or value.get("required_hash_disposition", {}).get("q2_hash", {}).get("accepted") is not None:
        errors.append("fail-closed Gate-A/hash disposition")
    flags = value.get("claim_flags", {})
    expected_flags = {"STRICT_386_HH_HV_BV_COTANGENT_LIFT_COMPONENT_COMPLETE": True, "STRICT_386_FULL_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED": True, "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE": False, "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False, "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False, "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False, "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False, "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False, "CLASSICAL_IMPORT_GATE_PASSED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False}
    if any(flags.get(key) is not expected for key, expected in expected_flags.items()):
        errors.append("promotion firewall")
    pins = {item.get("path"): item for item in value.get("provenance", {}).get("inputs", [])}
    for path, result in ((V10, previous), (CLASSICAL, classical), (RECEIVER, receiver)):
        item = pins.get(str(path.relative_to(ROOT)), {})
        if item.get("sha256") != sha(path) or item.get("result_or_artifact_id") != result["result_id"]:
            errors.append("direct provenance " + path.name)
    expected_drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            expected_drift.append((source["path"], source["sha256"], current))
    drift = value.get("transitive_provenance_drift", {})
    actual_drift = [(item.get("path"), item.get("historical_v10_sha256"), item.get("current_worktree_sha256")) for item in drift.get("entries", [])]
    if drift.get("files_checked") != len(previous["provenance"]["inputs"]) or drift.get("drifted_files") != len(expected_drift) or actual_drift != expected_drift:
        errors.append("transitive provenance drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V11_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
