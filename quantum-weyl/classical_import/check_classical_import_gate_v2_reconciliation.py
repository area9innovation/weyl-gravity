#!/usr/bin/env python3
"""Independent boundary checker for the current Gate-A reconciliation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json"
EXPORT_IDS = ["field_ghost_antifield_dictionary", "field_gradings", "local_classical_bv_differential_q0", "support_local_classical_bv_q2", "local_D_action_on_bv_generators", "gauge_fixed_nonminimal_contractions", "trace_sector_contraction", "conformal_killing_zero_modes_15", "residual_representation_matrices", "so42_structure_constants", "classical_inclusion_iota_cl", "classical_projection_pi_cl", "classical_homotopy_s_cl", "cyclic_pairing", "taub_moment_map_normalization", "bfv_suspension_convention", "positive_frequency_state_ledger", "normalized_weyl_square_representatives", "centered_cohomology_bases_h3_h4_h5", "residual_differential_q_res_0"]
CHECK_IDS = ["q0_squared_zero", "q1_q2_arity_two_nilpotency", "D_q1_commutator_zero", "D_q2_derivation", "q2_cyclic_compatibility", "pi_cl_iota_cl_identity", "classical_contraction_identity", "q0_iota_intertwining", "pi_q0_intertwining", "cyclic_compatibility"]
STATUSES = {"RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "LEGACY_ACCEPTED_SCOPED", "SUPPORTING_EVIDENCE_ONLY", "MISSING_PORTABLE_OBJECT", "BLOCKED_MISSING_COMMON_SNAPSHOT"}
EXPORT_STATUS = ["RECEIVER_VERIFIED_SCOPED", "RECEIVER_VERIFIED_SCOPED", "RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "CERTIFIED_DIFFERENT_THEORY", "RECEIVER_VERIFIED_SCOPED", "RECEIVER_VERIFIED_SCOPED", "SUPPORTING_EVIDENCE_ONLY", "SUPPORTING_EVIDENCE_ONLY", "SUPPORTING_EVIDENCE_ONLY", "MISSING_PORTABLE_OBJECT", "MISSING_PORTABLE_OBJECT", "MISSING_PORTABLE_OBJECT", "SUPPORTING_EVIDENCE_ONLY", "LEGACY_ACCEPTED_SCOPED", "LEGACY_ACCEPTED_SCOPED", "LEGACY_ACCEPTED_SCOPED", "SUPPORTING_EVIDENCE_ONLY", "SUPPORTING_EVIDENCE_ONLY", "SUPPORTING_EVIDENCE_ONLY"]
CHECK_STATUS = ["RECEIVER_VERIFIED_SCOPED", "CERTIFIED_DIFFERENT_THEORY", "CERTIFIED_DIFFERENT_THEORY", "CERTIFIED_DIFFERENT_THEORY", "CERTIFIED_DIFFERENT_THEORY", "BLOCKED_MISSING_COMMON_SNAPSHOT", "BLOCKED_MISSING_COMMON_SNAPSHOT", "BLOCKED_MISSING_COMMON_SNAPSHOT", "BLOCKED_MISSING_COMMON_SNAPSHOT", "BLOCKED_MISSING_COMMON_SNAPSHOT"]
FALSE_FLAGS = {"CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "LORENTZIAN_QUANTUM_THEORY", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED"}
HISTORICAL_COMMITS = ["a3fc926cc289e5a545933a43331e395328580e0e", "318589ffae21fb1ae1abfd046b2f367b05c52bab", "3e15eafa5e0bb8cbc3eb1d2ad79a669c54ce9cca"]
MIGRATED_VERIFIERS = ["ci/standalone_provenance.py", "reports/standalone-history-crosswalk.json", "quantum-weyl/classical_import/verify_snapshot.py", "quantum-weyl/classical_import/verify_antifield_export.py", "quantum-weyl/classical_import/verify_antifield_export_v2.py", "quantum-weyl/classical_import/verify_support_local_q2_export.py", "quantum-weyl/classical_import/analytic_operator_snapshot_attribution.py"]


def digest(value: dict[str, Any]) -> str:
    payload = {key: value[key] for key in ("standalone_history_replay", "status_vocabulary", "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != EXPORT_IDS:
        errors.append("export identity/order")
    if [row.get("check_id") for row in checks] != CHECK_IDS:
        errors.append("freeze-check identity/order")
    if [row.get("status") for row in exports] != EXPORT_STATUS:
        errors.append("export status firewall")
    if [row.get("status") for row in checks] != CHECK_STATUS:
        errors.append("freeze-check status firewall")
    if {row.get("id") for row in value.get("status_vocabulary", [])} != STATUSES:
        errors.append("status vocabulary")
    evidence_ids = {row.get("result_or_artifact_id") for row in value.get("provenance", {}).get("inputs", [])}
    for row in exports + checks:
        if not row.get("established") or not row.get("remaining_for_gate_a") or not row.get("boundary"):
            errors.append("empty boundary field")
        if not set(row.get("evidence", [])).issubset(evidence_ids):
            errors.append("unresolved evidence id")
    hashes = value.get("required_hash_disposition", {})
    if len(hashes) != 7 or any(row.get("accepted") is not None for row in hashes.values()):
        errors.append("accepted common hash promotion")
    if [row.get("id") for row in value.get("minimal_missing_bundle", [])] != [f"M{i}_{name}" for i, name in enumerate(("COMMON_STRICT_SNAPSHOT", "STRICT_Q2_D", "RESIDUAL_SDR", "FULL_CYCLIC_PAIRING", "RESIDUAL_EXACT_PAYLOAD", "CENTERED_REPRESENTATIVES"), 1)]:
        errors.append("minimal missing bundle")
    gate = value.get("gate_disposition", {})
    expected_counts = {"gate_a_status": "FAIL_CLOSED", "claim_state": "CLASSICAL_IMPORT_PARTIALLY_REPAIRED", "publishable_quantum_results_allowed_by_gate_a": False, "exports_total": 20, "same_theory_receiver_verified_scoped": 5, "different_theory_controls": 2, "legacy_accepted_scoped": 3, "supporting_evidence_only": 7, "missing_portable_objects": 3, "freeze_checks_total": 10, "freeze_checks_receiver_verified_scoped": 1, "freeze_checks_different_theory": 4, "freeze_checks_blocked": 5, "accepted_common_snapshot_hashes": 0}
    if any(gate.get(key) != expected for key, expected in expected_counts.items()):
        errors.append("gate disposition")
    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS):
        errors.append("claim flag promotion")
    if value.get("historical_certificate_preserved") is not True:
        errors.append("historical certificate preservation")
    replay = value.get("standalone_history_replay", {})
    if (
        replay.get("status") != "VERIFIED_BY_EXACT_CONTENT"
        or replay.get("historical_commits") != HISTORICAL_COMMITS
        or replay.get("historical_identifiers_preserved") is not True
        or replay.get("historical_paths_preserved") is not True
        or value.get("claim_flags", {}).get("STANDALONE_HISTORY_REPLAY_VERIFIED") is not True
    ):
        errors.append("standalone history replay firewall")
    verifier_rows = replay.get("verifier_sources", [])
    if [row.get("path") for row in verifier_rows] != MIGRATED_VERIFIERS:
        errors.append("standalone verifier source identity")
    for item in verifier_rows:
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("standalone verifier source " + item.get("path", ""))
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"exports": len(exports), "checks": len(checks), "inputs": len(value.get("provenance", {}).get("inputs", []))}


def main() -> int:
    errors, counts = check()
    print("CLASSICAL_IMPORT_GATE_V2_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['exports']} exports and {counts['checks']} freeze checks reconciled against {counts['inputs']} pinned inputs")
        print("  - Gate A remains fail-closed with six exact missing payload families")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
