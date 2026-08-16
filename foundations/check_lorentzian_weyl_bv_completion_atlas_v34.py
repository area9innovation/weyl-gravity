#!/usr/bin/env python3
"""Independently check Atlas V34 residual-payload frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
RESIDUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v16_reconciliation", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous = json.loads(PREDECESSOR.read_text())
    gate = json.loads(GATE.read_text())
    residual = json.loads(RESIDUAL.read_text())
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell atlas")

    projection = value.get("strict_residual_zero_mode_payload", {})
    expected = {
        "result_id": residual["result_id"],
        "residual_snapshot_sha256": residual["residual_snapshot"]["sha256"],
        "zero_mode_basis_sha256": residual["canonical_hashes"]["zero_mode_basis_sha256"],
        "primal_modes": 15, "dual_modes": 15, "residual_cotangent_dimension": 30,
        "structure_nonzero_entries": 120, "representation_matrices": 15,
        "identity_defects": 0, "M5_payload_complete": True, "common_freeze_bound": False,
    }
    if projection != expected:
        errors.append("residual payload projection")
    gate_projection = value.get("strict_gate_v16_reconciliation", {})
    if gate_projection.get("gate_a_status") != "FAIL_CLOSED" or gate_projection.get("accepted_top_level_hashes") != 1 or gate_projection.get("remaining_top_level_hashes") != 6 or gate_projection.get("exports_receiver_verified_scoped") != 15 or gate_projection.get("exports_supporting_only") != 2 or gate_projection.get("M5_payload_complete") is not True or gate_projection.get("zero_mode_hash_common_bound") is not False:
        errors.append("Gate V16 projection")
    if gate_projection.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M6_CENTERED_REPRESENTATIVES"]:
        errors.append("four-package gate frontier")

    routes = value.get("route_selection", [])
    expected_routes = [
        "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    if len(routes) != 10 or [row.get("rank") for row in routes] != list(range(1, 11)) or [row.get("route") for row in routes] != expected_routes:
        errors.append("route frontier")
    if [row.get("object") for row in value.get("research_queue", [])] != expected_routes:
        errors.append("research queue frontier")

    flags = value.get("claim_flags", {})
    for key in (
        "strict_residual_primal_dual_modes_serialized",
        "strict_so42_structure_constants_serialized",
        "strict_residual_representation_matrices_serialized",
        "strict_q_res_0_serialized", "strict_M5_residual_exact_payload_complete",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_residual_zero_mode_hash_common_bound", "strict_pure_weyl_classical_gate_passed",
        "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, RESIDUAL):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
