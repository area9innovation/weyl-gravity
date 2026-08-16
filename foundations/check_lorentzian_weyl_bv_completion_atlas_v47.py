#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V47."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
PRIMAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
GATE_CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v29_reconciliation.py"
PRIMAL_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1b_primal_composite_contraction.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v29_reconciliation", "strict_m1b_primal_composite_contraction",
        "strict_gate_v28_reconciliation", "strict_m1a_represented_crosswalk",
        "strict_m1a_immutable_typed_ledger", "strict_gate_v27_reconciliation",
        "strict_m1a_local_semantic_extension", "strict_m1_common_snapshot_preflight",
        "strict_dfinite_cotangent_dual_comparison", "strict_m3rc_action_support_dual_identification",
        "strict_typed_residual_cyclicity", "strict_endpoint_to_residual_spectral_comparison",
        "strict_residual_cyclic_carrier_obstruction", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    primal = json.loads(PRIMAL.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47", "result identity")
    require(value.get("lifecycle") == "CLASSIFIED", "lifecycle")
    require(value.get("dependency_tags") == previous.get("dependency_tags"), "dependency tags")
    require(value.get("predecessor", {}).get("result_id") == previous.get("result_id"), "predecessor identity")
    require(value.get("predecessor", {}).get("sha256") == hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(), "predecessor hash")
    require(value.get("stages") == previous.get("stages"), "global stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")

    previous_branches = {branch["id"]: branch for branch in previous["branches"]}
    current_branches = {branch["id"]: branch for branch in value.get("branches", [])}
    for branch_id, branch in previous_branches.items():
        current = current_branches.get(branch_id)
        if branch_id != "STRICT_PURE_WEYL_386":
            require(current == branch, f"unrelated branch drift {branch_id}")
        elif current:
            old_stages = {row["stage"]: row for row in branch["stages"]}
            new_stages = {row["stage"]: row for row in current["stages"]}
            for stage_id, row in old_stages.items():
                if stage_id != "S0_CLASSICAL_AUTHORITY":
                    require(new_stages.get(stage_id) == row, f"unrelated strict stage drift {stage_id}")
            authority = new_stages.get("S0_CLASSICAL_AUTHORITY", {})
            require(primal["result_id"] in authority.get("evidence", []) and gate["result_id"] in authority.get("evidence", []), "S0 evidence")
            require("D-finite" in authority.get("boundary", "") and "support-expanding" in authority.get("boundary", ""), "S0 boundary")

    try:
        require(not load_module(GATE_CHECKER, "gate_v29_atlas_receiver").check(gate), "Gate V29 receiver replay")
        require(not load_module(PRIMAL_CHECKER, "m1b_primal_atlas_receiver").check(primal), "M1B primal receiver replay")
    except Exception as exc:
        errors.append(f"dependency checker exception:{exc}")

    gate_projection = value.get("strict_gate_v29_reconciliation", {})
    require(gate_projection.get("result_id") == gate.get("result_id"), "Gate V29 projection")
    require((gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes")) == (1, 6), "Gate hash counts")
    require(gate_projection.get("M1B_primal_complete") is True, "M1B primal lifecycle")
    require(gate_projection.get("M1B_action_dual_complete") is False, "M1B dual promotion")
    require(gate_projection.get("M1B_cyclic_replay_complete") is False, "M1B cyclic promotion")
    require(gate_projection.get("M1B_complete") is False, "M1B promotion")
    require(gate_projection.get("M1C_common_manifest_replay_complete") is False, "M1C promotion")
    require(gate_projection.get("gate_a_status") == "FAIL_CLOSED", "Gate A promotion")

    aggregate = primal["represented_contraction"]["aggregate"]
    projection = value.get("strict_m1b_primal_composite_contraction", {})
    require(projection.get("result_id") == primal.get("result_id"), "M1B primal result identity")
    require(projection.get("content_sha256") == primal.get("content_sha256"), "M1B primal content hash")
    require((projection.get("represented_endpoint_rows"), projection.get("primal_residual_rows")) == (4080, 470), "M1B dimensions")
    require((projection.get("q0_nonzero_entries"), projection.get("homotopy_nonzero_entries"), projection.get("inclusion_nonzero_entries"), projection.get("projection_nonzero_entries")) == (1805, 1805, 470, 470), "M1B matrix census")
    require((projection.get("represented_identity_defects"), projection.get("formal_composition_defects")) == (0, 0), "M1B defects")
    require(projection.get("local_graph_factor_support_local") is True, "local support boundary")
    require(projection.get("harmonic_restriction_support_local") is False, "harmonic support promotion")
    require(projection.get("raw_component_matrix_constructed") is False, "raw matrix promotion")
    require(projection.get("M1B_primal_complete") is True and projection.get("M1B_complete") is False, "M1B sublayer boundary")
    require(aggregate["represented_rows"] == projection.get("represented_endpoint_rows"), "source dimension drift")

    expected_routes = [
        "STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY",
        "STRICT_M1C_COMMON_MANIFEST_REPLAY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    routes = value.get("route_selection", [])
    require([row.get("route") for row in routes] == expected_routes, "route order")
    require([row.get("rank") for row in routes] == list(range(1, 10)), "route ranks")
    require([row.get("priority") for row in value.get("research_queue", [])] == list(range(1, 10)), "queue priorities")
    require(value.get("frontier_summary", {}).get("highest_value_next_route") == expected_routes[0], "frontier route")
    require(value.get("frontier_summary", {}).get("completed_since_v46") == ["STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION", "GATE_V29_M1B_PRIMAL_RECONCILIATION"], "completion ledger")

    flags = value.get("claim_flags", {})
    for key in ("v46_preserved", "strict_M1B_primal_composite_contraction_complete"):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_M1B_action_dual_lift_complete", "strict_M1B_typed_cyclic_replay_complete",
        "strict_M1B_represented_composite_contraction_complete", "strict_M1C_common_manifest_replay_complete",
        "strict_M1_common_strict_snapshot_complete", "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, PRIMAL):
        require(pins.get(str(path.relative_to(ROOT))) == hashlib.sha256(path.read_bytes()).hexdigest(), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text(encoding="utf-8")))
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M1B primal complete as an exact typed D-finite composite")
        print("  - action-dual lift is now the ranked frontier")
        print("  - Gate A, Hadamard and QME remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
