#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v27."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
LOCAL = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V27_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V27.md"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous = json.loads(PREVIOUS.read_text())
    local = json.loads(LOCAL.read_text())
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V27_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("identity/predecessor")
    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREVIOUS, LOCAL):
        if provenance.get(str(path.relative_to(ROOT)), {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {path.name}")
    resolution = value.get("m1a_local_semantic_resolution", {})
    expected = {
        "extension_rows": 356, "auxiliary_rows_fully_namespaced": 36,
        "mapping_cone_rows_fully_namespaced": 320, "local_386_rows_fully_namespaced": 386,
        "unresolved_fields": 0, "cotton_weyl_component_checks": 2560,
        "cotton_weyl_defects": 0, "scalar_nonlinear_weyl_weight_for_fixed_background_cone": "NOT_APPLICABLE",
        "M1A_complete": False, "remaining_M1A_package": "M1A3_REPRESENTED_CROSSWALK_AND_M1A4_LEDGER_FREEZE",
    }
    for key, expected_value in expected.items():
        if resolution.get(key) != expected_value:
            errors.append(f"local resolution {key}")
    preflight = value.get("m1_common_snapshot_preflight_resolution", {})
    if preflight.get("local_386_rows_fully_namespaced") != 386 or preflight.get("local_386_rows_remaining_partial") != 0 or preflight.get("m1a_represented_crosswalk_complete") is not False:
        errors.append("M1A remaining boundary")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate inventory preservation")
    disposition = value.get("gate_disposition", {})
    if disposition.get("accepted_common_snapshot_hashes") != 1 or disposition.get("gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate disposition")
    flags = value.get("claim_flags", {})
    for flag in ("M1A2_LOCAL_SEMANTIC_EXTENSION_COMPLETE", "LOCAL_386_FULLY_TYPED"):
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in ("M1A3_REPRESENTED_CROSSWALK_COMPLETE", "M1A4_LEDGER_FREEZE_COMPLETE", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED"):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    if value.get("independent_checker", {}).get("expected_digest") != canonical_digest(value):
        errors.append("certificate digest")
    if not REPORT.exists():
        errors.append("report absent")
    else:
        report = REPORT.read_text()
        for token in ("386 of 386", "4,080", "410", "470", "FAIL_CLOSED", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text()))
    if errors:
        print("CLASSICAL_IMPORT_GATE_V27_RECONCILIATION: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("CLASSICAL_IMPORT_GATE_V27_RECONCILIATION: PASS")
    print("  - local 386-row M1A semantics complete")
    print("  - represented crosswalk and ledger freeze remain open")
    print("  - Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
