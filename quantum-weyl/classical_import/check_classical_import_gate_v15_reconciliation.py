#!/usr/bin/env python3
"""Independently check Gate-A V15 q3 acceptance and freeze firewalls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
V14 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
Q2 = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
Q3 = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
AUXILIARY = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution",
        "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution",
        "m2_nonlinear_ghost_manifest_resolution", "m2_source_q2_assembly_resolution",
        "m2_source_q3_assembly_resolution", "transitive_provenance_drift",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous, q2, q3, auxiliary, quartic = (json.loads(path.read_text()) for path in (V14, Q2, Q3, AUXILIARY, QUARTIC))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V15_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate manifest cardinality")
    q2_hash, q3_hash = q2["source_q2_snapshot"]["sha256"], q3["source_q3_snapshot"]["sha256"]
    resolution = value.get("m2_source_q3_assembly_resolution", {})
    expected = {
        "status": "ACCEPTED_ARITY_THREE_COMMON_SNAPSHOT", "evidence": q3["result_id"],
        "accepted_q2_sha256": q2_hash, "accepted_q3_sha256": q3_hash,
        "minimal_natural_operator_components": 1, "auxiliary_ordered_component_coefficients": 5952,
        "source_q3_family_count": 2, "graph_block_quadruples": 40,
        "arity_three_defects": 0, "cyclicity_defects_mod_d": 0, "D_q3_defects": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    if resolution != expected:
        errors.append("source q3 resolution")
    if q3["source_q3_snapshot"].get("accepted_q2_snapshot_sha256") != q2_hash:
        errors.append("q2/q3 common-byte link")
    missing = [item.get("id") for item in value.get("minimal_missing_bundle", [])]
    if missing != ["M1_COMMON_STRICT_SNAPSHOT", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES"]:
        errors.append("current missing bundle")
    accepted = [row.get("accepted") for row in value.get("required_hash_disposition", {}).values() if row.get("accepted") is not None]
    if accepted != [q2_hash]:
        errors.append("exactly one accepted top-level hash")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("freeze_checks_blocked") != 1:
        errors.append("Gate-A fail-closed disposition")
    if auxiliary["exact_replay"].get("cyclicity_defects") != 0 or auxiliary["shifted_mass_q3_lift"]["component_counts"].get("total_ordered_q3_coefficients") != 5952:
        errors.append("auxiliary q3 source rail")
    if quartic["exact_replay"].get("mixed_conformal_recursion_defects") != 0 or quartic["exact_replay"].get("pure_trace_second_variation_defects") != 0:
        errors.append("classical quartic Ward rail")
    if q3["arity_three_replay"].get("graph_386_arity_three_defects") != 0 or q3["q3_cyclicity_replay"].get("graph_386_q3_cyclicity_defects_mod_d") != 0 or q3["D_q3_replay"].get("graph_D_q3_derivation_defects") != 0:
        errors.append("common q3 identity rails")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3", "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED", "STRICT_386_FULL_ARITY_THREE_IDENTITY_REPLAYED", "STRICT_386_FULL_Q3_CYCLICITY_REPLAYED_MOD_D", "STRICT_386_FULL_D_Q3_DERIVATION_REPLAYED"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (V14, Q3, AUXILIARY, QUARTIC):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V15_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
