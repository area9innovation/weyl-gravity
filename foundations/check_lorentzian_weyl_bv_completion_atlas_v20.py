#!/usr/bin/env python3
"""Independently check Atlas V20 and its formal-coefficient projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"
FORMAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"


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
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous = load(PREDECESSOR)
    formal = load(FORMAL)
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20" or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v20" or value.get("lifecycle") != "CLASSIFIED":
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

    rows = formal.get("catalan_tree_formula", {}).get("checked_rows", [])
    diagnostic = formal.get("bv_equation_diagnostic", {})
    foundation = formal.get("foundational_strength", {})
    expected = {
        "result_id": formal.get("result_id"),
        "status": formal.get("result_state"),
        "orientations": 2,
        "checked_through_leaves": formal.get("catalan_tree_formula", {}).get("checked_through_leaves"),
        "largest_checked_tree_count": rows[-1].get("plane_tree_count") if rows else None,
        "coefficientwise_fixed_point": True,
        "catalan_formula": True,
        "formal_inverse": True,
        "lambda_adic_stabilization": True,
        "analytic_convergence": False,
        "nonperturbative_inverse": False,
        "order_lambda_bv_residual_zero": True,
        "order_lambda_squared_bv_residual": diagnostic.get("order_lambda_squared_residual"),
        "order_lambda_squared_bv_residual_zero_certified": False,
        "weyl_bv_maurer_cartan_series": False,
        "authoritative_weyl_bv_moller_map": False,
        "typed_field_equation_green_inverse": False,
        "q3_or_higher_imported": False,
        "foundational_classification": foundation.get("classification"),
        "weakest_complete_foundational_base": foundation.get("weakest_complete_foundational_base"),
        "next_gate": formal.get("next_gate"),
    }
    if value.get("strict_polarized_formal_coefficients") != expected:
        errors.append("formal-coefficient projection")
    if not rows or rows[-1].get("leaves") != 9 or rows[-1].get("plane_tree_count") != 1430:
        errors.append("formal census invariant")

    strict = new_branches.get("STRICT_PURE_WEYL_386", {})
    nonlinear = next((item for item in strict.get("stages", []) if item.get("stage") == "S3_NONLINEAR_CARTAN"), {})
    if nonlinear.get("status") != "PARTIAL_CERTIFIED" or formal.get("result_id") not in nonlinear.get("evidence", []) or "lambda squared" not in nonlinear.get("statement", "") or strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY":
        errors.append("strict nonlinear stage/frontier")

    expected_routes = [
        "STRICT_386_AUTHORITATIVE_Q2_IDENTITY",
        "STRICT_TYPED_FIELD_EQUATION_GREEN_INVERSE",
        "STRICT_Q2_Q3_MAURER_CARTAN_CLOSURE",
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
    if [item.get("route") for item in routes] != expected_routes or [item.get("rank") for item in routes] != list(range(1, 13)):
        errors.append("route ranking")
    if [item.get("object") for item in queue] != expected_routes or [item.get("priority") for item in queue] != list(range(1, 13)):
        errors.append("research queue")

    provenance = value.get("provenance", {}).get("inputs", [])
    if provenance[:len(previous["provenance"]["inputs"])] != previous["provenance"]["inputs"]:
        errors.append("append-only provenance")
    if provenance[-2:] != [
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V19 atlas predecessor"},
        {"path": str(FORMAL.relative_to(ROOT)), "sha256": sha(FORMAL), "role": "strict candidate polarized formal coefficients and BV promotion diagnostic"},
    ]:
        errors.append("new provenance")

    flags = value.get("claim_flags", {})
    required_true = (
        "v19_preserved", "strict_386_candidate_polarized_formal_coefficients_certified",
        "strict_386_candidate_coefficientwise_fixed_point_verified", "strict_386_candidate_catalan_formula_verified",
        "strict_386_candidate_lambda_adic_stabilization_verified",
    )
    required_false = (
        "strict_386_order_lambda_squared_bv_residual_zero_certified", "strict_386_typed_field_equation_green_inverse_certified",
        "strict_386_weyl_bv_maurer_cartan_series_certified", "strict_386_authoritative_formal_moller_map_certified",
        "strict_386_analytic_moller_convergence_certified", "strict_386_nonperturbative_moller_map_constructed",
        "strict_386_q3_or_higher_causal_trees_certified", "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed", "renormalized_lorentzian_products_constructed",
        "strict_pure_weyl_qme_restored", "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
    )
    if not all(flags.get(key) is True for key in required_true) or not all(flags.get(key) is False for key in required_false):
        errors.append("claim/lifecycle firewall")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 77 cells preserved and exact polarized formal coefficients project")
        print("  - lambda-adic stabilization is separated from analytic convergence")
        print("  - the lambda-squared BV/Moller promotion gate remains fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
