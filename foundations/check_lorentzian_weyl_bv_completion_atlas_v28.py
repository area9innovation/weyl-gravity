#!/usr/bin/env python3
"""Independent structural checker for completion Atlas V28."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
INVENTORY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
GATE_V10 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_gate_v10_reconciliation",
        "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains",
        "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness",
        "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight",
        "strict_nonminimal_theory_identity_obstruction", "strict_quadratic_auxiliary_elimination",
        "strict_shifted_auxiliary_cubic_inventory", "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def cells(value: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(branch["id"], stage["stage"]): stage for branch in value["branches"] for stage in branch["stages"]}


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    previous, inventory, gate_v10 = (json.loads(path.read_text()) for path in (PREDECESSOR, INVENTORY, GATE_V10))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v28" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        return ["result identity/version/dependency drift"]
    predecessor = value.get("predecessor", {})
    if predecessor.get("sha256") != sha(PREDECESSOR) or predecessor.get("preserved") is not True:
        errors.append("V27 predecessor binding")
    before, after = cells(previous), cells(value)
    if set(before) != set(after) or len(after) != 77:
        errors.append("77-cell preservation")
    if {key for key in before if before[key] != after[key]} != {("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")}:
        errors.append("unexpected completion-cell mutation")

    exact = value.get("strict_shifted_auxiliary_cubic_inventory", {})
    expected = {
        "result_id": inventory["result_id"], "carrier_rows": 386,
        "known_required_cubic_families": 7, "component_complete_families": 2, "component_open_families": 5,
        "family_ids": [row["family_id"] for row in inventory["required_cubic_family_inventory"]],
        "h_f_hat_f_hat_source_coefficients": 72, "h_f_hat_f_hat_candidate_coefficients": 0,
        "vv_field_map_coefficients": 22, "vv_cotangent_partner_coefficients": 16,
        "vv_active_output_rows": 14, "vv_zero_output_rows": 372,
        "vv_canonicality_slices": 4, "vv_canonicality_defects": 0,
        "vv_BV_cotangent_lift_component_complete": True,
        "hh_hv_BV_cotangent_lift_component_complete": False,
        "diffeomorphism_BV_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "full_386_BV_cotangent_lift_serialized": False,
        "full_source_q2_q3_pullback_replayed": False,
        "full_nonlinear_equivalence_obstructed": False,
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_COMPONENT_ALGEBRA",
        "next_gate": inventory["next_gate"],
    }
    if exact != expected:
        errors.append("shifted-cubic inventory projection")
    gate = value.get("strict_gate_v10_reconciliation", {})
    if gate.get("result_id") != gate_v10["result_id"] or gate.get("gate_a_status") != "FAIL_CLOSED" or gate.get("accepted_top_level_hashes") != 0 or gate.get("known_required_cubic_families") != 7 or gate.get("vv_BV_lift_canonical") is not True or gate.get("full_bv_cotangent_lift_serialized") is not False or gate.get("complete_source_q2_q3_pullback_replayed") is not False:
        errors.append("Gate V10 projection")
    nonlinear = after.get(("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED_SEVEN_CUBIC_FAMILIES_VV_BV_LIFT_CANONICAL_FULL_PULLBACK_OPEN" or inventory["result_id"] not in nonlinear.get("evidence", []):
        errors.append("strict nonlinear cell")

    routes = value.get("route_selection", [])
    expected_front = [
        "STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS",
        "STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS",
        "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST",
        "STRICT_386_BV_COTANGENT_LIFT_COMPONENTS",
        "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
    ]
    if len(routes) != 14 or [item.get("rank") for item in routes] != list(range(1, 15)) or [item.get("route") for item in routes[:7]] != expected_front:
        errors.append("route ordering")
    queue = value.get("research_queue", [])
    if [item.get("priority") for item in queue] != list(range(1, 15)) or [item.get("object") for item in queue] != [item.get("route") for item in routes]:
        errors.append("research queue")

    flags = value.get("claim_flags", {})
    for key in ("v27_preserved", "strict_386_known_required_cubic_families_enumerated", "strict_386_h_f_hat_f_hat_components_imported", "strict_386_vv_field_map_components_imported", "strict_386_vv_cotangent_partner_components_serialized", "strict_386_vv_bv_cotangent_lift_canonical"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_386_exhaustive_full_nonlinear_bv_family_census", "strict_386_hh_hv_bv_cotangent_lift_component_complete", "strict_386_diff_bv_representation_component_complete", "strict_386_full_bv_cotangent_lift_serialized", "strict_386_full_source_q2_pullback_replayed", "strict_386_full_source_q3_pullback_replayed", "strict_386_nonlinear_equivalence_constructed", "strict_386_nonlinear_equivalence_obstructed", "strict_386_authoritative_q2_imported", "strict_386_authoritative_q3_imported", "strict_386_candidate_causal_lambda2_source_closure_certified", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3:
        errors.append("provenance count")
    else:
        for item, path in zip(provenance[-3:], (PREDECESSOR, INVENTORY, GATE_V10)):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
                errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28_CHECK: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
