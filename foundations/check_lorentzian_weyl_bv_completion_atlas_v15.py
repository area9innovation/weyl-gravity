#!/usr/bin/env python3
"""Independent structural and claim-boundary checker for completion atlas V15."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14.json"
GRAPH = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
GREEN = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
COMMON = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
STAGES = [f"S{i}_{name}" for i, name in enumerate((
    "CLASSICAL_AUTHORITY", "OFF_SHELL_BV", "CAUSAL_GREEN", "NONLINEAR_CARTAN",
    "HADAMARD_CCR", "BRST_WARD", "PHYSICAL_POSITIVITY", "RENORMALIZED_PRODUCTS",
    "QME", "RESIDUAL_TRANSFER", "LORENTZIAN_CERTIFIED",
))]
BRANCHES = [
    "STRICT_PURE_WEYL_386", "PURE_WEYL_BACH_FLAT_RANK310", "EINSTEIN_NARIAI_KS",
    "BERGER_POSITIVE_CLOCK_54", "VACUUM_CYLINDER_REDUCED", "TAU_ADIC_COMPENSATOR",
    "COMPLEX_COMPENSATOR_CHANGED_ACTION",
]
ROUTES = [
    "STRICT_386_FULL_D_ACTION", "STRICT_386_Q2_D_COMMON_CARRIER",
    "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING",
    "STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_CENTERED_REPRESENTATIVES",
    "DIRECT_SPACETIME_Q26_HADAMARD", "STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT",
]


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
        {key: value[key] for key in keys}, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous, source, green, common = (
        json.loads(path.read_text()) for path in (PREDECESSOR, GRAPH, GREEN, COMMON)
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v15"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage axis identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch axis identity/order")

    branches = {item.get("id"): item for item in value.get("branches", [])}
    old_branches = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, item in branches.items():
        if len(item.get("stages", [])) != 11:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and item != old_branches.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))
    strict, old_strict = branches.get("STRICT_PURE_WEYL_386", {}), old_branches.get("STRICT_PURE_WEYL_386", {})
    cells = {item.get("stage"): item for item in strict.get("stages", [])}
    old_cells = {item.get("stage"): item for item in old_strict.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in [item for item in STAGES if item not in ("S0_CLASSICAL_AUTHORITY", "S2_CAUSAL_GREEN")]:
        if cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    for key in set(old_strict) - {"stages", "next_decisive_object"}:
        if strict.get(key) != old_strict.get(key):
            errors.append("unlicensed strict branch mutation " + key)
    expected_evidence = [*old_cells.get("S0_CLASSICAL_AUTHORITY", {}).get("evidence", []), green["result_id"], common["result_id"]]
    if cells.get("S0_CLASSICAL_AUTHORITY", {}).get("evidence") != expected_evidence:
        errors.append("strict S0 evidence augmentation")
    expected_s2_evidence = [*old_cells.get("S2_CAUSAL_GREEN", {}).get("evidence", []), green["result_id"], common["result_id"]]
    if cells.get("S2_CAUSAL_GREEN", {}).get("evidence") != expected_s2_evidence or cells.get("S2_CAUSAL_GREEN", {}).get("status") != "SCOPED_CERTIFIED":
        errors.append("strict S2 evidence augmentation")

    counts, maps, replay, flags = (
        source["graph_q1_serialization"]["counts"], source["graph_sdr_component_maps"],
        source["exact_replay"], source["claim_flags"],
    )
    expected_projection = {
        "result_id": source["result_id"], "status": source["result_state"],
        "carrier_dimension": 386, "retained_endpoint_dimension": 30, "contracted_dimension": 356,
        "operator_tables": counts["operator_tables"], "split_operator_tables": counts["split_operator_tables"],
        "graph_attachment_tables": counts["graph_attachment_tables"],
        "combined_derivative_multiindices": counts["combined_derivative_multiindices"],
        "nonzero_rational_coefficients": counts["nonzero_rational_coefficients"],
        "maximum_order": source["graph_q1_serialization"]["maximum_order"],
        "H_alg_nonzero_entries": maps["H_alg_graph"]["nonzero_coefficients"],
        "inclusion_nonzero_entries": maps["i_end_graph"]["nonzero_coefficients"],
        "projection_nonzero_entries": maps["p_end_graph"]["nonzero_coefficients"],
        "retained_projector_nonzero_entries": maps["P_end_graph"]["nonzero_coefficients"],
        "contracted_projector_nonzero_entries": maps["P_alg_graph"]["nonzero_coefficients"],
        "homotopy_defects": replay["qH_plus_Hq_defects"],
        "retract_defects": replay["p_graph_i_graph_identity_defects"],
        "side_condition_defects": sum(replay[key] for key in (
            "H_squared_defects", "H_i_graph_defects", "p_graph_H_defects",
            "P_end_squared_defects", "P_alg_squared_defects", "P_end_P_alg_defects", "P_alg_P_end_defects",
        )),
        "H_cyclicity_defects": replay["H_alg_graph_cyclicity_defects"],
        "transported_suspension_entries": maps["R_graph"]["nonzero_coefficients"],
        "transported_suspension_off_diagonal_entries": 8,
        "transported_suspension_involution_defects": replay["R_graph_squared_defects"],
        "old_diagonal_suspension_cyclicity_defects": replay["untransported_diagonal_R_cyclicity_defects"],
        "raw_graph_suspension_cyclicity_residuals": replay["transported_R_raw_parallel_cyclicity_residual_coefficients"],
        "raw_second_chain_relation_residuals": replay["raw_N_A_minus_B_C_parallel_residual_coefficients"],
        "PBW_reduced_cyclicity_defects": replay["transported_R_PBW_reduced_cyclicity_defects"],
        "graph_snapshot_sha256": source["graph_snapshot"]["snapshot_sha256"],
        "represented_green_actions_serialized": False,
        "classical_import_gate_passed": False,
        "next_gate": source["next_gate"],
    }
    if value.get("strict_graph_q1_sdr_component_jets") != expected_projection:
        errors.append("graph q1/SDR projection")
    if (
        expected_projection["operator_tables"] != 27
        or expected_projection["nonzero_rational_coefficients"] != 4374
        or expected_projection["homotopy_defects"]
        or expected_projection["retract_defects"]
        or expected_projection["side_condition_defects"]
        or expected_projection["H_cyclicity_defects"]
        or expected_projection["transported_suspension_entries"] != 394
        or expected_projection["old_diagonal_suspension_cyclicity_defects"] != 8
        or expected_projection["raw_graph_suspension_cyclicity_residuals"] != 32
        or expected_projection["raw_second_chain_relation_residuals"] != 16
        or expected_projection["PBW_reduced_cyclicity_defects"]
    ):
        errors.append("graph exact inventory/replay")
    expected_green = {
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
    expected_common = {
        "result_id": common["result_id"], "status": common["result_state"],
        "carrier_rows": 386, "accepted_hashes": 13,
        "snapshot_sha256": common["common_snapshot"]["sha256"],
        "receiver_status": "ACCEPTED_SCOPED",
        "represented_green_actions_serialized": True,
        "classical_gate_a_passed": False,
        "gate_a_exports_required": 20, "gate_a_hashes_required": 7,
        "gate_a_freeze_checks_required": 10,
        "gate_a_hashes_accepted_by_scoped_result": 0,
        "missing_bundle_ids": [item["id"] for item in common["gate_v5_reconciliation"]["missing_bundle"]],
        "next_gate": common["next_gate"],
    }
    if value.get("strict_graph_green_action_name") != expected_green:
        errors.append("Green-action-name projection")
    if value.get("strict_unary_causal_common_snapshot") != expected_common:
        errors.append("unary-causal snapshot projection")
    if expected_green["spatial_spectral_branches"] != 3 or not expected_green["zero_mode_explicit"] or expected_green["plus_name_sha256"] == expected_green["minus_name_sha256"]:
        errors.append("Green spectral/sign inventory")
    if expected_green["effective_solver"] or expected_green["kernel_bytes"] or expected_common["classical_gate_a_passed"]:
        errors.append("analytic/Gate-A firewall")
    if expected_common["missing_bundle_ids"] != [
        "M1_COMMON_STRICT_SNAPSHOT", "M2_STRICT_Q2_D", "M3_RESIDUAL_SDR",
        "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES",
    ]:
        errors.append("Gate-V5 missing bundle")
    progress = value.get("strict_gate_a_progress", {})
    if (
        progress.get("status") != "UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED_FULL_GATE_A_Q2_D_RESIDUAL_BUNDLE_REQUIRED"
        or progress.get("graph_q1_sdr_component_jet_control") != expected_projection
        or progress.get("graph_green_action_name_control") != expected_green
        or progress.get("unary_causal_common_snapshot_control") != expected_common
    ):
        errors.append("Gate-A progress ledger")

    inherited = (
        "classical_import_reconciliation", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "strict_canonical_shear_component_jets", "berger_h26_c26_decision_chain",
    )
    for key in inherited:
        if value.get(key) != previous.get(key):
            errors.append("predecessor control mutation " + key)
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 9)):
        errors.append("graph-aware route ranking")
    expected_queue = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value.get("route_selection", [])
    ]
    if value.get("research_queue") != expected_queue:
        errors.append("research queue projection")

    atlas_flags = value.get("claim_flags", {})
    for key in (
        "v14_preserved", "strict_386_unshifted_graph_q1_snapshot_complete",
        "strict_386_unshifted_graph_sdr_snapshot_complete", "strict_386_graph_suspension_transported",
        "strict_386_represented_green_actions_serialized", "strict_386_unary_causal_common_snapshot_accepted",
    ):
        if atlas_flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "strict_386_effective_numeric_green_solver", "strict_386_distribution_kernel_bytes_serialized",
        "strict_pure_weyl_classical_gate_passed",
        "strict_386_local_d_certified", "strict_386_q2_green_compatibility_certified",
        "lorentzian_full_theory_certified",
    ):
        if atlas_flags.get(key) is not False:
            errors.append("claim promotion " + key)
    for key in (
        "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED", "STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED",
        "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED", "STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED",
        "STRICT_386_GRAPH_SDR_CYCLICITY_REPLAYED", "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED",
    ):
        if flags.get(key) is not True:
            errors.append("source positive flag " + key)
    for key in (
        "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED", "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY",
    ):
        if flags.get(key) is not False:
            errors.append("source downstream promotion " + key)
    for key in (
        "STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED",
        "STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED",
        "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED",
    ):
        if green.get("claim_flags", {}).get(key) is not True:
            errors.append("Green source positive flag " + key)
    for key in ("CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if common.get("claim_flags", {}).get(key) is not False:
            errors.append("common source downstream promotion " + key)

    expected_predecessor = {
        "result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)),
        "sha256": sha(PREDECESSOR), "preserved": True,
    }
    if value.get("predecessor") != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V14 atlas predecessor"},
        {"path": str(GREEN.relative_to(ROOT)), "sha256": sha(GREEN), "role": "represented endpoint and full graph Green-action names"},
        {"path": str(COMMON.relative_to(ROOT)), "sha256": sha(COMMON), "role": "receiver-accepted scoped unary-causal common snapshot"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    historical = {
        "quantum-weyl/classical_import/certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json",
        "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json",
        "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
    }
    for item in expected_inputs:
        path = ROOT / item["path"]
        if item["path"] in historical:
            if len(item["sha256"]) != 64:
                errors.append("historical repair provenance")
        elif not path.is_file() or sha(path) != item["sha256"]:
            errors.append("provenance " + item["path"])
    if digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 77 cells preserved; strict S0/S2 receive scoped unary-causal evidence")
        print("  - represented endpoint/full Green names and thirteen-hash snapshot project independently")
        print("  - Gate V5, effective solver, Hadamard and every quantum lifecycle remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
