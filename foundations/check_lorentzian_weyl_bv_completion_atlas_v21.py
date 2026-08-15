#!/usr/bin/env python3
"""Independently check Atlas V21 and the quotient-inverse projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20.json"
TYPED = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Mapping[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous = load(PREDECESSOR)
    typed = load(TYPED)
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v21" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("predecessor") != {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}:
        errors.append("predecessor binding")

    old_branches = {item["id"]: item for item in previous.get("branches", [])}
    new_branches = {item["id"]: item for item in value.get("branches", [])}
    if set(old_branches) != set(new_branches) or len(new_branches) != 7 or sum(len(item.get("stages", [])) for item in new_branches.values()) != 77:
        errors.append("branch/77-cell preservation")
    for branch_id, old in old_branches.items():
        old_stages = {item["stage"]: item for item in old["stages"]}
        new_stages = {item["stage"]: item for item in new_branches.get(branch_id, {}).get("stages", [])}
        if set(old_stages) != set(new_stages):
            errors.append("stage preservation " + branch_id)
            continue
        for stage_id, old_stage in old_stages.items():
            if (branch_id, stage_id) != ("STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN") and new_stages[stage_id] != old_stage:
                errors.append("unrelated stage drift " + branch_id + "/" + stage_id)

    c = typed.get("typed_complex", {})
    h = typed.get("restricted_homotopy_identities", {})
    o = typed.get("full_inverse_obstruction", {})
    n = typed.get("nonlinear_consequence", {})
    f = typed.get("foundational_strength", {})
    expected = {
        "result_id": typed.get("result_id"),
        "status": typed.get("result_state"),
        "field_rows": c.get("field_space", {}).get("rows"),
        "equation_rows": c.get("equation_space", {}).get("rows"),
        "gauge_nonzero_coefficients": o.get("nonzero_gauge_coefficients"),
        "field_equation_nonzero_coefficients": c.get("field_equation_operator", {}).get("nonzero_rational_jet_coefficients"),
        "noether_nonzero_coefficients": o.get("nonzero_noether_coefficients"),
        "green_component_typed": True,
        "constrained_right_inverse": True,
        "quotient_left_inverse": True,
        "source_identity": h.get("source_identity"),
        "field_identity": h.get("field_identity"),
        "full_ungauge_fixed_two_sided_inverse": False,
        "full_inverse_obstructed": True,
        "first_order_candidate_source_typed": True,
        "all_order_nonlinear_source_closure": False,
        "corrected_promotion_gate": n.get("corrected_promotion_gate"),
        "quotient_representative_selection_required": False,
        "foundational_classification": f.get("classification"),
        "weakest_complete_foundational_base": f.get("weakest_complete_foundational_base"),
        "next_gate": typed.get("next_gate"),
    }
    if value.get("strict_field_equation_green_quotient_inverse") != expected:
        errors.append("typed quotient-inverse projection")
    if (expected["field_rows"], expected["equation_rows"], expected["gauge_nonzero_coefficients"], expected["field_equation_nonzero_coefficients"], expected["noether_nonzero_coefficients"]) != (116, 116, 425, 3264, 425):
        errors.append("typed component census invariant")

    strict = new_branches.get("STRICT_PURE_WEYL_386", {})
    nonlinear = next((item for item in strict.get("stages", []) if item.get("stage") == "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED" or typed.get("result_id") not in nonlinear.get("evidence", []) or "lambda-squared" not in nonlinear.get("statement", "") or strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY":
        errors.append("strict nonlinear stage/frontier")

    expected_routes = [
        "STRICT_386_AUTHORITATIVE_Q2_IDENTITY",
        "STRICT_Q2_Q3_SOURCE_COCYCLE_CLOSURE",
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER",
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_RESIDUAL_EXACT_PAYLOAD",
        "STRICT_CENTERED_REPRESENTATIVES",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
        "STRICT_GREEN_FOUNDATIONAL_CALIBRATION",
    ]
    routes = value.get("route_selection", [])
    queue = value.get("research_queue", [])
    if [item.get("route") for item in routes] != expected_routes or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route ranking")
    if [item.get("object") for item in queue] != expected_routes or [item.get("priority") for item in queue] != list(range(1, 12)):
        errors.append("research queue")
    if "STRICT_TYPED_FIELD_EQUATION_GREEN_INVERSE" in expected_routes:
        errors.append("impossible legacy route retained")

    provenance = value.get("provenance", {}).get("inputs", [])
    if provenance[:len(previous["provenance"]["inputs"])] != previous["provenance"]["inputs"]:
        errors.append("append-only provenance")
    if provenance[-2:] != [
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V20 atlas predecessor"},
        {"path": str(TYPED.relative_to(ROOT)), "sha256": sha(TYPED), "role": "typed field-equation quotient inverse and full inverse obstruction"},
    ]:
        errors.append("new provenance")

    flags = value.get("claim_flags", {})
    required_true = (
        "v20_preserved", "strict_386_field_equation_green_component_typed",
        "strict_386_field_equation_constrained_right_inverse_certified",
        "strict_386_field_equation_quotient_left_inverse_certified",
        "strict_386_ungauge_fixed_two_sided_green_inverse_obstructed",
        "strict_386_candidate_first_order_source_cocycle_certified",
    )
    required_false = (
        "strict_386_ungauge_fixed_two_sided_green_inverse_constructed",
        "strict_386_all_order_nonlinear_source_closure_certified",
        "strict_386_order_lambda_squared_bv_residual_zero_certified",
        "strict_386_authoritative_formal_moller_map_certified",
        "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed",
        "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored",
        "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
    )
    if not all(flags.get(key) is True for key in required_true) or not all(flags.get(key) is False for key in required_false):
        errors.append("claim/lifecycle firewall")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 77 cells preserved and the 116/116 quotient inverse projects")
        print("  - full ungauge-fixed inverse is rejected by exact gauge/Noether witnesses")
        print("  - source-cocycle closure is now the highest nonlinear promotion gate")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
