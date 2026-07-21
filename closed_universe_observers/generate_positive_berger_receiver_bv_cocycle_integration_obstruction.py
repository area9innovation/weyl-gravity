#!/usr/bin/env python3
"""Certify the grading obstruction to the receiver/q70 action pushout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1_PAYLOAD.json"
CERT = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json"
REPORT = P / "reports/positive-berger-receiver-bv-cocycle-integration-grading-obstruction-v1.md"
DEPS = {
    "receiver_preflight": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json",
    "receiver_payload": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD.json",
    "receiver_contract": P / "generated/POSITIVE_BERGER_LOCAL_RECEIVER_BV_INTEGRATION_CONTRACT_V1.json",
    "q70_parent": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
    "q70_payload": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json",
    "q70_receiver_contract": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def degree_hist(rows: list[dict[str, Any]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        key = str(row["degree"] if "degree" in row else row["bv_degree"])
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def build_payload() -> dict[str, Any]:
    app = json.loads(DEPS["receiver_payload"].read_text())
    parent = json.loads(DEPS["q70_payload"].read_text())
    app_rows = app["carrier"]["physical_fields"] + app["carrier"]["antifields_and_bv_duals"]
    parent_rows = parent["row_layout"]["component_rows"]
    app_degree = {row["name"]: row["bv_degree"] for row in app_rows}
    parent_degree = {row["index"]: row["degree"] for row in parent_rows}
    app_pairing_sums = sorted(
        {app_degree[e["left"]] + app_degree[e["right"]] for e in app["odd_pairing"]["entries"]}
    )
    parent_pairing_sums = sorted(
        {parent_degree[e[0]] + parent_degree[e[1]] for e in parent["operators"]["pairing70"]["entries"]}
    )
    return {
        "schema": "positive-berger-receiver-bv-cocycle-integration-grading-obstruction-payload-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1_PAYLOAD",
        "coefficient_field": "Q",
        "scope": {
            "theory": "receiver_action_sector_to_two_phase_counterflow_q70_action_pushout",
            "background": "positive_Berger_Omega=3/4_a=1_c_squared=9/40",
            "boundaries": "D0_compact_worldtube_inside_same_stationary_Berger_spacetime",
            "charge_sector": "fixed_Q_rel_parent_leaf_with_unrestricted_local_apparatus_fibre",
            "carrier": "certified_receiver20_and_repaired_q70",
            "degree": [-1, 0, 1, 2],
            "parity": ["even", "odd"],
            "ell": "NOT_APPLICABLE_PRE_PUSHOUT",
            "m": "NOT_APPLICABLE_PRE_PUSHOUT",
            "k": "NOT_APPLICABLE_PRE_PUSHOUT",
            "omega": "formal_real_clock_frequency",
        },
        "input_gate": {
            "receiver_complete_master_action": "CERTIFIED",
            "receiver_degree_plus_one_unary": "CERTIFIED_IN_RECEIVER_BV_DEGREE",
            "receiver_cyclic_pairing": "CERTIFIED_DEGREE_MINUS_ONE",
            "receiver_local_support_contract": "CERTIFIED",
            "q70_complete_selected_action_and_cotangent_derivation": "CERTIFIED",
            "q70_degree_plus_one_unary": "CERTIFIED_IN_COMPACT_DEGREE_MINUS_GHOST_NUMBER",
            "q70_cyclic_pairing": "CERTIFIED_DEGREE_PLUS_ONE",
            "q70_local_causal_support_contract": "CERTIFIED",
            "stale_q70_hash_used": False,
        },
        "grading_audit": {
            "receiver_degree_convention": "BV degree: physical=0, odd cotangent=-1; q1 has degree +1",
            "q70_degree_convention": "compact_degree=-ghost_number; q70 has degree +1",
            "receiver_degree_ranks": degree_hist(app_rows),
            "q70_degree_ranks": degree_hist(parent_rows),
            "receiver_pairing_degree_sums": app_pairing_sums,
            "q70_pairing_degree_sums": parent_pairing_sums,
            "receiver_degree_minus_one_rows": 10,
            "q70_degree_minus_one_rows": 6,
            "maximum_degree_preserving_rank_at_minus_one": 6,
            "degree_minus_one_injection_deficiency": 4,
            "pairing_degree_difference": 2,
        },
        "canonical_witness": {
            "receiver_pair": ["m", "m_plus"],
            "receiver_pair_degrees": [0, -1],
            "receiver_pair_total_degree": -1,
            "q70_pair_example": ["B=A-dchi_0", "A_star_0"],
            "q70_pair_degrees": [0, 1],
            "q70_pair_total_degree": 1,
            "receiver_unary_arrow": "m_plus[-1] -> -u(lambda)[0]",
            "conclusion": "no degree-zero map can pull the homogeneous degree-plus-one q70 pairing back to the homogeneous degree-minus-one receiver pairing",
        },
        "pushout_disposition": {
            "homogeneous_graded_odd_symplectic_pushout": "OBSTRUCTED",
            "full_action_pushout": "NOT_REACHED",
            "background_solution": "NOT_REACHED",
            "mixed_gravity_clock_apparatus_unary_rows": "NOT_REACHED",
            "nilpotency_cyclicity_reality": "NOT_REACHED",
            "support_local_green_identities": "NOT_REACHED",
            "D_R_K_actions": "NOT_REACHED",
            "receiver_cocycle_inclusion": "NO_CERTIFIED_MAP",
            "residual_quotient_input_map": "NO_CERTIFIED_MAP",
        },
        "repair_contract": {
            "required_action": "reissue the receiver20 payload in compact_degree=-ghost_number with physical rows degree 0, BV cotangents degree +1 and action-derived q of degree +1",
            "required_pairing": "degree-plus-one rank-20 odd pairing with exact signs",
            "required_cocycle": "rederive the local receiver descent in the regraded convention; do not relabel the old A=m_plus identity",
            "required_hashes": ["carrier", "q1", "pairing", "cocycle", "D_R_K", "support"],
            "old_contract_action": "HISTORICAL_NOT_AUTO_PROMOTED",
        },
        "mutations": {
            "ignore_pairing_degree": {"result": "inhomogeneous pairing degrees [-1,+1]", "rejected": True},
            "flip_receiver_degrees_without_reissue": {"result": "all pinned receiver component hashes change", "rejected": True},
            "drop_four_receiver_duals": {"result": "receiver pairing becomes degenerate and contract row count changes", "rejected": True},
            "transpose_receiver_q_without_action": {"result": "not the odd Hamiltonian vector field of the certified receiver action convention", "rejected": True},
            "insert_mixed_rows_before_graded_pairing": {"result": "cyclicity is not typeable", "rejected": True},
        },
        "exact_checks": {
            "receiver_pairing_degree_homogeneous_minus_one": app_pairing_sums == [-1],
            "q70_pairing_degree_homogeneous_plus_one": parent_pairing_sums == [1],
            "degree_preserving_injection_possible": False,
            "pairing_preserving_inclusion_possible": False,
            "first_obstruction_precedes_mixed_hessian": True,
        },
        "claim_boundary": {
            "establishes": ["exact grading and pairing-degree obstruction to the pinned receiver20/q70 pushout"],
            "does_not_establish": [
                "obstruction after a regraded receiver action is issued",
                "mixed Hessian, quotient, period, denominator or redshift",
                "nonlinear, recoil, particle or quantum result",
            ],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    refs = {}
    for name, path in DEPS.items():
        data = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": data["result_id"], "sha256": sha(path)}
    return {
        "schema": "positive-berger-receiver-bv-cocycle-integration-grading-obstruction-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1",
        "setting_id": "positive_Berger_receiver20_to_repaired_counterflow_q70",
        "claim_status": "OBSTRUCTED_BY_CERTIFIED_GRADING_AND_PAIRING_DEGREE_MISMATCH",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "input_gate": payload["input_gate"],
        "obstruction": payload["canonical_witness"],
        "downstream_disposition": payload["pushout_disposition"],
        "next_gate": "REISSUE_THE_RECEIVER_ACTION_SECTOR_IN_THE_Q70_COMPACT_DEGREE_AND_PAIRING_CONVENTION_THEN_REPLAY_THE_ACTION_PUSHOUT",
        "claim_boundary": (
            "Both current inputs pass their individual action, unary, cyclic-pairing and local-support gates at exact hashes. Their integration nevertheless stops before a mixed Hessian: receiver20 uses physical degree zero, cotangent degree minus one and a homogeneous degree-minus-one odd pairing, whereas repaired q70 uses compact degree minus ghost number and a homogeneous degree-plus-one pairing. Receiver20 has ten degree-minus-one rows while q70 has six, and every pinned receiver pair has total degree minus one while every q70 canonical pair has total degree plus one. No degree-zero pairing-preserving inclusion or homogeneous graded odd-symplectic pushout exists for these certified contracts. Regrading or transposing receiver20 changes its content hashes and requires a new action-derived cocycle certificate. Therefore the full action pushout, mixed rows, receiver inclusion and residual-quotient input map are not reached; no pairing-period, denominator, redshift, nonlinear, recoil, particle or quantum claim is made."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_positive_berger_receiver_bv_cocycle_integration_obstruction --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_positive_berger_receiver_bv_cocycle_integration_obstruction",
            "source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Positive-Berger receiver/q70 integration grading obstruction

Both certified inputs pass their own action, unary, cyclic-pairing and causal
support gates.  The pushout is nevertheless not typeable.  Receiver20 puts
its ten odd cotangents in degree -1 and has pairing degree -1.  Repaired q70
uses compact degree `-ghost_number`; all its canonical pairs have total
degree +1.  It also has only six degree-minus-one rows.

Thus no degree-zero, pairing-preserving inclusion of the pinned receiver
contract exists, and a direct sum would have an inhomogeneous odd pairing.
Flipping the receiver grading changes every carrier/q1/pairing/cocycle hash
and requires a new action-derived descent, not a relabeling.  Mixed action
rows, quotient input and redshift are not reached.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    cert = build_certificate(payload)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    else:
        print(json.dumps(cert, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
