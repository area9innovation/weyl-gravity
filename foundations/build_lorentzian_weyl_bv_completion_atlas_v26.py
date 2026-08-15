#!/usr/bin/env python3
"""Build Atlas V26 from V25 plus the exact nonminimal theory-identity obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
GATE_V8 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v26.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_gate_v8_reconciliation",
        "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "strict_386_stabilized_q3_preflight", "strict_nonminimal_theory_identity_obstruction",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    gate_v8 = json.loads(GATE_V8.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25":
        raise ValueError("V25 predecessor drift")
    flags = obstruction.get("claim_flags", {})
    if flags.get("LITERAL_TRIVIAL_STABILIZATION_THEORY_IDENTITY_REFUTED") is not True or flags.get("LINEAR_SHEAR_ONLY_THEORY_IDENTITY_REFUTED") is not True:
        raise ValueError("theory-identity obstruction unavailable")
    if flags.get("NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_OBSTRUCTED") is not False:
        raise ValueError("nonlinear-equivalence no-go firewall drift")
    if gate_v8.get("result_id") != "CLASSICAL_IMPORT_GATE_V8_RECONCILIATION" or gate_v8.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V8 reconciliation unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v26",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26",
        "created": "2026-08-15",
        "repository_base_commit": "5013af08d48bf45d99d9b841a75244122e3822f9",
        "question": "Is the exact 386-row trivial q2/q3 stabilization literally the authoritative ordinary-derivative nonminimal Weyl theory, and if not, what is the first required correction?",
        "answer": "Atlas V26 resolves literal theory identity negatively without abandoning the stabilization architecture. The authoritative ordinary-derivative action has an exact auxiliary cubic cyclic-form value Omega(f_hat,q2(v,v))=-1, while the trivial stabilization gives zero because AUX_F_HAT and AUX_V are interaction-inert. Thus zero-extension plus the recorded linear shear is not the source nonlinear theory. This does not obstruct nonlinear equivalence: the next object is the quadratic auxiliary-elimination or cyclic L-infinity map whose pullback supplies the missing channel, followed by source q2/q3 pullback identities and lambda-squared causal closure.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v26.md",
    })
    comparison = obstruction["exact_channel_comparison"]
    disposition = obstruction["theory_identity_disposition"]
    value["strict_nonminimal_theory_identity_obstruction"] = {
        "result_id": obstruction["result_id"],
        "carrier_rows": obstruction["scope"]["carrier_rows"],
        "cyclic_form_channel": comparison["cyclic_form_channel"],
        "block_channel": comparison["block_channel"],
        "source_value": comparison["source_ordinary_derivative_value"],
        "candidate_value": comparison["candidate_trivial_stabilization_value"],
        "source_minus_candidate_defect": comparison["source_minus_candidate_defect"],
        "literal_identity_refuted": True,
        "linear_shear_only_identity_refuted": True,
        "candidate_internal_identities_preserved": disposition["candidate_internal_q1_q2_and_cyclicity_certificates_preserved"],
        "nonlinear_equivalence_may_exist": disposition["nonlinear_canonical_or_L_infinity_equivalence_may_exist"],
        "nonlinear_equivalence_constructed": disposition["nonlinear_equivalence_constructed"],
        "nonlinear_equivalence_obstructed": False,
        "first_required_correction": disposition["first_required_correction"],
        "classical_import_gate_a_passed": False,
        "foundational_classification": "FINITE_EXACT_LOCAL_ACTION_POLARIZATION",
        "next_gate": obstruction["next_gate"],
    }
    gate_m2 = gate_v8["m2_theory_identity_obstruction"]
    gate_disposition = gate_v8["gate_disposition"]
    value["strict_gate_v8_reconciliation"] = {
        "result_id": gate_v8["result_id"],
        "status": gate_v8["result_state"],
        "exports_total": len(gate_v8["export_reconciliation"]),
        "exports_receiver_verified_scoped": gate_disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate_v8["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": gate_disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate_disposition["freeze_checks_supporting_evidence_only"],
        "freeze_checks_blocked": gate_disposition["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate_disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": gate_disposition["gate_a_status"],
        "candidate_q2_hash_accepted": gate_v8["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "cyclic_form_channel": gate_m2["cyclic_form_channel"],
        "source_value": gate_m2["source_value"],
        "candidate_value": gate_m2["candidate_value"],
        "defect": gate_m2["defect"],
        "literal_and_linear_identity_refuted": True,
        "candidate_internal_identities_preserved": gate_m2["candidate_internal_identities_preserved"],
        "nonlinear_equivalence_may_exist": gate_m2["nonlinear_equivalence_may_exist"],
        "nonlinear_equivalence_constructed": gate_m2["nonlinear_equivalence_constructed"],
        "nonlinear_equivalence_obstructed": gate_m2["nonlinear_equivalence_obstructed"],
        "missing_bundle_ids": [item["id"] for item in gate_v8["minimal_missing_bundle"]],
        "next_gate": gate_v8["next_gate"],
    }

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_WITH_LINEAR_THEORY_IDENTITY_OBSTRUCTED_NONLINEAR_EQUIVALENCE_OPEN",
        "statement": "The exact q2/q3 stabilization remains an internally valid cyclic candidate, but literal equality with the ordinary-derivative source theory is refuted by Omega(f_hat,q2(v,v))=-1 versus candidate zero. A nonlinear auxiliary-elimination or cyclic L-infinity map is required and remains open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], obstruction["result_id"]])),
        "boundary": "This refutes zero-extension plus the recorded linear shear as the authoritative nonlinear theory. It does not refute nonlinear equivalence, invalidate the candidate identities, import full source q2/q3, or enter Gate A or the causal/Hadamard/QME chain.",
    })
    strict = next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Construct the quadratic auxiliary-elimination/cyclic L-infinity map beginning with Omega(f_hat,q2(v,v))=-1, then replay source q2/q3 pullback identities before lambda-squared Green composition."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "Literal and linear-shear theory identity are exactly refuted in one authoritative auxiliary cubic channel; nonlinear equivalence remains viable.",
        "best_next_object": "The quadratic component of the nonlinear auxiliary-elimination or cyclic L-infinity map.",
        "falsification_target": "Its pullback must reproduce Omega(f_hat,q2(v,v))=-1 while preserving the certified minimal bracket and cyclic pairing.",
        "foundational_boundary": "The obstruction is finite exact local algebra. It uses neither Choice nor an infinite sum and makes no causal analytic claim.",
    }

    routes = [
        ("STRICT_NONLINEAR_AUXILIARY_ELIMINATION_MAP_Q2", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Derive the quadratic source-to-split map and require its pullback to reproduce the exact f_hat-v-v defect."),
        ("STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Replay the authoritative source master action through arity three under the nonlinear map before accepting q2/q3 hashes."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "After nonlinear theory identity, prove Noether closure of the general lambda-squared source."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose the accepted source-equivalent q2/q3 with both Green orientations and verify support and response identities."),
    ]
    retained = [item for item in previous["route_selection"] if item["route"] in {
        "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_RESIDUAL_EXACT_PAYLOAD",
        "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    }]
    routes.extend((item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"]) for item in retained)
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V25 atlas predecessor"},
        {"path": str(OBSTRUCTION.relative_to(ROOT)), "sha256": sha(OBSTRUCTION), "role": "exact source-versus-candidate nonlinear theory-identity obstruction"},
        {"path": str(GATE_V8.relative_to(ROOT)), "sha256": sha(GATE_V8), "role": "fail-closed Gate-A successor after the exact theory-identity decision"},
    ]
    value["claim_flags"].update({
        "v25_preserved": True,
        "strict_386_literal_trivial_stabilization_identity_refuted": True,
        "strict_386_linear_shear_theory_identity_refuted": True,
        "strict_386_candidate_internal_identities_preserved": True,
        "strict_386_nonlinear_equivalence_may_exist": True,
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
        "nonexistence of a nonlinear auxiliary-elimination or cyclic L-infinity equivalence",
        "that the internally certified q1/q2/q3 candidate algebra is inconsistent",
        "the complete authoritative 386-row q2/q3 or its causal lambda-squared source closure",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v26.py",
        "checks": ["V25 predecessor and 77-cell preservation", "exact -1 versus 0 cyclic-channel comparison", "Gate V8 fail-closed projection", "literal/linear obstruction versus nonlinear-equivalence firewall", "eleven-route deterministic queue", "Gate-A/Hadamard/QME firewalls"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_nonminimal_theory_identity_obstruction"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v26", "", "## Outcome", "", value["answer"], "",
        "## Exact theory-identity obstruction", "",
        f"- Channel: `{p['cyclic_form_channel']}` on `{', '.join(p['block_channel'])}`.",
        f"- Source / candidate / defect: **{p['source_value']} / {p['candidate_value']} / {p['source_minus_candidate_defect']}**.",
        f"- Literal / linear identity refuted: **{p['literal_identity_refuted']} / {p['linear_shear_only_identity_refuted']}**.",
        f"- Nonlinear equivalence may exist / constructed / obstructed: **{p['nonlinear_equivalence_may_exist']} / {p['nonlinear_equivalence_constructed']} / {p['nonlinear_equivalence_obstructed']}**.", "",
        "## Gate-A disposition", "",
        f"Gate V8 remains **{value['strict_gate_v8_reconciliation']['gate_a_status']}** with **{value['strict_gate_v8_reconciliation']['accepted_top_level_hashes']}** accepted authoritative hashes.  It records the literal/linear rejection and makes the nonlinear auxiliary-elimination map the next M2 object.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v26.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v26.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v26.py", "python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v26", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
