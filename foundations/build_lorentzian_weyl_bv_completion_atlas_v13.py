#!/usr/bin/env python3
"""Build atlas V13 from V12 plus the exact fixed-basis canonical shear."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12.json"
SHEAR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v13.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "strict_canonical_shear_component_jets", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, shear = json.loads(PREDECESSOR.read_text()), json.loads(SHEAR.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12":
        raise ValueError("V12 predecessor drift")
    if shear.get("result_id") != "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1":
        raise ValueError("canonical shear dependency drift")
    flags = shear["claim_flags"]
    for key in (
        "STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED",
        "STRICT_386_CANONICAL_SHEAR_INVERSE_REPLAYED",
        "STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED",
    ):
        if flags.get(key) is not True:
            raise ValueError("canonical shear positive flag drift: " + key)
    if flags["STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED"] or flags["STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED"] or flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] or flags["CLASSICAL_IMPORT_GATE_PASSED"]:
        raise ValueError("graph/Green/import promotion drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v13",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13",
        "created": "2026-08-15",
        "repository_base_commit": "b3c49286d8623aed1a7ca0b2a95f7ad3d134a77f",
        "question": "Can the highest-ranked V12 finite coordinate gate be closed on the same 386-row bytes, including the ordered T/A/B cross terms, without implicitly claiming the graph differential, graph SDR or a represented causal Green action?",
        "answer": "Atlas V13 closes the canonical-shear route on the fixed 386-row Gate basis. The old T_state, A_equation and B_identity maps are first reconstructed from the serialized endpoint graph maps and curved projections; all three hashes agree exactly with the authoritative mapping-cylinder substitution. In the ordered 30+36 split the generalized-auxiliary attachment columns vanish, so the shear acts through the retained endpoint. Gate transport and the fixed odd pairing then determine three primal blocks and three BV-forced partners. Their ordered product and inverse each contain seven off-diagonal component-jet tables with 1,321 nonzero rational coefficients and maximum order three. The producer and independent rail retain the genuine A(-Tsharp) forward cross block and T(-Asharp) inverse cross block. Both left and right inverse replay with zero defects, every entry has degree zero, and each elementary type-II factor has zero BV-canonicality defects. This is meaningful progress but not Gate A: graph q1=S q1 S^-1 and the graph SDR remain distinct open component replays. The next certificate must explicitly conjugate the fixed split q1 and all five SDR maps through these shear bytes and independently replay nilpotency, both chain maps, homotopy, side conditions, projectors and cyclicity; none of those checks is inferred from shear invertibility alone. Represented endpoint Green actions, the full causal homotopy, local D, q2, Hadamard, Ward, QME and residual-transfer work remain downstream.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v13.md",
    })
    transform = shear["canonical_transform"]
    replay = shear["exact_replay"]
    projection = {
        "result_id": shear["result_id"],
        "status": shear["result_state"],
        "carrier_dimension": shear["scope"]["carrier_dimension"],
        "forward_table_count": transform["forward"]["table_count"],
        "inverse_table_count": transform["inverse"]["table_count"],
        "forward_nonzero_off_diagonal_coefficients": transform["forward"]["nonzero_off_diagonal_coefficients"],
        "inverse_nonzero_off_diagonal_coefficients": transform["inverse"]["nonzero_off_diagonal_coefficients"],
        "maximum_order": transform["forward"]["maximum_order"],
        "raw_T_A_B_hash_defects": replay["raw_T_A_B_hash_defects"],
        "generalized_auxiliary_attachment_nonzero_coefficients": replay["generalized_auxiliary_attachment_nonzero_coefficients"],
        "elementary_BV_canonicality_defects": replay["elementary_BV_canonicality_defects"],
        "left_inverse_defects": replay["full_left_inverse_defects"],
        "right_inverse_defects": replay["full_right_inverse_defects"],
        "forbidden_derivative_derivative_products": replay["forbidden_derivative_derivative_products_in_inverse_replay"],
        "forward_cross_terms": replay["forward_cross_terms"],
        "inverse_cross_terms": replay["inverse_cross_terms"],
        "canonical_shear_snapshot_sha256": shear["canonical_shear_snapshot"]["snapshot_sha256"],
        "graph_q1_replay_complete": shear["gate_disposition"]["graph_coordinate_q1_component_replay_complete"],
        "graph_sdr_replay_complete": shear["gate_disposition"]["graph_coordinate_sdr_component_replay_complete"],
        "represented_green_actions_serialized": flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"],
        "classical_import_gate_passed": flags["CLASSICAL_IMPORT_GATE_PASSED"],
        "next_gate": shear["next_gate"],
    }
    value["strict_canonical_shear_component_jets"] = projection
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The split q1/local-SDR snapshot and the separate degree-zero canonical shear are now exact fixed-basis component objects. The shear and inverse each have seven off-diagonal tables and 1,321 coefficients; raw authority hashes, inverse identities, degree and elementary BV canonicality all replay with zero defects. Gate A remains closed pending graph-coordinate q1/SDR replay and represented Green actions.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], shear["result_id"]],
        "boundary": "Canonical coordinate transport is certified, but q1_graph, the graph SDR, represented advanced/retarded actions and their common snapshot are not. Local D and q2 remain outside the accepted carrier.",
    })
    strict_branch(value)["next_decisive_object"] = "Conjugate q1 and the split local SDR through the exact shear bytes, reduce the curved-jet compositions using independently pinned chain relations, and replay the graph-coordinate identities before importing represented endpoint Green actions."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The fixed split unary/SDR snapshot and the complete canonical shear/inverse are now separate content-addressed exact component objects. The remaining finite theory-identity gate is their graph-coordinate conjugation replay.",
        "best_next_object": "A fixed-basis graph q1 and SDR component snapshot with explicit chain-relation/PBW provenance, nilpotency transport, chain maps, homotopy and cyclicity replayed.",
    }
    value["strict_gate_a_progress"].update({
        "status": "FULL_Q1_SPLIT_SDR_AND_CANONICAL_SHEAR_SERIALIZED_GRAPH_REPLAY_GREEN_COMMON_SNAPSHOT_REQUIRED",
        "canonical_shear_component_jet_control": projection,
        "remaining_common_carrier": shear["next_gate"],
        "boundary": "The split unary/SDR and canonical-shear snapshots pass their exact tests. Gate A still requires graph-coordinate q1/SDR bytes, represented Green actions and one receiver-accepted common snapshot before q2 or D are bound.",
    })
    routes = [
        ("STRICT_386_SPLIT_TO_GRAPH_SDR_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Conjugate q1 and the complete local SDR by the certified shear; reduce every curved-jet composition against pinned T/A/B chain relations and replay nilpotency transport, chain maps, homotopy and cyclicity on the graph bytes."),
        ("STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Declare represented test/distribution spaces and import advanced/retarded endpoint actions with topology, continuity, uniqueness, support and adjoint data."),
        ("STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose the represented endpoint action with the graph-coordinate SDR and replay full homotopy, causal support and suspended adjointness on the fixed carrier."),
        ("STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Bind basis, pairing, graph q1/SDR and represented Green actions into one receiver-accepted import snapshot without treating producer regeneration as independent verification."),
        ("STRICT_386_LOCAL_D", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Serialize cylinder-time D on the accepted common carrier and verify its q1 commutator before any nonlinear promotion."),
        ("STRICT_386_Q2_GREEN_COMPATIBILITY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional state selection."),
        ("BACH_FLAT_NONLINEAR_CARTAN", "PURE_WEYL_BACH_FLAT_RANK310", "HIGH", "MEDIUM", "MEDIUM", "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory import route advances."),
    ]
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V12 atlas predecessor"},
        {"path": str(SHEAR.relative_to(ROOT)), "sha256": sha(SHEAR), "role": "exact fixed-basis canonical shear and inverse component jets"},
    ]
    value["claim_flags"].update({
        "v12_preserved": True,
        "strict_386_canonical_shear_component_jets_serialized": True,
        "strict_386_canonical_shear_inverse_replayed": True,
        "strict_386_canonical_shear_bv_canonicality_replayed": True,
        "strict_386_unshifted_graph_q1_snapshot_complete": False,
        "strict_386_unshifted_graph_sdr_snapshot_complete": False,
        "strict_386_represented_green_actions_serialized": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + shear["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v13.py",
        "checks": ["V12 preservation", "77-cell closure", "strict S0-only mutation", "canonical-shear projection", "raw T/A/B hash closure", "seven-table forward/inverse inventory", "cross-term preservation", "zero inverse/degree/canonicality defects", "graph/Green/import firewall", "eight-route ranking", "append-only provenance", "content hashes", "canonical digest"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_canonical_shear_component_jets"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V13", "", "## Outcome", "", value["answer"], "",
        "## Exact fixed-basis canonical shear", "", "| direction | off-diagonal tables | nonzero exact coefficients | maximum order | inverse defects |", "|---|---:|---:|---:|---:|",
        f"| forward | {item['forward_table_count']} | {item['forward_nonzero_off_diagonal_coefficients']} | {item['maximum_order']} | {item['left_inverse_defects']} |",
        f"| inverse | {item['inverse_table_count']} | {item['inverse_nonzero_off_diagonal_coefficients']} | {item['maximum_order']} | {item['right_inverse_defects']} |", "",
        f"Raw T/A/B hash defects: **{item['raw_T_A_B_hash_defects']}**. Elementary BV-canonicality defects: **{item['elementary_BV_canonicality_defects']}**. Generalized-auxiliary attachment coefficients: **{item['generalized_auxiliary_attachment_nonzero_coefficients']}**.", "",
        f"Canonical-shear snapshot: `{item['canonical_shear_snapshot_sha256']}`.", "",
        "The forward `A(-Tsharp)` and inverse `T(-Asharp)` cross blocks are serialized; neither needs a derivative/derivative PBW composition because `A` and `Asharp` are pointwise after Gate transport.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v13.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v13.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v13.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v13.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {boundary}." for boundary in value["does_not_establish"])
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
