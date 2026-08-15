#!/usr/bin/env python3
"""Independent fail-closed audit of Gate-A reconciliation v5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
PREDECESSOR = HERE / "certificates/CLASSICAL_IMPORT_GATE_V4_RECONCILIATION.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
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
            "standalone_history_replay", "status_vocabulary",
            "export_reconciliation", "freeze_check_reconciliation",
            "required_hash_disposition", "minimal_missing_bundle",
            "gate_disposition", "m3_scoped_resolution",
            "m2_minimal_resolution", "m4_minimal_resolution",
        )
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous, cyclic = (json.loads(path.read_text()) for path in (PREDECESSOR, CYCLIC))
    errors: list[str] = []
    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    old_exports = {row["export_id"]: row for row in previous["export_reconciliation"]}
    old_checks = {row["check_id"]: row for row in previous["freeze_check_reconciliation"]}
    if [row.get("export_id") for row in exports] != list(old_exports):
        errors.append("twenty-export identity/order")
    if [row.get("check_id") for row in checks] != list(old_checks):
        errors.append("ten-check identity/order")

    allowed_exports = {"local_classical_bv_differential_q0", "support_local_classical_bv_q2", "cyclic_pairing"}
    for row in exports:
        export_id = row.get("export_id")
        if export_id not in allowed_exports and row != old_exports.get(export_id):
            errors.append("unlicensed export mutation " + str(export_id))
    export_map = {row["export_id"]: row for row in exports}
    pairing = export_map.get("cyclic_pairing", {})
    if pairing.get("status") != "RECEIVER_VERIFIED_SCOPED" or pairing.get("evidence") != [cyclic["result_id"]]:
        errors.append("minimal cyclic-pairing scoped promotion")
    if not all(token in " ".join(map(str, pairing.values())).lower() for token in ("thirty", "minimal", "nonminimal", "residual")):
        errors.append("minimal pairing full-carrier boundary")
    q2 = export_map.get("support_local_classical_bv_q2", {})
    if q2.get("status") != "RECEIVER_VERIFIED_SCOPED" or cyclic["result_id"] not in q2.get("evidence", []):
        errors.append("translated minimal q2 evidence")
    q0 = export_map.get("local_classical_bv_differential_q0", {})
    if q0.get("status") != "RECEIVER_VERIFIED_SCOPED" or cyclic["result_id"] not in q0.get("evidence", []):
        errors.append("translated minimal q1 evidence")

    allowed_checks = {"q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility"}
    for row in checks:
        check_id = row.get("check_id")
        if check_id not in allowed_checks and row != old_checks.get(check_id):
            errors.append("unlicensed freeze-check mutation " + str(check_id))
    check_map = {row["check_id"]: row for row in checks}
    q2_cyclic = check_map.get("q2_cyclic_compatibility", {})
    if q2_cyclic.get("status") != "RECEIVER_VERIFIED_SCOPED" or q2_cyclic.get("evidence") != [cyclic["result_id"]]:
        errors.append("minimal q2 cyclicity scoped promotion")
    if "932" not in q2_cyclic.get("established", "") or "full" not in q2_cyclic.get("remaining_for_gate_a", ""):
        errors.append("q2 cyclicity evidence or full-carrier boundary")
    q1q2 = check_map.get("q1_q2_arity_two_nilpotency", {})
    if q1q2.get("status") != "RECEIVER_VERIFIED_SCOPED" or q1q2.get("evidence") != ["STRICT_LOCAL_Q1_Q2_IDENTITY_V1", cyclic["result_id"]]:
        errors.append("translated q1q2 evidence")
    if check_map.get("cyclic_compatibility") != old_checks.get("cyclic_compatibility"):
        errors.append("full cyclic-SDR check was promoted")
    for check_id in ("D_q1_commutator_zero", "D_q2_derivation"):
        if check_map.get(check_id) != old_checks.get(check_id):
            errors.append("D check mutated " + check_id)

    export_counts = {status: sum(row.get("status") == status for row in exports) for status in {"RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "LEGACY_ACCEPTED_SCOPED", "SUPPORTING_EVIDENCE_ONLY", "MISSING_PORTABLE_OBJECT"}}
    if export_counts != {"RECEIVER_VERIFIED_SCOPED": 10, "CERTIFIED_DIFFERENT_THEORY": 1, "LEGACY_ACCEPTED_SCOPED": 3, "SUPPORTING_EVIDENCE_ONLY": 6, "MISSING_PORTABLE_OBJECT": 0}:
        errors.append("export count firewall")
    check_counts = {status: sum(row.get("status") == status for row in checks) for status in {"RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "BLOCKED_MISSING_COMMON_SNAPSHOT"}}
    if check_counts != {"RECEIVER_VERIFIED_SCOPED": 7, "CERTIFIED_DIFFERENT_THEORY": 2, "BLOCKED_MISSING_COMMON_SNAPSHOT": 1}:
        errors.append("freeze-check count firewall")
    disposition = value.get("gate_disposition", {})
    expected_disposition = dict(previous["gate_disposition"])
    expected_disposition.update(
        {
            "claim_state": "CLASSICAL_IMPORT_MINIMAL_Q1_Q2_PAIRING_CYCLIC_REPAIRED_D_FULL_CARRIER_OPEN",
            "same_theory_receiver_verified_scoped": 10,
            "different_theory_controls": 1,
            "supporting_evidence_only": 6,
            "freeze_checks_receiver_verified_scoped": 7,
            "freeze_checks_different_theory": 2,
        }
    )
    if disposition != expected_disposition:
        errors.append("Gate-A disposition")
    hashes = value.get("required_hash_disposition", {})
    if len(hashes) != 7 or any(row.get("accepted") is not None for row in hashes.values()):
        errors.append("accepted common hash promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim promotion")
    if any(flags.get(flag) is not True for flag in ("STRICT_MINIMAL_CANONICAL_PAIRING_SCOPED_REPLAY", "STRICT_MINIMAL_Q1_Q2_CYCLICITY_SCOPED_REPLAY", "CANONICAL_GHOST_ANTIFIELD_SIGN_TRANSLATION")):
        errors.append("minimal cyclic scoped flags")

    missing = value.get("minimal_missing_bundle", [])
    if [item.get("id") for item in missing] != [item.get("id") for item in previous["minimal_missing_bundle"]]:
        errors.append("six-family ledger identity/order")
    for item, old in zip(missing, previous["minimal_missing_bundle"]):
        if item.get("id") in {"M2_STRICT_Q2_D", "M4_FULL_CYCLIC_PAIRING"}:
            text = str(item.get("object", "")).lower()
            if not all(token in text for token in (("minimal", "common", "d") if item["id"].startswith("M2") else ("rank-thirty", "nonminimal", "residual"))):
                errors.append(item["id"] + " narrowed boundary")
        elif item != old:
            errors.append("unlicensed missing-family mutation " + str(item.get("id")))

    m4 = value.get("m4_minimal_resolution", {})
    if (
        m4.get("status") != "STRICT_MINIMAL_CANONICAL_PAIRING_AND_Q1_Q2_CYCLICITY_CERTIFIED"
        or m4.get("evidence") != cyclic["result_id"]
        or m4.get("component_basis_dimension") != 30
        or m4.get("pairing_rank") != 30
        or m4.get("expanded_non_Bach_q2_coefficient_count") != 932
        or m4.get("source_convention_defect_coefficient_count") != 540
        or m4.get("translated_convention_defect_coefficient_count") != 0
    ):
        errors.append("M4 minimal resolution")
    m2 = value.get("m2_minimal_resolution", {})
    if m2.get("status") != "STRICT_MINIMAL_Q1_Q2_ARITY_TWO_AND_CYCLIC_CONVENTION_CERTIFIED" or m2.get("evidence", [])[-1:] != [cyclic["result_id"]]:
        errors.append("M2 minimal resolution")
    if value.get("m3_scoped_resolution") != previous.get("m3_scoped_resolution"):
        errors.append("M3 regression")

    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(PREDECESSOR), "role": "immutable Gate-A V4 predecessor"},
        {"path": str(CYCLIC.relative_to(ROOT)), "result_or_artifact_id": cyclic["result_id"], "sha256": file_hash(CYCLIC), "role": "canonical minimal pairing and cyclic sign reconciliation"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for source in expected_inputs:
        path = ROOT / source["path"]
        if not path.is_file() or file_hash(path) != source["sha256"]:
            errors.append("provenance " + source["path"])
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    if value.get("supersedes_for_current_status") != previous.get("result_id") or value.get("historical_certificate_preserved") is not True:
        errors.append("predecessor or history preservation")
    return errors, {"exports": len(exports), "checks": len(checks), "inputs": len(expected_inputs)}


def main() -> int:
    errors, counts = check()
    print("CLASSICAL_IMPORT_GATE_V5_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - rank-30 pairing and 540-to-zero cyclic repair reconcile across {counts['inputs']} pins")
        print("  - local D, full carrier, common hashes and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
