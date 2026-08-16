#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V46."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
M1A3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
M1A4 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
GATE_CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v28_reconciliation.py"
M1A3_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_represented_carrier_crosswalk.py"
M1A4_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_immutable_typed_ledger.py"


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
    m1a3 = json.loads(M1A3.read_text(encoding="utf-8"))
    m1a4 = json.loads(M1A4.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46", "result identity")
    require(value.get("predecessor", {}).get("result_id") == previous.get("result_id"), "predecessor identity")
    require(value.get("stages") == previous.get("stages"), "global stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")
    try:
        require(not load(GATE_CHECKER, "gate_v28_atlas_receiver").check(gate), "Gate V28 receiver replay")
        require(not load(M1A3_CHECKER, "m1a3_atlas_receiver").check(m1a3), "M1A3 receiver replay")
        require(not load(M1A4_CHECKER, "m1a4_atlas_receiver").check(m1a4), "M1A4 receiver replay")
    except Exception as exc:
        errors.append(f"dependency checker exception: {exc}")

    gate_projection = value.get("strict_gate_v28_reconciliation", {})
    require(gate_projection.get("result_id") == gate.get("result_id"), "Gate V28 projection")
    require((gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes")) == (1, 6), "Gate hash counts")
    require(gate_projection.get("authoritative_rows_total") == 17779, "Gate M1A row count")
    require(gate_projection.get("M1A_complete") is True, "M1A lifecycle")
    require(gate_projection.get("M1B_represented_composite_contraction_complete") is False, "M1B promotion")
    require(gate_projection.get("M1C_common_manifest_replay_complete") is False, "M1C promotion")
    require(gate_projection.get("gate_a_status") == "FAIL_CLOSED", "Gate A promotion")

    crosswalk = value.get("strict_m1a_represented_crosswalk", {})
    require(crosswalk.get("result_id") == m1a3.get("result_id"), "M1A3 result identity")
    require((crosswalk.get("represented_endpoint_rows"), crosswalk.get("excluded_test_rows"), crosswalk.get("excluded_test_doublets")) == (4080, 410, 205), "M1A3 D-finite partition")
    require((crosswalk.get("action_residual_primal_rows"), crosswalk.get("action_residual_dual_rows")) == (470, 470), "M1A3 residual partition")
    require((crosswalk.get("q0_cross_partition_defects"), crosswalk.get("q0_chain_degree_defects"), crosswalk.get("residual_crosswalk_defects")) == (0, 0, 0), "M1A3 defect counts")
    require(crosswalk.get("M1A3_complete") is True, "M1A3 lifecycle")

    ledger = value.get("strict_m1a_immutable_typed_ledger", {})
    require(ledger.get("result_id") == m1a4.get("result_id"), "M1A4 result identity")
    require((ledger.get("authoritative_rows_total"), ledger.get("authoritative_carrier_objects"), ledger.get("untyped_authoritative_rows"), ledger.get("category_identification_defects")) == (17779, 6, 0, 0), "M1A4 carrier census")
    require(ledger.get("typed_field_dictionary_sha256") == m1a4["typed_field_dictionary"]["sha256"], "M1A4 field dictionary hash")
    require(ledger.get("typed_diagram_sha256") == m1a4["diagram_freeze"]["sha256"], "M1A4 diagram hash")
    require(ledger.get("M1A4_complete") is True and ledger.get("M1A_complete") is True, "M1A4/M1A lifecycle")

    expected_routes = [
        "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION", "STRICT_M1B_ACTION_DUAL_LIFT",
        "STRICT_M1B_TYPED_CYCLIC_REPLAY", "STRICT_M1C_COMMON_MANIFEST_REPLAY",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    routes = value.get("route_selection", [])
    require([row.get("route") for row in routes] == expected_routes, "route order")
    require([row.get("rank") for row in routes] == list(range(1, 11)), "route ranks")
    require([row.get("priority") for row in value.get("research_queue", [])] == list(range(1, 11)), "queue priorities")
    require(value.get("frontier_summary", {}).get("highest_value_next_route") == expected_routes[0], "frontier route")

    flags = value.get("claim_flags", {})
    for key in ("v45_preserved", "strict_M1A3_represented_crosswalk_complete", "strict_M1A4_ledger_freeze_complete", "strict_M1A_full_typed_carrier_ledger_complete"):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_M1B_represented_composite_contraction_complete", "strict_M1C_common_manifest_replay_complete",
        "strict_M1_common_strict_snapshot_complete", "strict_pure_weyl_classical_gate_passed",
        "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored",
        "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, M1A3, M1A4):
        require(pins.get(str(path.relative_to(ROOT))) == hashlib.sha256(path.read_bytes()).hexdigest(), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text(encoding="utf-8")))
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V46: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M1A complete across 17,779 rows and six typed carrier objects")
        print("  - M1B primal, action-dual and cyclic composition is the ranked frontier")
        print("  - Gate A, Hadamard and QME remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
