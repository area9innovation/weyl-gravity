#!/usr/bin/env python3
"""Independently check Lorentzian Weyl BV completion Atlas V49."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48.json"
CAUSAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
HADAMARD = ROOT / "quantum-weyl/lorentzian/certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json"
CAUSAL_CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m2_q2_q3_typed_green_compatibility.py"
HADAMARD_CHECKER = ROOT / "quantum-weyl/lorentzian/check_strict_386_brst_hadamard_two_point.py"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v49.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v30_reconciliation", "strict_m1b_action_dual_lift",
        "strict_m1b_typed_cyclic_composite", "strict_m1c_common_snapshot",
        "strict_m2_q2_q3_typed_green_compatibility",
        "strict_386_brst_hadamard_two_point", "route_selection",
        "research_queue", "claim_flags", "does_not_establish",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous, causal, hadamard = map(load, (PREDECESSOR, CAUSAL, HADAMARD))
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
    require(value.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49", "result identity")
    require(value.get("lifecycle") == "CLASSIFIED", "lifecycle")
    require(value.get("dependency_tags") == previous.get("dependency_tags"), "dependency tags")
    require(value.get("predecessor") == {
        "result_id": previous["result_id"],
        "path": str(PREDECESSOR.relative_to(ROOT)),
        "sha256": sha(PREDECESSOR),
        "preserved": True,
    }, "predecessor")
    require(value.get("stages") == previous.get("stages"), "stage vocabulary changed")
    require(len(value.get("branches", [])) == 7, "branch count")
    require(sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) == 77, "77-cell preservation")

    old_branches = {branch["id"]: branch for branch in previous["branches"]}
    new_branches = {branch["id"]: branch for branch in value.get("branches", [])}
    changed_stages = {"S3_NONLINEAR_CARTAN", "S4_HADAMARD_CCR", "S5_BRST_WARD", "S10_LORENTZIAN_CERTIFIED"}
    for branch_id, old_branch in old_branches.items():
        current = new_branches.get(branch_id)
        if branch_id != "STRICT_PURE_WEYL_386":
            require(current == old_branch, f"unrelated branch drift {branch_id}")
            continue
        require(current is not None, "strict branch missing")
        if current is None:
            continue
        old_stages = {row["stage"]: row for row in old_branch["stages"]}
        new_stages = {row["stage"]: row for row in current["stages"]}
        for stage_id, row in old_stages.items():
            if stage_id not in changed_stages:
                require(new_stages.get(stage_id) == row, f"unrelated strict stage drift {stage_id}")
        require(new_stages["S3_NONLINEAR_CARTAN"].get("status") == "CERTIFIED_TYPED_Q2_Q3_GREEN_COMPATIBILITY", "S3 promotion")
        require(new_stages["S4_HADAMARD_CCR"].get("status") == "CERTIFIED_FULL_386_HADAMARD_CCR_PSEUDO_STATE", "S4 promotion")
        require(new_stages["S5_BRST_WARD"].get("status") == "CERTIFIED_EXACT_FULL_386_BRST_WARD", "S5 promotion")
        require(new_stages["S10_LORENTZIAN_CERTIFIED"].get("status") == "FREE_HADAMARD_LAYER_CERTIFIED_FULL_THEORY_FAIL_CLOSED", "S10 boundary")
        require("not a positive Hadamard state" in new_stages["S4_HADAMARD_CCR"].get("boundary", ""), "S4 positivity boundary")
        require("complete Lorentzian theory remain open" in new_stages["S10_LORENTZIAN_CERTIFIED"].get("boundary", ""), "S10 full-theory boundary")

    try:
        require(not module(CAUSAL_CHECKER, "atlas_v49_causal_checker").check(causal), "causal receiver")
        require(not module(HADAMARD_CHECKER, "atlas_v49_hadamard_checker").check(hadamard), "Hadamard receiver")
    except Exception as exc:
        errors.append(f"dependency checker exception:{exc}")

    causal_projection = value.get("strict_m2_q2_q3_typed_green_compatibility", {})
    require(causal_projection.get("result_id") == causal["result_id"], "causal identity")
    require(causal_projection.get("content_sha256") == causal["content_sha256"], "causal content")
    require(causal_projection.get("snapshot_sha256") == causal["scope"]["snapshot_sha256"], "causal snapshot")
    require((causal_projection.get("carrier_rows"), causal_projection.get("orientations_checked"), causal_projection.get("nonlinear_arities")) == (386, 2, [2, 3]), "causal census")
    require(causal_projection.get("exact_or_structural_defects") == 0, "causal defects")
    require(causal_projection.get("all_finite_same_orientation_q2_q3_trees") is True, "finite tree theorem")
    require(causal_projection.get("general_second_source_cocycle_closed") is True, "second source")
    require(causal_projection.get("arbitrary_mixed_orientation_trees") is False and causal_projection.get("infinite_tree_series_convergence") is False, "causal scope boundary")

    hprojection = value.get("strict_386_brst_hadamard_two_point", {})
    require(hprojection.get("result_id") == hadamard["result_id"], "Hadamard identity")
    require(hprojection.get("content_sha256") == hadamard["content_sha256"], "Hadamard content")
    require(hprojection.get("hadamard_snapshot_sha256") == hadamard["hadamard_snapshot"]["sha256"], "Hadamard snapshot")
    require(hprojection.get("classical_snapshot_sha256") == causal["scope"]["snapshot_sha256"], "common classical snapshot")
    require((hprojection.get("carrier_rows"), hprojection.get("parent_rank_profile"), hprojection.get("proof_obligations"), hprojection.get("proof_defects")) == (386, [15, 60, 60, 15], 11, 0), "Hadamard census")
    for key in ("zero_mode_retained", "BRST_Ward_exact", "graded_CCR_exact", "Hadamard_wavefront_exact"):
        require(hprojection.get(key) is True, "Hadamard positive projection " + key)
    require(hprojection.get("object_type") == "BRST_HADAMARD_PSEUDO_STATE_TWO_POINT_PAIR", "pseudo-state type")
    require(hprojection.get("positive_state_constructed") is False and hprojection.get("physical_cohomology_positivity") is False, "positivity firewall")

    expected_routes = [
        "STRICT_PHYSICAL_COHOMOLOGY_POSITIVITY_DECISION",
        "STRICT_LORENTZIAN_RENORMALIZED_TIME_ORDERED_PRODUCTS",
        "STRICT_LOCAL_ANOMALY_CLASSIFICATION_AND_QME_RESTORATION",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
        "DIRECT_SPACETIME_Q26_HADAMARD",
    ]
    routes = value.get("route_selection", [])
    require([row.get("route") for row in routes] == expected_routes, "route order")
    require([row.get("rank") for row in routes] == list(range(1, 8)), "route ranks")
    require(value.get("frontier_summary", {}).get("highest_value_next_route") == expected_routes[0], "frontier route")
    require([row.get("priority") for row in value.get("research_queue", [])] == list(range(1, 8)), "queue priorities")
    require(not {
        "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_BRST_HADAMARD_TWO_POINT_OR_OBSTRUCTION",
    }.intersection(expected_routes), "closed routes not retired")

    flags = value.get("claim_flags", {})
    for key in (
        "v48_preserved", "strict_386_q2_q3_green_compatibility_certified",
        "strict_386_lambda2_general_source_cocycle_closed",
        "strict_386_full_bv_hadamard_two_point_constructed",
        "strict_386_full_bv_brst_ward_certified",
    ):
        require(flags.get(key) is True, "positive flag " + key)
    for key in (
        "strict_386_full_bv_hadamard_state_constructed",
        "strict_386_physical_cohomology_positivity_certified",
        "renormalized_lorentzian_products_constructed",
        "strict_pure_weyl_qme_restored", "residual_quantum_transfer_authorized",
        "lorentzian_full_theory_certified",
    ):
        require(flags.get(key) is False, "fail-closed flag " + key)

    nonclaims = value.get("does_not_establish", [])
    for stale in (
        "q2/q3 compatibility with both typed advanced and retarded Lorentzian Green homotopies",
        "a full-complex BRST-compatible Hadamard two-point function or a no-go theorem for one",
    ):
        require(stale not in nonclaims, "stale pre-V49 nonclaim")
    for boundary in (
        "a positive full-complex Hadamard state or positive covariance on physical cohomology",
        "renormalized Lorentzian Wick or time-ordered products and a causal perturbative AQFT construction",
        "a complete interacting Lorentzian quantum theory",
    ):
        require(boundary in nonclaims, "missing current nonclaim " + boundary)

    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, CAUSAL, HADAMARD):
        require(pins.get(str(path.relative_to(ROOT))) == sha(path), "provenance " + path.name)
    try:
        require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "independent digest")
    except KeyError as exc:
        errors.append("canonical projection missing " + str(exc))
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT))
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - nonlinear typed Green and second-source gates are closed")
        print("  - full 386-row BRST Hadamard pseudo-state pair is certified")
        print("  - positivity, products, QME and full theory remain fail closed")
        print("  - physical-cohomology positivity is the ranked frontier")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
