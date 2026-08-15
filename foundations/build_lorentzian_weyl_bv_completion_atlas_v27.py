#!/usr/bin/env python3
"""Build Atlas V27 from V26 plus the first nonlinear auxiliary correction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26.json"
CHANNEL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
GATE_V9 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v27.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_gate_v9_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "strict_386_stabilized_q3_preflight", "strict_nonminimal_theory_identity_obstruction",
        "strict_quadratic_auxiliary_elimination", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, channel, gate_v9 = (
        json.loads(path.read_text()) for path in (PREDECESSOR, CHANNEL, GATE_V9)
    )
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26":
        raise ValueError("V26 predecessor drift")
    flags = channel.get("claim_flags", {})
    if (
        flags.get("FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED") is not True
        or flags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is not False
        or flags.get("FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED") is not False
    ):
        raise ValueError("quadratic channel boundary drift")
    if gate_v9.get("result_id") != "CLASSICAL_IMPORT_GATE_V9_RECONCILIATION" or gate_v9.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V9 unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v27",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27",
        "created": "2026-08-15",
        "repository_base_commit": "a004672f18a9011ff65b7e79b498d4a3f7985bec",
        "question": "Does the exact nonlinear auxiliary shift repair the first strict source/candidate mismatch, and what is the next complete-equivalence obligation?",
        "answer": "Atlas V27 constructs the first nonlinear equivalence component. The exact source-to-split quadratic map F_(2)(v)=v tensor v-(1/2)g v^2 induces a +1 inverse-shift mass cross term, canceling the authoritative source value Omega(f_hat,q2(v,v))=-1 and matching candidate zero. Full theory identity remains open because metric-dependent h-f_hat-f_hat and ghost/antifield channels have not been serialized or replayed. The next decisive work is a complete induced-cubic-channel inventory and componentwise 386-row cotangent lift, followed by full source q2/q3 identities and lambda-squared causal closure.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v27.md",
    })
    replay = channel["channel_pullback_replay"]
    boundary = channel["equivalence_boundary"]
    value["strict_quadratic_auxiliary_elimination"] = {
        "result_id": channel["result_id"],
        "carrier_rows": replay["carrier_rows"],
        "field_map_component": replay["source_to_split_homogeneous_quadratic_component"],
        "second_Frechet_component": replay["source_to_split_second_Frechet_component"],
        "cyclic_form_channel": replay["cyclic_form_channel"],
        "source_before_correction": replay["pre_correction_source_value"],
        "inverse_shift_correction": replay["inverse_shift_mass_cross_correction"],
        "transformed_source": replay["transformed_source_value"],
        "candidate": replay["candidate_value"],
        "residual": replay["transformed_source_minus_candidate_residual"],
        "first_nonlinear_component_constructed": True,
        "component_support_local": replay["support_local"],
        "component_uses_green_operator": replay["uses_green_operator"],
        "component_uses_choice_principle": replay["uses_choice_principle"],
        "source_local_BV_canonical_lift_available": boundary["source_certified_local_BV_canonical_lift_available"],
        "receiver_componentwise_386_cotangent_lift_serialized": boundary["receiver_componentwise_386_cotangent_lift_serialized"],
        "complete_source_q2_pullback_replayed": boundary["complete_source_q2_pullback_replayed"],
        "complete_source_q3_pullback_replayed": boundary["complete_source_q3_pullback_replayed"],
        "full_cyclic_L_infinity_equivalence_constructed": boundary["full_cyclic_L_infinity_equivalence_constructed"],
        "nonlinear_equivalence_obstructed": boundary["nonlinear_equivalence_obstructed"],
        "remaining_shifted_cubic_families": boundary["remaining_shifted_cubic_families"],
        "foundational_classification": "FINITE_EXACT_SUPPORT_LOCAL_POINTWISE_ALGEBRAIC_MAP",
        "next_gate": channel["next_gate"],
    }
    gate_m2 = gate_v9["m2_quadratic_elimination_resolution"]
    gate_disposition = gate_v9["gate_disposition"]
    value["strict_gate_v9_reconciliation"] = {
        "result_id": gate_v9["result_id"],
        "status": gate_v9["result_state"],
        "exports_total": len(gate_v9["export_reconciliation"]),
        "exports_receiver_verified_scoped": gate_disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate_v9["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": gate_disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate_disposition["freeze_checks_supporting_evidence_only"],
        "freeze_checks_blocked": gate_disposition["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate_disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": gate_disposition["gate_a_status"],
        "candidate_q2_hash_accepted": gate_v9["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "first_nonlinear_component_constructed": True,
        "cyclic_form_channel": gate_m2["cyclic_form_channel"],
        "source_before_correction": gate_m2["source_before_correction"],
        "inverse_shift_correction": gate_m2["inverse_shift_correction"],
        "transformed_source": gate_m2["transformed_source"],
        "candidate": gate_m2["candidate"],
        "residual": gate_m2["residual"],
        "full_bv_cotangent_lift_serialized": gate_m2["receiver_componentwise_386_cotangent_lift_serialized"],
        "complete_source_q2_pullback_replayed": gate_m2["complete_source_q2_pullback_replayed"],
        "complete_source_q3_pullback_replayed": gate_m2["complete_source_q3_pullback_replayed"],
        "full_nonlinear_equivalence_constructed": gate_m2["full_cyclic_L_infinity_equivalence_constructed"],
        "missing_bundle_ids": [item["id"] for item in gate_v9["minimal_missing_bundle"]],
        "next_gate": gate_v9["next_gate"],
    }

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_FIRST_NONLINEAR_COMPONENT_CONSTRUCTED_FULL_BV_PULLBACK_OPEN",
        "statement": "The exact quadratic auxiliary-elimination component closes the previously mismatched f_hat-v-v cyclic channel. Full source/candidate theory identity remains open until the 386-row BV cotangent lift and every metric-dependent auxiliary and ghost/antifield cubic channel are serialized and replayed.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], channel["result_id"]])),
        "boundary": "This constructs one necessary nonlinear component and repairs one channel. It does not establish the complete cyclic L-infinity equivalence, authoritative q2/q3 hashes, causal lambda-squared closure, Hadamard data or QME restoration.",
    })
    strict = next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Enumerate all cubic channels induced by the exact auxiliary shift and serialize the componentwise 386-row BV cotangent lift, beginning with h-f_hat-f_hat and ghost/antifield families."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The first exact nonlinear auxiliary-elimination component cancels the f_hat-v-v mismatch; full source pullback remains open.",
        "best_next_object": "A complete induced-cubic-channel inventory followed by the componentwise 386-row BV cotangent lift.",
        "falsification_target": "Every metric-dependent auxiliary and ghost/antifield channel must match the transported candidate while preserving q1/q2/q3 identities, cyclicity and D-equivariance.",
        "foundational_boundary": "The constructed component is finite exact support-local algebra, uses neither a Green operator nor Choice, and makes no causal analytic claim.",
    }

    front_routes = [
        ("STRICT_NONLINEAR_SHIFT_CUBIC_CHANNEL_INVENTORY", "HIGH", "Enumerate every cubic channel induced by the exact auxiliary shift, beginning with h-f_hat-f_hat and ghost/antifield families."),
        ("STRICT_386_BV_COTANGENT_LIFT_COMPONENTS", "MEDIUM", "Serialize the local canonical cotangent lift on the exact 386-row carrier with hashes and independent checks."),
        ("STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "MEDIUM", "Replay the authoritative source master action through arity three under the complete nonlinear map."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "MEDIUM", "After nonlinear theory identity, prove Noether closure of the general lambda-squared source."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "MEDIUM", "Compose accepted source-equivalent q2/q3 with both Green orientations and verify response identities."),
    ]
    routes = [
        (route, "STRICT_PURE_WEYL_386", "VERY_HIGH", tractability, "HIGH" if rank > 1 else "MEDIUM", recommendation)
        for rank, (route, tractability, recommendation) in enumerate(front_routes, 1)
    ]
    retained_ids = {
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_RESIDUAL_EXACT_PAYLOAD", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    }
    routes.extend(
        (item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"])
        for item in previous["route_selection"] if item["route"] in retained_ids
    )
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V26 atlas predecessor"},
        {"path": str(CHANNEL.relative_to(ROOT)), "sha256": sha(CHANNEL), "role": "first exact nonlinear auxiliary channel pullback"},
        {"path": str(GATE_V9.relative_to(ROOT)), "sha256": sha(GATE_V9), "role": "fail-closed Gate-A successor after first nonlinear component"},
    ]
    value["claim_flags"].update({
        "v26_preserved": True,
        "strict_386_first_nonlinear_equivalence_component_constructed": True,
        "strict_386_f_hat_v_v_pullback_channel_closed": True,
        "strict_386_component_support_local": True,
        "strict_386_component_uses_green_operator": False,
        "strict_386_component_uses_choice_principle": False,
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
        "a componentwise 386-row BV cotangent lift or complete source q2/q3 pullback",
        "agreement of the metric-dependent h-f_hat-f_hat and ghost/antifield channel families",
        "a full cyclic L-infinity equivalence, authoritative q2/q3 hashes, or causal lambda-squared closure",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v27.py",
        "checks": [
            "V26 predecessor and 77-cell preservation",
            "exact -1 + 1 = 0 nonlinear-channel projection",
            "Gate V9 fail-closed projection",
            "first-component promotion versus full-equivalence firewall",
            "twelve-route deterministic queue",
            "Gate-A/Hadamard/QME firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_quadratic_auxiliary_elimination"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v27", "", f"**Result:** {value['result_id']}", "", "## Outcome", "", value["answer"], "",
        "## First nonlinear correction", "",
        f"- Component: {p['field_map_component']}.",
        f"- Source / correction / transformed / candidate / residual: **{p['source_before_correction']} / {p['inverse_shift_correction']} / {p['transformed_source']} / {p['candidate']} / {p['residual']}**.",
        f"- Full 386-row cotangent lift / q2 pullback / q3 pullback: **{p['receiver_componentwise_386_cotangent_lift_serialized']} / {p['complete_source_q2_pullback_replayed']} / {p['complete_source_q3_pullback_replayed']}**.", "",
        "## Gate-A disposition", "",
        f"Gate V9 remains **{value['strict_gate_v9_reconciliation']['gate_a_status']}** with **{value['strict_gate_v9_reconciliation']['accepted_top_level_hashes']}** accepted authoritative hashes. One necessary channel is closed; the full source pullback remains open.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(
        f"| {item['rank']} | {item['route']} | {item['branch']} | {item['scientific_leverage']} | {item['tractability']} |"
        for item in value["route_selection"]
    )
    lines += [
        "", "## Reproduction", "",
        "    python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v27.py --check",
        "    python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v27.py",
        "    python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v27.py",
        "    python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v27",
        "", "## Boundaries", "",
    ]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
