#!/usr/bin/env python3
"""Independently check Gate-A v8 and its nonlinear-equivalence boundary."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
V7 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
OBSTRUCTION = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def digest(value: dict[str, Any]) -> str:
    keys = ("standalone_history_replay", "status_vocabulary", "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution", "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction", "m4_minimal_resolution", "transitive_provenance_drift")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text()); previous = json.loads(V7.read_text()); obstruction = json.loads(OBSTRUCTION.read_text()); classical = json.loads(CLASSICAL.read_text()); errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V8_RECONCILIATION" or value.get("result_state") != "LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_REQUIRED_GATE_FAIL_CLOSED" or value.get("supersedes_for_current_status") != previous["result_id"] or value.get("lifecycle") != "CLASSIFIED": errors.append("identity/predecessor/lifecycle")
    exports, checks = value.get("export_reconciliation", []), value.get("freeze_check_reconciliation", [])
    if [x.get("export_id") for x in exports] != [x.get("export_id") for x in previous["export_reconciliation"]] or len(exports) != 20: errors.append("export inventory")
    if [x.get("check_id") for x in checks] != [x.get("check_id") for x in previous["freeze_check_reconciliation"]] or len(checks) != 10: errors.append("check inventory")
    export = {x["export_id"]: x for x in exports}["support_local_classical_bv_q2"]
    if classical["result_id"] not in export.get("evidence", []) or obstruction["result_id"] not in export.get("evidence", []) or "-1" not in export.get("established", ""): errors.append("q2 obstruction projection")
    p = value.get("m2_theory_identity_obstruction", {})
    expected = {"status": "LITERAL_AND_LINEAR_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN", "classical_evidence": classical["result_id"], "receiver_evidence": obstruction["result_id"], "carrier_rows": 386, "cyclic_form_channel": "Omega(f_hat,q2(v,v))", "source_value": "-1", "candidate_value": "0", "defect": "-1", "candidate_internal_identities_preserved": True, "nonlinear_equivalence_may_exist": True, "nonlinear_equivalence_constructed": False, "nonlinear_equivalence_obstructed": False, "first_required_correction": obstruction["theory_identity_disposition"]["first_required_correction"]}
    if p != expected: errors.append("M2 theory-identity obstruction")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0 or gate.get("claim_state") != "CLASSICAL_IMPORT_LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN": errors.append("Gate-A disposition")
    q2_hash = value.get("required_hash_disposition", {}).get("q2_hash", {})
    if q2_hash.get("accepted") is not None or q2_hash.get("candidate_scope") != "LITERAL_SOURCE_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN": errors.append("q2 hash disposition")
    m2 = next((x for x in value.get("minimal_missing_bundle", []) if x.get("id") == "M2_STRICT_Q2_D"), {})
    if "Omega(f_hat,q2(v,v))=-1" not in m2.get("object", "") or len(m2.get("unlocks", [])) != 3: errors.append("M2 next object")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_LITERAL_TRIVIAL_STABILIZATION_IDENTITY_REFUTED", "STRICT_386_LINEAR_SHEAR_THEORY_IDENTITY_REFUTED", "STRICT_386_CANDIDATE_INTERNAL_IDENTITIES_PRESERVED", "STRICT_386_NONLINEAR_EQUIVALENCE_MAY_EXIST"):
        if flags.get(key) is not True: errors.append("positive flag " + key)
    for key in ("STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED", "STRICT_386_NONLINEAR_EQUIVALENCE_OBSTRUCTED", "STRICT_386_CANDIDATE_THEORY_IDENTITY", "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2", "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(key) is not False: errors.append("promotion flag " + key)
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3: errors.append("provenance count")
    else:
        for item, path, result_id in zip(provenance[-3:], (V7, CLASSICAL, OBSTRUCTION), (previous["result_id"], classical["result_id"], obstruction["result_id"])):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path) or item.get("result_or_artifact_id") != result_id: errors.append("direct provenance " + path.name)
    expected_drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]; current = sha(path) if path.is_file() else None
        if current != source["sha256"]: expected_drift.append((source["path"], source["sha256"], current))
    drift = value.get("transitive_provenance_drift", {})
    actual = [(x.get("path"), x.get("historical_v7_sha256"), x.get("current_worktree_sha256")) for x in drift.get("entries", [])]
    if drift.get("files_checked") != len(previous["provenance"]["inputs"]) or drift.get("drifted_files") != len(expected_drift) or actual != expected_drift: errors.append("transitive provenance drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value): errors.append("canonical digest")
    return errors

def main() -> int:
    errors = check(); print("CLASSICAL_IMPORT_GATE_V8_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors: print("  - " + error)
    return bool(errors)

if __name__ == "__main__": raise SystemExit(main())
