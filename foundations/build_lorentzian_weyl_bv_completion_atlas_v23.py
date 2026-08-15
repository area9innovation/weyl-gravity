#!/usr/bin/env python3
"""Build Atlas V23 from V22 plus the exact pure-Weyl q3 witness."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22.json"
Q3_WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v23.md"


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
        "strict_pure_weyl_q3_witness", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    witness = json.loads(Q3_WITNESS.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22":
        raise ValueError("V22 predecessor drift")
    if witness.get("result_id") != "STRICT_386_PURE_WEYL_Q3_WITNESS_V1":
        raise ValueError("q3 witness dependency drift")
    flags = witness["claim_flags"]
    if not flags.get("STRICT_PURE_WEYL_Q3_WITNESS_CANCELLATION_CERTIFIED") or not flags.get("STRICT_386_WITNESS_FULL_SOURCE_CLOSURE_CERTIFIED"):
        raise ValueError("q3 witness cancellation unavailable")
    if flags.get("STRICT_386_AUTHORITATIVE_Q3_IMPORTED") is not False or flags.get("STRICT_386_GENERAL_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED") is not False:
        raise ValueError("q3 witness authority boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v23",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23",
        "created": "2026-08-15",
        "repository_base_commit": "f6e40e94b18a9efda1dc0aac60efaed0ac4b0789",
        "question": "Can the missing cubic source cancellation be constructed in pure Weyl gravity, and does any existing complete q3 directly fill the strict carrier?",
        "answer": "Atlas V23 constructs the missing pure-Weyl cubic cancellation on the exact V22 witness. Direct third differentiation of the action-normalized Bach Euler density produces 41 rational coefficients across all ten metric-equation rows and gives q1 q3=-75760/9. This cancels three times the 75760/27 q2 Jacobiator, so the complete lambda-squared source is q1-closed on that witness. The result is deliberately scoped: it is a receiver-derived diagonal metric-sector calculation, not the authoritative arbitrary-input full-BV q3. The repository's complete Berger q3 is not a direct substitute because it belongs to Weyl-plus-clock theory at a fixed Berger background on a different 54-row carrier, with no certified same-theory cyclic map. The leading route is now the full arbitrary-input pure-Weyl q2/q3 export and 386-row stabilization.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v23.md",
    })

    fixture = witness["exact_cubic_fixture"]
    cancellation = witness["arity_three_cancellation"]
    compatibility = witness["q3_source_compatibility"]
    projection = {
        "result_id": witness["result_id"],
        "status": witness["result_state"],
        "fixture_id": fixture["fixture_id"],
        "metric_q3_term_count": fixture["metric_output_term_count"],
        "metric_q3_nonzero_rows": fixture["nonzero_metric_output_rows"],
        "q2_jacobiator_weyl_identity_value": cancellation["q2_jacobiator_weyl_noether"],
        "computed_q1_q3_weyl_identity_value": cancellation["computed_q1_q3"],
        "arity_three_witness_defect": cancellation["arity_three_defect"],
        "lambda2_witness_source_q1_defect": cancellation["full_lambda2_source_q1_defect_on_witness"],
        "lambda2_witness_source_closed": True,
        "general_full_weyl_lambda2_source_closed": False,
        "receiver_derived_metric_sector": True,
        "authoritative_arbitrary_input_q3_imported": False,
        "Berger_q3_direct_import_compatible": False,
        "Berger_disposition": next(item["disposition"] for item in compatibility["sources"] if item["source_id"] == "BERGER_SUPPORT_LOCAL_Q3"),
        "authoritative_export_contract_id": witness["authoritative_q3_export_contract"]["contract_id"],
        "foundational_classification": witness["foundational_strength"]["classification"],
        "next_gate": witness["next_gate"],
    }
    value["strict_pure_weyl_q3_witness"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_WITH_EXACT_Q3_WITNESS_CANCELLATION",
        "statement": "The q2-only lambda-squared source fails, but the action-derived pure-Weyl cubic metric source now cancels its exact Weyl-Noether defect on the pinned q1-closed fixture: q1 q3=-75760/9 and q1 S2=0. Arbitrary-input full-BV q3, its authoritative source status, and the 386-row arity-three identity remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], witness["result_id"]])),
        "boundary": "This is a receiver-derived diagonal metric-sector witness. It does not promote the candidate q2, import the Berger-plus-clock q3, certify arbitrary-input full-BV arity three, or prove general source closure.",
    })
    strict = branch(value, "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Export authoritative arbitrary-input pure-Weyl q2/q3 on one full minimal BV carrier, reproduce the -75760/9 witness, and stabilize the complete arity-three identity to all 386 rows."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The exact cubic Bach source realizes the required q3 cancellation and closes the full lambda-squared source on one q1-closed metric witness.",
        "best_next_object": "Authoritative arbitrary-input full-BV pure-Weyl q2/q3 exports plus a cyclic stabilization map to the 386-row graph carrier.",
        "falsification_target": "Every full export must reproduce q1(q3(x,x,x))_omega_star=-75760/9 on FLAT_PURE_DIFF_GAUGE_SEED_1 and then pass arbitrary-input q1q3+q3q1+q2q2=0.",
        "foundational_boundary": "The present witness is finite exact rational jet algebra; arbitrary smooth naturality, carrier stabilization, and later Green actions add separate mathematical commitments.",
    }

    routes = [
        ("STRICT_AUTHORITATIVE_ARBITRARY_FULL_BV_Q2_Q3_EXPORT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export arbitrary-input pure-Weyl q2/q3 with all ghost and antifield partners, reproduce the exact witness, and replay the complete arity-three identity."),
        ("STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Construct a content-addressed cyclic stabilization or L-infinity morphism from the authoritative minimal BV carrier to all 386 graph rows."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "HIGH", "After full export and stabilization, replay N S2=0 for arbitrary q1-closed inputs before applying a Green operator."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature Berger Hadamard route as a different-theory control, never as the strict pure-Weyl q3 import."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V22 atlas predecessor"},
        {"path": str(Q3_WITNESS.relative_to(ROOT)), "sha256": sha(Q3_WITNESS), "role": "exact pure-Weyl q3 witness cancellation and source compatibility inventory"},
    ]
    value["claim_flags"].update({
        "v22_preserved": True,
        "strict_pure_weyl_metric_q3_witness_derived": True,
        "strict_pure_weyl_q3_witness_cancellation_certified": True,
        "strict_386_lambda2_witness_full_source_closed": True,
        "strict_386_Berger_q3_direct_import_compatible": False,
        "strict_386_authoritative_q3_imported": False,
        "strict_386_arbitrary_input_q3_certified": False,
        "strict_386_full_bv_arity_three_identity_certified": False,
        "strict_386_general_full_weyl_lambda2_source_closure_certified": False,
        "strict_386_authoritative_formal_moller_map_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "an authoritative arbitrary-input pure-Weyl q3 or complete full-BV arity-three identity",
        "general lambda-squared source closure from one exact diagonal metric witness",
        "a direct import of the Berger-plus-clock q3 into the strict pure-Weyl carrier",
        "nonexistence of every possible future relation between the Berger and strict theories",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v23.py",
        "checks": [
            "V22 predecessor and all 77 cells preserved",
            "41-term ten-row pure-Weyl cubic metric witness projection",
            "-75760/9 q1 q3 and exact arity-three/source cancellation",
            "witness closure versus general full-BV closure firewall",
            "Berger different-theory/carrier direct-import firewall",
            "eleven-route deterministic queue",
            "Gate-A/Hadamard/QME lifecycle firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_pure_weyl_q3_witness"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v23", "", "## Outcome", "", value["answer"], "",
        "## Cubic source decision", "",
        f"- Exact q1-closed fixture: `{p['fixture_id']}`.",
        f"- Cubic metric payload: **{p['metric_q3_term_count']} terms / {p['metric_q3_nonzero_rows']} rows**.",
        f"- q2 Jacobiator / computed q1 q3: **{p['q2_jacobiator_weyl_identity_value']} / {p['computed_q1_q3_weyl_identity_value']}**.",
        f"- Arity-three defect / full source defect on the witness: **{p['arity_three_witness_defect']} / {p['lambda2_witness_source_q1_defect']}**.",
        f"- Witness closure / general closure: **{p['lambda2_witness_source_closed']} / {p['general_full_weyl_lambda2_source_closed']}**.",
        f"- Berger direct-import disposition: **{p['Berger_disposition']}**.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v23.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v23.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v23.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v23.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
