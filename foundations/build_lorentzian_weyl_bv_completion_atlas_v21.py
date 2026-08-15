#!/usr/bin/env python3
"""Build Atlas V21 from V20 plus the field-equation quotient inverse."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20.json"
TYPED = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v21.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    typed = json.loads(TYPED.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20":
        raise ValueError("V20 predecessor drift")
    if typed.get("result_id") != "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1":
        raise ValueError("typed inverse dependency drift")
    flags = typed["claim_flags"]
    required = (
        "STRICT_386_FIELD_EQUATION_GREEN_COMPONENT_TYPED",
        "STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED",
        "STRICT_386_FIELD_EQUATION_QUOTIENT_LEFT_INVERSE_CERTIFIED",
        "STRICT_386_UNGAUGE_FIXED_TWO_SIDED_GREEN_INVERSE_OBSTRUCTED",
    )
    if not all(flags.get(key) is True for key in required):
        raise ValueError("typed quotient inverse unavailable")
    if flags.get("STRICT_386_ALL_ORDER_NONLINEAR_SOURCE_CLOSURE_CERTIFIED") is not False:
        raise ValueError("nonlinear closure over-promotion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v21",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21",
        "created": "2026-08-15",
        "repository_base_commit": "f828b7b249d8ce762e4cabec6f2bae2ee0f381c6",
        "question": "Does the 386-row Green homotopy supply the field-equation inverse needed by the formal response series, and what gate remains after the types are corrected?",
        "answer": "Atlas V21 closes the typed unary Green route by correcting its target. The degree-one-to-zero component of each accepted Green homotopy is an exact right inverse of the field equation on Noether-compatible sources and an exact left inverse modulo gauge. A two-sided inverse on the full ungauge-fixed spaces is not merely absent but impossible because the certified gauge and Noether maps are nonzero and satisfy K R=0 and N K=0. Hence a full Hessian inverse is neither available nor required. The decisive nonlinear gate is now coefficientwise source-cocycle closure N S_m=0 from authoritative q2/q3/higher identities. First order passes for the candidate; lambda squared remains undecided. All 77 cells and the Gate-A/Hadamard/QME firewalls are preserved.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v21.md",
    })

    complex_data = typed["typed_complex"]
    identities = typed["restricted_homotopy_identities"]
    obstruction = typed["full_inverse_obstruction"]
    nonlinear_gate = typed["nonlinear_consequence"]
    foundations = typed["foundational_strength"]
    projection = {
        "result_id": typed["result_id"],
        "status": typed["result_state"],
        "field_rows": complex_data["field_space"]["rows"],
        "equation_rows": complex_data["equation_space"]["rows"],
        "gauge_nonzero_coefficients": obstruction["nonzero_gauge_coefficients"],
        "field_equation_nonzero_coefficients": complex_data["field_equation_operator"]["nonzero_rational_jet_coefficients"],
        "noether_nonzero_coefficients": obstruction["nonzero_noether_coefficients"],
        "green_component_typed": True,
        "constrained_right_inverse": True,
        "quotient_left_inverse": True,
        "source_identity": identities["source_identity"],
        "field_identity": identities["field_identity"],
        "full_ungauge_fixed_two_sided_inverse": False,
        "full_inverse_obstructed": True,
        "first_order_candidate_source_typed": True,
        "all_order_nonlinear_source_closure": False,
        "corrected_promotion_gate": nonlinear_gate["corrected_promotion_gate"],
        "quotient_representative_selection_required": False,
        "foundational_classification": foundations["classification"],
        "weakest_complete_foundational_base": foundations["weakest_complete_foundational_base"],
        "next_gate": typed["next_gate"],
    }
    value["strict_field_equation_green_quotient_inverse"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED",
        "statement": "The field/equation restriction of both Green homotopies is now typed: it is a right inverse on Noether-compatible sources and a left inverse modulo gauge. A full ungauge-fixed two-sided inverse is exactly obstructed by the nonzero gauge and Noether maps. The candidate first-order nonlinear source is a certified cocycle; lambda-squared and all-order source closure remain open pending authoritative q2/q3/higher identities.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], typed["result_id"]])),
        "boundary": "The quotient inverse does not select a gauge, certify authoritative q2/q3, close the lambda-squared source, construct an analytic Moller map, pass Gate A, select Hadamard data or restore the QME.",
    })
    strict = branch(value, "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Source-certify q2/q3/higher identities and replay N S_m=0, beginning with the displayed lambda-squared source; the unary Green inverse route is closed in its correct quotient/constrained form."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The accepted Green homotopy induces the exact field-equation inverse on ker N and modulo im R; no full ungauge-fixed inverse can exist. The first candidate source closes, while lambda-squared source closure is undecided.",
        "best_next_object": "Authoritative q2/q3/higher source identities plus an exact coefficientwise N S_m=0 replay.",
        "foundational_boundary": "The quotient proof is finite exact algebra and selects no representative; the Green action retains its imported classical infinite-analysis assumptions.",
    }

    routes = [
        ("STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export authoritative nonlinear brackets or a source-certified cyclic L-infinity equivalence and bind their exact hashes."),
        ("STRICT_Q2_Q3_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Apply the authoritative identities to N S_m=0, beginning with the lambda-squared B(q2) source, and continue coefficientwise only when each source closes."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized centered representative vectors and H3/H4/H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature independent Hadamard route as a control without importing its theory identity."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "HIGH", "Only after source closure, derive seminorm majorants and a nonzero convergence domain; lambda-adic stabilization is not evidence for this route."),
        ("STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Test weighted or decaying opposite-polarity domains against the scalar zero-mode witness; polarized recursion does not require this."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V20 atlas predecessor"},
        {"path": str(TYPED.relative_to(ROOT)), "sha256": sha(TYPED), "role": "typed field-equation quotient inverse and full inverse obstruction"},
    ]
    value["claim_flags"].update({
        "v20_preserved": True,
        "strict_386_field_equation_green_component_typed": True,
        "strict_386_field_equation_constrained_right_inverse_certified": True,
        "strict_386_field_equation_quotient_left_inverse_certified": True,
        "strict_386_ungauge_fixed_two_sided_green_inverse_obstructed": True,
        "strict_386_ungauge_fixed_two_sided_green_inverse_constructed": False,
        "strict_386_candidate_first_order_source_cocycle_certified": True,
        "strict_386_all_order_nonlinear_source_closure_certified": False,
        "strict_386_order_lambda_squared_bv_residual_zero_certified": False,
        "strict_386_authoritative_formal_moller_map_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "a full two-sided inverse of the ungauge-fixed field-equation operator",
        "a selected gauge fixing or quotient representative",
        "all-order nonlinear source-cocycle closure",
        "authoritative q2, q3 or higher source identities",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v21.py",
        "checks": [
            "V20 predecessor and all 77 cells preserved",
            "116/116 typed field/equation and 425/3264/425 coefficient projection",
            "constrained-right and quotient-left identities",
            "full ungauge-fixed inverse no-go and no representative selection",
            "first-order versus all-order source-cocycle firewall",
            "eleven-route deterministic queue with the impossible route retired",
            "Gate-A/Hadamard/QME lifecycle firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_field_equation_green_quotient_inverse"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v21", "", "## Outcome", "", value["answer"], "",
        "## Corrected field-equation gate", "",
        f"- Field/equation rows: **{p['field_rows']} / {p['equation_rows']}**.",
        f"- Nonzero exact jet coefficients `R / K / N`: **{p['gauge_nonzero_coefficients']} / {p['field_equation_nonzero_coefficients']} / {p['noether_nonzero_coefficients']}**.",
        f"- Green component typed / constrained right inverse / quotient left inverse: **{p['green_component_typed']} / {p['constrained_right_inverse']} / {p['quotient_left_inverse']}**.",
        f"- Full ungauge-fixed two-sided inverse / exact obstruction: **{p['full_ungauge_fixed_two_sided_inverse']} / {p['full_inverse_obstructed']}**.",
        f"- All-order nonlinear source closure: **{p['all_order_nonlinear_source_closure']}**.", "",
        "```text", p["source_identity"], p["field_identity"], "```", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v21.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v21.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v21.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v21.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
