#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v28."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V27_RECONCILIATION.json"
M1A3 = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
M1A4 = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V28.md"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous = json.loads(PREVIOUS.read_text())
    m1a3 = json.loads(M1A3.read_text())
    m1a4 = json.loads(M1A4.read_text())
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V28_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("identity/predecessor")
    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREVIOUS, M1A3, M1A4):
        if provenance.get(str(path.relative_to(ROOT)), {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {path.name}")

    resolution = value.get("m1a_completion_resolution", {})
    expected = {
        "represented_endpoint_rows": 4080,
        "test_nonminimal_rows_excluded": 410,
        "test_nonminimal_doublets": 205,
        "action_residual_primal_rows": 470,
        "action_residual_dual_rows": 470,
        "authoritative_rows_total": 17779,
        "authoritative_carrier_objects": 6,
        "untyped_authoritative_rows": 0,
        "category_identification_defects": 0,
        "q0_cross_partition_defects": 0,
        "q0_chain_degree_defects": 0,
        "residual_crosswalk_defects": 0,
        "typed_field_dictionary_candidate_sha256": m1a4["typed_field_dictionary"]["sha256"],
        "typed_diagram_candidate_sha256": m1a4["diagram_freeze"]["sha256"],
        "M1A_complete": True,
        "remaining_M1_packages": ["M1B_REPRESENTED_COMPOSITE_CONTRACTION", "M1C_COMMON_MANIFEST_REPLAY"],
    }
    for key, expected_value in expected.items():
        if resolution.get(key) != expected_value:
            errors.append(f"M1A resolution {key}")
    preflight = value.get("m1_common_snapshot_preflight_resolution", {})
    packages = {row.get("id"): row.get("status") for row in preflight.get("work_packages", [])}
    if packages != {
        "M1A_FULL_TYPED_CARRIER_LEDGER": "COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION": "OPEN",
        "M1C_COMMON_MANIFEST_REPLAY": "OPEN_AFTER_M1B",
    }:
        errors.append("M1 work-package frontier")
    if preflight.get("m1a_full_typed_carrier_ledger_complete") is not True or preflight.get("m1b_represented_composite_contraction_complete") is not False:
        errors.append("M1A/M1B boundary")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate inventory preservation")
    field_exports = [row for row in value.get("export_reconciliation", []) if row.get("export_id") in {"field_ghost_antifield_dictionary", "field_gradings"}]
    if len(field_exports) != 2 or any(row.get("m1_v28_status") != "M1A_TYPED_DIAGRAM_FROZEN_AWAIT_M1C_COMMON_BINDING" for row in field_exports):
        errors.append("field export M1A disposition")
    hashes = value.get("required_hash_disposition", {})
    if hashes.get("field_dictionary_hash", {}).get("candidate") != m1a4["typed_field_dictionary"]["sha256"] or hashes.get("field_dictionary_hash", {}).get("accepted") is not None:
        errors.append("field dictionary candidate/acceptance")
    disposition = value.get("gate_disposition", {})
    if (
        disposition.get("accepted_common_snapshot_hashes") != 1
        or disposition.get("gate_a_status") != "FAIL_CLOSED"
        or disposition.get("claim_state") != "CLASSICAL_IMPORT_M1A_COMPLETE_M1B_COMPOSITE_OPEN"
    ):
        errors.append("Gate disposition")
    flags = value.get("claim_flags", {})
    for flag in ("M1A3_REPRESENTED_CROSSWALK_COMPLETE", "M1A4_LEDGER_FREEZE_COMPLETE", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE"):
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in (
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    if value.get("independent_checker", {}).get("expected_digest") != canonical_digest(value):
        errors.append("certificate digest")
    if not REPORT.exists():
        errors.append("report absent")
    else:
        report = REPORT.read_text()
        for token in ("17,779", "4,080", "410", "205", "470", "12,343", "M1B", "FAIL_CLOSED", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text()))
    if errors:
        print("CLASSICAL_IMPORT_GATE_V28_RECONCILIATION: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("CLASSICAL_IMPORT_GATE_V28_RECONCILIATION: PASS")
    print("  - M1A typed diagram complete across 17,779 authoritative rows")
    print("  - M1B composite contraction and M1C common replay remain open")
    print("  - Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
