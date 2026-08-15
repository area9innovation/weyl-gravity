#!/usr/bin/env python3
"""Build Atlas V30 after the three auxiliary Diff BV lifts."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29.json"
DIFF = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
GATE_V12 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v30.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_gate_v10_reconciliation",
        "strict_gate_v11_reconciliation", "strict_gate_v12_reconciliation",
        "strict_q2_green_composition_preflight", "strict_recursive_causal_tree_domains",
        "strict_polarized_formal_coefficients", "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction", "strict_pure_weyl_q3_witness",
        "strict_minimal_q3_completion", "strict_386_stabilized_q3_preflight",
        "strict_nonminimal_theory_identity_obstruction", "strict_quadratic_auxiliary_elimination",
        "strict_shifted_auxiliary_cubic_inventory", "strict_hh_hv_auxiliary_cotangent_lift",
        "strict_diff_auxiliary_bv_representation", "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, receiver, gate_v12 = (json.loads(path.read_text()) for path in (PREDECESSOR, DIFF, GATE_V12))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29":
        raise ValueError("V29 predecessor drift")
    flags = receiver.get("claim_flags", {})
    if flags.get("THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED") is not True or flags.get("SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE") is not True:
        raise ValueError("Diff auxiliary receiver drift")
    if flags.get("EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS") is not False:
        raise ValueError("exhaustive family boundary drift")
    if gate_v12.get("result_id") != "CLASSICAL_IMPORT_GATE_V12_RECONCILIATION" or gate_v12.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V12 unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v30",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30",
        "created": "2026-08-15",
        "repository_base_commit": "95decea291a6a12c7f0cdab017d4bcd0da9aaf92",
        "question": "After exact completion of the three named auxiliary Diff BV families, what is the shortest remaining route to an authoritative nonlinear source import?",
        "answer": "Atlas V30 closes the highest-ranked V29 route. All seven currently known required cubic families now have exact component tables on the fixed 386-row carrier. The three Diff families contribute 264 master-density, 336 field, 632 antifield and 704 c-star coefficients with zero variational or Koszul defect. The next frontier is not another named tensor representation: it is the authoritative exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest. Only after that manifest is pinned can the full source q2/q3 be assembled and the q1/q2, cyclicity, D and lambda-squared causal identities be replayed. Gate A remains fail closed with zero accepted hashes.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v30.md",
    })
    summary, complete = receiver["component_summary"], receiver["inventory_completeness"]
    value["strict_diff_auxiliary_bv_representation"] = {
        "result_id": receiver["result_id"],
        **summary,
        "known_required_cubic_families": complete["known_required_cubic_block_families_enumerated"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "diffeomorphism_BV_representation_component_complete": complete["diffeomorphism_BV_representation_component_complete"],
        "exhaustive_full_nonlinear_BV_family_census": complete["exhaustive_full_nonlinear_BV_family_census"],
        "full_source_q2_q3_pullback_replayed": complete["full_source_q2_q3_pullback_replayed"],
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_FIRST_JET_BV_VARIATIONAL_ALGEBRA",
        "next_gate": receiver["next_gate"],
    }
    gate = gate_v12["gate_disposition"]
    value["strict_gate_v12_reconciliation"] = {
        "result_id": gate_v12["result_id"], "status": gate_v12["result_state"],
        "exports_total": len(gate_v12["export_reconciliation"]), "exports_receiver_verified_scoped": gate["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate_v12["freeze_check_reconciliation"]), "freeze_checks_receiver_verified_scoped": gate["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate["freeze_checks_supporting_evidence_only"], "freeze_checks_blocked": gate["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate["accepted_common_snapshot_hashes"], "gate_a_status": gate["gate_a_status"],
        "candidate_q2_hash_accepted": gate_v12["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "seven_known_required_cubic_families_component_complete": True,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "complete_source_q2_q3_pullback_replayed": False,
        "missing_bundle_ids": [item["id"] for item in gate_v12["minimal_missing_bundle"]], "next_gate": gate_v12["next_gate"],
    }
    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_SEVEN_KNOWN_CUBIC_FAMILIES_COMPLETE_EXHAUSTIVE_GHOST_MANIFEST_OPEN",
        "statement": "All seven currently known required cubic families are component-complete on the 386-row carrier, including exact Diff cotangent and c-star rows. The exhaustive nonlinear Weyl/conformal-boost manifest and assembled source q2/q3 remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], receiver["result_id"]])),
        "boundary": "A complete named-family list is not an exhaustive source-family theorem and does not establish q1/q2, cyclicity, causal lambda-squared closure, Hadamard data or QME restoration.",
    })
    strict = next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Derive and independently audit the authoritative nonlinear Weyl/conformal-boost ghost-antifield manifest."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386", "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "All seven known-required cubic families have exact component tables, including the three Diff representations and their cotangent/momentum-map rows.",
        "best_next_object": "The exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest, followed immediately by common-byte source q2 assembly.",
        "falsification_target": "The manifest must either close the family census and yield a source q2 satisfying q1/q2, cyclicity and D, or expose a nonzero exact defect after allowed local canonical normalization.",
        "foundational_boundary": "The completed Diff step is finite exact support-local first-jet variational algebra. No Green, Hadamard or quantum claim follows.",
    }
    front = [
        ("STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST", "HIGH", "Derive the source-authoritative nonlinear ghost and antifield family manifest; do not infer exhaustiveness from the seven named families."),
        ("STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "MEDIUM", "Assemble the authoritative source master action through arity three and replay q1/q2, cyclicity and D on common bytes."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "MEDIUM", "After nonlinear identity, prove Noether closure of the general lambda-squared source."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "MEDIUM", "Compose accepted q2/q3 with both Green orientations and verify response identities."),
    ]
    routes = [(route, "STRICT_PURE_WEYL_386", "VERY_HIGH", tractability, "MEDIUM" if rank <= 2 else "HIGH", recommendation) for rank, (route, tractability, recommendation) in enumerate(front, 1)]
    retained = {"STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_RESIDUAL_EXACT_PAYLOAD", "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN"}
    routes.extend((item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"]) for item in previous["route_selection"] if item["route"] in retained)
    value["route_selection"] = [{"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation} for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V29 atlas predecessor"}, {"path": str(DIFF.relative_to(ROOT)), "sha256": sha(DIFF), "role": "three exact Diff auxiliary BV representation lifts"}, {"path": str(GATE_V12.relative_to(ROOT)), "sha256": sha(GATE_V12), "role": "fail-closed Gate-A successor after Diff-family completion"}]
    value["claim_flags"].update({
        "v29_preserved": True,
        "strict_386_diff_bv_representation_component_complete": True,
        "strict_386_seven_known_required_cubic_families_component_complete": True,
        "strict_386_exhaustive_full_nonlinear_bv_family_census": False,
        "strict_386_full_source_q2_pullback_replayed": False,
        "strict_386_full_source_q3_pullback_replayed": False,
        "strict_386_nonlinear_equivalence_constructed": False,
        "strict_386_authoritative_q2_imported": False,
        "strict_386_authoritative_q3_imported": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if "three Diff auxiliary" not in item]
    value["does_not_establish"] = list(dict.fromkeys([*value["does_not_establish"], "an exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest or proof that the seven known families exhaust the source theory", "the assembled source q2/q3, accepted nonlinear hashes, or cyclic L-infinity equivalence", "causal lambda-squared closure, a Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer"]))
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v30.py", "checks": ["V29 predecessor and 77-cell preservation", "264/336/632/704 exact Diff projection", "Gate V12 fail-closed projection", "seven-known-family promotion versus exhaustive-census firewall", "eleven-route deterministic queue", "Gate-A/Hadamard/QME firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_diff_auxiliary_bv_representation"]
    lines = ["# Lorentzian Weyl BV completion atlas v30", "", f"**Result:** {value['result_id']}", "", "## Outcome", "", value["answer"], "", "## Exact Diff frontier", "", f"- Known required / complete / open families: **{p['known_required_cubic_families']} / {p['component_complete_families']} / {p['component_open_families']}**.", f"- Master / field / antifield / c-star coefficients: **{p['master_density_coefficients']} / {p['field_output_coefficients']} / {p['antifield_output_coefficients']} / {p['c_star_output_coefficients']}**.", f"- Formal-variation / Koszul defects: **{p['formal_variational_defects']} / {p['Koszul_symmetry_defects']}**.", "", "## Gate-A disposition", "", f"Gate V12 remains **{value['strict_gate_v12_reconciliation']['gate_a_status']}** with **{value['strict_gate_v12_reconciliation']['accepted_top_level_hashes']}** accepted authoritative hashes.", "", "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|"]
    lines.extend(f"| {item['rank']} | {item['route']} | {item['branch']} | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "    python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v30.py --check", "    python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v30.py", "    python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v30.py", "    python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v30", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
