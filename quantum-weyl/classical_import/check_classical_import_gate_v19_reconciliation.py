#!/usr/bin/env python3
"""Independently check Gate-A v19 M3L integration."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
V18 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
BINDING = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
BINDING_CHECKER = HERE / "check_strict_386_common_endpoint_sdr_binding.py"


def load_binding_checker():
    spec = importlib.util.spec_from_file_location("gate_v19_binding_checker", BINDING_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load M3L checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m5_residual_exact_payload_resolution", "m6_centered_representatives_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any], *, replay_binding: bool = True) -> list[str]:
    errors: list[str] = []
    previous = json.loads(V18.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    if (
        value.get("result_id") != "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION"
        or value.get("result_state") != "M3L_COMMON_ENDPOINT_SDR_BOUND_THREE_TYPED_PACKAGES_OPEN_GATE_FAIL_CLOSED"
        or value.get("supersedes_for_current_status") != previous.get("result_id")
    ):
        errors.append("result identity/state/predecessor")
    if replay_binding and load_binding_checker().check(binding):
        errors.append("independent M3L replay")
    for key in ("export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition"):
        if value.get(key) != previous.get(key):
            errors.append(key + " changed")
    missing = [item.get("id") for item in value.get("minimal_missing_bundle", [])]
    if missing != ["M1_COMMON_STRICT_SNAPSHOT", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"]:
        errors.append("three-package missing bundle")

    m3 = value.get("m3_scoped_resolution", {})
    if (
        m3.get("status") != "LOCAL_ENDPOINT_COMMON_BINDING_COMPLETE_TYPED_RESIDUAL_COMPARISON_OPEN"
        or m3.get("local_common_binding_evidence") != binding["result_id"]
        or m3.get("local_common_manifest_sha256") != binding["common_manifest"]["sha256"]
        or m3.get("remaining") != ["M3R_TYPED_RESIDUAL_COMPARISON"]
        or m3.get("direct_support_local_identification") != "OBSTRUCTED_FOR_THE_SPECIFIED_GLOBAL_MODE_PROJECTORS"
    ):
        errors.append("M3 scoped resolution")
    typed = value.get("m3_type_and_locality_resolution", {})
    if (
        typed.get("M3L_common_endpoint_sdr_bound") is not True
        or typed.get("M3R_typed_residual_comparison_constructed") is not False
        or typed.get("dfinite_residual_projector_support_local") is not False
        or typed.get("zero_mode_projector_support_local") is not False
        or typed.get("accepted_common_snapshot_hashes_added") != 0
        or typed.get("gate_a_status") != "FAIL_CLOSED"
    ):
        errors.append("M3 type/locality resolution")

    resolution = value.get("m3l_common_endpoint_sdr_binding_resolution", {})
    expected_resolution = {
        "status": "RECEIVER_VERIFIED_SCOPED_COMPLETE",
        "evidence": binding["result_id"],
        "certificate_sha256": hashlib.sha256(BINDING.read_bytes()).hexdigest(),
        "common_manifest_id": binding["common_manifest"]["manifest_id"],
        "common_manifest_sha256": binding["common_manifest"]["sha256"],
        "carrier_rows": 386,
        "endpoint_rows": 30,
        "contracted_rows": 356,
        "artifact_pins": 10,
        "canonical_object_hashes": 17,
        "compatibility_links_checked": 15,
        "total_projected_identity_defects": 0,
        "support_local": True,
        "residual_comparison_included": False,
        "accepted_common_snapshot_hashes_added": 0,
    }
    if resolution != expected_resolution:
        errors.append("M3L resolution")
    gate = value.get("gate_disposition", {})
    if (
        gate.get("gate_a_status") != "FAIL_CLOSED"
        or gate.get("accepted_common_snapshot_hashes") != 1
        or gate.get("same_theory_receiver_verified_scoped") != 17
        or gate.get("freeze_checks_receiver_verified_scoped") != 9
        or gate.get("claim_state") != "CLASSICAL_IMPORT_M3L_COMPLETE_THREE_TYPED_PACKAGES_OPEN"
    ):
        errors.append("Gate disposition")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL", "M3_TYPED_SPLIT_REQUIRED",
        "STRICT_386_COMMON_ENDPOINT_SDR_MANIFEST_BOUND",
        "STRICT_386_COMMON_ENDPOINT_SDR_IDENTITIES_REPLAYED",
        "STRICT_386_Q1_D_Q2_Q3_SAME_LOCAL_CARRIER", "M3L_COMMON_ENDPOINT_SDR_BOUND",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30", "DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL",
        "ZERO_MODE_PROJECTOR_SUPPORT_LOCAL", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (V18, BINDING):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    try:
        actual_digest = digest(value)
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != actual_digest:
            errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V19_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
