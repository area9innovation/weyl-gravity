#!/usr/bin/env python3
"""Build Atlas V22 from V21 plus the exact q2-only lambda2 obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"
OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v22.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21":
        raise ValueError("V21 predecessor drift")
    if obstruction.get("result_id") != "STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1":
        raise ValueError("lambda2 obstruction dependency drift")
    flags = obstruction["claim_flags"]
    if not flags.get("STRICT_386_Q2_ONLY_LAMBDA2_SOURCE_OBSTRUCTED") or not flags.get("STRICT_386_AUTHORITATIVE_Q3_REQUIRED"):
        raise ValueError("q2-only obstruction unavailable")
    if flags.get("STRICT_386_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED") is not False:
        raise ValueError("full Weyl source closure over-promotion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v22",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22",
        "created": "2026-08-15",
        "repository_base_commit": "aa45be6ffca005e79c38c43dfafefe3c8c76a366",
        "question": "Does the surviving strict q2-only response close at lambda squared, and what exact classical export is required if it does not?",
        "answer": "Atlas V22 decides the first nonlinear source question negatively for the quadratic receiver truncation. An exact q1-closed pure-diffeomorphism metric fixture has q2 Jacobiator 75760/27 in the Weyl Noether row, so the q2-only lambda-squared source has nonzero closure defect 37880/27. The quadratic candidate therefore cannot by itself be a Weyl-BV Maurer-Cartan or Moller map. This is not a no-go for full Weyl gravity: the arity-three identity requires q1 q3=-3 q2 q2, fixing the missing q3 witness value at -75760/9. The highest-leverage route is now an authoritative classical q2/q3 export and arity-three carrier bridge, followed by exact full-source closure. All 77 cells and Gate-A/Hadamard/QME firewalls remain preserved.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v22.md",
    })

    fixture = obstruction["exact_q1_closed_fixture"]
    disposition = obstruction["quadratic_truncation_disposition"]
    contract = obstruction["authoritative_q3_export_contract"]
    projection = {
        "result_id": obstruction["result_id"],
        "status": obstruction["result_state"],
        "fixture_id": fixture["fixture_id"],
        "q1_closed_fixture": True,
        "q2_jacobiator_nonzero": True,
        "q2_jacobiator_weyl_identity_value": disposition["witness_jacobiator_weyl_identity"],
        "q2_only_lambda2_source_closed": False,
        "q2_only_lambda2_source_defect": disposition["witness_source_closure_defect"],
        "authoritative_q3_required": True,
        "required_q3_q1_image": disposition["required_q3_q1_image_on_witness"],
        "authoritative_q3_imported": False,
        "full_weyl_lambda2_source_closure": False,
        "not_a_full_weyl_no_go": True,
        "export_contract_id": contract["contract_id"],
        "export_contract_gate": contract["gate_disposition"],
        "analytic_green_action_needed_for_obstruction": False,
        "foundational_classification": obstruction["foundational_strength"]["classification"],
        "next_gate": obstruction["next_gate"],
    }
    value["strict_quadratic_truncation_lambda2_source_obstruction"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_WITH_SCOPED_OBSTRUCTION",
        "statement": "The typed unary inverse remains closed on compatible sources. The q2-only nonlinear candidate now fails source closure at lambda squared on an exact q1-closed fixture: its Weyl-Noether defect is 37880/27. An authoritative q3 satisfying q1 q3=-3 q2 q2 is necessary and would cancel this scoped defect; full Weyl source closure is not yet decided.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], obstruction["result_id"]])),
        "boundary": "The nonzero witness rules out only the receiver q2-only truncation. It neither supplies authoritative q2/q3 nor obstructs the full Weyl theory, whose arity-three term may cancel it.",
    })
    strict = branch(value, "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Export authoritative q2/q3 and a source-certified arity-three bridge; require the q3 witness image -75760/9 and then replay N S2=0 exactly."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The unary quotient inverse is complete, but the q2-only lambda-squared source is exactly nonclosed with defect 37880/27 on a q1-closed fixture.",
        "best_next_object": "Authoritative q2/q3 Taylor exports plus q1 q3+q3 q1+q2 q2=0 on a content-addressed common carrier.",
        "falsification_target": "q1(q3(x,x,x))_omega_star=-75760/9 on FLAT_PURE_DIFF_GAUGE_SEED_1.",
        "foundational_boundary": "The obstruction is finite exact rational jet algebra; the later Green action retains its imported smooth infinite-analysis assumptions.",
    }

    routes = [
        ("STRICT_AUTHORITATIVE_Q2_Q3_ARITY_THREE_EXPORT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export authoritative q2 and q3, their convention and carrier bridge; replay q1 q3+q3 q1+q2 q2=0 and the fixed -75760/9 witness target."),
        ("STRICT_LAMBDA2_FULL_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "HIGH", "After the authoritative export, assemble S2=q2(x,r1)+(1/6)q3(x,x,x) and replay N S2=0 before any Green action."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized centered representative vectors and H3/H4/H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature independent Hadamard route as a control without importing its theory identity."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "HIGH", "Only after all-order source closure, derive seminorm majorants and a nonzero convergence domain."),
        ("STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Test weighted opposite-polarity domains against the scalar zero-mode witness; polarized recursion does not require this."),
        ("STRICT_GREEN_FOUNDATIONAL_CALIBRATION", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Calibrate the weakest reverse-mathematical and choice principles behind the PC/FC Green extensions and formal sequence coding."),
    ]
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch_id, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch_id, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V21 atlas predecessor"},
        {"path": str(OBSTRUCTION.relative_to(ROOT)), "sha256": sha(OBSTRUCTION), "role": "exact q2-only lambda2 source obstruction and q3 export contract"},
    ]
    value["claim_flags"].update({
        "v21_preserved": True,
        "strict_386_q2_only_lambda2_source_obstructed": True,
        "strict_386_q2_jacobiator_nonzero_witness_certified": True,
        "strict_386_authoritative_q3_required": True,
        "strict_386_authoritative_q3_imported": False,
        "strict_386_full_weyl_lambda2_source_closure_certified": False,
        "strict_386_quadratic_truncation_moller_map_certified": False,
        "strict_386_authoritative_formal_moller_map_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the q2-only receiver obstruction is a no-go theorem for full Weyl gravity",
        "an authoritative q3 or arity-three carrier bridge",
        "lambda-squared source closure after the full Weyl q3 term is included",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v22.py",
        "checks": [
            "V21 predecessor and all 77 cells preserved",
            "q1-closed fixture and 75760/27 Jacobiator projection",
            "37880/27 q2-only source defect and -75760/9 q3 target",
            "q2-only obstruction versus full-Weyl no-go firewall",
            "authoritative q3 import and full-source closure remain false",
            "eleven-route deterministic queue",
            "Gate-A/Hadamard/QME lifecycle firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_quadratic_truncation_lambda2_source_obstruction"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v22", "", "## Outcome", "", value["answer"], "",
        "## Lambda-squared source decision", "",
        f"- Exact q1-closed fixture: `{p['fixture_id']}`.",
        f"- q2 Jacobiator / q2-only source defect: **{p['q2_jacobiator_weyl_identity_value']} / {p['q2_only_lambda2_source_defect']}**.",
        f"- Required q1 q3 witness image: **{p['required_q3_q1_image']}**.",
        f"- q2-only source closed / full Weyl source closed: **{p['q2_only_lambda2_source_closed']} / {p['full_weyl_lambda2_source_closure']}**.",
        f"- Scoped obstruction is a full-Weyl no-go: **{not p['not_a_full_weyl_no_go']}**.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v22.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v22.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v22.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v22.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
