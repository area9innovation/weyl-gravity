#!/usr/bin/env python3
"""Independently check Gate-A v20 and the typed M4 replacement."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
V19 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
M4L_CHECKER = HERE / "check_strict_386_local_cyclic_pairing_closure.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m4_typed_local_cyclicity_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


def checker_module():
    spec = importlib.util.spec_from_file_location("m4l_checker_for_gate", M4L_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def one(items: list[dict[str, Any]], key: str, wanted: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == wanted]
    return matches[0] if len(matches) == 1 else {}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous = json.loads(V19.read_text())
    closure = json.loads(M4L.read_text())
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V20_RECONCILIATION" or value.get("lifecycle") != previous.get("lifecycle"):
        errors.append("identity/lifecycle")
    if checker_module().check(closure):
        errors.append("independent M4L replay")
    pins = value.get("provenance", {}).get("inputs", [])
    for path, result_id in ((V19, previous["result_id"]), (M4L, closure["result_id"])):
        matches = [item for item in pins if item.get("result_or_artifact_id") == result_id and item.get("sha256") == sha(path)]
        if not matches:
            errors.append("provenance pin " + result_id)
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate census")
    gate = value.get("gate_disposition", {})
    if (
        gate.get("exports_total") != 20 or gate.get("same_theory_receiver_verified_scoped") != 17
        or gate.get("freeze_checks_total") != 10 or gate.get("freeze_checks_receiver_verified_scoped") != 9
        or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("gate_a_status") != "FAIL_CLOSED"
        or gate.get("publishable_quantum_results_allowed_by_gate_a") is not False
    ):
        errors.append("Gate disposition counts")
    missing = value.get("minimal_missing_bundle", [])
    if [item.get("id") for item in missing] != ["M1_COMMON_STRICT_SNAPSHOT", "M3R_TYPED_RESIDUAL_COMPARISON", "M4R_TYPED_RESIDUAL_CYCLICITY"]:
        errors.append("typed missing bundle")
    if any(item.get("id") == "M4_FULL_CYCLIC_PAIRING" for item in missing):
        errors.append("unsplit M4 retained")
    resolution = value.get("m4_typed_local_cyclicity_resolution", {})
    expected_resolution = {
        "status": "M4L_RECEIVER_VERIFIED_SCOPED_COMPLETE_M4R_OPEN",
        "evidence": closure["result_id"],
        "certificate_sha256": sha(M4L),
        "carrier_rows": 386,
        "pairing_entries": 410,
        "exact_pairing_rank": 386,
        "local_cyclicity_defects": 0,
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": "COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN_BLOCKED_BY_M3R",
        "accepted_common_snapshot_hashes_added": 0,
    }
    if resolution != expected_resolution:
        errors.append("M4 resolution projection")
    cyclic_export = one(value.get("export_reconciliation", []), "export_id", "cyclic_pairing")
    cyclic_check = one(value.get("freeze_check_reconciliation", []), "check_id", "cyclic_compatibility")
    if closure["result_id"] not in cyclic_export.get("evidence", []) or cyclic_export.get("status") != "RECEIVER_VERIFIED_SCOPED":
        errors.append("cyclic-pairing export")
    if cyclic_check.get("status") != "BLOCKED_MISSING_TYPED_RESIDUAL_COMPARISON" or closure["result_id"] not in cyclic_check.get("evidence", []):
        errors.append("residual cyclic check")
    if value.get("required_hash_disposition", {}).get("pairing_hash") != {
        "accepted": None,
        "candidate": closure["pairing_replay"]["pairing_sha256"],
        "candidate_scope": "STRICT_386_FULL_LOCAL_PAIRING_M4L_COMPLETE_M4R_AND_M1_OPEN",
    }:
        errors.append("pairing hash disposition")
    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_FULL_LOCAL_ODD_PAIRING_NONDEGENERATE",
        "STRICT_386_LOCAL_Q1_SDR_D_Q2_Q3_CYCLICITY_COMPLETE",
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED", "COMMON_GATE_A_FREEZE_BOUND",
        "CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    try:
        expected_digest = digest(value)
    except KeyError as error:
        errors.append("digest projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
            errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V20_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
