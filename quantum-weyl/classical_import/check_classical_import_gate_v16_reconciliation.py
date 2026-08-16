#!/usr/bin/env python3
"""Independently check Gate-A v16 residual-payload reconciliation."""

from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
V15 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
RESIDUAL = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
RESIDUAL_CHECKER = HERE / "check_strict_residual_zero_mode_payload.py"


def load_residual_checker():
    spec = importlib.util.spec_from_file_location("gate_v16_residual_checker", RESIDUAL_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load residual checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation",
        "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m5_residual_exact_payload_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous = json.loads(V15.read_text())
    residual = json.loads(RESIDUAL.read_text())
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V16_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if load_residual_checker().check(residual):
        errors.append("independent residual payload replay")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate manifest cardinality")

    promoted_ids = {
        "conformal_killing_zero_modes_15", "residual_representation_matrices",
        "so42_structure_constants", "residual_differential_q_res_0",
    }
    exports = {row.get("export_id"): row for row in value.get("export_reconciliation", [])}
    for export_id in promoted_ids:
        row = exports.get(export_id, {})
        if row.get("status") != "RECEIVER_VERIFIED_SCOPED" or residual["result_id"] not in row.get("evidence", []):
            errors.append("residual export " + export_id)
    if exports.get("normalized_weyl_square_representatives", {}).get("status") != "SUPPORTING_EVIDENCE_ONLY" or exports.get("centered_cohomology_bases_h3_h4_h5", {}).get("status") != "SUPPORTING_EVIDENCE_ONLY":
        errors.append("M6 supporting-only firewall")

    missing = [item.get("id") for item in value.get("minimal_missing_bundle", [])]
    if missing != ["M1_COMMON_STRICT_SNAPSHOT", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M6_CENTERED_REPRESENTATIVES"]:
        errors.append("current missing bundle")
    hashes = value.get("required_hash_disposition", {})
    zero_hash = residual["canonical_hashes"]["zero_mode_basis_sha256"]
    if hashes.get("zero_mode_basis_hash") != {
        "accepted": None,
        "candidate": zero_hash,
        "candidate_scope": "EXACT_PRIMAL_DUAL_RESIDUAL_PAYLOAD_READY_NOT_BOUND_TO_COMMON_GATE_A_FREEZE",
    }:
        errors.append("zero-mode hash candidate")
    accepted = [row.get("accepted") for row in hashes.values() if row.get("accepted") is not None]
    if accepted != [previous["required_hash_disposition"]["q2_hash"]["accepted"]]:
        errors.append("exactly one accepted top-level hash")

    resolution = value.get("m5_residual_exact_payload_resolution", {})
    expected_resolution = {
        "status": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
        "evidence": residual["result_id"],
        "residual_snapshot_sha256": residual["residual_snapshot"]["sha256"],
        "zero_mode_basis_sha256": zero_hash,
        "structure_constants_sha256": residual["canonical_hashes"]["structure_constants_sha256"],
        "representation_matrices_sha256": residual["canonical_hashes"]["representation_matrices_sha256"],
        "q_res_0_sha256": residual["canonical_hashes"]["q_res_0_sha256"],
        "primal_modes": 15,
        "dual_modes": 15,
        "structure_nonzero_entries": 120,
        "representation_matrices": 15,
        "identity_defects": 0,
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    if resolution != expected_resolution:
        errors.append("M5 resolution")

    statuses = Counter(row.get("status") for row in value.get("export_reconciliation", []))
    gate = value.get("gate_disposition", {})
    expected_counts = {
        "same_theory_receiver_verified_scoped": statuses["RECEIVER_VERIFIED_SCOPED"],
        "different_theory_controls": statuses["CERTIFIED_DIFFERENT_THEORY"],
        "legacy_accepted_scoped": statuses["LEGACY_ACCEPTED_SCOPED"],
        "supporting_evidence_only": statuses["SUPPORTING_EVIDENCE_ONLY"],
        "missing_portable_objects": statuses["MISSING_PORTABLE_OBJECT"],
    }
    if any(gate.get(key) != count for key, count in expected_counts.items()) or expected_counts != {
        "same_theory_receiver_verified_scoped": 15,
        "different_theory_controls": 0,
        "legacy_accepted_scoped": 3,
        "supporting_evidence_only": 2,
        "missing_portable_objects": 0,
    }:
        errors.append("twenty-row status counts")
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("publishable_quantum_results_allowed_by_gate_a") is not False:
        errors.append("Gate-A fail-closed disposition")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_PRIMAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_DUAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_SO42_STRUCTURE_CONSTANTS_SERIALIZED",
        "STRICT_RESIDUAL_REPRESENTATION_MATRICES_SERIALIZED",
        "STRICT_Q_RES_0_SERIALIZED", "STRICT_RESIDUAL_ZERO_MODE_IDENTITIES_REPLAYED",
        "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)

    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (V15, RESIDUAL):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V16_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
