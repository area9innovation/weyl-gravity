#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V39."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V38.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
M3R = ROOT / "quantum-weyl/classical_import/certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v21_reconciliation", "strict_endpoint_to_residual_spectral_comparison",
        "strict_local_cyclic_pairing_closure", "strict_common_endpoint_sdr_binding",
        "strict_residual_sdr_type_audit", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
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
    comparison = json.loads(M3R.read_text(encoding="utf-8"))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if value.get("stages") != previous.get("stages"):
        errors.append("global stage vocabulary changed")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell preservation")
    gate_projection = value.get("strict_gate_v21_reconciliation", {})
    if (
        gate_projection.get("result_id") != gate.get("result_id")
        or gate_projection.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M4R_TYPED_RESIDUAL_CYCLICITY"]
        or (
            gate_projection.get("accepted_top_level_hashes"),
            gate_projection.get("remaining_top_level_hashes"),
            gate_projection.get("exports_receiver_verified_scoped"),
            gate_projection.get("freeze_checks_receiver_verified_scoped"),
        ) != (1, 6, 17, 9)
        or gate_projection.get("M3R_typed_residual_comparison_constructed") is not True
        or gate_projection.get("M4L_local_graph_cyclic_pairing_complete") is not True
        or gate_projection.get("M4R_typed_residual_cyclicity_complete") is not False
    ):
        errors.append("Gate V21 projection")
    projected = value.get("strict_endpoint_to_residual_spectral_comparison", {})
    expected_projection = {
        "result_id": comparison["result_id"],
        "source_category": "represented D-finite globally smooth endpoint harmonics",
        "target_category": "finite W+/W- residual coefficient space",
        "energies": [2, 3, 4, 5, 6],
        "represented_endpoint_coordinates": 4080,
        "residual_coordinates": 470,
        "level_dimensions": [10, 40, 82, 136, 202],
        "ordered_crosswalk_defects": 0,
        "chain_identity_defects": 0,
        "support_local": False,
        "smooth_completion_certified": False,
        "M3R_status": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
    }
    if projected != expected_projection:
        errors.append("M3R projection")
    if value.get("strict_local_cyclic_pairing_closure", {}).get("M4R_status") != "OPEN_READY_AFTER_M3R":
        errors.append("M4R readiness")
    expected_routes = [
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
    if [row.get("route") for row in routes] != expected_routes or [row.get("rank") for row in routes] != list(range(1, 9)):
        errors.append("route completion or ordering")
    if [row.get("priority") for row in value.get("research_queue", [])] != list(range(1, 9)):
        errors.append("queue priorities")
    flags = value.get("claim_flags", {})
    for key in (
        "v38_preserved", "strict_M3R_typed_residual_comparison_constructed",
        "strict_M3R_ordered_470_mode_crosswalk_bijective",
        "strict_M3R_chain_identities_replayed",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_harmonic_analysis_support_local", "strict_all_energy_or_smooth_completion_certified",
        "strict_M4R_typed_residual_cyclicity_complete", "strict_full_residual_cyclic_pairing_certified",
        "strict_pure_weyl_classical_gate_passed", "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {
        item.get("path"): item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
    }
    for path in (PREDECESSOR, GATE, M3R):
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
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
