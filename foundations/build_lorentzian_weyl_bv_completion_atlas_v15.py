#!/usr/bin/env python3
"""Build atlas V15 from V14 plus represented Green names and scoped binding."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14.json"
GRAPH = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
GREEN = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
COMMON = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v15.md"


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
        "strict_graph_green_action_name", "strict_unary_causal_common_snapshot",
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
    previous, graph, green, common = (
        json.loads(path.read_text()) for path in (PREDECESSOR, GRAPH, GREEN, COMMON)
    )
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14":
        raise ValueError("V14 predecessor drift")
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
    if green.get("result_id") != "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1" or not all(
        green["claim_flags"].get(key) is True
        for key in (
            "STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED",
            "STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED",
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED",
        )
    ):
        raise ValueError("represented Green-name dependency drift")
    if common.get("result_id") != "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1" or (
        common["claim_flags"].get("STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED") is not True
    ):
        raise ValueError("unary-causal common snapshot dependency drift")
    if common["claim_flags"].get("CLASSICAL_IMPORT_GATE_PASSED") is not False:
        raise ValueError("scoped snapshot promoted full Gate A")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v15",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15",
        "created": "2026-08-15",
        "repository_base_commit": "37b3cac874c0662d09206d9d6a6b5362f7c4bf57",
        "question": "Can the V14 theorem-characterized endpoint and full Green homotopies be turned into portable represented actions on declared spaces, bound to the exact 386-row graph snapshot, and cleanly separated from the much broader twenty-export classical Gate-A freeze?",
        "answer": "Atlas V15 closes the V14 analytic portability route at the level the contract actually requested: a convergent operator name rather than a fictitious finite Green matrix. On the unit ultrastatic cylinder, compact smooth adjoint-tractor sources are represented by support-indexed canonical whole-eigenspace Hodge projections on S3. The parent Hodge wave acts modewise with the exact Duhamel kernel s_lambda(tau)=sin(sqrt(lambda)tau)/sqrt(lambda), while the scalar harmonic zero mode uses s_0(tau)=tau. The plus name is future-supported and the minus name past-supported; exact symbolic replay gives the oscillator ODE, unit derivative jump, zero-mode identity and transpose relation. Smooth spectral truncations converge in the LF source topology, and the content-pinned normally-hyperbolic theorem supplies continuous LF-to-Frechet extension, uniqueness and causal support. No eigenvector is selected inside a degenerate eigenspace. The exact support-local curved BGG maps, trace/Weyl shear and graph SDR then produce content-addressed endpoint and full 386-row action DAGs. A second independent receiver binds thirteen hashes—the basis, odd pairing, graph q1, five SDR maps, transported suspension, both Green names, represented spaces and transport contract—into one accepted unary-causal snapshot. This is not classical Gate A. The authoritative V5 freeze requires twenty exports, seven accepted top-level hashes and ten common-byte identities. The scoped analytic result accepts none of those seven top-level hashes and preserves all six missing bundles: a complete strict manifest, full q2 and local D with both D identities, continuum residual SDR, full cyclic pairing, exact residual SO(4,2) payload and centered H3/H4/H5 representatives. The route ranking therefore moves away from already-closed Green-name work and toward strict D/q2 on the accepted 386-row carrier. Effective numerical projector algorithms, kernel coordinate bytes, weakest-base calibration, Hadamard, Ward, positivity, renormalized products, QME restoration and residual quantum transfer all remain unpromoted.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v15.md",
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
    green_projection = {
        "result_id": green["result_id"],
        "status": green["result_state"],
        "name_kind": green["parent_spectral_name"]["name_kind"],
        "source_space": green["represented_spaces"]["source"]["space"],
        "source_topology": green["represented_spaces"]["source"]["topology"],
        "target_space": green["represented_spaces"]["target"]["space"],
        "target_topology": green["represented_spaces"]["target"]["topology"],
        "spatial_spectral_branches": len(green["parent_spectral_name"]["spatial_spectrum"]),
        "tractor_rank": green["carrier"]["tractor_rank"],
        "zero_mode_explicit": green["parent_spectral_name"]["spatial_spectrum"][0]["zero_mode"] == "k=0",
        "modal_inverse_jump_checked": green["analytic_and_exact_replay"]["modal_inverse_jump_checked_exactly"],
        "endpoint_name_serialized": green["claim_flags"]["STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED"],
        "full_graph_name_serialized": green["claim_flags"]["STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED"],
        "plus_name_sha256": green["canonical_hashes"]["plus_action_name_sha256"],
        "minus_name_sha256": green["canonical_hashes"]["minus_action_name_sha256"],
        "effective_solver": green["claim_flags"]["STRICT_386_RECEIVER_EXECUTABLE_NUMERIC_GREEN_SOLVER"],
        "kernel_bytes": green["claim_flags"]["STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED"],
        "weakest_base": green["foundational_strength"]["weakest_base"],
        "next_gate": green["next_gate"],
    }
    common_projection = {
        "result_id": common["result_id"],
        "status": common["result_state"],
        "carrier_rows": common["scope"]["carrier_rows"],
        "accepted_hashes": common["scope"]["accepted_hashes"],
        "snapshot_sha256": common["common_snapshot"]["sha256"],
        "receiver_status": common["common_snapshot"]["receiver_status"],
        "represented_green_actions_serialized": common["claim_flags"]["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"],
        "classical_gate_a_passed": common["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"],
        "gate_a_exports_required": common["gate_v5_reconciliation"]["exports_required"],
        "gate_a_hashes_required": common["gate_v5_reconciliation"]["top_level_hashes_required"],
        "gate_a_freeze_checks_required": common["gate_v5_reconciliation"]["freeze_checks_required"],
        "gate_a_hashes_accepted_by_scoped_result": common["gate_v5_reconciliation"]["top_level_hashes_accepted_by_this_scoped_result"],
        "missing_bundle_ids": [item["id"] for item in common["gate_v5_reconciliation"]["missing_bundle"]],
        "next_gate": common["next_gate"],
    }
    value["strict_graph_green_action_name"] = green_projection
    value["strict_unary_causal_common_snapshot"] = common_projection
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The 386-row unary-causal package is now one receiver-accepted scoped snapshot with thirteen hashes, including represented endpoint/full Green names. The broader classical Gate-A authority remains fail closed because its twenty exports, seven top-level hashes and ten identities are not on common bytes.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], green["result_id"], common["result_id"]],
        "boundary": "Unary graph algebra and causal action names are jointly accepted. This does not supply full strict q2/D, continuum residual SDR, full cyclic pairing, exact residual payload or centered representatives required by Gate V5.",
    })
    stage(value, "S2_CAUSAL_GREEN").update({
        "status": "SCOPED_CERTIFIED",
        "statement": "Both causal orientations now have receiver-readable convergent S3 Hodge-projector/Duhamel names transported through the exact BGG, trace/Weyl and graph SDR maps on all 386 rows.",
        "evidence": [*stage(value, "S2_CAUSAL_GREEN")["evidence"], green["result_id"], common["result_id"]],
        "boundary": "The representation is a classical convergent operator name, not an effective numerical projector implementation, kernel coordinate archive, Hadamard state or interacting causal construction.",
    })
    strict_branch(value)["next_decisive_object"] = "Select and serialize strict cylinder D on all 386 accepted rows, extend strict q2 to every required nonminimal/auxiliary row, and replay [D,q1] and D/q2 without importing Berger data."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The exact graph unary/SDR and both represented causal Green names are accepted together in a thirteen-hash scoped snapshot. The first missing common-carrier theory-identity datum is strict local D together with the required full-carrier q2 extension.",
        "best_next_object": "A content-addressed 386-row cylinder D action and strict q2 extension with independent [D,q1] and D/q2 replays, kept distinct from the Berger control theory.",
    }
    value["strict_gate_a_progress"].update({
        "status": "UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED_FULL_GATE_A_Q2_D_RESIDUAL_BUNDLE_REQUIRED",
        "graph_q1_sdr_component_jet_control": projection,
        "graph_green_action_name_control": green_projection,
        "unary_causal_common_snapshot_control": common_projection,
        "remaining_common_carrier": common["next_gate"],
        "boundary": "The scoped unary-causal snapshot is accepted, but it accepts zero of Gate V5's seven top-level hashes. Full q2/D, residual SDR, cyclic pairing, residual representation data and centered representatives remain separate required bundles.",
    })
    routes = [
        ("STRICT_386_FULL_D_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "MEDIUM", "Select the strict cylinder residual generator, serialize its local action on every accepted graph row, and independently replay [D,q1] before extending any nonlinear claim."),
        ("STRICT_386_Q2_D_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Extend the canonical strict q2 convention to required nonminimal and auxiliary rows on the accepted carrier and replay the D/q2 derivation identity without borrowing Berger rows."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control on the same support-local carrier and replay every contraction and chain-map identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "HIGH", "MEDIUM", "HIGH", "Bind the full pairing and sign convention to all nonminimal, auxiliary and residual rows, then replay q1/q2 and residual-SDR cyclic side conditions."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual fifteen-mode bases, exact SO(4,2) structure constants, representation matrices and q_res on one residual carrier."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized W-plus-squared and W-minus-squared representative vectors together with centered H3, H4 and H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent Hadamard route as a control while refusing to use its q2 or D as strict-theory Gate-A evidence."),
        ("STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "MEDIUM", "Optionally add effective projector and tail algorithms or kernel coordinate bytes without making that strengthening a prerequisite for the already-certified classical convergent name."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V14 atlas predecessor"},
        {"path": str(GREEN.relative_to(ROOT)), "sha256": sha(GREEN), "role": "represented endpoint and full graph Green-action names"},
        {"path": str(COMMON.relative_to(ROOT)), "sha256": sha(COMMON), "role": "receiver-accepted scoped unary-causal common snapshot"},
    ]
    value["claim_flags"].update({
        "v14_preserved": True,
        "strict_386_unshifted_graph_q1_snapshot_complete": True,
        "strict_386_unshifted_graph_sdr_snapshot_complete": True,
        "strict_386_graph_suspension_transported": True,
        "strict_386_represented_green_actions_serialized": True,
        "strict_386_unary_causal_common_snapshot_accepted": True,
        "strict_386_effective_numeric_green_solver": False,
        "strict_386_distribution_kernel_bytes_serialized": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_local_d_certified": False,
        "strict_386_q2_green_compatibility_certified": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(
        previous["does_not_establish"] + green["does_not_establish"] + common["does_not_establish"]
    ))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v15.py",
        "checks": [
            "V14 preservation", "77-cell closure", "strict S0/S2-only mutation",
            "graph q1/SDR projection", "27-table and 4374-coefficient inventory",
            "zero direct SDR defects", "transported suspension inventory",
            "eight-defect obsolete-suspension diagnostic", "exact PBW boundary",
            "three-branch Hodge spectrum and zero mode", "opposite Green signs",
            "thirteen-hash scoped snapshot", "twenty-export Gate-V5 firewall",
            "six missing-bundle preservation", "effective/kernel/quantum firewall", "eight-route ranking",
            "append-only provenance", "content hashes", "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_graph_q1_sdr_component_jets"]
    green = value["strict_graph_green_action_name"]
    common = value["strict_unary_causal_common_snapshot"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V15", "", "## Outcome", "", value["answer"], "",
        "## Exact graph-coordinate unary and retract", "",
        "| object | exact inventory | defects |", "|---|---:|---:|",
        f"| graph q1 | {item['operator_tables']} tables / {item['nonzero_rational_coefficients']:,} coefficients | formal transport: 0 |",
        f"| H_alg | {item['H_alg_nonzero_entries']} entries | {item['homotopy_defects']} |",
        f"| inclusion / projection | {item['inclusion_nonzero_entries']} / {item['projection_nonzero_entries']} | {item['retract_defects']} |",
        f"| retained / contracted projectors | {item['retained_projector_nonzero_entries']:,} / {item['contracted_projector_nonzero_entries']:,} | {item['side_condition_defects']} |", "",
        "## Suspension finding", "",
        f"The obsolete split diagonal suspension has **{item['old_diagonal_suspension_cyclicity_defects']}** graph-cyclicity defects. The transported suspension has **{item['transported_suspension_entries']}** entries, including **{item['transported_suspension_off_diagonal_entries']}** off diagonal, and its involution defect is **{item['transported_suspension_involution_defects']}**. Its **{item['raw_graph_suspension_cyclicity_residuals']}** raw residuals reduce to zero only by the pinned exact curved `Ncurv A=B C` relation whose raw residual has **{item['raw_second_chain_relation_residuals']}** entries.", "",
        "## Represented Green actions", "",
        f"The parent action is now a `{green['name_kind']}` on `{green['source_space']}` with its LF topology. It has **{green['spatial_spectral_branches']}** spatial Hodge branches, rank **{green['tractor_rank']}** tractor multiplicity, an explicit zero mode, and distinct content hashes for the future- and past-supported names. These names are transported to the 30-row endpoint and full 386-row graph action.", "",
        "## Scoped snapshot versus Gate A", "",
        f"The receiver accepts **{common['accepted_hashes']}** unary-causal hashes in snapshot `{common['snapshot_sha256']}`. Classical Gate A nevertheless remains fail closed: it requires **{common['gate_a_exports_required']}** exports, **{common['gate_a_hashes_required']}** top-level hashes and **{common['gate_a_freeze_checks_required']}** identity checks. This scoped result accepts **{common['gate_a_hashes_accepted_by_scoped_result']}** of those top-level hashes and preserves `{', '.join(common['missing_bundle_ids'])}`.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(
        f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |"
        for route in value["route_selection"]
    )
    lines += [
        "", "## Reproduction", "", "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v15.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v15.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v15.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v15.py",
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
