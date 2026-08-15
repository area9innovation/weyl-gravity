#!/usr/bin/env python3
"""Independently check Atlas V19 and its recursive-tree projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18.json"
TREE_DOMAINS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Mapping[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous = load(PREDECESSOR)
    trees = load(TREE_DOMAINS)
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v19"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if value.get("predecessor") != {
        "result_id": previous["result_id"],
        "path": str(PREDECESSOR.relative_to(ROOT)),
        "sha256": sha(PREDECESSOR),
        "preserved": True,
    }:
        errors.append("predecessor binding")

    old_branches = {item["id"]: item for item in previous.get("branches", [])}
    new_branches = {item["id"]: item for item in value.get("branches", [])}
    if set(old_branches) != set(new_branches) or len(new_branches) != 7:
        errors.append("branch preservation")
    if sum(len(item.get("stages", [])) for item in new_branches.values()) != 77:
        errors.append("77-cell preservation")
    for branch_id, old in old_branches.items():
        if branch_id not in new_branches:
            continue
        old_stages = {item["stage"]: item for item in old["stages"]}
        new_stages = {item["stage"]: item for item in new_branches[branch_id]["stages"]}
        if set(old_stages) != set(new_stages):
            errors.append("stage preservation " + branch_id)
        for stage_id, old_stage in old_stages.items():
            if branch_id == "STRICT_PURE_WEYL_386" and stage_id == "S3_NONLINEAR_CARTAN":
                continue
            if new_stages.get(stage_id) != old_stage:
                errors.append("unrelated stage drift " + branch_id + "/" + stage_id)

    theorem = trees.get("recursive_polarized_tree_theorem", {})
    mixed = trees.get("mixed_sign_boundary", {})
    foundation = trees.get("foundational_strength", {})
    census4 = next((item for item in trees.get("sign_decoration_census", []) if item.get("leaves") == 4), {})
    expected_projection = {
        "result_id": trees.get("result_id"),
        "status": trees.get("result_state"),
        "retarded_all_finite_trees": theorem.get("retarded", {}).get("all_finite_plane_binary_trees"),
        "advanced_all_finite_trees": theorem.get("advanced", {}).get("all_finite_plane_binary_trees"),
        "support_domain_defects": theorem.get("finite_tree_support_domain_defects"),
        "nodewise_homotopy_domain_defects": theorem.get("finite_tree_nodewise_homotopy_domain_defects"),
        "continuity_scope": theorem.get("continuity_scope"),
        "first_mixed_failure_leaves": mixed.get("first_uniform_failure_leaf_count"),
        "first_mixed_failure_topology": mixed.get("first_failure_topology"),
        "four_leaf_all_sign_decorations": census4.get("all_sign_decorations"),
        "four_leaf_admissible": census4.get("admissible_total"),
        "four_leaf_not_uniformly_defined": census4.get("not_uniformly_defined"),
        "all_comb_sign_decorations_admissible": mixed.get("all_comb_trees_every_sign_decoration_admissible"),
        "unrestricted_mixed_sign_trees": False,
        "arbitrary_causal_difference_trees": False,
        "infinite_tree_series_convergence": False,
        "q3_or_higher_trees": False,
        "authoritative_q2": False,
        "foundational_classification": foundation.get("classification"),
        "weakest_complete_foundational_base": foundation.get("weakest_complete_foundational_base"),
        "next_gate": trees.get("next_gate"),
    }
    if value.get("strict_recursive_causal_tree_domains") != expected_projection:
        errors.append("recursive-tree projection")
    if (
        expected_projection["retarded_all_finite_trees"] is not True
        or expected_projection["advanced_all_finite_trees"] is not True
        or expected_projection["support_domain_defects"] != 0
        or expected_projection["nodewise_homotopy_domain_defects"] != 0
        or (expected_projection["four_leaf_all_sign_decorations"], expected_projection["four_leaf_admissible"], expected_projection["four_leaf_not_uniformly_defined"]) != (40, 38, 2)
    ):
        errors.append("projected invariant")

    strict = new_branches.get("STRICT_PURE_WEYL_386", {})
    nonlinear = next((item for item in strict.get("stages", []) if item.get("stage") == "S3_NONLINEAR_CARTAN"), {})
    if (
        nonlinear.get("status") != "PARTIAL_CERTIFIED"
        or trees.get("result_id") not in nonlinear.get("evidence", [])
        or "every finite polarized" not in nonlinear.get("statement", "")
        or strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY"
    ):
        errors.append("strict nonlinear stage/frontier")

    expected_routes = [
        "STRICT_386_AUTHORITATIVE_Q2_IDENTITY",
        "STRICT_POLARIZED_FORMAL_MOLLER_COEFFICIENTS",
        "STRICT_HIGHER_BRACKET_CAUSAL_IMPORT",
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER",
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_RESIDUAL_EXACT_PAYLOAD",
        "STRICT_CENTERED_REPRESENTATIVES",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
        "STRICT_GREEN_FOUNDATIONAL_CALIBRATION",
    ]
    routes = value.get("route_selection", [])
    if [item.get("route") for item in routes] != expected_routes or [item.get("rank") for item in routes] != list(range(1, 12)):
        errors.append("route ranking")
    queue = value.get("research_queue", [])
    if [item.get("object") for item in queue] != expected_routes or [item.get("priority") for item in queue] != list(range(1, 12)):
        errors.append("research queue")

    provenance = value.get("provenance", {}).get("inputs", [])
    if provenance[: len(previous["provenance"]["inputs"])] != previous["provenance"]["inputs"]:
        errors.append("append-only provenance")
    if provenance[-2:] != [
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V18 atlas predecessor"},
        {"path": str(TREE_DOMAINS.relative_to(ROOT)), "sha256": sha(TREE_DOMAINS), "role": "strict candidate polarized recursive-tree theorem and mixed-sign boundary"},
    ]:
        errors.append("new provenance")

    flags = value.get("claim_flags", {})
    required_true = {
        "v18_preserved",
        "strict_386_candidate_retarded_all_finite_q2_trees_certified",
        "strict_386_candidate_advanced_all_finite_q2_trees_certified",
        "strict_386_candidate_fixed_step_tree_continuity_certified",
        "strict_386_first_mixed_sign_domain_nondefinition_at_four_leaves",
    }
    required_false = {
        "strict_386_unrestricted_mixed_sign_trees_certified",
        "strict_386_arbitrary_causal_difference_trees_certified",
        "strict_386_infinite_tree_series_convergence_certified",
        "strict_386_authoritative_q2_recursive_trees_certified",
        "strict_386_q3_or_higher_causal_trees_certified",
        "strict_386_authoritative_full_q2_imported",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed",
        "renormalized_lorentzian_products_constructed",
        "strict_pure_weyl_qme_restored",
        "residual_quantum_transfer_authorized",
        "lorentzian_full_theory_certified",
    }
    if not all(flags.get(key) is True for key in required_true) or not all(flags.get(key) is False for key in required_false):
        errors.append("claim/lifecycle firewall")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 77 cells preserved and finite polarized candidate trees close")
        print("  - the exact four-leaf mixed-sign boundary projects as 40/38/2")
        print("  - authority, higher-bracket, infinite-series, Hadamard and QME firewalls remain closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
