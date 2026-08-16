#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V37."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
BINDING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v19_reconciliation", "strict_common_endpoint_sdr_binding",
        "strict_residual_sdr_type_audit", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37"
        or value.get("predecessor", {}).get("result_id") != previous.get("result_id")
    ):
        errors.append("result identity or predecessor")
    if value.get("stages") != previous.get("stages"):
        errors.append("global stage vocabulary changed")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell preservation")
    gate_projection = value.get("strict_gate_v19_reconciliation", {})
    if (
        gate_projection.get("result_id") != gate.get("result_id")
        or gate_projection.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"]
        or (gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes"), gate_projection.get("exports_receiver_verified_scoped"), gate_projection.get("freeze_checks_receiver_verified_scoped")) != (1, 6, 17, 9)
        or gate_projection.get("M3L_common_endpoint_sdr_bound") is not True
        or gate_projection.get("M3R_typed_residual_comparison_constructed") is not False
    ):
        errors.append("Gate V19 projection")
    endpoint = value.get("strict_common_endpoint_sdr_binding", {})
    expected_endpoint = {
        "result_id": binding["result_id"],
        "manifest_id": binding["common_manifest"]["manifest_id"],
        "manifest_sha256": binding["common_manifest"]["sha256"],
        "carrier_rows": 386,
        "endpoint_rows": 30,
        "contracted_rows": 356,
        "artifact_pins": 10,
        "canonical_object_hashes": 17,
        "compatibility_links_checked": 15,
        "projected_identity_defects": 0,
        "support_local": True,
        "residual_comparison_included": False,
    }
    if endpoint != expected_endpoint:
        errors.append("M3L projection")
    route_names = [row.get("route") for row in value.get("route_selection", [])]
    expected_routes = [
        "STRICT_FULL_CYCLIC_PAIRING", "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    if route_names != expected_routes:
        errors.append("route completion or ordering")
    if [row.get("rank") for row in value.get("route_selection", [])] != list(range(1, 10)):
        errors.append("route ranks")
    if [row.get("priority") for row in value.get("research_queue", [])] != list(range(1, 10)):
        errors.append("queue priorities")
    flags = value.get("claim_flags", {})
    for key in (
        "v36_preserved", "strict_386_graph_endpoint_sdr_support_local",
        "strict_M3_typed_split_required", "strict_386_common_endpoint_sdr_manifest_bound",
        "strict_386_common_endpoint_sdr_identities_replayed",
        "strict_386_q1_d_q2_q3_same_local_carrier", "strict_M3L_common_endpoint_sdr_bound",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_graph_endpoint_30_is_finite_residual_30", "strict_dfinite_residual_projector_support_local",
        "strict_zero_mode_projector_support_local", "strict_M3R_typed_residual_comparison_constructed",
        "strict_pure_weyl_classical_gate_passed", "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, BINDING):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    try:
        actual_digest = digest(value)
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != actual_digest:
            errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
