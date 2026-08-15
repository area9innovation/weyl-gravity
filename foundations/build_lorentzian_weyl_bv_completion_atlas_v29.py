#!/usr/bin/env python3
"""Build Atlas V29 after the curved hh/hv quadratic BV lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28.json"
LIFT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
GATE_V11 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v29.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_gate_v10_reconciliation", "strict_gate_v11_reconciliation",
        "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains",
        "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness",
        "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight",
        "strict_nonminimal_theory_identity_obstruction", "strict_quadratic_auxiliary_elimination",
        "strict_shifted_auxiliary_cubic_inventory", "strict_hh_hv_auxiliary_cotangent_lift",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, receiver, gate_v11 = (json.loads(path.read_text()) for path in (PREDECESSOR, LIFT, GATE_V11))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28":
        raise ValueError("V28 predecessor drift")
    flags = receiver.get("claim_flags", {})
    if flags.get("FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED") is not True or flags.get("DIFF_AUXILIARY_BV_REPRESENTATION_COMPLETE") is not False:
        raise ValueError("hh/hv receiver boundary drift")
    if gate_v11.get("result_id") != "CLASSICAL_IMPORT_GATE_V11_RECONCILIATION" or gate_v11.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V11 unavailable")
    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v29",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29",
        "created": "2026-08-15",
        "repository_base_commit": "229fd0f2147e8ed611c5147328459f7678b1f605",
        "question": "After the exact curved hh/hv field and cotangent tables, what is the shortest remaining path from the strict 386-row carrier to source-equivalent causal transfer?",
        "answer": "Atlas V29 closes the highest-ranked V28 route. The declared 386-row cylinder carrier now has the complete quadratic auxiliary canonical transformation: 1392 hh, 76 hv and 22 vv field coefficients induce 3907 collected cotangent coefficients with zero formal-adjoint defect. Four of seven known-required cubic families are component-complete. The frontier contracts to two source-census tasks—the three Diff auxiliary BV representation vertices and the exhaustive nonlinear Weyl/boost ghost-antifield manifest—followed by the complete source q2/q3 pullback and lambda-squared causal closure test. Gate A remains fail closed with zero accepted hashes.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v29.md",
    })
    lift, complete = receiver["quadratic_BV_cotangent_lift"], receiver["inventory_completeness"]
    value["strict_hh_hv_auxiliary_cotangent_lift"] = {
        "result_id": receiver["result_id"], "carrier_rows": lift["carrier_rows"],
        "hh_field_coefficients": lift["field_second_Frechet_component_counts"]["hh"],
        "hv_field_coefficients": lift["field_second_Frechet_component_counts"]["hv"],
        "vv_field_coefficients": lift["field_second_Frechet_component_counts"]["vv"],
        "combined_cotangent_coefficients": lift["cotangent_component_counts_after_collection"]["combined"],
        "metric_variation_slices_declared": lift["formal_adjoint_replay"]["metric_variation_jet_slices_declared"],
        "vector_variation_slices": lift["formal_adjoint_replay"]["vector_variation_slices"],
        "formal_adjoint_defects": lift["formal_adjoint_replay"]["coefficient_defects"],
        "known_required_cubic_families": complete["known_required_cubic_block_families_enumerated"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "full_quadratic_BV_cotangent_lift_serialized": complete["full_386_quadratic_BV_cotangent_lift_serialized"],
        "diffeomorphism_BV_representation_component_complete": complete["diffeomorphism_BV_representation_component_complete"],
        "exhaustive_full_nonlinear_BV_family_census": complete["exhaustive_full_nonlinear_BV_family_census"],
        "full_source_q2_q3_pullback_replayed": complete["full_source_q2_q3_pullback_replayed"],
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_CURVED_TWO_JET_ALGEBRA",
        "next_gate": receiver["next_gate"],
    }
    gate = gate_v11["gate_disposition"]
    value["strict_gate_v11_reconciliation"] = {
        "result_id": gate_v11["result_id"], "status": gate_v11["result_state"],
        "exports_total": len(gate_v11["export_reconciliation"]), "exports_receiver_verified_scoped": gate["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate_v11["freeze_check_reconciliation"]), "freeze_checks_receiver_verified_scoped": gate["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate["freeze_checks_supporting_evidence_only"], "freeze_checks_blocked": gate["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate["accepted_common_snapshot_hashes"], "gate_a_status": gate["gate_a_status"],
        "candidate_q2_hash_accepted": gate_v11["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "full_quadratic_BV_cotangent_lift_serialized": True, "diffeomorphism_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False, "complete_source_q2_q3_pullback_replayed": False,
        "missing_bundle_ids": [item["id"] for item in gate_v11["minimal_missing_bundle"]], "next_gate": gate_v11["next_gate"],
    }
    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_FULL_QUADRATIC_AUXILIARY_BV_LIFT_DIFF_AND_GHOST_CENSUS_OPEN",
        "statement": "The curved hh/hv/vv quadratic field and cotangent transformation is component-complete and canonical on the declared carrier. The three Diff families and nonlinear Weyl/boost census remain before full source q2/q3 replay.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], receiver["result_id"]])),
        "boundary": "A complete quadratic canonical lift does not establish the source master-action pullback, cyclic L-infinity equivalence, causal lambda-squared closure, Hadamard state or QME restoration.",
    })
    strict = next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Derive the three Diff auxiliary BV representation vertices and exhaustively audit nonlinear Weyl/boost ghost-antifield families."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386", "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The full quadratic auxiliary canonical lift is exact on the curved 386-row carrier; four of seven known-required cubic families are complete.",
        "best_next_object": "The three Diff auxiliary representation vertices, followed by the exhaustive nonlinear Weyl/boost family manifest.",
        "falsification_target": "The completed family census must either yield a source q2/q3 pullback satisfying all cyclic/D identities or an exact defect surviving allowed local canonical normalizations.",
        "foundational_boundary": "This remains finite exact support-local two-jet algebra. No Green, Hadamard or quantum claim follows.",
    }
    front = [
        ("STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "HIGH", "Derive the f_hat, v and eta Diff ghost-antifield vertices on the exact carrier."),
        ("STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST", "MEDIUM", "Close the family census by auditing nonlinear Weyl and boost ghost-antifield terms."),
        ("STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "MEDIUM", "Replay the authoritative source master action through arity three under the complete lift."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "MEDIUM", "After nonlinear identity, prove Noether closure of the general lambda-squared source."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "MEDIUM", "Compose accepted q2/q3 with both Green orientations and verify response identities."),
    ]
    routes = [(route, "STRICT_PURE_WEYL_386", "VERY_HIGH", tractability, "MEDIUM" if rank <= 2 else "HIGH", recommendation) for rank, (route, tractability, recommendation) in enumerate(front, 1)]
    retained = {"STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_RESIDUAL_EXACT_PAYLOAD", "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN"}
    routes.extend((item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"]) for item in previous["route_selection"] if item["route"] in retained)
    value["route_selection"] = [{"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation} for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V28 atlas predecessor"}, {"path": str(LIFT.relative_to(ROOT)), "sha256": sha(LIFT), "role": "curved hh/hv/vv quadratic BV cotangent lift"}, {"path": str(GATE_V11.relative_to(ROOT)), "sha256": sha(GATE_V11), "role": "fail-closed Gate-A successor after quadratic lift"}]
    value["claim_flags"].update({
        "v28_preserved": True, "strict_386_hh_hv_bv_cotangent_lift_component_complete": True,
        "strict_386_full_bv_cotangent_lift_serialized": True, "strict_386_full_quadratic_bv_cotangent_lift_serialized": True,
        "strict_386_diff_bv_representation_component_complete": False, "strict_386_exhaustive_full_nonlinear_bv_family_census": False,
        "strict_386_full_source_q2_pullback_replayed": False, "strict_386_full_source_q3_pullback_replayed": False,
        "strict_386_nonlinear_equivalence_constructed": False, "strict_386_authoritative_q2_imported": False, "strict_386_authoritative_q3_imported": False,
        "strict_pure_weyl_classical_gate_passed": False, "strict_386_full_bv_hadamard_state_constructed": False, "strict_pure_weyl_qme_restored": False, "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([*previous["does_not_establish"], "the three Diff auxiliary BV representation component tables or an exhaustive nonlinear Weyl/boost ghost-antifield census", "the complete source q2/q3 pullback, accepted nonlinear hashes, or cyclic L-infinity equivalence", "causal lambda-squared closure, a Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer"]))
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v29.py", "checks": ["V28 predecessor and 77-cell preservation", "1392+76+22 field and 3907 cotangent projection", "Gate V11 fail-closed projection", "quadratic-lift promotion versus Diff/full-source firewalls", "twelve-route deterministic queue", "Gate-A/Hadamard/QME firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_hh_hv_auxiliary_cotangent_lift"]
    lines = ["# Lorentzian Weyl BV completion atlas v29", "", f"**Result:** {value['result_id']}", "", "## Outcome", "", value["answer"], "", "## Exact quadratic frontier", "", f"- Known required / complete / open families: **{p['known_required_cubic_families']} / {p['component_complete_families']} / {p['component_open_families']}**.", f"- hh / hv / vv field coefficients: **{p['hh_field_coefficients']} / {p['hv_field_coefficients']} / {p['vv_field_coefficients']}**.", f"- Combined cotangent coefficients: **{p['combined_cotangent_coefficients']}**.", f"- Metric + vector slices / defects: **{p['metric_variation_slices_declared']} + {p['vector_variation_slices']} / {p['formal_adjoint_defects']}**.", "", "## Gate-A disposition", "", f"Gate V11 remains **{value['strict_gate_v11_reconciliation']['gate_a_status']}** with **{value['strict_gate_v11_reconciliation']['accepted_top_level_hashes']}** accepted authoritative hashes.", "", "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|"]
    lines.extend(f"| {item['rank']} | {item['route']} | {item['branch']} | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "    python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v29.py --check", "    python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v29.py", "    python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v29.py", "    python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v29", "", "## Boundaries", ""]
    lines.extend("- This does not establish " + item + "." for item in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
