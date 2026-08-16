#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V40."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v22_reconciliation", "strict_endpoint_to_residual_spectral_comparison",
        "strict_residual_cyclic_carrier_obstruction", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if value.get("stages") != previous.get("stages"):
        errors.append("global stage vocabulary changed")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell preservation")
    gate_projection = value.get("strict_gate_v22_reconciliation", {})
    if (
        gate_projection.get("result_id") != gate.get("result_id")
        or gate_projection.get("minimal_missing_bundle") != [
            "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION",
            "M4R_TYPED_RESIDUAL_CYCLICITY",
            "M1_COMMON_STRICT_SNAPSHOT",
        ]
        or (
            gate_projection.get("accepted_top_level_hashes"),
            gate_projection.get("remaining_top_level_hashes"),
            gate_projection.get("exports_receiver_verified_scoped"),
            gate_projection.get("freeze_checks_receiver_verified_scoped"),
        ) != (1, 6, 17, 9)
        or gate_projection.get("current_470_induced_odd_pairing_rank_zero") is not True
        or gate_projection.get("finite_940_cotangent_preflight_constructed") is not True
        or gate_projection.get("M3RC_dual_comparison_maps_constructed") is not False
        or gate_projection.get("M4R_typed_residual_cyclicity_complete") is not False
    ):
        errors.append("Gate V22 projection")
    projected = value.get("strict_residual_cyclic_carrier_obstruction", {})
    expected_projection = {
        "result_id": obstruction["result_id"],
        "current_carrier_coordinates": 470,
        "current_carrier_degree_counts": {"0": 470},
        "authoritative_pairing_degree": -1,
        "current_induced_pairing_rank": 0,
        "current_induced_pairing_nullity": 470,
        "nondegeneracy_rank_defect": 470,
        "older_even_form_is_BV_antibracket": False,
        "cotangent_preflight_coordinates": 940,
        "cotangent_preflight_pairing_rank": 940,
        "cotangent_action_pairing_identified": False,
        "M3RC_status": "OPEN",
        "M4R_status": "BLOCKED_BY_M3RC",
    }
    if projected != expected_projection:
        errors.append("residual obstruction projection")
    closure = value.get("strict_local_cyclic_pairing_closure", {})
    if closure.get("M3RC_status") != "OPEN" or closure.get("M4R_status") != "BLOCKED_BY_M3RC_RANK_ZERO":
        errors.append("M3RC/M4R dependency")
    expected_routes = [
        "STRICT_M3RC_DUAL_RESIDUAL_COMPARISON",
        "STRICT_TYPED_RESIDUAL_CYCLICITY",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    routes = value.get("route_selection", [])
    if [row.get("route") for row in routes] != expected_routes or [row.get("rank") for row in routes] != list(range(1, 10)):
        errors.append("route insertion or ordering")
    if [row.get("priority") for row in value.get("research_queue", [])] != list(range(1, 10)):
        errors.append("queue priorities")
    if value.get("frontier_summary", {}).get("highest_value_next_route") != "STRICT_M3RC_DUAL_RESIDUAL_COMPARISON":
        errors.append("frontier route")
    flags = value.get("claim_flags", {})
    for key in (
        "v39_preserved", "strict_current_470_induced_odd_pairing_rank_zero",
        "strict_finite_940_cotangent_carrier_constructed",
        "strict_finite_940_canonical_odd_pairing_nondegenerate",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_current_470_induced_odd_pairing_nondegenerate",
        "strict_older_even_cohomology_form_is_BV_antibracket",
        "strict_finite_940_pairing_action_identified",
        "strict_M3RC_dual_comparison_maps_constructed",
        "strict_M4R_typed_residual_cyclicity_complete",
        "strict_full_residual_cyclic_pairing_certified",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {
        item.get("path"): item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
    }
    for path in (PREDECESSOR, GATE, OBSTRUCTION):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    try:
        expected = digest(value)
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != expected:
            errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - nine routes ranked with M3RC before M4R and M1")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
