#!/usr/bin/env python3
"""Independently check Gate-A v17 centered-payload reconciliation."""

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
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
V16 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
CENTERED_CHECKER = HERE / "check_strict_centered_cohomology_payload.py"


def load_centered_checker():
    spec = importlib.util.spec_from_file_location("gate_v17_centered_checker", CENTERED_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load centered checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation",
        "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any], *, replay_centered: bool = True) -> list[str]:
    previous = json.loads(V16.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V17_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if replay_centered and load_centered_checker().check(centered):
        errors.append("independent centered payload replay")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate manifest cardinality")

    exports = {row.get("export_id"): row for row in value.get("export_reconciliation", [])}
    for export_id in ("normalized_weyl_square_representatives", "centered_cohomology_bases_h3_h4_h5"):
        row = exports.get(export_id, {})
        if row.get("status") != "RECEIVER_VERIFIED_SCOPED" or centered["result_id"] not in row.get("evidence", []):
            errors.append("centered export " + export_id)
    missing = [item.get("id") for item in value.get("minimal_missing_bundle", [])]
    if missing != ["M1_COMMON_STRICT_SNAPSHOT", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING"]:
        errors.append("current missing bundle")

    hashes = value.get("required_hash_disposition", {})
    representative_hash = centered["canonical_hashes"]["representatives_sha256"]
    if hashes.get("representative_hash") != {
        "accepted": None,
        "candidate": representative_hash,
        "candidate_scope": "EXACT_CENTERED_C3_C4_C5_AND_NORMALIZED_H4_PAYLOAD_READY_NOT_BOUND_TO_COMMON_GATE_A_FREEZE",
    }:
        errors.append("representative hash candidate")
    accepted = [row.get("accepted") for row in hashes.values() if row.get("accepted") is not None]
    if accepted != [previous["required_hash_disposition"]["q2_hash"]["accepted"]]:
        errors.append("exactly one accepted top-level hash")

    resolution = value.get("m6_centered_representatives_resolution", {})
    expected_resolution = {
        "status": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
        "evidence": centered["result_id"],
        "centered_snapshot_sha256": centered["centered_snapshot"]["sha256"],
        "ordered_centered_basis_sha256": centered["canonical_hashes"]["ordered_centered_basis_sha256"],
        "representatives_sha256": representative_hash,
        "cochain_dimensions_C3_C4_C5": [727, 3084, 8532],
        "differential_nonzero_coefficients": 85091,
        "ranks_d3_d4": [636, 2446],
        "H4_dimension": 2,
        "normalized_gram": [[1, 0], [0, 1]],
        "identity_defects": 0,
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    if resolution != expected_resolution:
        errors.append("M6 resolution")

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
        "same_theory_receiver_verified_scoped": 17,
        "different_theory_controls": 0,
        "legacy_accepted_scoped": 3,
        "supporting_evidence_only": 0,
        "missing_portable_objects": 0,
    }:
        errors.append("twenty-row status counts")
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("publishable_quantum_results_allowed_by_gate_a") is not False:
        errors.append("Gate-A fail-closed disposition")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_CENTERED_C3_C4_C5_BASES_SERIALIZED",
        "STRICT_CENTERED_DIFFERENTIAL_RECONSTRUCTED",
        "STRICT_NORMALIZED_WEYL_SQUARE_REPRESENTATIVES_SERIALIZED",
        "STRICT_CENTERED_H4_COHOMOLOGY_REPLAYED",
        "M6_CENTERED_REPRESENTATIVES_COMPLETE",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (V16, CENTERED):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V17_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
