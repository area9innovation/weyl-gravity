#!/usr/bin/env python3
"""Independently check Gate-A v9 and its bounded nonlinear-component promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
V8 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
CLASSICAL_MAP = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
CHANNEL = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, classical_map, channel = (
        json.loads(path.read_text()) for path in (V8, CLASSICAL_MAP, CHANNEL)
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "CLASSICAL_IMPORT_GATE_V9_RECONCILIATION"
        or value.get("result_state") != "FIRST_NONLINEAR_COMPONENT_IMPORTED_ONE_CHANNEL_CLOSED_FULL_PULLBACK_OPEN_GATE_FAIL_CLOSED"
        or value.get("supersedes_for_current_status") != previous["result_id"]
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/predecessor/lifecycle/dependency")

    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous["export_reconciliation"]] or len(exports) != 20:
        errors.append("export inventory")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous["freeze_check_reconciliation"]] or len(checks) != 10:
        errors.append("check inventory")
    q2_export = next((row for row in exports if row.get("export_id") == "support_local_classical_bv_q2"), {})
    if (
        classical_map["result_id"] not in q2_export.get("evidence", [])
        or channel["result_id"] not in q2_export.get("evidence", [])
        or "f_hat-v-v" not in q2_export.get("established", "")
        or "every" not in q2_export.get("remaining_for_gate_a", "")
    ):
        errors.append("q2 nonlinear-component projection")
    check_rows = {row.get("check_id"): row for row in checks}
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = check_rows.get(check_id, {})
        if channel["result_id"] not in row.get("evidence", []) or "complete" not in row.get("remaining_for_gate_a", ""):
            errors.append("freeze-check projection " + check_id)

    replay = channel["channel_pullback_replay"]
    boundary = channel["equivalence_boundary"]
    resolution = value.get("m2_quadratic_elimination_resolution", {})
    expected_resolution = {
        "status": "FIRST_QUADRATIC_COMPONENT_IMPORTED_ONE_CUBIC_CHANNEL_CLOSED_FULL_PULLBACK_OPEN",
        "classical_evidence": classical_map["result_id"],
        "receiver_evidence": channel["result_id"],
        "carrier_rows": 386,
        "field_map_component": "F_(2)(v)=v tensor v-(1/2)g v^2",
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "source_before_correction": "-1",
        "inverse_shift_correction": "1",
        "transformed_source": "0",
        "candidate": "0",
        "residual": "0",
        "component_support_local": True,
        "component_uses_green_operator": False,
        "component_uses_choice_principle": False,
        "source_local_BV_canonical_lift_available": True,
        "receiver_componentwise_386_cotangent_lift_serialized": False,
        "complete_source_q2_pullback_replayed": False,
        "complete_source_q3_pullback_replayed": False,
        "full_cyclic_L_infinity_equivalence_constructed": False,
        "nonlinear_equivalence_obstructed": False,
        "remaining_shifted_cubic_families": boundary["remaining_shifted_cubic_families"],
    }
    if resolution != expected_resolution:
        errors.append("M2 quadratic-elimination resolution")
    if any(resolution.get(key) != replay.get(source) for key, source in (
        ("source_before_correction", "pre_correction_source_value"),
        ("inverse_shift_correction", "inverse_shift_mass_cross_correction"),
        ("transformed_source", "transformed_source_value"),
        ("candidate", "candidate_value"),
        ("residual", "transformed_source_minus_candidate_residual"),
    )):
        errors.append("receiver channel import")

    gate = value.get("gate_disposition", {})
    if (
        gate.get("gate_a_status") != "FAIL_CLOSED"
        or gate.get("accepted_common_snapshot_hashes") != 0
        or gate.get("claim_state") != "CLASSICAL_IMPORT_FIRST_NONLINEAR_COMPONENT_CONSTRUCTED_FULL_PULLBACK_OPEN"
    ):
        errors.append("Gate-A disposition")
    q2_hash = value.get("required_hash_disposition", {}).get("q2_hash", {})
    if q2_hash.get("accepted") is not None or q2_hash.get("candidate_scope") != "FIRST_NONLINEAR_COMPONENT_CLOSED_FULL_SOURCE_PULLBACK_OPEN":
        errors.append("q2 hash disposition")
    m2 = next((item for item in value.get("minimal_missing_bundle", []) if item.get("id") == "M2_STRICT_Q2_D"), {})
    if "h-f_hat-f_hat" not in m2.get("object", "") or "ghost/antifield" not in m2.get("object", "") or len(m2.get("unlocks", [])) != 3:
        errors.append("M2 next object")

    flags = value.get("claim_flags", {})
    positive = (
        "STRICT_386_FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED",
        "STRICT_386_F_HAT_V_V_PULLBACK_CHANNEL_CLOSED",
        "STRICT_386_COMPONENT_SUPPORT_LOCAL",
    )
    negative = (
        "STRICT_386_COMPONENT_USES_GREEN_OPERATOR",
        "STRICT_386_COMPONENT_USES_CHOICE_PRINCIPLE",
        "STRICT_386_FULL_BV_COTANGENT_LIFT_SERIALIZED",
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED",
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED",
        "STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED",
        "STRICT_386_NONLINEAR_EQUIVALENCE_OBSTRUCTED",
        "STRICT_386_CANDIDATE_THEORY_IDENTITY",
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2",
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
    )
    if any(flags.get(key) is not True for key in positive):
        errors.append("positive claim flags")
    if any(flags.get(key) is not False for key in negative):
        errors.append("claim firewall")

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3:
        errors.append("provenance count")
    else:
        for item, path, result_id in zip(
            provenance[-3:],
            (V8, CLASSICAL_MAP, CHANNEL),
            (previous["result_id"], classical_map["result_id"], channel["result_id"]),
        ):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path) or item.get("result_or_artifact_id") != result_id:
                errors.append("direct provenance " + path.name)
    expected_drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            expected_drift.append((source["path"], source["sha256"], current))
    drift = value.get("transitive_provenance_drift", {})
    actual_drift = [
        (item.get("path"), item.get("historical_v8_sha256"), item.get("current_worktree_sha256"))
        for item in drift.get("entries", [])
    ]
    if (
        drift.get("files_checked") != len(previous["provenance"]["inputs"])
        or drift.get("drifted_files") != len(expected_drift)
        or actual_drift != expected_drift
    ):
        errors.append("transitive provenance drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V9_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
