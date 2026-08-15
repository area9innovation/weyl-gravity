#!/usr/bin/env python3
"""Independently check Gate-A V14 q2 acceptance and q3 firewalls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
V13 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
ASSEMBLY = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
DIFF = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
MASS = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = ("export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution", "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution", "m2_nonlinear_ghost_manifest_resolution", "m2_source_q2_assembly_resolution", "transitive_provenance_drift")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous, assembly, diff, mass = (json.loads(path.read_text()) for path in (V13, ASSEMBLY, DIFF, MASS))
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V14_RECONCILIATION" or value.get("supersedes_for_current_status") != previous.get("result_id"):
        errors.append("result identity or predecessor mismatch")
    if len(value.get("export_reconciliation", [])) != 20 or len(value.get("freeze_check_reconciliation", [])) != 10:
        errors.append("Gate manifest cardinality drift")
    resolution = value.get("m2_source_q2_assembly_resolution", {})
    q2_hash = assembly["source_q2_snapshot"]["sha256"]
    expected = {"status": "ACCEPTED_ARITY_TWO_COMMON_SNAPSHOT", "evidence": assembly["result_id"], "accepted_q2_sha256": q2_hash, "minimal_ordered_symbolic_components": 22, "auxiliary_ordered_component_coefficients": 2064, "graph_block_triples": assembly["graph_transport"]["graph_block_triples"], "q1_q2_defects": 0, "cyclicity_defects": 0, "D_q2_defects": 0, "full_source_q3_assembled": False}
    if resolution != expected:
        errors.append("source-q2 assembly projection mismatch")
    q2_disposition = value.get("required_hash_disposition", {}).get("q2_hash", {})
    if q2_disposition != {"accepted": q2_hash, "candidate": q2_hash, "candidate_scope": "COMMON_386_SHIFTED_SOURCE_Q2_AND_EXACT_GRAPH_DAG"}:
        errors.append("accepted q2 hash mismatch")
    accepted = [row.get("accepted") for row in value.get("required_hash_disposition", {}).values() if row.get("accepted") is not None]
    if accepted != [q2_hash]:
        errors.append("exactly one top-level hash should be accepted")
    checks = {row["check_id"]: row for row in value.get("freeze_check_reconciliation", [])}
    for name in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        if checks.get(name, {}).get("status") != "RECEIVER_VERIFIED_SCOPED" or assembly["result_id"] not in checks[name].get("evidence", []):
            errors.append(f"q2 identity promotion mismatch: {name}")
    gate = value.get("gate_disposition", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_common_snapshot_hashes") != 1 or gate.get("freeze_checks_supporting_evidence_only") != 0:
        errors.append("Gate-A disposition mismatch")
    repair = value.get("m2_diff_auxiliary_resolution", {})
    if repair.get("unrepaired_q1_q2_defects") != 336 or repair.get("repaired_q1_q2_defects") != 0 or diff["canonical_sign_repair"]["translated_coefficients"] != 704:
        errors.append("append-only c_star repair projection mismatch")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_FULL_CARRIER_Q2", "STRICT_386_D_Q2_DERIVATION", "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2", "STRICT_386_AUTHORITATIVE_D_Q2_DERIVATION", "STRICT_386_FULL_SOURCE_Q2_ASSEMBLED", "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED", "STRICT_386_FULL_Q1_Q2_IDENTITY_REPLAYED", "STRICT_386_FULL_Q2_CYCLICITY_REPLAYED", "STRICT_386_FULL_D_Q2_DERIVATION_REPLAYED"):
        if flags.get(key) is not True:
            errors.append(f"positive flag drift: {key}")
    for key in ("STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(key) is not False:
            errors.append(f"fail-closed flag drift: {key}")
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (V13, ASSEMBLY, DIFF, MASS):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"provenance pin mismatch: {path.name}")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_IMPORT_GATE_V14_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
