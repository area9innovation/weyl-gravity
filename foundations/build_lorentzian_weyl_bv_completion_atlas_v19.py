#!/usr/bin/env python3
"""Build Atlas V19 from V18 plus recursive causal-tree support domains."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18.json"
TREE_DOMAINS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v19.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    trees = json.loads(TREE_DOMAINS.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18":
        raise ValueError("V18 predecessor drift")
    if trees.get("result_id") != "STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1":
        raise ValueError("tree-domain dependency drift")
    flags = trees["claim_flags"]
    if not flags.get("STRICT_386_CANDIDATE_RETARDED_ALL_FINITE_Q2_TREES_CERTIFIED") or not flags.get("STRICT_386_CANDIDATE_ADVANCED_ALL_FINITE_Q2_TREES_CERTIFIED"):
        raise ValueError("polarized tree theorem unavailable")
    if flags.get("STRICT_386_UNRESTRICTED_MIXED_SIGN_TREES_CERTIFIED") is not False or flags.get("STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED") is not False:
        raise ValueError("tree over-promotion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v19",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19",
        "created": "2026-08-15",
        "repository_base_commit": "a10212695438b66626f72a468928320f7f3f2def",
        "question": "Which recursive candidate q2/Green trees close on honest support spaces, where does sign mixing first fail, and what is the next route toward a formal interacting causal architecture?",
        "answer": "Atlas V19 replaces the undifferentiated recursive-domain gap by a sharp split. Every finite all-retarded and every finite all-advanced candidate q2 tree closes continuously on fixed past-compact or future-compact support steps, with zero support-domain defects. Unrestricted sign mixing is not uniformly defined: the first two missing decorations occur in the balanced four-leaf topology, while all comb trees remain admissible. Thus polarized finite Møller trees survive, but arbitrary causal-difference trees, an infinite or formal series, higher brackets, authoritative q2 identity, Hadamard data and QME restoration remain open. All 77 cells and the classical authority firewall are preserved.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v19.md",
    })
    theorem = trees["recursive_polarized_tree_theorem"]
    mixed = trees["mixed_sign_boundary"]
    foundation = trees["foundational_strength"]
    census4 = next(item for item in trees["sign_decoration_census"] if item["leaves"] == 4)
    projection = {
        "result_id": trees["result_id"],
        "status": trees["result_state"],
        "retarded_all_finite_trees": theorem["retarded"]["all_finite_plane_binary_trees"],
        "advanced_all_finite_trees": theorem["advanced"]["all_finite_plane_binary_trees"],
        "support_domain_defects": theorem["finite_tree_support_domain_defects"],
        "nodewise_homotopy_domain_defects": theorem["finite_tree_nodewise_homotopy_domain_defects"],
        "continuity_scope": theorem["continuity_scope"],
        "first_mixed_failure_leaves": mixed["first_uniform_failure_leaf_count"],
        "first_mixed_failure_topology": mixed["first_failure_topology"],
        "four_leaf_all_sign_decorations": census4["all_sign_decorations"],
        "four_leaf_admissible": census4["admissible_total"],
        "four_leaf_not_uniformly_defined": census4["not_uniformly_defined"],
        "all_comb_sign_decorations_admissible": mixed["all_comb_trees_every_sign_decoration_admissible"],
        "unrestricted_mixed_sign_trees": False,
        "arbitrary_causal_difference_trees": False,
        "infinite_tree_series_convergence": False,
        "q3_or_higher_trees": False,
        "authoritative_q2": False,
        "foundational_classification": foundation["classification"],
        "weakest_complete_foundational_base": foundation["weakest_complete_foundational_base"],
        "next_gate": trees["next_gate"],
    }
    value["strict_recursive_causal_tree_domains"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED",
        "statement": "The candidate nonlinear causal architecture now closes on every finite polarized retarded or advanced q2/Green tree. The exact support grammar locates the first unrestricted mixed-sign nondefinition at the balanced four-leaf topology. Authoritative q2 identity, higher brackets, a formal or convergent Møller series and the D-Cartan classification remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], trees["result_id"]])),
        "boundary": "Finite polarized candidate trees are not an authoritative interaction, an unrestricted causal-difference recursion, an infinite perturbation series, a Hadamard state or a QME theorem.",
    })
    branch(value, "STRICT_PURE_WEYL_386")["next_decisive_object"] = "Source-certify q2 theory identity; meanwhile assemble the polarized finite trees coefficientwise into a formal Møller map and identify every required q3/higher source bracket."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "All finite polarized candidate q2/Green trees close on PC/FC support steps; 38/40 four-leaf sign decorations are uniformly defined.",
        "best_next_object": "A coefficientwise polarized formal Møller map, kept candidate-scoped, plus a source inventory of q3 and higher brackets.",
        "foundational_boundary": "Finite support grammar is primitive recursive; PC/FC Green extensions remain imported classical smooth analysis with uncalibrated weakest base.",
    }
    routes = [
        ("STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export the authoritative full nonlinear q2 or a source-certified cyclic L-infinity equivalence; compare it to the candidate and bind its hash."),
        ("STRICT_POLARIZED_FORMAL_MOLLER_COEFFICIENTS", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "MEDIUM", "Use the now-closed finite polarized domains to construct retarded and advanced formal coefficients and replay the fixed-point recursion without asserting analytic convergence."),
        ("STRICT_HIGHER_BRACKET_CAUSAL_IMPORT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Inventory and source-certify q3 and every higher classical bracket required beyond the binary candidate, then test their support-local causal insertion."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized centered representative vectors and H3/H4/H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature independent Hadamard route as a control without importing its theory identity."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Test weighted or decaying opposite-polarity domains against the scalar zero-mode witness; do not require them for polarized Møller recursion."),
        ("STRICT_GREEN_FOUNDATIONAL_CALIBRATION", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Calibrate the weakest reverse-mathematical and choice principles behind the PC/FC Green extensions and spectral completeness."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V18 atlas predecessor"},
        {"path": str(TREE_DOMAINS.relative_to(ROOT)), "sha256": sha(TREE_DOMAINS), "role": "strict candidate polarized recursive-tree theorem and mixed-sign boundary"},
    ]
    value["claim_flags"].update({
        "v18_preserved": True,
        "strict_386_candidate_retarded_all_finite_q2_trees_certified": True,
        "strict_386_candidate_advanced_all_finite_q2_trees_certified": True,
        "strict_386_candidate_fixed_step_tree_continuity_certified": True,
        "strict_386_first_mixed_sign_domain_nondefinition_at_four_leaves": True,
        "strict_386_unrestricted_mixed_sign_trees_certified": False,
        "strict_386_arbitrary_causal_difference_trees_certified": False,
        "strict_386_infinite_tree_series_convergence_certified": False,
        "strict_386_authoritative_q2_recursive_trees_certified": False,
        "strict_386_q3_or_higher_causal_trees_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "uniform definition of all mixed-sign or arbitrary causal-difference candidate trees",
        "a formal or convergent infinite polarized Møller series",
        "q3 or higher causal brackets on the strict carrier",
        "authoritative recursive Weyl interaction rather than candidate binary recursion",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v19.py",
        "checks": [
            "V18 predecessor and all 77 cells preserved",
            "polarized retarded/advanced finite-tree projection",
            "four-leaf 40/38/2 mixed-sign boundary projection",
            "finite exact versus imported analytic foundation split",
            "candidate, higher-bracket, infinite-series and authority firewalls",
            "eleven-route deterministic queue",
            "Hadamard/QME/lifecycle firewall",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_recursive_causal_tree_domains"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v19", "", "## Outcome", "", value["answer"], "",
        "## Recursive causal-tree decision", "",
        f"- Every finite retarded tree: **{p['retarded_all_finite_trees']}**.",
        f"- Every finite advanced tree: **{p['advanced_all_finite_trees']}**.",
        f"- Support and nodewise homotopy domain defects: **{p['support_domain_defects']} / {p['nodewise_homotopy_domain_defects']}**.",
        f"- First mixed failure: **{p['first_mixed_failure_leaves']} leaves**, `{p['first_mixed_failure_topology']}`.",
        f"- Four-leaf census: **{p['four_leaf_admissible']} / {p['four_leaf_all_sign_decorations']}** admissible; **{p['four_leaf_not_uniformly_defined']}** not uniformly defined.",
        f"- Unrestricted mixed trees / infinite convergence / authoritative q2: **{p['unrestricted_mixed_sign_trees']} / {p['infinite_tree_series_convergence']} / {p['authoritative_q2']}**.", "",
        "## Foundational boundary", "",
        f"The classification is `{p['foundational_classification']}`. The weakest complete base remains `{p['weakest_complete_foundational_base']}`. Finite sign grammar is exact; the PC/FC Green extension remains classical completed smooth analysis.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v19.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v19.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v19.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v19.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
