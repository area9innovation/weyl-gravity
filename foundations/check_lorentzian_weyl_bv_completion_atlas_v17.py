#!/usr/bin/env python3
"""Independently check atlas V17 and its authoritative-q2 frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Mapping[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge",
        "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization",
        "strict_operator_portability", "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "strict_canonical_shear_component_jets", "strict_graph_q1_sdr_component_jets",
        "strict_graph_green_action_name", "strict_unary_causal_common_snapshot",
        "strict_full_d_action", "strict_gate_v6_reconciliation", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    previous, preflight, gate = load(PREDECESSOR), load(PREFLIGHT), load(GATE)
    errors: list[str] = []
    if (
        value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17"
        or value.get("schema_version") != "foundational-lorentzian-weyl-bv-completion-atlas-v17"
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("predecessor", {}).get("result_id") != previous.get("result_id")
        or value.get("predecessor", {}).get("sha256") != sha(PREDECESSOR)
    ):
        errors.append("identity/predecessor/lifecycle")
    previous_grid = [(branch["id"], [item["stage"] for item in branch["stages"]]) for branch in previous.get("branches", [])]
    current_grid = [(branch["id"], [item["stage"] for item in branch["stages"]]) for branch in value.get("branches", [])]
    if current_grid != previous_grid or len(current_grid) != 7 or sum(len(stages) for _, stages in current_grid) != 77:
        errors.append("77-cell branch/stage preservation")
    q2 = value.get("strict_stabilized_q2_lift_preflight", {})
    dag = preflight["graph_transport_dag"]
    identities = preflight["identity_transport"]
    expected_q2 = {
        "result_id": preflight["result_id"], "carrier_rows": 386, "endpoint_rows": 30,
        "split_contractible_rows": 356, "minimal_primary_components": 12,
        "minimal_ordered_components": 22, "expanded_component_channels": 140,
        "unique_block_triples": 68, "input_row_envelope": 110,
        "output_row_envelope": 110, "interaction_inert_rows": 196,
        "q1_q2_defects": 0, "koszul_defects": 0, "cyclicity_defects": 0,
        "D_q2_defects": 0, "candidate_q2_sha256": preflight["canonical_hashes"]["graph_transport_dag_sha256"],
        "authoritative_full_q2_imported": False, "candidate_theory_identity_certified": False,
    }
    if any(q2.get(key) != expected for key, expected in expected_q2.items()):
        errors.append("q2 preflight projection")
    if (
        dag["expanded_ordered_component_channels"] != 140
        or identities["q1_q2_arity_two"]["defects"]
        or identities["q2_cyclicity"]["defects"]
        or identities["D_q2_derivation"]["derivation_defects"]
    ):
        errors.append("q2 source authority")
    projected_gate = value.get("strict_gate_v7_reconciliation", {})
    expected_gate = {
        "result_id": gate["result_id"], "exports_total": 20,
        "exports_receiver_verified_scoped": 11, "freeze_checks_total": 10,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_supporting_evidence_only": 1, "freeze_checks_blocked": 1,
        "accepted_top_level_hashes": 0, "gate_a_status": "FAIL_CLOSED",
        "candidate_q2_hash_accepted": False, "transitive_provenance_files_checked": 23,
        "transitive_provenance_drifted_files": 5,
    }
    if any(projected_gate.get(key) != expected for key, expected in expected_gate.items()):
        errors.append("Gate V7 projection")
    if gate["required_hash_disposition"]["q2_hash"]["accepted"] is not None:
        errors.append("source q2 hash unexpectedly accepted")

    routes = value.get("route_selection", [])
    expected_routes = [
        "STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_RESIDUAL_SDR_COMMON_CARRIER",
        "STRICT_FULL_CYCLIC_PAIRING", "STRICT_RESIDUAL_EXACT_PAYLOAD",
        "STRICT_CENTERED_REPRESENTATIVES", "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT",
    ]
    if [item.get("route") for item in routes] != expected_routes or [item.get("rank") for item in routes] != list(range(1, 9)):
        errors.append("route ranking")
    if value.get("research_queue") != [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in routes
    ]:
        errors.append("research queue")
    frontier = value.get("frontier_summary", {}).get("theory_identity_front", {})
    if frontier.get("first_gate") != "S0_CLASSICAL_AUTHORITY" or "source-certified" not in frontier.get("best_next_object", ""):
        errors.append("theory identity frontier")
    flags = value.get("claim_flags", {})
    for key in (
        "v16_preserved", "strict_386_stabilized_q2_candidate_certified",
        "strict_386_stabilized_q1_q2_identity_verified", "strict_386_stabilized_q2_cyclicity_verified",
        "strict_386_stabilized_d_q2_derivation_verified",
    ):
        if flags.get(key) is not True:
            errors.append("missing true flag " + key)
    for key in (
        "strict_386_authoritative_full_q2_imported", "strict_386_candidate_theory_identity_certified",
        "strict_386_full_carrier_q2_certified", "strict_386_d_q2_derivation_replayed",
        "strict_pure_weyl_classical_gate_passed", "berger_brst_hadamard_state_constructed",
        "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored",
        "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
    ):
        if flags.get(key) is not False:
            errors.append("promotion flag " + key)
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(previous["provenance"]["inputs"]) + 3:
        errors.append("provenance count")
    else:
        for item, path in zip(provenance[-3:], (PREDECESSOR, PREFLIGHT, GATE), strict=True):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
                errors.append("direct provenance " + str(path))
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 77 cells preserved and the exact stabilized q2 projection replays")
        print("  - first route is now authoritative q2 theory identity, not algebraic q2 invention")
        print("  - Gate A, Hadamard, QME and residual transfer remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
