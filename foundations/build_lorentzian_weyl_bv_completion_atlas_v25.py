#!/usr/bin/env python3
"""Build Atlas V25 from V24 plus the 386-row candidate q3 stabilization."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24.json"
Q3_PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v25.md"


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
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "strict_386_stabilized_q3_preflight", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    preflight = json.loads(Q3_PREFLIGHT.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24":
        raise ValueError("V24 predecessor drift")
    flags = preflight.get("claim_flags", {})
    for key in (
        "STRICT_386_STABILIZED_Q3_CANDIDATE_CONSTRUCTED",
        "STRICT_386_STABILIZED_Q1_Q2_Q3_ARITY_THREE_IDENTITY_VERIFIED",
        "STRICT_386_STABILIZED_Q3_CYCLICITY_MOD_D_VERIFIED",
        "STRICT_386_STABILIZED_D_Q3_DERIVATION_VERIFIED",
    ):
        if flags.get(key) is not True:
            raise ValueError("q3 preflight positive gate unavailable: " + key)
    if flags.get("STRICT_386_AUTHORITATIVE_FULL_Q3_IMPORTED") is not False:
        raise ValueError("q3 preflight authority firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v25",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25",
        "created": "2026-08-15",
        "repository_base_commit": "5013af08d48bf45d99d9b841a75244122e3822f9",
        "question": "Does the accepted minimal q3 admit an exact cyclic stabilization to the 386-row causal graph, and which gate remains before that construction can represent the authoritative nonminimal theory?",
        "answer": "Atlas V25 constructs the 386-row candidate q3 explicitly. Zero-extension over the 356-row contractible complement followed by the same BV-canonical shear used for q1 and q2 gives a 16-channel ternary action DAG. Orthogonal direct sum and exact conjugation transport the full 72-channel/212-path arity-three identity, S3 symmetry, S4 quartic cyclicity modulo horizontal boundary, and the stationary D/q3 derivation with zero defects. This proves a valid candidate stabilization, not the authoritative nonminimal theory: the source has supplied neither a full 386-row q2/q3 export nor a cyclic L-infinity equivalence. The leading gate is therefore theory identity, followed by general lambda-squared source closure and q2/q3/Green response composition.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v25.md",
    })

    dag = preflight["graph_transport_dag"]
    identity = preflight["identity_transport"]
    theory = preflight["theory_identity_boundary"]
    projection = {
        "result_id": preflight["result_id"],
        "carrier_rows": preflight["scope"]["carrier_rows"],
        "endpoint_rows": preflight["scope"]["endpoint_rows"],
        "contractible_rows": preflight["scope"]["split_contractible_rows"],
        "construction_kind": preflight["split_candidate"]["construction_kind"],
        "graph_transport_kind": dag["construction_kind"],
        "expanded_ternary_block_channels": dag["expanded_ternary_block_channels"],
        "active_input_row_envelope": dag["active_input_row_envelope"],
        "active_output_row_envelope": dag["active_output_row_envelope"],
        "interaction_inert_rows": dag["interaction_inert_rows"],
        "arity_three_channels_transported": identity["q1_q2_q3_arity_three"]["minimal_typed_channels"],
        "arity_three_paths_transported": identity["q1_q2_q3_arity_three"]["minimal_composable_paths"],
        "arity_three_defects": identity["q1_q2_q3_arity_three"]["defects"],
        "q3_S3_defects": identity["q3_S3_symmetry"]["defects"],
        "q3_cyclicity_mod_d_defects": identity["q3_cyclicity_mod_d"]["defects_mod_d"],
        "D_q3_derivation_defects": identity["D_q3_derivation"]["derivation_defects"],
        "candidate_q3_stabilized": True,
        "authoritative_full_q3_imported": False,
        "authoritative_nonminimal_equivalence": False,
        "candidate_causal_lambda2_source_closure": theory["candidate_causal_lambda2_source_closure"],
        "classical_import_gate_a_passed": False,
        "foundational_classification": "FINITE_EXACT_STABILIZATION_PLUS_SMOOTH_LOCAL_VARIATIONAL_INPUT",
        "next_gate": preflight["next_gate"],
    }
    value["strict_386_stabilized_q3_preflight"] = projection
    value["strict_minimal_q3_completion"]["strict_386_candidate_q3_stabilized"] = True
    value["strict_minimal_q3_completion"]["strict_386_q3_stabilized"] = False

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_WITH_386_CANDIDATE_Q3_ARITY_AND_CYCLICITY",
        "statement": "The minimal q3 and the same-stabilization q2 now extend by exact direct sum and BV-canonical shear to a 386-row candidate. The 72-channel/212-path arity-three identity, S3 symmetry, cyclicity modulo d, and D/q3 derivation transport with zero defects. Authoritative nonminimal theory identity and causal lambda-squared source closure remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], preflight["result_id"]])),
        "boundary": "This is a mathematically valid candidate stabilization, not a source-certified full nonminimal export or cyclic L-infinity equivalence. It cannot enter Gate A or the Green/Hadamard/QME chain as authoritative nonlinear data.",
    })
    strict = branch(value, "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Obtain authoritative nonminimal theory identity for the common q1/q2/q3 stabilization; then replay general lambda-squared source closure and compose the accepted brackets with the Green homotopy."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "An exact 386-row candidate q3 stabilization now shares the q1/q2 shear and transports arity three, cyclicity and D/q3 with zero defects.",
        "best_next_object": "A source-certified nonminimal q2/q3 export or cyclic L-infinity equivalence identifying the candidate with the authoritative classical theory.",
        "falsification_target": "Compare all authoritative nonminimal interaction rows, or replay a source-provided cyclic L-infinity morphism, before accepting q2/q3 hashes into Gate A.",
        "foundational_boundary": "The stabilization is finite exact and adds no choice or infinite sum. Its q3 input uses smooth local variational calculus; Green/Hadamard topology remains a separate layer.",
    }

    routes = [
        ("STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Obtain a source-certified full nonminimal q2/q3 export or cyclic L-infinity equivalence and compare it with the exact candidate."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "After theory identity, replay the general lambda-squared Noether source cocycle on arbitrary q1-closed graph inputs."),
        ("STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose both Green orientations with the accepted q2/q3 source at lambda squared and verify the response identity and support domains."),
    ]
    retained = [item for item in previous["route_selection"] if item["route"] not in {
        "STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE"
    }]
    for item in retained:
        routes.append((item["route"], item["branch"], item["scientific_leverage"], item["tractability"], item["dependency_depth"], item["recommendation"]))
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V24 atlas predecessor"},
        {"path": str(Q3_PREFLIGHT.relative_to(ROOT)), "sha256": sha(Q3_PREFLIGHT), "role": "exact 386-row candidate q3 stabilization and identity transport"},
    ]
    value["claim_flags"].update({
        "v24_preserved": True,
        "strict_386_candidate_q3_stabilized": True,
        "strict_386_candidate_full_bv_arity_three_identity_certified": True,
        "strict_386_candidate_q3_cyclicity_mod_d_certified": True,
        "strict_386_candidate_D_q3_derivation_certified": True,
        "strict_386_authoritative_q3_imported": False,
        "strict_386_authoritative_nonminimal_equivalence_certified": False,
        "strict_386_candidate_causal_lambda2_source_closure_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the exact 386-row q3 candidate is the authoritative nonminimal pure-Weyl BV interaction",
        "a source-certified cyclic L-infinity equivalence from the authoritative nonminimal action to the candidate",
        "general lambda-squared causal source closure or q2/q3/Green compatibility from local arity three alone",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v25.py",
        "checks": [
            "V24 predecessor and all 77 cells preserved except the strict nonlinear stage",
            "16-channel 386-row ternary DAG projection",
            "72-channel/212-path arity-three and S4-mod-d cyclicity transport",
            "candidate versus authoritative nonminimal theory firewall",
            "eleven-route deterministic queue",
            "Gate-A/Hadamard/QME lifecycle firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_386_stabilized_q3_preflight"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v25", "", "## Outcome", "", value["answer"], "",
        "## 386-row candidate q3 stabilization", "",
        f"- Carrier: **{p['carrier_rows']}={p['endpoint_rows']}+{p['contractible_rows']} rows**.",
        f"- Ternary support envelope: **{p['expanded_ternary_block_channels']} block channels; {p['active_input_row_envelope']} input / {p['active_output_row_envelope']} output rows**.",
        f"- Transported arity three: **{p['arity_three_channels_transported']} channels / {p['arity_three_paths_transported']} paths / {p['arity_three_defects']} defects**.",
        f"- S3 / cyclicity mod d / D-q3 defects: **{p['q3_S3_defects']} / {p['q3_cyclicity_mod_d_defects']} / {p['D_q3_derivation_defects']}**.",
        f"- Candidate / authoritative q3: **{p['candidate_q3_stabilized']} / {p['authoritative_full_q3_imported']}**.",
        f"- Candidate causal lambda2 closure / Gate A: **{p['candidate_causal_lambda2_source_closure']} / {p['classical_import_gate_a_passed']}**.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v25.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v25.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v25.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v25.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
