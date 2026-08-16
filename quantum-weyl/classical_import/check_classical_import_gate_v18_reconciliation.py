#!/usr/bin/env python3
"""Independently check Gate-A v18 residual-SDR type repair."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
V17 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
AUDIT_CHECKER = HERE / "check_strict_residual_sdr_type_audit.py"


def load_audit_checker():
    spec = importlib.util.spec_from_file_location("gate_v18_type_audit_checker", AUDIT_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load type-audit checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any], *, replay_audit: bool = True) -> list[str]:
    errors: list[str] = []
    previous = json.loads(V17.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if replay_audit and load_audit_checker().check(audit):
        errors.append("independent M3 type audit")
    if value.get("export_reconciliation") != previous.get("export_reconciliation") or value.get("freeze_check_reconciliation") != previous.get("freeze_check_reconciliation"):
        errors.append("export or freeze rows changed")
    if value.get("required_hash_disposition") != previous.get("required_hash_disposition"):
        errors.append("hash disposition changed")
    missing = [item.get("id") for item in value.get("minimal_missing_bundle", [])]
    if missing != ["M1_COMMON_STRICT_SNAPSHOT", "M3L_COMMON_ENDPOINT_SDR_BINDING", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"]:
        errors.append("typed missing bundle")

    m3 = value.get("m3_scoped_resolution", {})
    expected_m3 = {
        "status": "TWO_CERTIFIED_SCOPES_SEPARATED_TYPED_COMPARISON_OPEN",
        "local_endpoint_evidence": graph["result_id"],
        "local_carrier_component_species": 386,
        "local_endpoint_component_species": 30,
        "local_graph_sdr_sha256": graph["canonical_hashes"]["graph_sdr_component_maps_sha256"],
        "dfinite_evidence": dfinite["result_id"],
        "dfinite_full_coordinates": 4490,
        "dfinite_residual_coordinates": 470,
        "dfinite_residual_sdr_hash": dfinite["global_direct_sum"]["residual_sdr_hash"],
        "direct_support_local_identification": "OBSTRUCTED_FOR_THE_SPECIFIED_GLOBAL_MODE_PROJECTORS",
        "remaining": ["M3L_COMMON_ENDPOINT_SDR_BINDING", "M3R_TYPED_RESIDUAL_COMPARISON"],
        "boundary": "The local endpoint SDR and finite harmonic residual SDR remain valid in their own categories; neither is promoted to the other category.",
    }
    if m3 != expected_m3:
        errors.append("M3 scoped resolution")
    resolution = value.get("m3_type_and_locality_resolution", {})
    if resolution != {
        "status": "ORIGINAL_M3_REPLACED_BY_TYPED_TWO_STAGE_CONTRACT",
        "evidence": audit["result_id"],
        "type_census_sha256": audit["type_census"]["sha256"],
        "architecture_decision_sha256": audit["architecture_decision"]["sha256"],
        "graph_endpoint_30_is_finite_residual_30": False,
        "dfinite_residual_projector_support_local": False,
        "zero_mode_projector_support_local": False,
        "M3L_common_endpoint_sdr_bound": False,
        "M3R_typed_residual_comparison_constructed": False,
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }:
        errors.append("M3 type/locality resolution")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("same_theory_receiver_verified_scoped") != 17 or gate.get("freeze_checks_receiver_verified_scoped") != 9:
        errors.append("Gate disposition")

    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL", "M3_TYPED_SPLIT_REQUIRED"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30", "DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL",
        "ZERO_MODE_PROJECTOR_SUPPORT_LOCAL", "ORIGINAL_M3_SINGLE_OBJECT_TYPE_CORRECT",
        "M3L_COMMON_ENDPOINT_SDR_BOUND", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (V17, AUDIT, GRAPH, DFINITE):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V18_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
