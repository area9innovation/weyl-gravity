#!/usr/bin/env python3
"""Independent fail-closed audit of Gate-A reconciliation v3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
PREDECESSOR = DIRECTORY / "certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json"
SDR = DIRECTORY / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
MAP_IDS = (
    "classical_inclusion_iota_cl",
    "classical_projection_pi_cl",
    "classical_homotopy_s_cl",
)
IDENTITY_IDS = (
    "pi_cl_iota_cl_identity",
    "classical_contraction_identity",
    "q0_iota_intertwining",
    "pi_q0_intertwining",
)
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
        )
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(PREDECESSOR.read_text())
    sdr = json.loads(SDR.read_text())
    errors: list[str] = []

    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    previous_exports = previous.get("export_reconciliation", [])
    previous_checks = previous.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous_exports]:
        errors.append("twenty-export identity/order")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous_checks]:
        errors.append("ten-check identity/order")

    previous_export_by_id = {row["export_id"]: row for row in previous_exports}
    previous_check_by_id = {row["check_id"]: row for row in previous_checks}
    for row in exports:
        export_id = row.get("export_id")
        if export_id in MAP_IDS:
            if row.get("status") != "RECEIVER_VERIFIED_SCOPED":
                errors.append("finite map status " + str(export_id))
            if row.get("evidence") != ["STRICT_DFINITE_RESIDUAL_SDR_V1"]:
                errors.append("finite map evidence " + str(export_id))
            text = " ".join(str(row.get(key, "")) for key in ("established", "remaining_for_gate_a", "boundary")).lower()
            if "finite" not in text or "common" not in text or "support-local" not in text:
                errors.append("finite map scope boundary " + str(export_id))
        elif row != previous_export_by_id.get(export_id):
            errors.append("unlicensed export mutation " + str(export_id))
    for row in checks:
        check_id = row.get("check_id")
        if check_id in IDENTITY_IDS:
            if row.get("status") != "RECEIVER_VERIFIED_SCOPED":
                errors.append("finite identity status " + str(check_id))
            if row.get("evidence") != ["STRICT_DFINITE_RESIDUAL_SDR_V1"]:
                errors.append("finite identity evidence " + str(check_id))
            text = " ".join(str(row.get(key, "")) for key in ("established", "remaining_for_gate_a", "boundary")).lower()
            if "common" not in text or "support-local" not in text:
                errors.append("finite identity scope boundary " + str(check_id))
        elif row != previous_check_by_id.get(check_id):
            errors.append("unlicensed freeze-check mutation " + str(check_id))

    export_counts = {
        status: sum(row.get("status") == status for row in exports)
        for status in {
            "RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY",
            "LEGACY_ACCEPTED_SCOPED", "SUPPORTING_EVIDENCE_ONLY",
            "MISSING_PORTABLE_OBJECT",
        }
    }
    check_counts = {
        status: sum(row.get("status") == status for row in checks)
        for status in {
            "RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY",
            "BLOCKED_MISSING_COMMON_SNAPSHOT",
        }
    }
    if export_counts != {
        "RECEIVER_VERIFIED_SCOPED": 8,
        "CERTIFIED_DIFFERENT_THEORY": 2,
        "LEGACY_ACCEPTED_SCOPED": 3,
        "SUPPORTING_EVIDENCE_ONLY": 7,
        "MISSING_PORTABLE_OBJECT": 0,
    }:
        errors.append("export count firewall")
    if check_counts != {
        "RECEIVER_VERIFIED_SCOPED": 5,
        "CERTIFIED_DIFFERENT_THEORY": 4,
        "BLOCKED_MISSING_COMMON_SNAPSHOT": 1,
    }:
        errors.append("freeze-check count firewall")

    disposition = value.get("gate_disposition", {})
    expected_disposition = {
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_DFINITE_SDR_REPAIRED_FULL_CARRIER_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
        "exports_total": 20,
        "same_theory_receiver_verified_scoped": 8,
        "different_theory_controls": 2,
        "legacy_accepted_scoped": 3,
        "supporting_evidence_only": 7,
        "missing_portable_objects": 0,
        "freeze_checks_total": 10,
        "freeze_checks_receiver_verified_scoped": 5,
        "freeze_checks_different_theory": 4,
        "freeze_checks_blocked": 1,
        "accepted_common_snapshot_hashes": 0,
        "rule": previous["gate_disposition"]["rule"],
    }
    if disposition != expected_disposition:
        errors.append("Gate-A disposition")
    hashes = value.get("required_hash_disposition", {})
    if len(hashes) != 7 or any(item.get("accepted") is not None for item in hashes.values()):
        errors.append("accepted common hash promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim promotion")
    if flags.get("STRICT_DFINITE_M3_SCOPED_REPLAY") is not True:
        errors.append("scoped replay flag")

    missing = value.get("minimal_missing_bundle", [])
    if [item.get("id") for item in missing] != [item.get("id") for item in previous.get("minimal_missing_bundle", [])]:
        errors.append("six-family ledger identity/order")
    else:
        for item, old_item in zip(missing, previous["minimal_missing_bundle"]):
            if item.get("id") == "M3_RESIDUAL_SDR":
                text = str(item.get("object", "")).lower()
                if not all(token in text for token in ("extend or reconstruct", "common full support-local", "finite")):
                    errors.append("M3 carrier-extension boundary")
            elif item != old_item:
                errors.append("unlicensed missing-family mutation " + str(item.get("id")))

    scoped = value.get("m3_scoped_resolution", {})
    expected_scoped = {
        "status": "SCOPED_PORTABILITY_AND_IDENTITIES_CERTIFIED",
        "evidence": "STRICT_DFINITE_RESIDUAL_SDR_V1",
        "full_coordinates": sdr.get("global_direct_sum", {}).get("full_dimension"),
        "residual_coordinates": sdr.get("global_direct_sum", {}).get("residual_dimension"),
        "energies": sdr.get("scope", {}).get("energies"),
        "residual_sdr_hash": sdr.get("global_direct_sum", {}).get("residual_sdr_hash"),
        "remaining": sdr.get("gate_a_effect", {}).get("remaining_m3_gap"),
        "boundary": "This resolves the missing portable object in a finite split scope, not the common full support-local M3 gate.",
    }
    if scoped != expected_scoped:
        errors.append("M3 scoped resolution")

    expected_inputs = [
        *previous.get("provenance", {}).get("inputs", []),
        {
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "result_or_artifact_id": previous.get("result_id"),
            "sha256": file_hash(PREDECESSOR),
            "role": "immutable Gate-A V2 predecessor",
        },
        {
            "path": str(SDR.relative_to(ROOT)),
            "result_or_artifact_id": sdr.get("result_id"),
            "sha256": file_hash(SDR),
            "role": "same-theory scoped portable residual SDR and independent identity replay",
        },
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for source in expected_inputs:
        path = ROOT / source["path"]
        if not path.is_file() or file_hash(path) != source["sha256"]:
            errors.append("provenance " + source["path"])

    checker = value.get("independent_checker", {})
    if checker.get("expected_digest") != digest(value):
        errors.append("canonical digest")
    if value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("predecessor identity")
    if value.get("historical_certificate_preserved") is not True:
        errors.append("historical certificate preservation")
    return errors, {
        "exports": len(exports),
        "checks": len(checks),
        "inputs": len(expected_inputs),
        "scoped_maps": len(MAP_IDS),
        "scoped_identities": len(IDENTITY_IDS),
    }


def main() -> int:
    errors, counts = check()
    print("CLASSICAL_IMPORT_GATE_V3_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(
            f"  - {counts['scoped_maps']} maps and {counts['scoped_identities']} identities "
            f"reconciled across {counts['inputs']} content-pinned inputs"
        )
        print("  - portable-object absence closed in finite scope; common support-local Gate A remains fail-closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
