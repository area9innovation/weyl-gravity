#!/usr/bin/env python3
"""Independently check Gate-A v7 and its candidate/import boundary."""

from __future__ import annotations

from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
V6 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
PREFLIGHT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"


def load(path: Path) -> dict[str, Any]:
    return loads(path.read_text())


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def digest(value: Mapping[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay", "status_vocabulary", "export_reconciliation",
            "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
            "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution",
            "m2_d_resolution", "m2_stabilized_candidate_resolution", "m4_minimal_resolution",
            "transitive_provenance_drift",
        )
    }
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous, preflight = load(V6), load(PREFLIGHT)
    errors: list[str] = []
    if (
        value.get("result_id") != "CLASSICAL_IMPORT_GATE_V7_RECONCILIATION"
        or value.get("result_state") != "STABILIZED_Q2_CANDIDATE_CERTIFIED_AUTHORITATIVE_IDENTITY_OPEN"
        or value.get("supersedes_for_current_status") != previous.get("result_id")
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/predecessor/lifecycle")
    exports = value.get("export_reconciliation", [])
    checks = value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous["export_reconciliation"]] or len(exports) != 20:
        errors.append("export order/inventory")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous["freeze_check_reconciliation"]] or len(checks) != 10:
        errors.append("check order/inventory")
    export = {row.get("export_id"): row for row in exports}.get("support_local_classical_bv_q2", {})
    q1q2 = {row.get("check_id"): row for row in checks}.get("q1_q2_arity_two_nilpotency", {})
    cyclic = {row.get("check_id"): row for row in checks}.get("q2_cyclic_compatibility", {})
    dq2 = {row.get("check_id"): row for row in checks}.get("D_q2_derivation", {})
    if export.get("status") != "RECEIVER_VERIFIED_SCOPED" or preflight["result_id"] not in export.get("evidence", []):
        errors.append("q2 export candidate projection")
    if q1q2.get("status") != "RECEIVER_VERIFIED_SCOPED" or preflight["result_id"] not in q1q2.get("evidence", []):
        errors.append("candidate q1/q2 projection")
    if cyclic.get("status") != "RECEIVER_VERIFIED_SCOPED" or preflight["result_id"] not in cyclic.get("evidence", []):
        errors.append("candidate cyclicity projection")
    if dq2.get("status") != "SUPPORTING_EVIDENCE_ONLY" or dq2.get("evidence") != [preflight["result_id"]] or "authoritative" not in dq2.get("remaining_for_gate_a", ""):
        errors.append("D/q2 candidate classification")

    q2_hash = value.get("required_hash_disposition", {}).get("q2_hash", {})
    if not (
        q2_hash.get("accepted") is None
        and q2_hash.get("candidate") == preflight["canonical_hashes"]["graph_transport_dag_sha256"]
        and q2_hash.get("candidate_scope") == "STRICT_386_STABILIZED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT"
    ):
        errors.append("q2 hash firewall")
    gate = value.get("gate_disposition", {})
    expected_gate_counts = {
        "gate_a_status": "FAIL_CLOSED", "same_theory_receiver_verified_scoped": 11,
        "freeze_checks_total": 10, "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_different_theory": 0, "freeze_checks_supporting_evidence_only": 1,
        "freeze_checks_blocked": 1, "accepted_common_snapshot_hashes": 0,
    }
    if any(gate.get(key) != expected for key, expected in expected_gate_counts.items()):
        errors.append("Gate-A disposition")
    resolution = value.get("m2_stabilized_candidate_resolution", {})
    expected_projection = {
        "status": "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT",
        "evidence": preflight["result_id"],
        "carrier_rows": 386, "split_endpoint_rows": 30, "split_contractible_rows": 356,
        "graph_input_row_envelope": 110, "graph_output_row_envelope": 110,
        "expanded_component_channels": 140, "unique_block_triples": 68,
        "interaction_inert_rows": 196, "q1_q2_defects": 0,
        "q2_cyclicity_defects": 0, "D_q2_derivation_defects": 0,
        "candidate_q2_sha256": preflight["canonical_hashes"]["graph_transport_dag_sha256"],
    }
    if any(resolution.get(key) != expected for key, expected in expected_projection.items()):
        errors.append("M2 candidate crosswalk")
    m2 = next((item for item in value.get("minimal_missing_bundle", []) if item.get("id") == "M2_STRICT_Q2_D"), {})
    if "theory identity" not in m2.get("object", "").lower() or len(m2.get("unlocks", [])) != 3:
        errors.append("M2 frontier")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_STABILIZED_Q2_CANDIDATE", "STRICT_386_STABILIZED_Q1_Q2_IDENTITY",
        "STRICT_386_STABILIZED_Q2_CYCLICITY", "STRICT_386_STABILIZED_D_Q2_DERIVATION",
    ):
        if flags.get(key) is not True:
            errors.append("missing candidate flag " + key)
    for key in (
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2", "STRICT_386_AUTHORITATIVE_D_Q2_DERIVATION",
        "STRICT_386_CANDIDATE_THEORY_IDENTITY", "STRICT_386_FULL_CARRIER_Q2",
        "STRICT_386_D_Q2_DERIVATION", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "LORENTZIAN_QUANTUM_THEORY",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("promotion flag " + key)

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 2:
        errors.append("provenance count")
    else:
        for item, path, expected in (
            (provenance[-2], V6, previous["result_id"]),
            (provenance[-1], PREFLIGHT, preflight["result_id"]),
        ):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != file_hash(path) or item.get("result_or_artifact_id") != expected:
                errors.append("direct provenance " + str(path))
    expected_drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = file_hash(path) if path.is_file() else None
        if current != source["sha256"]:
            expected_drift.append((source["path"], source["sha256"], current))
    drift = value.get("transitive_provenance_drift", {})
    actual_drift = [
        (item.get("path"), item.get("historical_v6_sha256"), item.get("current_worktree_sha256"))
        for item in drift.get("entries", [])
    ]
    if drift.get("files_checked") != len(previous["provenance"]["inputs"]) or drift.get("drifted_files") != len(expected_drift) or actual_drift != expected_drift:
        errors.append("transitive provenance drift")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V7_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - exact stabilized q2 candidate and its identities are classified")
        print("  - authoritative theory identity, q2 hash acceptance and Gate A remain open")
        print("  - D/q2 is strict supporting evidence, not a Berger control or freeze promotion")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
