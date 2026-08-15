#!/usr/bin/env python3
"""Independently check Gate-A v12 and its known-family boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
V11 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m2_hh_hv_cotangent_resolution", "m2_diff_auxiliary_resolution",
        "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V11, CLASSICAL, RECEIVER))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V12_RECONCILIATION" or value.get("supersedes_for_current_status") != previous["result_id"] or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("identity/predecessor/lifecycle/dependency")
    exports, checks = value.get("export_reconciliation", []), value.get("freeze_check_reconciliation", [])
    if [row.get("export_id") for row in exports] != [row.get("export_id") for row in previous["export_reconciliation"]] or len(exports) != 20:
        errors.append("export inventory")
    if [row.get("check_id") for row in checks] != [row.get("check_id") for row in previous["freeze_check_reconciliation"]] or len(checks) != 10:
        errors.append("check inventory")
    q2 = next((row for row in exports if row.get("export_id") == "support_local_classical_bv_q2"), {})
    if classical["result_id"] not in q2.get("evidence", []) or receiver["result_id"] not in q2.get("evidence", []) or "not an exhaustive" not in q2.get("boundary", ""):
        errors.append("q2 known-family projection")
    expected = {
        "status": "THREE_DIFF_AUXILIARY_BV_REPRESENTATIONS_EXACT_ON_386_ROWS",
        "classical_evidence": classical["result_id"], "receiver_evidence": receiver["result_id"],
        "carrier_rows": 386, "completed_families": 3,
        "master_density_coefficients": 264, "field_output_coefficients": 336,
        "antifield_output_coefficients": 632, "c_star_output_coefficients": 704,
        "formal_variational_defects": 0, "Koszul_symmetry_defects": 0,
        "known_required_cubic_families": 7, "known_required_component_complete_families": 7,
        "exhaustive_full_nonlinear_BV_family_census": False, "full_source_q2_q3_pullback_replayed": False,
    }
    if value.get("m2_diff_auxiliary_resolution") != expected:
        errors.append("Diff auxiliary resolution")
    inventory = value.get("m2_shifted_cubic_inventory_resolution", {})
    if inventory.get("component_complete_families") != 7 or inventory.get("component_open_families") != 0 or inventory.get("diffeomorphism_representation_component_complete") is not True or inventory.get("exhaustive_full_nonlinear_BV_family_census") is not False:
        errors.append("known versus exhaustive inventory boundary")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0 or value.get("required_hash_disposition", {}).get("q2_hash", {}).get("accepted") is not None:
        errors.append("fail-closed Gate-A/hash disposition")
    flags = value.get("claim_flags", {})
    expected_flags = {
        "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE": True,
        "STRICT_386_SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE": True,
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    }
    if any(flags.get(key) is not expected_value for key, expected_value in expected_flags.items()):
        errors.append("promotion firewall")
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (V11, CLASSICAL, RECEIVER):
        if pins.get(str(path.relative_to(ROOT))) != sha(path):
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V12_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
