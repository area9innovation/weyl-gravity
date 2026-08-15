#!/usr/bin/env python3
"""Build Atlas V28 from V27 plus the exact shifted-cubic inventory and Gate V10."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
INVENTORY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
GATE_V10 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v28.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_gate_v10_reconciliation",
        "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains",
        "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness",
        "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight",
        "strict_nonminimal_theory_identity_obstruction", "strict_quadratic_auxiliary_elimination",
        "strict_shifted_auxiliary_cubic_inventory", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, inventory, gate_v10 = (json.loads(path.read_text()) for path in (PREDECESSOR, INVENTORY, GATE_V10))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27":
        raise ValueError("V27 predecessor drift")
    flags = inventory.get("claim_flags", {})
    if flags.get("VV_BV_COTANGENT_LIFT_CANONICAL") is not True or flags.get("FULL_386_BV_COTANGENT_LIFT_SERIALIZED") is not False:
        raise ValueError("shifted-cubic inventory boundary drift")
    if gate_v10.get("result_id") != "CLASSICAL_IMPORT_GATE_V10_RECONCILIATION" or gate_v10.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V10 unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v28",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28",
        "created": "2026-08-15",
        "repository_base_commit": "dab6c761997f09fad3ca1f9aa87b009ec98ec1ad",
        "question": "What does the exact cubic-family census and canonical vv BV lift resolve, and which component families now form the shortest path to source-equivalent causal transfer?",
        "answer": "Atlas V28 turns the former generic cubic-inventory request into three explicit component fronts. Seven known-required cubic families are enumerated; two are exact, including a canonical vv field/cotangent lift with 22+16 coefficients, while 72 exact h-f_hat-f_hat source coefficients show that the vv shift alone is not the full normalization. The shortest path is now hh/hv second-Frechet and cotangent tables, the three Diff auxiliary representation vertices, and an exhaustive nonlinear Weyl/boost ghost-antifield manifest. Only then can the complete 386-row q2/q3 pullback and lambda-squared causal source closure be tested. Gate A remains fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v28.md",
    })

    lift = inventory["vv_BV_cotangent_lift"]
    complete = inventory["inventory_completeness"]
    comparison = inventory["candidate_comparison"]
    value["strict_shifted_auxiliary_cubic_inventory"] = {
        "result_id": inventory["result_id"],
        "carrier_rows": lift["carrier_rows"],
        "known_required_cubic_families": complete["known_required_cubic_block_families_enumerated"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "family_ids": [row["family_id"] for row in inventory["required_cubic_family_inventory"]],
        "h_f_hat_f_hat_source_coefficients": comparison["shifted_mass_h_f_hat_f_hat_source_nonzero_coefficients"],
        "h_f_hat_f_hat_candidate_coefficients": comparison["trivial_candidate_h_f_hat_f_hat_nonzero_coefficients"],
        "vv_field_map_coefficients": lift["field_map_nonzero_component_coefficients"],
        "vv_cotangent_partner_coefficients": lift["cotangent_partner_nonzero_component_coefficients"],
        "vv_active_output_rows": lift["quadratic_active_output_rows"],
        "vv_zero_output_rows": lift["quadratic_zero_output_rows"],
        "vv_canonicality_slices": len(lift["canonicality_slices"]),
        "vv_canonicality_defects": lift["canonicality_defects"],
        "vv_BV_cotangent_lift_component_complete": complete["vv_BV_cotangent_lift_component_complete"],
        "hh_hv_BV_cotangent_lift_component_complete": complete["hh_hv_BV_cotangent_lift_component_complete"],
        "diffeomorphism_BV_representation_component_complete": complete["diffeomorphism_BV_representation_component_complete"],
        "exhaustive_full_nonlinear_BV_family_census": complete["exhaustive_full_nonlinear_BV_family_census"],
        "full_386_BV_cotangent_lift_serialized": complete["full_386_quadratic_BV_cotangent_lift_serialized"],
        "full_source_q2_q3_pullback_replayed": complete["full_source_q2_q3_pullback_replayed"],
        "full_nonlinear_equivalence_obstructed": comparison["full_nonlinear_equivalence_obstructed"],
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_COMPONENT_ALGEBRA",
        "next_gate": inventory["next_gate"],
    }
    gate_resolution, gate = gate_v10["m2_shifted_cubic_inventory_resolution"], gate_v10["gate_disposition"]
    value["strict_gate_v10_reconciliation"] = {
        "result_id": gate_v10["result_id"],
        "status": gate_v10["result_state"],
        "exports_total": len(gate_v10["export_reconciliation"]),
        "exports_receiver_verified_scoped": gate["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate_v10["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": gate["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate["freeze_checks_supporting_evidence_only"],
        "freeze_checks_blocked": gate["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate["accepted_common_snapshot_hashes"],
        "gate_a_status": gate["gate_a_status"],
        "candidate_q2_hash_accepted": gate_v10["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "known_required_cubic_families": gate_resolution["known_required_cubic_block_families"],
        "vv_BV_lift_canonical": gate_resolution["vv_canonicality_defects"] == 0,
        "hh_hv_component_complete": gate_resolution["hh_hv_component_complete"],
        "diffeomorphism_representation_component_complete": gate_resolution["diffeomorphism_representation_component_complete"],
        "exhaustive_full_nonlinear_BV_family_census": gate_resolution["exhaustive_full_nonlinear_BV_family_census"],
        "full_bv_cotangent_lift_serialized": gate_resolution["full_386_BV_cotangent_lift_serialized"],
        "complete_source_q2_q3_pullback_replayed": gate_resolution["complete_source_q2_q3_pullback_replayed"],
        "full_nonlinear_equivalence_obstructed": gate_resolution["full_nonlinear_equivalence_obstructed"],
        "missing_bundle_ids": [item["id"] for item in gate_v10["minimal_missing_bundle"]],
        "next_gate": gate_v10["next_gate"],
    }

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_SEVEN_CUBIC_FAMILIES_VV_BV_LIFT_CANONICAL_FULL_PULLBACK_OPEN",
        "statement": "Seven known-required cubic families are enumerated. Exact h-f_hat-f_hat coefficients and the canonical vv field/cotangent sector are imported; hh/hv, Diff and nonlinear Weyl/boost ghost-antifield components remain before full source q2/q3 replay.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], inventory["result_id"]])),
        "boundary": "Two component-complete families and a zero-defect vv canonicality check do not establish an exhaustive family census, complete 386-row lift, cyclic L-infinity equivalence, causal lambda-squared closure, Hadamard state or QME restoration.",
    })
    strict = next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Derive exact hh/hv second-Frechet and cotangent tables, the three Diff auxiliary BV representation vertices, and an exhaustive nonlinear Weyl/boost ghost-antifield manifest."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "Seven required cubic families are known; h-f_hat-f_hat and vv are component-exact, and the vv BV lift is canonical. Five known families and possible nonlinear ghost-antifield families remain.",
        "best_next_object": "The hh/hv second-Frechet plus cotangent tables, followed by the three Diff auxiliary representation vertices and nonlinear Weyl/boost manifest.",
        "falsification_target": "A complete component census must either match the transported candidate in all q2/q3, cyclicity and D identities or provide an exact nonzero defect that survives allowed local canonical normalizations.",
        "foundational_boundary": "Current progress is finite exact support-local algebra and uses neither a Green operator nor Choice; no causal analytic claim follows.",
    }

    front_routes = [
        ("STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS", "HIGH", "Serialize the hh/hv field and cotangent tables of the metric-dependent auxiliary shift."),
        ("STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "HIGH", "Derive the f_hat, v and eta Diff ghost-antifield vertices on the exact carrier."),
        ("STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST", "MEDIUM", "Close the family census by auditing nonlinear Weyl and boost ghost-antifield terms."),
        ("STRICT_386_BV_COTANGENT_LIFT_COMPONENTS", "MEDIUM", "Assemble the complete local canonical lift from the certified component families."),
        ("STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "MEDIUM", "Replay the authoritative source master action through arity three under the complete lift."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "MEDIUM", "After nonlinear identity, prove Noether closure of the general lambda-squared source."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "MEDIUM", "Compose accepted q2/q3 with both Green orientations and verify response identities."),
    ]
    routes = [(route, "STRICT_PURE_WEYL_386", "VERY_HIGH", tractability, "MEDIUM" if rank <= 3 else "HIGH", recommendation) for rank, (route, tractability, recommendation) in enumerate(front_routes, 1)]
    retained_ids = {"STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_RESIDUAL_EXACT_PAYLOAD", "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN"}
    routes.extend((item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"]) for item in previous["route_selection"] if item["route"] in retained_ids)
    value["route_selection"] = [{"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation} for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V27 atlas predecessor"},
        {"path": str(INVENTORY.relative_to(ROOT)), "sha256": sha(INVENTORY), "role": "exact shifted-cubic census and canonical vv BV lift"},
        {"path": str(GATE_V10.relative_to(ROOT)), "sha256": sha(GATE_V10), "role": "fail-closed Gate-A successor after cubic inventory"},
    ]
    value["claim_flags"].update({
        "v27_preserved": True,
        "strict_386_known_required_cubic_families_enumerated": True,
        "strict_386_h_f_hat_f_hat_components_imported": True,
        "strict_386_vv_field_map_components_imported": True,
        "strict_386_vv_cotangent_partner_components_serialized": True,
        "strict_386_vv_bv_cotangent_lift_canonical": True,
        "strict_386_exhaustive_full_nonlinear_bv_family_census": False,
        "strict_386_hh_hv_bv_cotangent_lift_component_complete": False,
        "strict_386_diff_bv_representation_component_complete": False,
        "strict_386_full_bv_cotangent_lift_serialized": False,
        "strict_386_full_source_q2_pullback_replayed": False,
        "strict_386_full_source_q3_pullback_replayed": False,
        "strict_386_nonlinear_equivalence_constructed": False,
        "strict_386_nonlinear_equivalence_obstructed": False,
        "strict_386_authoritative_q2_imported": False,
        "strict_386_authoritative_q3_imported": False,
        "strict_386_candidate_causal_lambda2_source_closure_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "an exhaustive nonlinear BV family census or complete hh/hv, Diff, Weyl and boost component inventory",
        "that the 72 h-f_hat-f_hat comparison obstructs a further metric-dependent canonical or L-infinity normalization",
        "a complete source q2/q3 pullback, causal lambda-squared closure, Hadamard state, renormalized Lorentzian products, or QME restoration",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v28.py",
        "checks": [
            "V27 predecessor and 77-cell preservation",
            "seven-family, 72, 22+16 and four-slice projection",
            "Gate V10 fail-closed projection",
            "vv-sector promotion versus exhaustive-census and full-equivalence firewalls",
            "fourteen-route deterministic queue",
            "Gate-A/Hadamard/QME firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_shifted_auxiliary_cubic_inventory"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v28", "", f"**Result:** {value['result_id']}", "", "## Outcome", "", value["answer"], "",
        "## Exact cubic frontier", "",
        f"- Known required / complete / open families: **{p['known_required_cubic_families']} / {p['component_complete_families']} / {p['component_open_families']}**.",
        f"- h-f_hat-f_hat source / candidate coefficients: **{p['h_f_hat_f_hat_source_coefficients']} / {p['h_f_hat_f_hat_candidate_coefficients']}**.",
        f"- vv field / cotangent coefficients: **{p['vv_field_map_coefficients']} / {p['vv_cotangent_partner_coefficients']}**.",
        f"- vv canonicality slices / defects: **{p['vv_canonicality_slices']} / {p['vv_canonicality_defects']}**.", "",
        "## Gate-A disposition", "",
        f"Gate V10 remains **{value['strict_gate_v10_reconciliation']['gate_a_status']}** with **{value['strict_gate_v10_reconciliation']['accepted_top_level_hashes']}** accepted authoritative hashes.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | {item['route']} | {item['branch']} | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "    python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v28.py --check", "    python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v28.py", "    python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v28.py", "    python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v28", "", "## Boundaries", ""]
    lines.extend("- This does not establish " + item + "." for item in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
