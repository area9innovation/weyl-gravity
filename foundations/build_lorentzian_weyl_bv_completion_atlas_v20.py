#!/usr/bin/env python3
"""Build Atlas V20 from V19 plus polarized formal coefficients."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"
FORMAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v20.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
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
    formal = json.loads(FORMAL.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19":
        raise ValueError("V19 predecessor drift")
    if formal.get("result_id") != "STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1":
        raise ValueError("formal-coefficient dependency drift")
    flags = formal["claim_flags"]
    if not flags.get("STRICT_386_CANDIDATE_POLARIZED_FORMAL_COEFFICIENTS_CERTIFIED"):
        raise ValueError("formal coefficients unavailable")
    if flags.get("STRICT_386_WEYL_BV_MAURER_CARTAN_SERIES_CERTIFIED") is not False or flags.get("STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED") is not False:
        raise ValueError("formal coefficient over-promotion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v20",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20",
        "created": "2026-08-15",
        "repository_base_commit": "5754b7b4aa89243078e0bb4967a276c3c79a690f",
        "question": "Do the certified polarized trees define a formal Weyl-BV Moller map, or where does that promotion first require new classical data?",
        "answer": "Atlas V20 closes the purely formal combinatorial step but refuses the stronger name. Both polarized quadratic response equations have unique lambda-adic coefficient sequences: coefficient m is the exact Catalan(m) tree sum with weight (-1/2)^m, supported on the certified PC/FC domain. Yet the first-response homotopy identity proves the interacting BV equation only through order lambda. At lambda squared an explicit B(q2) residual remains undecided. Thus the new result is a candidate formal fixed-point inverse, not an authoritative Weyl-BV Moller map. The decisive next objects are now a typed field-equation Green inverse and source-certified q2/q3/higher identities. All 77 cells and every Hadamard/QME firewall remain preserved.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v20.md",
    })
    coefficient_rows = formal["catalan_tree_formula"]["checked_rows"]
    diagnostic = formal["bv_equation_diagnostic"]
    foundation = formal["foundational_strength"]
    projection = {
        "result_id": formal["result_id"],
        "status": formal["result_state"],
        "orientations": 2,
        "checked_through_leaves": formal["catalan_tree_formula"]["checked_through_leaves"],
        "largest_checked_tree_count": coefficient_rows[-1]["plane_tree_count"],
        "coefficientwise_fixed_point": True,
        "catalan_formula": True,
        "formal_inverse": True,
        "lambda_adic_stabilization": True,
        "analytic_convergence": False,
        "nonperturbative_inverse": False,
        "order_lambda_bv_residual_zero": True,
        "order_lambda_squared_bv_residual": diagnostic["order_lambda_squared_residual"],
        "order_lambda_squared_bv_residual_zero_certified": False,
        "weyl_bv_maurer_cartan_series": False,
        "authoritative_weyl_bv_moller_map": False,
        "typed_field_equation_green_inverse": False,
        "q3_or_higher_imported": False,
        "foundational_classification": foundation["classification"],
        "weakest_complete_foundational_base": foundation["weakest_complete_foundational_base"],
        "next_gate": formal["next_gate"],
    }
    value["strict_polarized_formal_coefficients"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED",
        "statement": "Every finite polarized response tree and the resulting unique lambda-adic coefficient sequence are certified for the candidate. The formal fixed-point residual vanishes coefficientwise, but the Weyl-BV equation is established only at first order: an explicit undecided B(q2) residual appears at lambda squared. A typed field-equation Green inverse and source q2/q3/higher identities remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], formal["result_id"]])),
        "boundary": "Formal coefficient existence and lambda-adic stabilization are not analytic convergence, an action-derived Moller theorem, a Maurer-Cartan solution, authoritative q2, Hadamard data or QME restoration.",
    })
    branch(value, "STRICT_PURE_WEYL_386")["next_decisive_object"] = "Source-certify q2/q3/higher theory identity and construct the typed field-equation Green inverse needed to decide the lambda-squared BV residual."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "Both candidate polarized fixed-point series exist uniquely lambda-adically with exact Catalan coefficients; the first unclosed BV equation coefficient is lambda squared.",
        "best_next_object": "A field-equation-sector Green inverse plus exact q2/q3/higher source identities that decide the displayed B(q2) residual.",
        "foundational_boundary": "Each coefficient is primitive-recursive finite data; the omega-sequence is formal, while every analytic coefficient still imports classical PC/FC Green analysis.",
    }
    routes = [
        ("STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export the authoritative nonlinear brackets or a source-certified cyclic L-infinity equivalence and bind their exact hashes."),
        ("STRICT_TYPED_FIELD_EQUATION_GREEN_INVERSE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Restrict the 386-row homotopy to the actual field-equation complex and prove the inverse identity required by Yang-Feldman, rather than a chain-homotopy identity alone."),
        ("STRICT_Q2_Q3_MAURER_CARTAN_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Replay the lambda-squared B(q2) residual with source q2/q3/higher identities and continue coefficientwise only when each obstruction closes."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized centered representative vectors and H3/H4/H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature independent Hadamard route as a control without importing its theory identity."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "HIGH", "Only after the BV coefficients close, derive seminorm majorants and a nonzero convergence domain; lambda-adic stabilization is not evidence for this route."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V19 atlas predecessor"},
        {"path": str(FORMAL.relative_to(ROOT)), "sha256": sha(FORMAL), "role": "strict candidate polarized formal coefficients and BV promotion diagnostic"},
    ]
    value["claim_flags"].update({
        "v19_preserved": True,
        "strict_386_candidate_polarized_formal_coefficients_certified": True,
        "strict_386_candidate_coefficientwise_fixed_point_verified": True,
        "strict_386_candidate_catalan_formula_verified": True,
        "strict_386_candidate_lambda_adic_stabilization_verified": True,
        "strict_386_order_lambda_squared_bv_residual_zero_certified": False,
        "strict_386_typed_field_equation_green_inverse_certified": False,
        "strict_386_weyl_bv_maurer_cartan_series_certified": False,
        "strict_386_authoritative_formal_moller_map_certified": False,
        "strict_386_analytic_moller_convergence_certified": False,
        "strict_386_nonperturbative_moller_map_constructed": False,
        "strict_386_q3_or_higher_causal_trees_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that coefficientwise formal fixed-point inversion is a Weyl-BV Maurer-Cartan or Moller theorem",
        "vanishing or nonvanishing of the lambda-squared B(q2) residual",
        "a typed field-equation Green inverse or source q3/higher brackets",
        "analytic convergence or a nonperturbative Moller inverse",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v20.py",
        "checks": [
            "V19 predecessor and all 77 cells preserved",
            "exact formal coefficient and Catalan projection",
            "lambda-adic versus analytic-convergence separation",
            "lambda and lambda-squared BV diagnostic projection",
            "field-inverse, higher-bracket, authority, Hadamard and QME firewalls",
            "twelve-route deterministic queue",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_polarized_formal_coefficients"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v20", "", "## Outcome", "", value["answer"], "",
        "## Formal coefficient decision", "",
        f"- Two polarized coefficient families: **{p['orientations']}**.",
        f"- Checked through **{p['checked_through_leaves']} leaves**; largest enumerated tree family **{p['largest_checked_tree_count']}**.",
        f"- Coefficientwise fixed point / Catalan formula / lambda-adic stabilization: **{p['coefficientwise_fixed_point']} / {p['catalan_formula']} / {p['lambda_adic_stabilization']}**.",
        f"- Analytic convergence / nonperturbative inverse: **{p['analytic_convergence']} / {p['nonperturbative_inverse']}**.",
        f"- Weyl-BV equation: order lambda closes, order lambda squared leaves `{p['order_lambda_squared_bv_residual']}` with zero **not certified**.",
        f"- Authoritative Weyl-BV Moller map: **{p['authoritative_weyl_bv_moller_map']}**.", "",
        "## Foundational boundary", "",
        f"`{p['foundational_classification']}`; weakest complete base `{p['weakest_complete_foundational_base']}`. Formal lambda-adic stabilization is coefficientwise arithmetic, not analytic convergence.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v20.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v20.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v20.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v20.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
