#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V36."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V35.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
AUDIT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v18_reconciliation", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if value.get("stages") != previous.get("stages") or len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("stage or 77-cell preservation")
    gate_projection = value.get("strict_gate_v18_reconciliation", {})
    if gate_projection.get("result_id") != gate.get("result_id") or gate_projection.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M3L_COMMON_ENDPOINT_SDR_BINDING", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"]:
        errors.append("Gate V18 projection")
    if (gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes"), gate_projection.get("exports_receiver_verified_scoped"), gate_projection.get("freeze_checks_receiver_verified_scoped")) != (1, 6, 17, 9):
        errors.append("Gate V18 counts")
    typed = value.get("strict_residual_sdr_type_audit", {})
    expected_typed = {
        "result_id": audit["result_id"],
        "type_census_sha256": audit["type_census"]["sha256"],
        "architecture_decision_sha256": audit["architecture_decision"]["sha256"],
        "graph_carrier_component_species": 386,
        "graph_endpoint_component_species": 30,
        "dfinite_full_coordinates": 4490,
        "dfinite_residual_coordinates": 470,
        "symmetry_cotangent_coordinates": 30,
        "graph_endpoint_is_symmetry_cotangent": False,
        "dfinite_projector_support_local": False,
        "M3_typed_split_required": True,
    }
    if typed != expected_typed:
        errors.append("type-audit projection")
    route_names = [row.get("route") for row in value.get("route_selection", [])]
    if route_names[:4] != ["STRICT_COMMON_ENDPOINT_SDR_BINDING", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"] or len(route_names) != 10 or "STRICT_RESIDUAL_SDR_COMMON_CARRIER" in route_names:
        errors.append("route repair or ordering")
    if [row.get("rank") for row in value.get("route_selection", [])] != list(range(1, 11)) or [row.get("priority") for row in value.get("research_queue", [])] != list(range(1, 11)):
        errors.append("route ranks")
    flags = value.get("claim_flags", {})
    for key in ("v35_preserved", "strict_386_graph_endpoint_sdr_support_local", "strict_M3_typed_split_required"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_graph_endpoint_30_is_finite_residual_30", "strict_dfinite_residual_projector_support_local",
        "strict_zero_mode_projector_support_local", "strict_M3L_common_endpoint_sdr_bound",
        "strict_M3R_typed_residual_comparison_constructed", "strict_pure_weyl_classical_gate_passed",
        "strict_386_q2_q3_green_compatibility_certified", "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, AUDIT):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
