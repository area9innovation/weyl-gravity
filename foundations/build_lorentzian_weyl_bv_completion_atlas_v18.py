#!/usr/bin/env python3
"""Build Atlas V18 from V17 plus the strict candidate q2/Green preflight."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v18.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
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
    preflight = json.loads(PREFLIGHT.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17":
        raise ValueError("V17 predecessor drift")
    if preflight.get("result_id") != "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1":
        raise ValueError("q2/Green dependency drift")
    flags = preflight["claim_flags"]
    if not flags.get("STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED"):
        raise ValueError("candidate q2/Green identity unavailable")
    if flags.get("STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED") is not False:
        raise ValueError("q2/Green authority over-promotion")
    if flags.get("STRICT_386_RECURSIVE_NONLINEAR_GREEN_TREES_CERTIFIED") is not False:
        raise ValueError("recursive tree over-promotion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v18",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18",
        "created": "2026-08-15",
        "repository_base_commit": "907095c2753a91c6bc4b1d1ee0dbb8bf55373e5f",
        "question": "Does the exact stabilized q2 candidate compose causally with the represented strict 386-row Green homotopies, and which mathematical assumptions enter before recursive interaction, Hadamard and QME gates?",
        "answer": "Atlas V18 advances the strict architecture from separate nonlinear and causal ingredients to one certified first nonlinear causal response. The candidate q2 and unary-causal snapshot have identical basis, pairing and graph-q1 hashes. Both sign-oriented compositions B_plus/minus=Lambda_plus/minus q2_candidate are well-defined continuous bilinear names for compact smooth inputs, obey causal support, and satisfy the exact arity-two homotopy-response identity; their causal difference is q1-compatible. The proof cleanly stratifies finite exact local algebra from the genuinely infinite analytic Green layer. It does not identify the candidate as the authoritative classical q2, certify recursive causal trees, or promote Hadamard, products, QME or residual transfer. All 77 branch-stage cells are preserved and the classical import gate remains fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v18.md",
    })
    align = preflight["carrier_alignment"]
    local = preflight["local_q2_continuity"]
    replay = preflight["homotopy_response_replay"]
    foundation = preflight["foundational_strength"]
    projection = {
        "result_id": preflight["result_id"],
        "status": preflight["result_state"],
        "carrier_rows": align["carrier_rows"],
        "basis_match": align["basis_match"],
        "pairing_match": align["pairing_match"],
        "graph_q1_match": align["graph_q1_match"],
        "causal_orientations_composed": replay["sign_orientations_checked"],
        "per_input_derivative_order_bound": local["conservative_per_input_derivative_order_bound"],
        "total_derivative_order_bound": local["conservative_total_derivative_order_bound"],
        "response_identity_defects": replay["response_identity_structural_defects"],
        "causal_difference_identity_defects": replay["causal_difference_identity_structural_defects"],
        "plus_response_name_sha256": preflight["canonical_hashes"]["plus_response_name_sha256"],
        "minus_response_name_sha256": preflight["canonical_hashes"]["minus_response_name_sha256"],
        "causal_difference_name_sha256": preflight["canonical_hashes"]["causal_difference_name_sha256"],
        "foundational_classification": foundation["classification"],
        "finite_exact_layer": foundation["layers"][0]["upper_bound"],
        "completed_infinite_spaces_required": foundation["layers"][2]["completed_infinite_spaces_required"],
        "new_choice_beyond_green_theorem": foundation["layers"][3]["new_choice_beyond_imported_green_theorem"],
        "weakest_complete_foundational_base": foundation["weakest_complete_foundational_base"],
        "candidate_only": True,
        "authoritative_q2_green_compatibility": False,
        "recursive_nonlinear_green_trees": False,
        "next_gate": preflight["next_gate"],
    }
    value["strict_q2_green_composition_preflight"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "OPEN_SEEDED",
        "statement": "The first strict nonlinear causal response is certified for the stabilized candidate: both sign-oriented Green compositions have causal support and exact arity-two homotopy identities on common 386-row bytes. Authoritative q2 identity, recursive causal-tree domains and the D-Cartan classification remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], preflight["result_id"]])),
        "boundary": "One Green application after one candidate q2 interaction is not an authoritative nonlinear theory, a recursive perturbative solution, a D-Cartan homotopy, a Hadamard state or a QME theorem.",
    })
    branch(value, "STRICT_PURE_WEYL_386")["next_decisive_object"] = "Source-certify q2 theory identity; in parallel, declare and prove domains for recursive causal q2/Green trees when causal outputs re-enter the local interaction."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "Both first-response sign orientations compose on exact common carrier bytes and the causal difference is q1-compatible.",
        "best_next_object": "A recursive-tree domain/continuity theorem, kept candidate-scoped until authoritative q2 identity is imported.",
        "foundational_boundary": "Finite exact q2 algebra is PRA-bounded conditionally, while the represented Green factor uses completed LF/Frechet spaces and countable spectral convergence.",
    }
    routes = [
        ("STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export the authoritative full nonlinear q2 or a source-certified cyclic L-infinity equivalence; compare it to the candidate and bind its hash."),
        ("STRICT_RECURSIVE_CAUSAL_TREE_DOMAINS", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Extend the certified first response to declared retarded/advanced tree domains and prove continuity/support when causal outputs re-enter q2, without assuming authoritative identity."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized centered representative vectors and H3/H4/H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature independent Hadamard route as a control without importing its theory identity."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_GREEN_FOUNDATIONAL_CALIBRATION", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Calibrate the weakest reverse-mathematical and choice principles behind S3 spectral completeness and the normally-hyperbolic Green theorem."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V17 atlas predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "sha256": sha(PREFLIGHT), "role": "strict candidate q2/Green first-response and foundations preflight"},
    ]
    value["claim_flags"].update({
        "v17_preserved": True,
        "strict_386_candidate_q2_green_same_carrier_verified": True,
        "strict_386_candidate_first_nonlinear_causal_response_certified": True,
        "strict_386_candidate_q2_green_causal_support_certified": True,
        "strict_386_candidate_q2_green_response_identity_verified": True,
        "strict_386_q2_green_foundations_stratified": True,
        "strict_386_authoritative_q2_green_compatibility_certified": False,
        "strict_386_recursive_nonlinear_green_trees_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "authoritative strict q2/Green compatibility rather than candidate first-response compatibility",
        "recursive nonlinear causal trees or closure when two noncompact causal outputs re-enter q2",
        "a weakest reverse-mathematical or choice-free proof of the analytic Green layer",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v18.py",
        "checks": [
            "V17 predecessor and all 77 cells preserved",
            "candidate q2/Green carrier-hash projection",
            "two response names, support and zero-defect identity projection",
            "finite/infinite foundational boundary",
            "candidate/authority and recursive-tree firewalls",
            "nine-route deterministic queue",
            "Hadamard/QME/lifecycle firewall",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_q2_green_composition_preflight"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v18", "", "## Outcome", "", value["answer"], "",
        "## First nonlinear causal response", "",
        f"- Common carrier: **{p['carrier_rows']}** rows; basis/pairing/q1 matches: **{p['basis_match']} / {p['pairing_match']} / {p['graph_q1_match']}**.",
        f"- Composed causal orientations: **{p['causal_orientations_composed']}**.",
        f"- Structural defects: response **{p['response_identity_defects']}**, causal difference **{p['causal_difference_identity_defects']}**.",
        f"- Conservative differential-order bounds: **{p['per_input_derivative_order_bound']}** per input, **{p['total_derivative_order_bound']}** total.",
        f"- Authoritative compatibility: **{p['authoritative_q2_green_compatibility']}**; recursive trees: **{p['recursive_nonlinear_green_trees']}**.", "",
        "## Foundational boundary", "",
        f"The classification is `{p['foundational_classification']}`. The local exact layer is `{p['finite_exact_layer']}`. Completed infinite spaces are required: **{p['completed_infinite_spaces_required']}**. No new choice is introduced by composing q2 with the already imported Green theorem: **{not p['new_choice_beyond_green_theorem']}**. The weakest complete base remains `{p['weakest_complete_foundational_base']}`.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v18.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v18.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v18.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v18.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
