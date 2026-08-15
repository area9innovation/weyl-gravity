#!/usr/bin/env python3
"""Independent fail-closed audit of Gate-A reconciliation v4."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V4_RECONCILIATION.json"
PREDECESSOR = HERE / "certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
IDENTITY = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
FALSE_FLAGS = {
    "CLASSICAL_IMPORT_GATE_PASSED",
    "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
    "LORENTZIAN_QUANTUM_THEORY",
    "QME_RESTORED",
    "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay",
            "status_vocabulary",
            "export_reconciliation",
            "freeze_check_reconciliation",
            "required_hash_disposition",
            "minimal_missing_bundle",
            "gate_disposition",
            "m3_scoped_resolution",
            "m2_minimal_resolution",
        )
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous, q1, q2, identity = (json.loads(path.read_text()) for path in (PREDECESSOR, Q1, Q2, IDENTITY))
    errors: list[str] = []
    exports, checks = value.get("export_reconciliation", []), value.get("freeze_check_reconciliation", [])
    previous_exports, previous_checks = previous["export_reconciliation"], previous["freeze_check_reconciliation"]
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous_exports]:
        errors.append("twenty-export identity/order")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous_checks]:
        errors.append("ten-check identity/order")
    old_exports = {row["export_id"]: row for row in previous_exports}
    old_checks = {row["check_id"]: row for row in previous_checks}
    for row in exports:
        if row.get("export_id") == "support_local_classical_bv_q2":
            if row.get("status") != "RECEIVER_VERIFIED_SCOPED" or row.get("evidence") != ["STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "STRICT_LOCAL_Q1_Q2_IDENTITY_V1"]:
                errors.append("minimal q2 scoped promotion")
            text = " ".join(str(row.get(key, "")) for key in ("established", "remaining_for_gate_a", "boundary")).lower()
            if not all(token in text for token in ("minimal", "full carrier", "local d", "cyclic")):
                errors.append("minimal q2 full-carrier boundary")
        elif row != old_exports.get(row.get("export_id")):
            errors.append("unlicensed export mutation " + str(row.get("export_id")))
    for row in checks:
        if row.get("check_id") == "q1_q2_arity_two_nilpotency":
            if row.get("status") != "RECEIVER_VERIFIED_SCOPED" or row.get("evidence") != ["STRICT_PORTABLE_LOCAL_Q1_AST_V1", "STRICT_LOCAL_Q1_Q2_IDENTITY_V1"]:
                errors.append("q1q2 scoped promotion")
            text = " ".join(str(row.get(key, "")) for key in ("established", "remaining_for_gate_a", "boundary")).lower()
            if not all(token in text for token in ("eighteen", "fifty-one", "full support-local", "not a d identity")):
                errors.append("q1q2 scope boundary")
        elif row != old_checks.get(row.get("check_id")):
            errors.append("unlicensed freeze-check mutation " + str(row.get("check_id")))

    export_counts = {status: sum(row.get("status") == status for row in exports) for status in {"RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "LEGACY_ACCEPTED_SCOPED", "SUPPORTING_EVIDENCE_ONLY", "MISSING_PORTABLE_OBJECT"}}
    if export_counts != {"RECEIVER_VERIFIED_SCOPED": 9, "CERTIFIED_DIFFERENT_THEORY": 1, "LEGACY_ACCEPTED_SCOPED": 3, "SUPPORTING_EVIDENCE_ONLY": 7, "MISSING_PORTABLE_OBJECT": 0}:
        errors.append("export count firewall")
    check_counts = {status: sum(row.get("status") == status for row in checks) for status in {"RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "BLOCKED_MISSING_COMMON_SNAPSHOT"}}
    if check_counts != {"RECEIVER_VERIFIED_SCOPED": 6, "CERTIFIED_DIFFERENT_THEORY": 3, "BLOCKED_MISSING_COMMON_SNAPSHOT": 1}:
        errors.append("freeze-check count firewall")
    expected_disposition = dict(previous["gate_disposition"])
    expected_disposition.update({"claim_state": "CLASSICAL_IMPORT_MINIMAL_Q1_Q2_REPAIRED_D_PAIRING_FULL_CARRIER_OPEN", "same_theory_receiver_verified_scoped": 9, "different_theory_controls": 1, "freeze_checks_receiver_verified_scoped": 6, "freeze_checks_different_theory": 3})
    if value.get("gate_disposition") != expected_disposition:
        errors.append("Gate-A disposition")
    hashes = value.get("required_hash_disposition", {})
    if len(hashes) != 7 or any(item.get("accepted") is not None for item in hashes.values()):
        errors.append("accepted common hash promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim promotion")
    if flags.get("STRICT_MINIMAL_LOCAL_Q1_Q2_SCOPED_REPLAY") is not True or flags.get("STRICT_MINIMAL_Q1_Q2_ARITY_TWO_IDENTITY") is not True:
        errors.append("minimal q1/q2 scoped flags")

    missing = value.get("minimal_missing_bundle", [])
    if [item.get("id") for item in missing] != [item.get("id") for item in previous["minimal_missing_bundle"]]:
        errors.append("six-family ledger identity/order")
    else:
        for item, old in zip(missing, previous["minimal_missing_bundle"]):
            if item.get("id") == "M2_STRICT_Q2_D":
                text = str(item.get("object", "")).lower()
                if not all(token in text for token in ("certified strict minimal", "common full support-local", "local d", "nonminimal")):
                    errors.append("M2 narrowed boundary")
            elif item != old:
                errors.append("unlicensed missing-family mutation " + str(item.get("id")))

    resolution = value.get("m2_minimal_resolution", {})
    expected_resolution = {
        "status": "STRICT_MINIMAL_Q1_Q2_AND_ARITY_TWO_IDENTITY_CERTIFIED",
        "evidence": [q1["result_id"], q2["result_id"], identity["result_id"]],
        "generator_count": 6,
        "q1_component_count": 5,
        "q2_primary_component_count": 12,
        "q2_ordered_component_count": 22,
        "q1q2_channel_count": 18,
        "q1q2_path_count": 51,
        "remaining": "The complete local D action, [D,q1], D derivation, common BV pairing/cyclicity, any full-carrier nonminimal extension, and accepted common snapshot hashes remain open.",
        "boundary": "This resolves the strict minimal local q1/q2 arity-two layer, not the complete M2/M4 full-carrier Gate-A bundle.",
    }
    if resolution != expected_resolution:
        errors.append("M2 minimal resolution")
    if value.get("m3_scoped_resolution") != previous.get("m3_scoped_resolution"):
        errors.append("M3 regression")

    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(PREDECESSOR), "role": "immutable Gate-A V3 predecessor"},
        {"path": str(Q1.relative_to(ROOT)), "result_or_artifact_id": q1["result_id"], "sha256": file_hash(Q1), "role": "portable strict minimal q1 and q1-square theorem"},
        {"path": str(Q2.relative_to(ROOT)), "result_or_artifact_id": q2["result_id"], "sha256": file_hash(Q2), "role": "portable six-row ordered strict minimal q2 ledger"},
        {"path": str(IDENTITY.relative_to(ROOT)), "result_or_artifact_id": identity["result_id"], "sha256": file_hash(IDENTITY), "role": "independent strict minimal arity-two receiver theorem"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for source in expected_inputs:
        path = ROOT / source["path"]
        if not path.is_file() or file_hash(path) != source["sha256"]:
            errors.append("provenance " + source["path"])
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    if value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("predecessor identity")
    if value.get("historical_certificate_preserved") is not True:
        errors.append("historical certificate preservation")
    return errors, {"exports": len(exports), "checks": len(checks), "inputs": len(expected_inputs), "channels": resolution.get("q1q2_channel_count", 0), "paths": resolution.get("q1q2_path_count", 0)}


def main() -> int:
    errors, counts = check()
    print("CLASSICAL_IMPORT_GATE_V4_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['channels']} channels / {counts['paths']} paths reconcile minimal q1/q2 across {counts['inputs']} pinned inputs")
        print("  - D, pairing, common hashes, and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
