#!/usr/bin/env python3
"""Independent fail-closed audit of Gate-A reconciliation v6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
PREDECESSOR = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
FULL_D = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
FALSE_FLAGS = {
    "CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
    "LORENTZIAN_QUANTUM_THEORY", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    "STRICT_386_FULL_CARRIER_Q2", "STRICT_386_D_Q2_DERIVATION",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay", "status_vocabulary", "export_reconciliation",
            "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
            "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution",
            "m2_d_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
        )
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous, full_d = (json.loads(path.read_text()) for path in (PREDECESSOR, FULL_D))
    errors: list[str] = []
    if (
        value.get("result_id") != "CLASSICAL_IMPORT_GATE_V6_RECONCILIATION"
        or value.get("result_state") != "FULL_D_AND_D_Q1_SCOPED_CERTIFIED_FULL_CARRIER_Q2_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/lifecycle/tags")

    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    old_exports = {row["export_id"]: row for row in previous["export_reconciliation"]}
    old_checks = {row["check_id"]: row for row in previous["freeze_check_reconciliation"]}
    if [row.get("export_id") for row in exports] != list(old_exports):
        errors.append("twenty-export identity/order")
    if [row.get("check_id") for row in checks] != list(old_checks):
        errors.append("ten-check identity/order")
    allowed_exports = {"local_D_action_on_bv_generators", "support_local_classical_bv_q2"}
    for row in exports:
        if row.get("export_id") not in allowed_exports and row != old_exports.get(row.get("export_id")):
            errors.append("unlicensed export mutation " + str(row.get("export_id")))
    export_map = {row["export_id"]: row for row in exports}
    d_export = export_map.get("local_D_action_on_bv_generators", {})
    if d_export.get("status") != "RECEIVER_VERIFIED_SCOPED" or d_export.get("evidence") != [full_d["result_id"]]:
        errors.append("strict D export promotion")
    if not all(token in " ".join(map(str, d_export.values())).lower() for token in ("386", "q2", "gate-a")):
        errors.append("strict D export evidence/boundary")
    q2_export = export_map.get("support_local_classical_bv_q2", {})
    if q2_export.get("status") != old_exports["support_local_classical_bv_q2"]["status"] or q2_export.get("evidence") != old_exports["support_local_classical_bv_q2"]["evidence"]:
        errors.append("q2 status/evidence mutation")
    if not all(token in (q2_export.get("remaining_for_gate_a", "") + q2_export.get("boundary", "")).lower() for token in ("386", "d/q2", "open")):
        errors.append("q2 remaining boundary")

    allowed_checks = {"D_q1_commutator_zero", "q1_q2_arity_two_nilpotency"}
    for row in checks:
        if row.get("check_id") not in allowed_checks and row != old_checks.get(row.get("check_id")):
            errors.append("unlicensed freeze-check mutation " + str(row.get("check_id")))
    check_map = {row["check_id"]: row for row in checks}
    d_q1 = check_map.get("D_q1_commutator_zero", {})
    if d_q1.get("status") != "RECEIVER_VERIFIED_SCOPED" or d_q1.get("evidence") != [full_d["result_id"]]:
        errors.append("D/q1 scoped promotion")
    if "4,374" not in d_q1.get("established", "") or "D/q2" not in d_q1.get("boundary", ""):
        errors.append("D/q1 evidence/boundary")
    if check_map.get("D_q2_derivation") != old_checks.get("D_q2_derivation"):
        errors.append("D/q2 check promoted")
    q1q2 = check_map.get("q1_q2_arity_two_nilpotency", {})
    if q1q2.get("status") != old_checks["q1_q2_arity_two_nilpotency"]["status"] or q1q2.get("evidence") != old_checks["q1_q2_arity_two_nilpotency"]["evidence"]:
        errors.append("q1q2 status/evidence mutation")
    if "not yet extended" not in q1q2.get("boundary", ""):
        errors.append("q1q2 full-carrier boundary")

    export_counts = {status: sum(row.get("status") == status for row in exports) for status in {
        "RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "LEGACY_ACCEPTED_SCOPED",
        "SUPPORTING_EVIDENCE_ONLY", "MISSING_PORTABLE_OBJECT",
    }}
    if export_counts != {"RECEIVER_VERIFIED_SCOPED": 11, "CERTIFIED_DIFFERENT_THEORY": 0, "LEGACY_ACCEPTED_SCOPED": 3, "SUPPORTING_EVIDENCE_ONLY": 6, "MISSING_PORTABLE_OBJECT": 0}:
        errors.append("export count firewall")
    check_counts = {status: sum(row.get("status") == status for row in checks) for status in {
        "RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "BLOCKED_MISSING_COMMON_SNAPSHOT",
    }}
    if check_counts != {"RECEIVER_VERIFIED_SCOPED": 8, "CERTIFIED_DIFFERENT_THEORY": 1, "BLOCKED_MISSING_COMMON_SNAPSHOT": 1}:
        errors.append("freeze-check count firewall")
    disposition = value.get("gate_disposition", {})
    expected_disposition = dict(previous["gate_disposition"])
    expected_disposition.update({
        "claim_state": "CLASSICAL_IMPORT_STRICT_FULL_D_AND_D_Q1_SCOPED_CERTIFIED_FULL_Q2_OPEN",
        "same_theory_receiver_verified_scoped": 11, "different_theory_controls": 0,
        "freeze_checks_receiver_verified_scoped": 8, "freeze_checks_different_theory": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    if disposition != expected_disposition:
        errors.append("Gate-A disposition")

    hashes = value.get("required_hash_disposition", {})
    if len(hashes) != 7 or any(row.get("accepted") is not None for row in hashes.values()):
        errors.append("accepted common hash promotion")
    expected_hashes = json.loads(json.dumps(previous["required_hash_disposition"]))
    expected_hashes["D_action_hash"].update({
        "accepted": None,
        "candidate": full_d["canonical_hashes"]["D_action_sha256"],
        "candidate_scope": "STRICT_386_UNARY_CAUSAL_D_SCOPED_NOT_GATE_A_COMMON_MANIFEST",
    })
    if hashes != expected_hashes:
        errors.append("D candidate hash disposition")

    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim promotion")
    for flag in (
        "STRICT_386_FULL_LOCAL_D_ACTION_SCOPED_REPLAY", "STRICT_386_D_Q1_COMMUTATOR_SCOPED_REPLAY",
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_SCOPED_REPLAY",
    ):
        if flags.get(flag) is not True:
            errors.append("missing D scoped flag " + flag)

    missing = value.get("minimal_missing_bundle", [])
    if [item.get("id") for item in missing] != [item.get("id") for item in previous["minimal_missing_bundle"]]:
        errors.append("six-family ledger identity/order")
    for item, old in zip(missing, previous["minimal_missing_bundle"], strict=True):
        if item.get("id") == "M2_STRICT_Q2_D":
            text = str(item.get("object", "")).lower()
            if not all(token in text for token in ("q2", "386", "d/q2", "no longer missing")) or "d_q1_commutator_zero" in item.get("unlocks", []):
                errors.append("M2 narrowed boundary")
        elif item != old:
            errors.append("unlicensed missing-family mutation " + str(item.get("id")))

    m2 = value.get("m2_d_resolution", {})
    replay = full_d["exact_replay"]
    if not (
        m2.get("status") == "STRICT_386_FULL_D_AND_D_Q1_RECEIVER_VERIFIED_SCOPED"
        and m2.get("evidence") == full_d["result_id"]
        and m2.get("carrier_rows") == 386 and m2.get("component_blocks") == 22
        and m2.get("D_component_coefficients") == 386
        and m2.get("q1_operator_tables_checked") == 27
        and m2.get("q1_rational_coefficients_checked") == 4374
        and m2.get("D_q1_commutator_defects") == 0
        and m2.get("pairing_entries_checked") == 410
        and m2.get("scoped_snapshot_hashes") == 14
        and m2.get("D_action_sha256") == full_d["canonical_hashes"]["D_action_sha256"]
        and replay["D_q1_commutator_defects"] == 0
    ):
        errors.append("M2 D resolution")
    if value.get("m3_scoped_resolution") != previous.get("m3_scoped_resolution") or value.get("m4_minimal_resolution") != previous.get("m4_minimal_resolution"):
        errors.append("M3/M4 regression")

    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(PREDECESSOR), "role": "immutable Gate-A V5 predecessor"},
        {"path": str(FULL_D.relative_to(ROOT)), "result_or_artifact_id": full_d["result_id"], "sha256": file_hash(FULL_D), "role": "strict 386-row full D action and D/q1 receiver replay"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for source in expected_inputs[-2:]:
        path = ROOT / source["path"]
        if not path.is_file() or file_hash(path) != source["sha256"]:
            errors.append("direct provenance " + source["path"])
    drift_entries = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = file_hash(path) if path.is_file() else None
        if current != source["sha256"]:
            drift_entries.append({
                "path": source["path"],
                "historical_v5_sha256": source["sha256"],
                "current_worktree_sha256": current,
                "status": "RECORDED_NOT_SILENTLY_REBOUND",
                "disposition": "V5 remains the content-pinned authority for its historical claim; the changed current file is not substituted without an independent successor replay.",
            })
    expected_drift = {
        "files_checked": len(previous["provenance"]["inputs"]),
        "drifted_files": len(drift_entries),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED",
        "entries": drift_entries,
    }
    if value.get("transitive_provenance_drift") != expected_drift or not drift_entries:
        errors.append("transitive provenance drift ledger")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    if value.get("supersedes_for_current_status") != previous.get("result_id") or value.get("historical_certificate_preserved") is not True:
        errors.append("predecessor/history preservation")
    return errors, {"exports": len(exports), "checks": len(checks), "inputs": len(expected_inputs)}


def main() -> int:
    errors, counts = check()
    print("CLASSICAL_IMPORT_GATE_V6_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - strict full D and D/q1 reconcile across {counts['inputs']} content pins")
        print("  - full-carrier q2, D/q2, all common hashes and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
