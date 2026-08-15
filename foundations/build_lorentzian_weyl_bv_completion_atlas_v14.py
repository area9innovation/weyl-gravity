#!/usr/bin/env python3
"""Build atlas V14 from V13 plus the exact graph-coordinate q1/SDR replay."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13.json"
GRAPH = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v14.md"


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
        "strict_canonical_shear_component_jets", "strict_graph_q1_sdr_component_jets",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, graph = json.loads(PREDECESSOR.read_text()), json.loads(GRAPH.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V13":
        raise ValueError("V13 predecessor drift")
    if graph.get("result_id") != "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1":
        raise ValueError("graph q1/SDR dependency drift")
    flags = graph["claim_flags"]
    for key in (
        "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED",
        "STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED",
        "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED",
        "STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED",
        "STRICT_386_GRAPH_SDR_CYCLICITY_REPLAYED",
        "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED",
    ):
        if flags.get(key) is not True:
            raise ValueError("graph q1/SDR positive flag drift: " + key)
    for key in (
        "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED", "CLASSICAL_IMPORT_GATE_PASSED",
        "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY",
    ):
        if flags.get(key) is not False:
            raise ValueError("graph result promoted downstream claim: " + key)

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v14",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14",
        "created": "2026-08-15",
        "repository_base_commit": "e96260407b1a665de31734018bd6c4cefd41590a",
        "question": "Can the V13 split unary complex, local SDR and canonical shear be assembled into one exact graph-coordinate component snapshot, including the changed suspension convention, while keeping represented Green actions and Gate A fail closed?",
        "answer": "Atlas V14 closes the finite graph-coordinate q1/SDR route on the same fixed 386-row carrier. Exact conjugation by the certified T/A/B shear, followed by the pinned curved chain relations and their formal adjoints, leaves eighteen split differential tables plus nine graph attachments: twenty-seven operator tables, seventy combined derivative multiindices and 4,374 nonzero rational coefficients through order four. The graph inclusion and projection each contain 488 coefficients, the retained and contracted projectors contain 1,756 and 2,082, and the unchanged algebraic homotopy contains 190. Direct exact component replay gives q_graph H+H q_graph=P_alg, p_graph i_graph=I, both projector identities, every normalized side condition and H cyclicity with zero defects. Formal nilpotency and both chain maps are bound to the coefficient-complete mapping-cylinder source and its exact curved PBW reductions rather than inferred from a naive commutative jet product. The replay also exposes a convention that V13 could not see: the old diagonal suspension has eight graph-cyclicity defects. The transported R_graph=S R S^-1 is an exact order-zero involution with 394 entries, eight off diagonal. Its 32 raw parallel-coefficient cyclic residuals are the paired image of the 16 raw Ncurv A-B C residuals and reduce to zero only under the pinned exact curved relation. The next frontier is now analytic, not finite algebraic: declare endpoint test and distribution spaces, serialize represented advanced and retarded actions with topology, continuity, uniqueness, causal support and adjoint data, compose them through this graph SDR, and bind the result into one receiver-accepted Gate-A snapshot. Local D, q2, Hadamard, Ward, positivity, products, QME and residual transfer remain downstream and false.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v14.md",
    })
    counts = graph["graph_q1_serialization"]["counts"]
    maps = graph["graph_sdr_component_maps"]
    replay = graph["exact_replay"]
    projection = {
        "result_id": graph["result_id"],
        "status": graph["result_state"],
        "carrier_dimension": graph["scope"]["carrier_dimension"],
        "retained_endpoint_dimension": graph["scope"]["retained_endpoint_dimension"],
        "contracted_dimension": graph["scope"]["contracted_dimension"],
        "operator_tables": counts["operator_tables"],
        "split_operator_tables": counts["split_operator_tables"],
        "graph_attachment_tables": counts["graph_attachment_tables"],
        "combined_derivative_multiindices": counts["combined_derivative_multiindices"],
        "nonzero_rational_coefficients": counts["nonzero_rational_coefficients"],
        "maximum_order": graph["graph_q1_serialization"]["maximum_order"],
        "H_alg_nonzero_entries": maps["H_alg_graph"]["nonzero_coefficients"],
        "inclusion_nonzero_entries": maps["i_end_graph"]["nonzero_coefficients"],
        "projection_nonzero_entries": maps["p_end_graph"]["nonzero_coefficients"],
        "retained_projector_nonzero_entries": maps["P_end_graph"]["nonzero_coefficients"],
        "contracted_projector_nonzero_entries": maps["P_alg_graph"]["nonzero_coefficients"],
        "homotopy_defects": replay["qH_plus_Hq_defects"],
        "retract_defects": replay["p_graph_i_graph_identity_defects"],
        "side_condition_defects": sum(replay[key] for key in (
            "H_squared_defects", "H_i_graph_defects", "p_graph_H_defects",
            "P_end_squared_defects", "P_alg_squared_defects", "P_end_P_alg_defects",
            "P_alg_P_end_defects",
        )),
        "H_cyclicity_defects": replay["H_alg_graph_cyclicity_defects"],
        "transported_suspension_entries": maps["R_graph"]["nonzero_coefficients"],
        "transported_suspension_off_diagonal_entries": 8,
        "transported_suspension_involution_defects": replay["R_graph_squared_defects"],
        "old_diagonal_suspension_cyclicity_defects": replay["untransported_diagonal_R_cyclicity_defects"],
        "raw_graph_suspension_cyclicity_residuals": replay["transported_R_raw_parallel_cyclicity_residual_coefficients"],
        "raw_second_chain_relation_residuals": replay["raw_N_A_minus_B_C_parallel_residual_coefficients"],
        "PBW_reduced_cyclicity_defects": replay["transported_R_PBW_reduced_cyclicity_defects"],
        "graph_snapshot_sha256": graph["graph_snapshot"]["snapshot_sha256"],
        "represented_green_actions_serialized": flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"],
        "classical_import_gate_passed": flags["CLASSICAL_IMPORT_GATE_PASSED"],
        "next_gate": graph["next_gate"],
    }
    value["strict_graph_q1_sdr_component_jets"] = projection
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The exact split unary/SDR, canonical shear, graph q1/SDR and transported graph suspension are now one content-addressed finite local chain. The graph differential has 27 tables and 4,374 rational coefficients; all direct retract, projector, homotopy and side-condition defects vanish. Gate A remains closed because represented advanced/retarded actions on declared analytic spaces have not been bound.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], graph["result_id"]],
        "boundary": "Graph-coordinate unary and SDR algebra is certified, including the non-diagonal transported suspension and exact curved PBW boundary. Represented Green actions, the full causal homotopy and their common receiver snapshot are not; local D and q2 remain outside the accepted carrier.",
    })
    strict_branch(value)["next_decisive_object"] = "Declare endpoint test/distribution spaces and serialize represented advanced/retarded actions with topology, continuity, uniqueness, causal support and adjoint data; then compose them through the certified graph SDR."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The complete finite graph-coordinate q1/SDR and transported suspension now replay exactly on the fixed 386 rows. The first missing theory-identity datum is represented endpoint Green action on declared analytic spaces.",
        "best_next_object": "A content-addressed endpoint test/distribution-space declaration and advanced/retarded action serialization with continuity, uniqueness, causal support and suspended-adjoint witnesses.",
    }
    value["strict_gate_a_progress"].update({
        "status": "GRAPH_Q1_SDR_AND_SUSPENSION_SERIALIZED_REPRESENTED_GREEN_AND_COMMON_SNAPSHOT_REQUIRED",
        "graph_q1_sdr_component_jet_control": projection,
        "remaining_common_carrier": graph["next_gate"],
        "boundary": "Finite graph unary, SDR and suspension data pass exact producer and independent replays. Gate A still requires represented endpoint Green actions, the composed full causal homotopy and one receiver-accepted common snapshot before q2 or D are bound.",
    })
    routes = [
        ("STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Declare represented test/distribution spaces and import advanced/retarded endpoint actions with topology, continuity, uniqueness, causal support and suspended-adjoint data."),
        ("STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose the represented endpoint action with the certified graph-coordinate SDR and replay the full 386-row homotopy, causal support and suspended adjointness."),
        ("STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Bind basis, pairing, graph q1/SDR, transported suspension and represented Green actions into one receiver-accepted import snapshot without treating producer regeneration as independent verification."),
        ("STRICT_386_LOCAL_D", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Serialize cylinder-time D on the accepted common carrier and verify its q1 commutator before any nonlinear promotion."),
        ("STRICT_386_Q2_GREEN_COMPATIBILITY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional state selection."),
        ("BACH_FLAT_NONLINEAR_CARTAN", "PURE_WEYL_BACH_FLAT_RANK310", "HIGH", "MEDIUM", "MEDIUM", "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory import route advances."),
        ("GRAPH_SUSPENSION_CONSUMER_AUDIT", "STRICT_PURE_WEYL_386", "MEDIUM", "HIGH", "LOW", "Require every downstream graph-coordinate cyclic calculation to consume R_graph rather than the obsolete split diagonal suspension and reject unpinned raw PBW simplifications."),
    ]
    value["route_selection"] = [
        {
            "rank": rank, "route": route, "branch": branch,
            "scientific_leverage": leverage, "tractability": tractability,
            "dependency_depth": depth, "recommendation": recommendation,
        }
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V13 atlas predecessor"},
        {"path": str(GRAPH.relative_to(ROOT)), "sha256": sha(GRAPH), "role": "exact graph-coordinate q1, SDR and transported suspension component jets"},
    ]
    value["claim_flags"].update({
        "v13_preserved": True,
        "strict_386_unshifted_graph_q1_snapshot_complete": True,
        "strict_386_unshifted_graph_sdr_snapshot_complete": True,
        "strict_386_graph_suspension_transported": True,
        "strict_386_represented_green_actions_serialized": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_local_d_certified": False,
        "strict_386_q2_green_compatibility_certified": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + graph["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v14.py",
        "checks": [
            "V13 preservation", "77-cell closure", "strict S0-only mutation",
            "graph q1/SDR projection", "27-table and 4374-coefficient inventory",
            "zero direct SDR defects", "transported suspension inventory",
            "eight-defect obsolete-suspension diagnostic", "exact PBW boundary",
            "represented-Green/import/quantum firewall", "eight-route ranking",
            "append-only provenance", "content hashes", "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_graph_q1_sdr_component_jets"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V14", "", "## Outcome", "", value["answer"], "",
        "## Exact graph-coordinate unary and retract", "",
        "| object | exact inventory | defects |", "|---|---:|---:|",
        f"| graph q1 | {item['operator_tables']} tables / {item['nonzero_rational_coefficients']:,} coefficients | formal transport: 0 |",
        f"| H_alg | {item['H_alg_nonzero_entries']} entries | {item['homotopy_defects']} |",
        f"| inclusion / projection | {item['inclusion_nonzero_entries']} / {item['projection_nonzero_entries']} | {item['retract_defects']} |",
        f"| retained / contracted projectors | {item['retained_projector_nonzero_entries']:,} / {item['contracted_projector_nonzero_entries']:,} | {item['side_condition_defects']} |", "",
        "## Suspension finding", "",
        f"The obsolete split diagonal suspension has **{item['old_diagonal_suspension_cyclicity_defects']}** graph-cyclicity defects. The transported suspension has **{item['transported_suspension_entries']}** entries, including **{item['transported_suspension_off_diagonal_entries']}** off diagonal, and its involution defect is **{item['transported_suspension_involution_defects']}**. Its **{item['raw_graph_suspension_cyclicity_residuals']}** raw residuals reduce to zero only by the pinned exact curved `Ncurv A=B C` relation whose raw residual has **{item['raw_second_chain_relation_residuals']}** entries.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(
        f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |"
        for route in value["route_selection"]
    )
    lines += [
        "", "## Reproduction", "", "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v14.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v14.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v14.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v14.py",
        "```", "", "## Boundaries", "",
    ]
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
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
