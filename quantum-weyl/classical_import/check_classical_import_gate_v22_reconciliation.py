#!/usr/bin/env python3
"""Independently check Gate-A v22 and its residual carrier obstruction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
V21 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
OBSTRUCTION_CHECKER = HERE / "check_strict_residual_cyclic_carrier_obstruction.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m3r_typed_residual_comparison_resolution", "m4_typed_local_cyclicity_resolution",
        "residual_cyclic_carrier_obstruction_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def obstruction_checker_module():
    spec = importlib.util.spec_from_file_location("residual_cyclic_obstruction_for_gate", OBSTRUCTION_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def one(items: list[dict[str, Any]], key: str, wanted: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == wanted]
    return matches[0] if len(matches) == 1 else {}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(V21.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V22_RECONCILIATION" or value.get("lifecycle") != previous.get("lifecycle"):
        errors.append("identity/lifecycle")
    if obstruction_checker_module().check(obstruction):
        errors.append("independent residual obstruction replay")
    pins = value.get("provenance", {}).get("inputs", [])
    for path, result_id in ((V21, previous["result_id"]), (OBSTRUCTION, obstruction["result_id"])):
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
        or gate.get("legacy_accepted_scoped") != 3
        or gate.get("freeze_checks_total") != 10
        or gate.get("freeze_checks_receiver_verified_scoped") != 9
        or gate.get("freeze_checks_blocked") != 1
        or gate.get("accepted_common_snapshot_hashes") != 1
        or gate.get("gate_a_status") != "FAIL_CLOSED"
        or gate.get("publishable_quantum_results_allowed_by_gate_a") is not False
    ):
        errors.append("Gate disposition counts")
    if [item.get("id") for item in value.get("minimal_missing_bundle", [])] != [
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION",
        "M4R_TYPED_RESIDUAL_CYCLICITY",
        "M1_COMMON_STRICT_SNAPSHOT",
    ]:
        errors.append("typed missing bundle")
    resolution = value.get("residual_cyclic_carrier_obstruction_resolution", {})
    expected_resolution = {
        "status": "RECEIVER_VERIFIED_RANK_ZERO_OBSTRUCTION_AND_940_COTANGENT_PREFLIGHT",
        "evidence": obstruction["result_id"],
        "certificate_sha256": sha(OBSTRUCTION),
        "current_primal_coordinates": 470,
        "current_induced_odd_pairing_rank": 0,
        "current_induced_odd_pairing_nullity": 470,
        "current_nondegeneracy_rank_defect": 470,
        "cotangent_preflight_coordinates": 940,
        "cotangent_preflight_pairing_rank": 940,
        "cotangent_pairing_action_identified": False,
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "OPEN",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC",
        "accepted_common_snapshot_hashes_added": 0,
    }
    if resolution != expected_resolution:
        errors.append("obstruction resolution projection")
    cyclic = one(value.get("freeze_check_reconciliation", []), "check_id", "cyclic_compatibility")
    if (
        cyclic.get("status") != "BLOCKED_RESIDUAL_CARRIER_RANK_ZERO_MISSING_M3RC"
        or obstruction["result_id"] not in cyclic.get("evidence", [])
    ):
        errors.append("cyclic check obstruction projection")
    m3r = value.get("m3r_typed_residual_comparison_resolution", {})
    if (
        m3r.get("status") != "M3R_PRIMAL_RECEIVER_VERIFIED_M3RC_REQUIRED_FOR_CYCLIC_COMPLETION"
        or m3r.get("M4R_TYPED_RESIDUAL_CYCLICITY") != "BLOCKED_BY_M3RC_RANK_ZERO"
    ):
        errors.append("M3R scope repair")
    m4 = value.get("m4_typed_local_cyclicity_resolution", {})
    if (
        m4.get("M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION") != "OPEN"
        or m4.get("M4R_TYPED_RESIDUAL_CYCLICITY") != "BLOCKED_BY_M3RC_RANK_ZERO"
    ):
        errors.append("M4R dependency repair")

    flags = value.get("claim_flags", {})
    for key in (
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "M3R_PRIMAL_ONLY_FOR_CYCLIC_PURPOSES",
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO",
        "FINITE_940_SHIFTED_COTANGENT_CARRIER_CONSTRUCTED",
        "FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_NONDEGENERATE",
        "FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING",
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED",
        "COMMON_GATE_A_FREEZE_BOUND",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
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
    print("CLASSICAL_IMPORT_GATE_V22_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - M3RC is now an explicit prerequisite to M4R")
        print("  - Gate A remains fail closed at one of seven accepted hashes")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
