#!/usr/bin/env python3
"""Independently check Atlas V18 and its candidate q2/Green projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Mapping[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous = load(PREDECESSOR)
    preflight = load(PREFLIGHT)
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v18"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    predecessor = value.get("predecessor", {})
    if predecessor != {
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

    align = preflight.get("carrier_alignment", {})
    local = preflight.get("local_q2_continuity", {})
    replay = preflight.get("homotopy_response_replay", {})
    foundation = preflight.get("foundational_strength", {})
    expected_projection = {
        "result_id": preflight.get("result_id"),
        "status": preflight.get("result_state"),
        "carrier_rows": align.get("carrier_rows"),
        "basis_match": align.get("basis_match"),
        "pairing_match": align.get("pairing_match"),
        "graph_q1_match": align.get("graph_q1_match"),
        "causal_orientations_composed": replay.get("sign_orientations_checked"),
        "per_input_derivative_order_bound": local.get("conservative_per_input_derivative_order_bound"),
        "total_derivative_order_bound": local.get("conservative_total_derivative_order_bound"),
        "response_identity_defects": replay.get("response_identity_structural_defects"),
        "causal_difference_identity_defects": replay.get("causal_difference_identity_structural_defects"),
        "plus_response_name_sha256": preflight.get("canonical_hashes", {}).get("plus_response_name_sha256"),
        "minus_response_name_sha256": preflight.get("canonical_hashes", {}).get("minus_response_name_sha256"),
        "causal_difference_name_sha256": preflight.get("canonical_hashes", {}).get("causal_difference_name_sha256"),
        "foundational_classification": foundation.get("classification"),
        "finite_exact_layer": foundation.get("layers", [{}])[0].get("upper_bound"),
        "completed_infinite_spaces_required": foundation.get("layers", [{}, {}, {}])[2].get("completed_infinite_spaces_required"),
        "new_choice_beyond_green_theorem": foundation.get("layers", [{}, {}, {}, {}])[3].get("new_choice_beyond_imported_green_theorem"),
        "weakest_complete_foundational_base": foundation.get("weakest_complete_foundational_base"),
        "candidate_only": True,
        "authoritative_q2_green_compatibility": False,
        "recursive_nonlinear_green_trees": False,
        "next_gate": preflight.get("next_gate"),
    }
    if value.get("strict_q2_green_composition_preflight") != expected_projection:
        errors.append("q2/Green projection")
    if (
        expected_projection["carrier_rows"] != 386
        or not all(expected_projection[key] for key in ("basis_match", "pairing_match", "graph_q1_match"))
        or expected_projection["causal_orientations_composed"] != 2
        or expected_projection["response_identity_defects"] != 0
        or expected_projection["causal_difference_identity_defects"] != 0
    ):
        errors.append("projected invariant")

    strict = new_branches.get("STRICT_PURE_WEYL_386", {})
    nonlinear = next((item for item in strict.get("stages", []) if item.get("stage") == "S3_NONLINEAR_CARTAN"), {})
    if (
        nonlinear.get("status") != "OPEN_SEEDED"
        or preflight.get("result_id") not in nonlinear.get("evidence", [])
        or "first strict nonlinear causal response" not in nonlinear.get("statement", "")
        or strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY"
    ):
        errors.append("strict nonlinear stage/frontier")

    routes = value.get("route_selection", [])
    expected_routes = [
        "STRICT_386_AUTHORITATIVE_Q2_IDENTITY",
        "STRICT_RECURSIVE_CAUSAL_TREE_DOMAINS",
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER",
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_RESIDUAL_EXACT_PAYLOAD",
        "STRICT_CENTERED_REPRESENTATIVES",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_GREEN_FOUNDATIONAL_CALIBRATION",
    ]
    if [item.get("route") for item in routes] != expected_routes or [item.get("rank") for item in routes] != list(range(1, 10)):
        errors.append("route ranking")
    queue = value.get("research_queue", [])
    if [item.get("object") for item in queue] != expected_routes or [item.get("priority") for item in queue] != list(range(1, 10)):
        errors.append("research queue")

    provenance = value.get("provenance", {}).get("inputs", [])
    if provenance[: len(previous["provenance"]["inputs"])] != previous["provenance"]["inputs"]:
        errors.append("append-only provenance")
    if provenance[-2:] != [
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V17 atlas predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "sha256": sha(PREFLIGHT), "role": "strict candidate q2/Green first-response and foundations preflight"},
    ]:
        errors.append("new provenance")

    flags = value.get("claim_flags", {})
    required_true = {
        "v17_preserved",
        "strict_386_candidate_q2_green_same_carrier_verified",
        "strict_386_candidate_first_nonlinear_causal_response_certified",
        "strict_386_candidate_q2_green_causal_support_certified",
        "strict_386_candidate_q2_green_response_identity_verified",
        "strict_386_q2_green_foundations_stratified",
    }
    required_false = {
        "strict_386_authoritative_q2_green_compatibility_certified",
        "strict_386_recursive_nonlinear_green_trees_certified",
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
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 77 cells preserved and the first candidate nonlinear causal response projects")
        print("  - exact local versus infinite analytic foundational layers remain distinct")
        print("  - authority, recursive-tree, Hadamard and QME firewalls remain closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
