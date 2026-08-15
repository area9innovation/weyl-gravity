#!/usr/bin/env python3
"""Independent structural and claim-boundary checker for atlas V16."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15.json"
FULL_D = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_D_ACTION_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
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
    "STRICT_386_Q2_D_COMMON_CARRIER", "STRICT_FULL_CYCLIC_PAIRING",
    "STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_RESIDUAL_EXACT_PAYLOAD",
    "STRICT_CENTERED_REPRESENTATIVES", "DIRECT_SPACETIME_Q26_HADAMARD",
    "STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT", "STRICT_D_CARTAN_AND_CHARGE_DECISION",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge",
        "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization",
        "strict_operator_portability", "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "strict_canonical_shear_component_jets", "strict_graph_q1_sdr_component_jets",
        "strict_graph_green_action_name", "strict_unary_causal_common_snapshot",
        "strict_full_d_action", "strict_gate_v6_reconciliation", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    previous, full_d, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, FULL_D, GATE))
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v16"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if [item.get("id") for item in value.get("stages", [])] != STAGES:
        errors.append("stage axis identity/order")
    if [item.get("id") for item in value.get("branches", [])] != BRANCHES:
        errors.append("branch axis identity/order")
    branches = {item.get("id"): item for item in value.get("branches", [])}
    old_branches = {item.get("id"): item for item in previous.get("branches", [])}
    for branch_id, branch in branches.items():
        if len(branch.get("stages", [])) != 11:
            errors.append("stage closure " + str(branch_id))
        if branch_id != "STRICT_PURE_WEYL_386" and branch != old_branches.get(branch_id):
            errors.append("unlicensed branch mutation " + str(branch_id))
    strict = branches.get("STRICT_PURE_WEYL_386", {})
    old_strict = old_branches.get("STRICT_PURE_WEYL_386", {})
    cells = {item.get("stage"): item for item in strict.get("stages", [])}
    old_cells = {item.get("stage"): item for item in old_strict.get("stages", [])}
    if strict.get("first_unclosed_gate") != "S0_CLASSICAL_AUTHORITY" or cells.get("S0_CLASSICAL_AUTHORITY", {}).get("status") != "FAIL_CLOSED":
        errors.append("Gate-A firewall")
    for stage_id in STAGES[1:]:
        if cells.get(stage_id) != old_cells.get(stage_id):
            errors.append("unlicensed strict stage mutation " + stage_id)
    for key in set(old_strict) - {"stages", "next_decisive_object"}:
        if strict.get(key) != old_strict.get(key):
            errors.append("unlicensed strict branch mutation " + key)
    expected_s0_evidence = [*old_cells["S0_CLASSICAL_AUTHORITY"]["evidence"], full_d["result_id"], gate["result_id"]]
    if cells.get("S0_CLASSICAL_AUTHORITY", {}).get("evidence") != expected_s0_evidence:
        errors.append("strict S0 evidence augmentation")

    replay = full_d["exact_replay"]
    expected_d = {
        "result_id": full_d["result_id"], "status": full_d["result_state"],
        "selected_real_generator": full_d["generator_selection"]["selected_real_generator"],
        "hermitian_mode_convention": full_d["D_action"]["hermitian_mode_convention"],
        "carrier_rows": 386, "component_blocks": 22, "D_coefficients": 386,
        "temporal_multiindex": [1, 0, 0, 0], "q1_tables_checked": 27,
        "q1_multiindices_checked": 70, "q1_coefficients_checked": 4374,
        "D_q1_commutator_defects": replay["D_q1_commutator_defects"],
        "pairing_entries_checked": 410, "formal_skew_adjoint_defects": replay["formal_skew_adjoint_defects"],
        "scoped_snapshot_hashes": 14, "D_action_sha256": full_d["canonical_hashes"]["D_action_sha256"],
        "full_q2_common_snapshot": False, "D_q2_derivation": False, "D_gauge_or_charge_decided": False,
        "next_gate": full_d["next_gate"],
    }
    if value.get("strict_full_d_action") != expected_d:
        errors.append("full D projection")
    if expected_d["D_q1_commutator_defects"] or expected_d["formal_skew_adjoint_defects"]:
        errors.append("full D exact replay")
    expected_gate = {
        "result_id": gate["result_id"], "status": gate["result_state"],
        "exports_total": 20, "exports_receiver_verified_scoped": 11,
        "freeze_checks_total": 10, "freeze_checks_receiver_verified_scoped": 8,
        "accepted_top_level_hashes": 0, "gate_a_status": "FAIL_CLOSED",
        "D_candidate_hash_accepted": False,
        "transitive_provenance_files_checked": gate["transitive_provenance_drift"]["files_checked"],
        "transitive_provenance_drifted_files": gate["transitive_provenance_drift"]["drifted_files"],
        "missing_bundle_ids": [item["id"] for item in gate["minimal_missing_bundle"]],
        "next_gate": gate["next_gate"],
    }
    if value.get("strict_gate_v6_reconciliation") != expected_gate:
        errors.append("Gate V6 projection")
    if expected_gate["transitive_provenance_drifted_files"] != 5:
        errors.append("Gate V6 drift count")
    if expected_gate["missing_bundle_ids"] != [
        "M1_COMMON_STRICT_SNAPSHOT", "M2_STRICT_Q2_D", "M3_RESIDUAL_SDR",
        "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES",
    ]:
        errors.append("Gate V6 missing bundle")

    inherited = (
        "classical_import_reconciliation", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge",
        "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair", "strict_full_q1_component_jet_table",
        "strict_local_sdr_component_maps", "strict_canonical_shear_component_jets",
        "strict_graph_q1_sdr_component_jets", "strict_graph_green_action_name",
        "strict_unary_causal_common_snapshot", "berger_h26_c26_decision_chain",
    )
    for key in inherited:
        if value.get(key) != previous.get(key):
            errors.append("predecessor control mutation " + key)
    progress = value.get("strict_gate_a_progress", {})
    expected_progress = dict(previous["strict_gate_a_progress"])
    expected_progress.update({
        "status": "UNARY_CAUSAL_D_COMMON_SNAPSHOT_ACCEPTED_FULL_Q2_AND_GATE_BUNDLES_REQUIRED",
        "full_d_action_control": expected_d, "gate_v6_reconciliation_control": expected_gate,
        "remaining_common_carrier": full_d["next_gate"],
        "boundary": "The scoped snapshot now includes D and D/q1, but Gate V6 accepts zero top-level hashes. Full-carrier q2/D-q2, residual SDR, full cyclic pairing, residual representation data and centered representatives remain independent required bundles.",
    })
    if progress != expected_progress:
        errors.append("Gate-A progress ledger")
    if [item.get("route") for item in value.get("route_selection", [])] != ROUTES or [item.get("rank") for item in value.get("route_selection", [])] != list(range(1, 9)):
        errors.append("route ranking")
    expected_queue = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value.get("route_selection", [])]
    if value.get("research_queue") != expected_queue:
        errors.append("research queue projection")

    flags = value.get("claim_flags", {})
    for key in (
        "v15_preserved", "strict_386_full_local_d_action_certified",
        "strict_386_d_q1_commutator_replayed", "strict_386_d_formal_skew_adjoint_replayed",
        "strict_386_unary_causal_d_scoped_snapshot_accepted",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "strict_386_full_carrier_q2_certified", "strict_386_d_q2_derivation_replayed",
        "strict_386_d_cartan_homotopy_constructed", "strict_d_gauge_or_charge_decided",
        "strict_pure_weyl_classical_gate_passed", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    if not all(full_d["claim_flags"].get(key) is True for key in (
        "STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED", "STRICT_386_D_Q1_COMMUTATOR_REPLAYED",
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED",
    )):
        errors.append("full D source positive flags")
    if any(full_d["claim_flags"].get(key) is not False for key in (
        "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT", "STRICT_386_D_Q2_DERIVATION_REPLAYED",
        "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY",
    )):
        errors.append("full D source promotion")
    if gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED" or gate["gate_disposition"]["accepted_common_snapshot_hashes"] != 0:
        errors.append("Gate source promotion")

    expected_predecessor = {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True}
    if value.get("predecessor") != expected_predecessor:
        errors.append("predecessor")
    expected_inputs = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V15 atlas predecessor"},
        {"path": str(FULL_D.relative_to(ROOT)), "sha256": sha(FULL_D), "role": "strict full cylinder D action and D/q1 replay"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "Gate-A V6 scoped D reconciliation and provenance drift ledger"},
    ]
    if value.get("provenance", {}).get("inputs") != expected_inputs:
        errors.append("append-only provenance")
    for item in expected_inputs[-3:]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append("direct provenance " + item["path"])
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 77 cells preserved; strict S0 receives full-D/Gate-V6 evidence")
        print("  - 386 D rows, 4,374 q1 coefficients and 410 pairing entries replay exactly")
        print("  - full-carrier q2, D/q2, Gate A and every quantum lifecycle remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
