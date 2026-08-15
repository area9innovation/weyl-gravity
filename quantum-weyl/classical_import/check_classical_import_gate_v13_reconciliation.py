#!/usr/bin/env python3
"""Independently check Gate-A V13 census promotion and firewalls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
V12 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = ("export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution", "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution", "m2_nonlinear_ghost_manifest_resolution", "transitive_provenance_drift")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous, manifest = json.loads(V12.read_text()), json.loads(MANIFEST.read_text())
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V13_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor mismatch")
    if len(value.get("export_reconciliation", [])) != len(previous.get("export_reconciliation", [])) or len(value.get("freeze_check_reconciliation", [])) != len(previous.get("freeze_check_reconciliation", [])):
        errors.append("Gate manifest cardinality drift")
    resolution = value.get("m2_nonlinear_ghost_manifest_resolution", {})
    expected = {**manifest["manifest_summary"], "Weyl_boost_internal_algebra_abelian": True, "shifted_f_hat_internal_invariant": True, "exhaustive_in_declared_scope": True, "full_386_source_q2_assembled": False}
    for key, expected_value in expected.items():
        if resolution.get(key) != expected_value:
            errors.append(f"ghost manifest projection mismatch: {key}")
    inventory = value.get("m2_shifted_cubic_inventory_resolution", {})
    if inventory.get("component_complete_families") != 7 or inventory.get("component_open_families") != 0 or inventory.get("exhaustive_full_nonlinear_BV_family_census") is not True or inventory.get("complete_source_q2_q3_pullback_replayed") is not False:
        errors.append("exhaustive family census or source assembly boundary mismatch")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 0:
        errors.append("Gate-A disposition mismatch")
    if any(item.get("accepted") is not None for item in value.get("required_hash_disposition", {}).values()):
        errors.append("a top-level hash was accepted")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS", "STRICT_386_SEVEN_AUXILIARY_CUBIC_FAMILIES_COMPONENT_COMPLETE"):
        if flags.get(key) is not True:
            errors.append(f"positive flag drift: {key}")
    for key in ("STRICT_386_FULL_SOURCE_Q2_ASSEMBLED", "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED", "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(key) is not False:
            errors.append(f"fail-closed flag drift: {key}")
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (V12, MANIFEST):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"provenance pin mismatch: {path.name}")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V13_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
