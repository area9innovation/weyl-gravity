#!/usr/bin/env python3
"""Independently check Atlas V35 centered-payload frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V34.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
CENTERED = ROOT / "quantum-weyl/classical_import/certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v17_reconciliation", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell atlas")

    projection = value.get("strict_centered_cohomology_payload", {})
    expected = {
        "result_id": centered["result_id"],
        "centered_snapshot_sha256": centered["centered_snapshot"]["sha256"],
        "ordered_centered_basis_sha256": centered["canonical_hashes"]["ordered_centered_basis_sha256"],
        "representatives_sha256": centered["canonical_hashes"]["representatives_sha256"],
        "cochain_dimensions_C3_C4_C5": [727, 3084, 8532],
        "differential_nonzero_coefficients": 85091,
        "ranks_d3_d4": [636, 2446], "H4_dimension": 2,
        "normalized_gram": [[1, 0], [0, 1]], "identity_defects": 0,
        "M6_payload_complete": True, "common_freeze_bound": False,
    }
    if projection != expected:
        errors.append("centered payload projection")
    gate_projection = value.get("strict_gate_v17_reconciliation", {})
    if gate_projection.get("gate_a_status") != "FAIL_CLOSED" or gate_projection.get("accepted_top_level_hashes") != 1 or gate_projection.get("remaining_top_level_hashes") != 6 or gate_projection.get("exports_receiver_verified_scoped") != 17 or gate_projection.get("exports_supporting_only") != 0 or gate_projection.get("M5_payload_complete") is not True or gate_projection.get("M6_payload_complete") is not True or gate_projection.get("representative_hash_common_bound") is not False:
        errors.append("Gate V17 projection")
    if gate_projection.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING"]:
        errors.append("three-package gate frontier")

    routes = value.get("route_selection", [])
    expected_routes = [
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    if len(routes) != 9 or [row.get("rank") for row in routes] != list(range(1, 10)) or [row.get("route") for row in routes] != expected_routes:
        errors.append("route frontier")
    if [row.get("object") for row in value.get("research_queue", [])] != expected_routes:
        errors.append("research queue frontier")
    if any(row.get("route") == "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD" for row in routes):
        errors.append("completed centered route retained")

    flags = value.get("claim_flags", {})
    for key in (
        "strict_centered_C3_C4_C5_bases_serialized",
        "strict_centered_differential_reconstructed",
        "strict_normalized_weyl_square_representatives_serialized",
        "strict_centered_H4_cohomology_replayed",
        "strict_M6_centered_representatives_complete",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_representative_hash_common_bound", "strict_pure_weyl_classical_gate_passed",
        "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, CENTERED):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
