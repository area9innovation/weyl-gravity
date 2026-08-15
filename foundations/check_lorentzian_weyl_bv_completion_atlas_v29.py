#!/usr/bin/env python3
"""Independently check Atlas V29 projections, routes, and firewalls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28.json"
LIFT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight", "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation", "strict_gate_v9_reconciliation", "strict_gate_v10_reconciliation", "strict_gate_v11_reconciliation", "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse", "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight", "strict_nonminimal_theory_identity_obstruction", "strict_quadratic_auxiliary_elimination", "strict_shifted_auxiliary_cubic_inventory", "strict_hh_hv_auxiliary_cotangent_lift", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, receiver, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, LIFT, GATE))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29" or value.get("predecessor", {}).get("result_id") != previous["result_id"] or value.get("predecessor", {}).get("sha256") != sha(PREDECESSOR):
        errors.append("identity/predecessor")
    if len(value.get("stages", [])) != len(previous["stages"]) or len(value.get("branches", [])) != len(previous["branches"]):
        errors.append("stage/branch preservation")
    p = value.get("strict_hh_hv_auxiliary_cotangent_lift", {})
    expected = {"result_id": receiver["result_id"], "carrier_rows": 386, "hh_field_coefficients": 1392, "hv_field_coefficients": 76, "vv_field_coefficients": 22, "combined_cotangent_coefficients": 3907, "metric_variation_slices_declared": 150, "vector_variation_slices": 4, "formal_adjoint_defects": 0, "known_required_cubic_families": 7, "component_complete_families": 4, "component_open_families": 3, "full_quadratic_BV_cotangent_lift_serialized": True, "diffeomorphism_BV_representation_component_complete": False, "exhaustive_full_nonlinear_BV_family_census": False, "full_source_q2_q3_pullback_replayed": False, "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_CURVED_TWO_JET_ALGEBRA", "next_gate": receiver["next_gate"]}
    if p != expected:
        errors.append("quadratic lift projection")
    g = value.get("strict_gate_v11_reconciliation", {})
    if g.get("result_id") != gate["result_id"] or g.get("gate_a_status") != "FAIL_CLOSED" or g.get("accepted_top_level_hashes") != 0 or g.get("candidate_q2_hash_accepted") is not False:
        errors.append("Gate V11 projection")
    routes = [item.get("route") for item in value.get("route_selection", [])]
    expected_front = ["STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST", "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE"]
    if len(routes) != 12 or routes[:5] != expected_front or "STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS" in routes or "STRICT_386_BV_COTANGENT_LIFT_COMPONENTS" in routes:
        errors.append("route contraction/order")
    if [item.get("priority") for item in value.get("research_queue", [])] != list(range(1, 13)):
        errors.append("research queue")
    flags = value.get("claim_flags", {})
    expected_flags = {"strict_386_hh_hv_bv_cotangent_lift_component_complete": True, "strict_386_full_quadratic_bv_cotangent_lift_serialized": True, "strict_386_diff_bv_representation_component_complete": False, "strict_386_exhaustive_full_nonlinear_bv_family_census": False, "strict_386_full_source_q2_pullback_replayed": False, "strict_386_full_source_q3_pullback_replayed": False, "strict_386_nonlinear_equivalence_constructed": False, "strict_386_authoritative_q2_imported": False, "strict_386_authoritative_q3_imported": False, "strict_pure_weyl_classical_gate_passed": False, "strict_386_full_bv_hadamard_state_constructed": False, "strict_pure_weyl_qme_restored": False, "lorentzian_full_theory_certified": False}
    if any(flags.get(key) is not expected for key, expected in expected_flags.items()):
        errors.append("promotion firewall")
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, LIFT, GATE):
        if pins.get(str(path.relative_to(ROOT))) != sha(path):
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
