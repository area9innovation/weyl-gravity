#!/usr/bin/env python3
"""Independently check Gate-A v21 and its M3R projection."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
V20 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
M3R_CHECKER = HERE / "check_strict_endpoint_to_residual_spectral_comparison.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m3r_typed_residual_comparison_resolution", "m4_typed_local_cyclicity_resolution",
        "m5_residual_exact_payload_resolution", "m6_centered_representatives_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def checker_module():
    spec = importlib.util.spec_from_file_location("m3r_checker_for_gate", M3R_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def one(items: list[dict[str, Any]], key: str, wanted: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == wanted]
    return matches[0] if len(matches) == 1 else {}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(V20.read_text(encoding="utf-8"))
    comparison = json.loads(M3R.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V21_RECONCILIATION" or value.get("lifecycle") != previous.get("lifecycle"):
        errors.append("identity/lifecycle")
    if checker_module().check(comparison):
        errors.append("independent M3R replay")
    pins = value.get("provenance", {}).get("inputs", [])
    for path, result_id in ((V20, previous["result_id"]), (M3R, comparison["result_id"])):
        if not any(
            item.get("result_or_artifact_id") == result_id and item.get("sha256") == sha(path)
            for item in pins
        ):
            errors.append("provenance pin " + result_id)
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate census")
    gate = value.get("gate_disposition", {})
    if (
        gate.get("exports_total") != 20
        or gate.get("same_theory_receiver_verified_scoped") != 17
        or gate.get("freeze_checks_total") != 10
        or gate.get("freeze_checks_receiver_verified_scoped") != 9
        or gate.get("freeze_checks_blocked") != 1
        or gate.get("accepted_common_snapshot_hashes") != 1
        or gate.get("gate_a_status") != "FAIL_CLOSED"
        or gate.get("publishable_quantum_results_allowed_by_gate_a") is not False
    ):
        errors.append("Gate disposition counts")
    if [item.get("id") for item in value.get("minimal_missing_bundle", [])] != [
        "M1_COMMON_STRICT_SNAPSHOT", "M4R_TYPED_RESIDUAL_CYCLICITY"
    ]:
        errors.append("typed missing bundle")
    resolution = value.get("m3r_typed_residual_comparison_resolution", {})
    expected_resolution = {
        "status": "M3R_RECEIVER_VERIFIED_SCOPED_COMPLETE_M4R_OPEN",
        "evidence": comparison["result_id"],
        "certificate_sha256": sha(M3R),
        "source_category": "represented D-finite globally smooth endpoint harmonics",
        "target_category": "finite W+/W- residual coefficient space",
        "energy_blocks": 5,
        "residual_coordinates": 470,
        "ordered_crosswalk_defects": 0,
        "chain_identity_defects": 0,
        "harmonic_analysis_support_local": False,
        "all_energy_or_smooth_completion_certified": False,
        "M3R_TYPED_RESIDUAL_COMPARISON": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN",
        "accepted_common_snapshot_hashes_added": 0,
    }
    if resolution != expected_resolution:
        errors.append("M3R resolution projection")
    for export_id in ("classical_inclusion_iota_cl", "classical_projection_pi_cl"):
        item = one(value.get("export_reconciliation", []), "export_id", export_id)
        if item.get("status") != "RECEIVER_VERIFIED_SCOPED" or comparison["result_id"] not in item.get("evidence", []):
            errors.append("M3R export projection " + export_id)
    for check_id in ("q0_iota_intertwining", "pi_q0_intertwining"):
        item = one(value.get("freeze_check_reconciliation", []), "check_id", check_id)
        if item.get("status") != "RECEIVER_VERIFIED_SCOPED" or comparison["result_id"] not in item.get("evidence", []):
            errors.append("M3R chain-check projection " + check_id)
    cyclic = one(value.get("freeze_check_reconciliation", []), "check_id", "cyclic_compatibility")
    if cyclic.get("status") != "BLOCKED_MISSING_TYPED_RESIDUAL_CYCLICITY" or comparison["result_id"] not in cyclic.get("evidence", []):
        errors.append("M4R blocked check")
    if value.get("m4_typed_local_cyclicity_resolution", {}).get("M4R_TYPED_RESIDUAL_CYCLICITY") != "OPEN_READY_AFTER_M3R":
        errors.append("M4R readiness")

    flags = value.get("claim_flags", {})
    for key in (
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "M3R_ORDERED_470_MODE_CROSSWALK_BIJECTIVE",
        "M3R_CHAIN_IDENTITIES_REPLAYED",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "HARMONIC_ANALYSIS_SUPPORT_LOCAL", "ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE", "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED",
        "COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
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
    print("CLASSICAL_IMPORT_GATE_V21_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
