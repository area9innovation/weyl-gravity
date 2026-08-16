#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V41."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
DUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
GATE_CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v23_reconciliation.py"
DUAL_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_dfinite_cotangent_dual_comparison.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v23_reconciliation", "strict_dfinite_cotangent_dual_comparison",
        "strict_endpoint_to_residual_spectral_comparison",
        "strict_residual_cyclic_carrier_obstruction", "strict_local_cyclic_pairing_closure",
        "strict_common_endpoint_sdr_binding", "strict_residual_sdr_type_audit",
        "strict_source_q2_common_assembly", "strict_source_q3_common_assembly",
        "strict_residual_zero_mode_payload", "strict_centered_cohomology_payload",
        "route_selection", "research_queue",
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
    dual = json.loads(DUAL.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41", "result identity")
    require(value.get("predecessor", {}).get("result_id") == previous.get("result_id"), "predecessor identity")
    require(value.get("stages") == previous.get("stages"), "global stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")
    try:
        require(not load(GATE_CHECKER, "gate_v23_atlas_receiver").check(gate), "Gate V23 receiver replay")
        require(not load(DUAL_CHECKER, "dual_atlas_receiver").check(dual), "formal-dual receiver replay")
    except Exception as exc:
        errors.append(f"dependency checker exception: {exc}")

    gate_projection = value.get("strict_gate_v23_reconciliation", {})
    require(gate_projection.get("result_id") == gate.get("result_id"), "Gate V23 identity projection")
    require(gate_projection.get("minimal_missing_bundle") == [
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION",
        "M4R_TYPED_RESIDUAL_CYCLICITY",
        "M1_COMMON_STRICT_SNAPSHOT",
    ], "Gate V23 missing bundle")
    require((
        gate_projection.get("accepted_top_level_hashes"),
        gate_projection.get("remaining_top_level_hashes"),
        gate_projection.get("exports_receiver_verified_scoped"),
        gate_projection.get("freeze_checks_receiver_verified_scoped"),
    ) == (1, 6, 17, 9), "Gate V23 counts")
    require(gate_projection.get("M3RC_A_formal_cotangent_dual_comparison_complete") is True, "M3RC-A projection")
    require(gate_projection.get("M3RC_B_action_support_dual_identification_complete") is False, "M3RC-B promotion")
    require(gate_projection.get("M4R_typed_residual_cyclicity_complete") is False, "M4R promotion")
    require(gate_projection.get("gate_a_status") == "FAIL_CLOSED", "Gate A promotion")

    comparison = value.get("strict_dfinite_cotangent_dual_comparison", {})
    require(comparison == {
        "result_id": dual["result_id"],
        "original_source_full_dimension": 4490,
        "original_source_H0_dimension": 470,
        "original_source_H1_dimension": 0,
        "same_source_retract_to_940_possible": False,
        "formal_cotangent_source_dimension": 8980,
        "formal_cotangent_residual_dimension": 940,
        "formal_full_pairing_rank": 8980,
        "formal_residual_pairing_rank": 940,
        "formal_identity_defects": 0,
        "M3RC_A_status": "COMPLETE",
        "M3RC_B_status": "OPEN",
        "action_support_dual_identified": False,
    }, "formal cotangent comparison projection")
    require(value.get("strict_residual_cyclic_carrier_obstruction", {}).get("M3RC_status") == "SPLIT_M3RC_A_COMPLETE_M3RC_B_OPEN", "M3RC split")
    require(value.get("strict_residual_cyclic_carrier_obstruction", {}).get("M4R_status") == "BLOCKED_BY_M3RC_B", "M4R dependency")

    expected_routes = [
        "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION",
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
    require([row.get("route") for row in routes] == expected_routes, "route order")
    require([row.get("rank") for row in routes] == list(range(1, 10)), "route ranks")
    require([row.get("priority") for row in value.get("research_queue", [])] == list(range(1, 10)), "queue priorities")
    require(value.get("frontier_summary", {}).get("highest_value_next_route") == expected_routes[0], "frontier route")

    flags = value.get("claim_flags", {})
    for key in (
        "v40_preserved", "strict_original_dfinite_H1_zero",
        "strict_M3RC_A_formal_cotangent_dual_comparison_complete",
        "strict_formal_8980_to_940_cotangent_SDR_exact",
        "strict_formal_cotangent_pairing_nondegenerate",
    ):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_unchanged_4490_source_retracts_to_940_residual",
        "strict_M3RC_B_action_support_dual_identification_complete",
        "strict_formal_dual_identified_with_action_support_dual",
        "strict_M3RC_dual_comparison_maps_constructed",
        "strict_M4R_typed_residual_cyclicity_complete",
        "strict_full_residual_cyclic_pairing_certified",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)

    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, DUAL):
        require(pins.get(str(path.relative_to(ROOT))) == hashlib.sha256(path.read_bytes()).hexdigest(), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V41: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - M3RC-A exact; M3RC-B ranked before M4R and M1")
        print("  - Gate A, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
