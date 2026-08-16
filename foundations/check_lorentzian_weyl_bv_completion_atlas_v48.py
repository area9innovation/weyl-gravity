#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V48."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V47.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json"
DUAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
M1C = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v48.schema.json"
CHECKERS = (
    (GATE, ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v30_reconciliation.py", "gate_v30_atlas_receiver"),
    (DUAL, ROOT / "quantum-weyl/classical_import/check_strict_m1b_action_dual_lift.py", "m1b_dual_atlas_receiver"),
    (CYCLIC, ROOT / "quantum-weyl/classical_import/check_strict_m1b_typed_cyclic_composite.py", "m1b_cyclic_atlas_receiver"),
    (M1C, ROOT / "quantum-weyl/classical_import/check_strict_m1c_common_snapshot.py", "m1c_atlas_receiver"),
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        "strict_gate_v30_reconciliation", "strict_m1b_action_dual_lift",
        "strict_m1b_typed_cyclic_composite", "strict_m1c_common_snapshot",
        "route_selection", "research_queue", "claim_flags", "does_not_establish",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous, gate, dual, cyclic, m1c = map(load, (PREDECESSOR, GATE, DUAL, CYCLIC, M1C))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        require(not list(Draft202012Validator(schema).iter_errors(value)), "schema validation")
    except Exception as exc:
        errors.append(f"schema exception:{exc}")
    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48", "result identity")
    require(value.get("lifecycle") == "CLASSIFIED", "lifecycle")
    require(value.get("dependency_tags") == previous.get("dependency_tags"), "dependency tags")
    require(value.get("predecessor") == {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}, "predecessor")
    require(value.get("stages") == previous.get("stages"), "stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")

    old_branches = {branch["id"]: branch for branch in previous["branches"]}
    new_branches = {branch["id"]: branch for branch in value.get("branches", [])}
    for branch_id, old_branch in old_branches.items():
        current = new_branches.get(branch_id)
        if branch_id != "STRICT_PURE_WEYL_386":
            require(current == old_branch, f"unrelated branch drift {branch_id}")
            continue
        if not current:
            errors.append("strict branch missing")
            continue
        old_stages = {row["stage"]: row for row in old_branch["stages"]}
        new_stages = {row["stage"]: row for row in current["stages"]}
        for stage_id, row in old_stages.items():
            if stage_id != "S0_CLASSICAL_AUTHORITY":
                require(new_stages.get(stage_id) == row, f"unrelated strict stage drift {stage_id}")
        authority = new_stages.get("S0_CLASSICAL_AUTHORITY", {})
        require(authority.get("status") == "CERTIFIED", "S0 status")
        for result_id in (dual["result_id"], cyclic["result_id"], m1c["result_id"], gate["result_id"]):
            require(result_id in authority.get("evidence", []), f"S0 evidence {result_id}")
        require("Hadamard" in authority.get("boundary", "") and "support-expanding" in authority.get("boundary", ""), "S0 boundary")

    for authority_path, checker_path, name in CHECKERS:
        try:
            require(not load_module(checker_path, name).check(load(authority_path)), f"dependency receiver {authority_path.name}")
        except Exception as exc:
            errors.append(f"dependency checker exception {authority_path.name}:{exc}")

    reconciliation = value.get("classical_import_reconciliation", {})
    require(reconciliation.get("result_id") == gate["result_id"], "Gate reconciliation identity")
    require((reconciliation.get("exports_receiver_verified_scoped"), reconciliation.get("exports_total")) == (20, 20), "export census")
    require((reconciliation.get("freeze_checks_receiver_verified_scoped"), reconciliation.get("freeze_checks_total")) == (10, 10), "check census")
    require(reconciliation.get("accepted_top_level_hashes") == 7 and reconciliation.get("gate_a_status") == "VERIFIED", "Gate decision")
    require(reconciliation.get("snapshot_id") == m1c["snapshot_id"] and reconciliation.get("snapshot_sha256") == m1c["snapshot_sha256"], "snapshot binding")
    require(reconciliation.get("minimal_missing_bundle") == [], "missing bundle")

    gate_projection = value.get("strict_gate_v30_reconciliation", {})
    require(gate_projection.get("result_id") == gate["result_id"], "Gate projection identity")
    require((gate_projection.get("accepted_top_level_hashes"), gate_projection.get("remaining_top_level_hashes")) == (7, 0), "Gate hash counts")
    require(gate_projection.get("M1B_complete") is True and gate_projection.get("M1C_complete") is True and gate_projection.get("gate_a_status") == "VERIFIED", "classical lifecycle")
    require(gate_projection.get("nonlinear_green_compatibility_certified") is False and gate_projection.get("full_complex_hadamard_state_constructed") is False, "Gate quantum firewall")

    dual_projection = value.get("strict_m1b_action_dual_lift", {})
    require(dual_projection.get("result_id") == dual["result_id"] and dual_projection.get("content_sha256") == dual["content_sha256"], "dual identity")
    require((dual_projection.get("compact_source_action_duals"), dual_projection.get("represented_check_coordinates")) == (470, 4080), "dual dimensions")
    require((dual_projection.get("local_pairing_rank"), dual_projection.get("residual_action_pairing_rank")) == (386, 940), "dual pairing ranks")
    require(dual_projection.get("identity_defects") == 0 and dual_projection.get("M1B_action_dual_complete") is True, "dual identities")
    require(dual_projection.get("full_algebraic_dual_identified_with_compact_sources") is False, "dual scope firewall")

    cyclic_projection = value.get("strict_m1b_typed_cyclic_composite", {})
    require(cyclic_projection.get("result_id") == cyclic["result_id"] and cyclic_projection.get("content_sha256") == cyclic["content_sha256"], "cyclic identity")
    require((cyclic_projection.get("verification_core_coordinates"), cyclic_projection.get("residual_action_pairing_rank"), cyclic_projection.get("typed_identities_replayed")) == (8160, 940, 13), "cyclic census")
    require(cyclic_projection.get("identity_defects") == 0 and cyclic_projection.get("M1B_complete") is True, "cyclic identities")
    require(cyclic_projection.get("verification_core_is_authoritative_full_bv_source") is False, "cyclic scope firewall")

    snapshot_projection = value.get("strict_m1c_common_snapshot", {})
    require(snapshot_projection.get("result_id") == m1c["result_id"] and snapshot_projection.get("content_sha256") == m1c["content_sha256"], "M1C identity")
    require(snapshot_projection.get("snapshot_id") == m1c["snapshot_id"] and snapshot_projection.get("snapshot_sha256") == m1c["snapshot_sha256"], "M1C digest")
    require(tuple(snapshot_projection.get(key) for key in ("artifact_pins", "exports_bound", "top_level_hashes_bound", "gate_checks_replayed", "supplemental_checks_replayed")) == (16, 20, 7, 10, 3), "M1C census")
    require(snapshot_projection.get("M1C_complete") is True, "M1C lifecycle")

    expected_routes = [
        "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_BRST_HADAMARD_TWO_POINT_OR_OBSTRUCTION", "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    routes = value.get("route_selection", [])
    require([row.get("route") for row in routes] == expected_routes, "route order")
    require([row.get("rank") for row in routes] == list(range(1, 8)), "route ranks")
    require([row.get("priority") for row in value.get("research_queue", [])] == list(range(1, 8)), "queue priorities")
    require(value.get("frontier_summary", {}).get("highest_value_next_route") == expected_routes[0], "frontier route")
    retired = {"STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY", "STRICT_M1C_COMMON_MANIFEST_REPLAY"}
    require(not retired.intersection(expected_routes), "classical routes not retired")

    flags = value.get("claim_flags", {})
    for key in (
        "v47_preserved", "strict_M1B_action_dual_lift_complete", "strict_M1B_typed_cyclic_replay_complete",
        "strict_M1B_represented_composite_contraction_complete", "strict_M1C_common_manifest_replay_complete",
        "strict_M1_common_strict_snapshot_complete", "strict_pure_weyl_classical_gate_passed",
    ):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_386_q2_q3_green_compatibility_certified", "strict_386_full_bv_hadamard_state_constructed",
        "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored",
        "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)

    nonclaims = value.get("does_not_establish", [])
    for stale in (
        "a passed strict pure-Weyl classical import gate",
        "the M1B action-dual lift, rank-940 cyclic replay, complete M1B package or M1C common replay",
        "the authoritative twenty-export, seven-hash, ten-identity classical Gate A",
    ):
        require(stale not in nonclaims, "stale pre-V48 nonclaim")
    for boundary in (
        "q2/q3 compatibility with both typed advanced and retarded Lorentzian Green homotopies",
        "a full-complex BRST-compatible Hadamard two-point function or a no-go theorem for one",
        "general lambda-squared source-cocycle closure or an analytic Moller inverse",
    ):
        require(boundary in nonclaims, "missing current nonclaim " + boundary)

    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, GATE, DUAL, CYCLIC, M1C):
        require(pins.get(str(path.relative_to(ROOT))) == sha(path), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT))
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - immutable strict classical BV snapshot passes Gate A")
        print("  - M1B, M1C and all classical-freeze routes retired")
        print("  - typed q2/q3 Lorentzian Green compatibility is now the ranked frontier")
        print("  - Hadamard, renormalization and QME remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
