#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V44."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V43.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
GATE_CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v26_reconciliation.py"
PREFLIGHT_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1_common_snapshot_preflight.py"


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
        "strict_gate_v26_reconciliation", "strict_m1_common_snapshot_preflight",
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
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44", "result identity")
    require(value.get("predecessor", {}).get("result_id") == previous.get("result_id"), "predecessor identity")
    require(value.get("stages") == previous.get("stages"), "global stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")
    try:
        require(not load(GATE_CHECKER, "gate_v26_atlas_receiver").check(gate), "Gate V26 receiver replay")
        require(not load(PREFLIGHT_CHECKER, "m1_preflight_atlas_receiver").check(preflight), "M1 preflight receiver replay")
    except Exception as exc:
        errors.append(f"dependency checker exception: {exc}")

    gate_projection = value.get("strict_gate_v26_reconciliation", {})
    require(gate_projection.get("result_id") == gate.get("result_id"), "Gate V26 projection")
    require((gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes")) == (1, 6), "Gate hash counts")
    require(gate_projection.get("minimal_missing_bundle") == ["M1_COMMON_STRICT_SNAPSHOT"], "sole M1 bundle")
    require(gate_projection.get("M1_preflight_complete") is True and gate_projection.get("M1_common_strict_snapshot_complete") is False, "preflight/snapshot lifecycle")
    require(gate_projection.get("gate_a_status") == "FAIL_CLOSED", "Gate A promotion")

    projected = value.get("strict_m1_common_snapshot_preflight", {})
    require(projected.get("result_id") == preflight.get("result_id"), "M1 preflight identity")
    require((projected.get("carrier_count"), projected.get("typed_edge_count")) == (8, 7), "typed diagram counts")
    require((projected.get("exports_total"), projected.get("exports_object_ready"), projected.get("exports_blocked_typed_ledger"), projected.get("exports_blocked_composite")) == (20, 14, 2, 4), "export partition")
    require((projected.get("hashes_total"), projected.get("hash_objects_ready"), projected.get("hashes_blocked")) == (7, 4, 3), "hash partition")
    require(projected.get("freeze_checks_common_snapshot_replayed") == 0, "final replay promotion")
    require(projected.get("work_packages") == ["M1A_FULL_TYPED_CARRIER_LEDGER", "M1B_REPRESENTED_COMPOSITE_CONTRACTION", "M1C_COMMON_MANIFEST_REPLAY"], "work-package order")
    require(projected.get("formal_8980_source_authoritative") is False, "formal source promotion")

    expected_routes = [
        "STRICT_M1A_FULL_TYPED_CARRIER_LEDGER", "STRICT_M1B_REPRESENTED_COMPOSITE_CONTRACTION",
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

    flags = value.get("claim_flags", {})
    for key in ("v43_preserved", "strict_M1_preflight_complete", "strict_M1_typed_diagram_required"):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_M1_is_clerical_hash_bundle", "strict_M1A_full_typed_carrier_ledger_complete",
        "strict_M1B_represented_composite_contraction_complete", "strict_M1C_common_manifest_replay_complete",
        "strict_M1_common_strict_snapshot_complete", "strict_formal_8980_source_is_authoritative_original_BV_complex",
        "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed",
        "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)

    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, PREFLIGHT):
        require(pins.get(str(path.relative_to(ROOT))) == hashlib.sha256(path.read_bytes()).hexdigest(), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V44: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M1 resolved into ordered M1A, M1B and M1C construction routes")
        print("  - Gate A, Hadamard and QME remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
