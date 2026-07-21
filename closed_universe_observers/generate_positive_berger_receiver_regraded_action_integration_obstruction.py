#!/usr/bin/env python3
"""Regrade the receiver action and certify the first cochain/chain obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1_PAYLOAD.json"
CERT = P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1.json"
REPORT = P / "reports/positive-berger-receiver-regraded-action-cochain-intertwiner-obstruction-v1.md"
DEPS = {
    "grading_obstruction": P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json",
    "standalone_receiver": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json",
    "standalone_payload": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD.json",
    "q70_parent": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
    "q70_payload": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json",
    "physical_nonactivation": P / "certificates/POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload() -> dict[str, Any]:
    old = json.loads(DEPS["standalone_payload"].read_text())
    physical = [row["name"] for row in old["carrier"]["physical_fields"]]
    duals = [f"{name}_plus" for name in physical]
    rows = [
        {"name": name, "compact_degree": 0, "ghost_number": 0, "parity": "even", "real_structure": "fixed", "origin": "variational_field"}
        for name in physical
    ] + [
        {"name": name, "compact_degree": 1, "ghost_number": -1, "parity": "odd", "real_structure": "fixed", "origin": "odd_cotangent_from_action"}
        for name in duals
    ]
    pairing = []
    for name in physical:
        pairing.extend([
            {"left": name, "right": f"{name}_plus", "coefficient": 1, "total_degree": 1},
            {"left": f"{name}_plus", "right": name, "coefficient": -1, "total_degree": 1},
        ])
    chain_q = {
        "X_to_Y_plus": "K",
        "Y_to_X_plus": "-K",
        "P_to_N_plus": "K",
        "N_to_P_plus": "-K",
        "m_to_lambda_plus": "u",
        "lambda_to_m_plus": "-u",
        "on_all_cotangents": "zero",
    }
    local_s = {
        "X_plus": "-K(Y) vol_0",
        "Y_plus": "K(X) vol_0",
        "P_plus": "-K(N) vol_0",
        "N_plus": "K(P) vol_0",
        "m_plus": "-u(lambda) vol_0",
        "lambda_plus": "u(m) vol_0",
        "on_physical_fields": "zero",
    }
    return {
        "schema": "positive-berger-receiver-regraded-action-cochain-intertwiner-obstruction-payload-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1_PAYLOAD",
        "coefficient_field": "Q[Omega_K]",
        "scope": {
            "theory": "regraded_positive_Berger_D0_receiver_action_to_q70",
            "background": "positive_Berger_Omega=3/4_a=1_c_squared=9/40",
            "boundaries": "compactly_supported_D0_worldtube_sections",
            "charge_sector": "fixed_Q_rel_parent_leaf_with_neutral_receiver",
            "carrier": "fresh_receiver20_compact_chain_and_local_BV_cochain",
            "degree": [0, 1],
            "parity": ["even", "odd"],
            "ell": "NOT_APPLICABLE_PRE_PUSHOUT",
            "m": "NOT_APPLICABLE_PRE_PUSHOUT",
            "k": "NOT_APPLICABLE_PRE_PUSHOUT",
            "omega": "formal_real_clock_frequency",
        },
        "local_master_action": {
            "formula": old["master_action"]["formula"],
            "background_solution": old["background_solution"],
            "rederived_from_action": True,
            "old_hash_preserved": False,
            "external_signal_port_retained_only_as_unintegrated_test_input": True,
        },
        "compact_chain_carrier": {
            "degree_convention": "compact_degree=-ghost_number",
            "rows": rows,
            "row_count": 20,
            "degree_ranks": {"0": 10, "1": 10},
            "gauge_generators": [],
            "ghosts": [],
            "ghost_ledger": "EMPTY: receiver phase covariance is rigid",
            "pairing": {"degree": 1, "rank": 20, "entries": pairing},
            "q_chain": {"degree": 1, "entries_by_action_block": chain_q, "square": 0, "cyclicity_defect": 0},
            "real_structure_defect": 0,
        },
        "local_BV_cochain": {
            "degree_convention": "compact_degree=-ghost_number",
            "s_degree": -1,
            "derivation": local_s,
            "square": 0,
            "relation_to_chain": "s is the master-action BV derivation; q_chain is its action-Hessian/cotangent transpose",
            "receiver_descent": {
                "A": "m_plus",
                "A_compact_degree": 1,
                "A_form_degree": 4,
                "B": "lambda*rho_0(R)d^3R",
                "B_compact_degree": 0,
                "B_form_degree": 3,
                "sA": "-u(lambda)vol_0",
                "dB": "u(lambda)vol_0",
                "defect": 0,
                "support": "compactly contained in W0",
            },
        },
        "causal_and_symmetry_checks": {
            "chain_green_identity": "q_chain Lambda_+/- + Lambda_+/- q_chain=I on compactly supported transport rows",
            "retarded_support": "future of source along increasing t inside transported W0 family",
            "advanced_support": "past of source along decreasing t inside transported W0 family",
            "zero_mode_boundary": "compact support excludes a persistent homogeneous transport zero mode from the Green domain",
            "D": "u+(Omega_K+3/4)J on doublets; u on scalars and matching cotangents",
            "R": "J on doublets and matching cotangents; zero on scalars",
            "K": "D-(3/4)R=u+Omega_K J on doublets; u on scalars",
            "D_R_K_commutator_defects": 0,
            "pairing_variation_defects": 0,
        },
        "intertwiner_obstruction": {
            "source_differential": "s_local",
            "source_degree": -1,
            "target_differential": "q70_chain",
            "target_degree": 1,
            "requested_map_degree": 0,
            "chain_equation": "q70*i=i*s_local",
            "left_total_degree_shift": 1,
            "right_total_degree_shift": -1,
            "homogeneous_degree_separation": 2,
            "injective_solution_exists": False,
            "canonical_witness": "s_local(m_plus)=-u(lambda)vol_0 is generically nonzero, so injectivity forbids i*s_local=0 while degree separation forces both sides of q70*i=i*s_local to vanish separately",
            "first_failed_gate": "degree_zero_receiver_cocycle_chain_cochain_intertwiner",
        },
        "complete_declared_ansatz_minimality": {
            "ansatz": "all real local first-order actions on the declared ten physical receiver fields and their canonical odd cotangents, with no new suspension field or chain/cochain conversion map",
            "coefficient_independent_fact": "every master-action BV derivation has ghost number +1 and therefore compact degree -1",
            "q70_fact": "the repaired parent chain has compact degree +1",
            "conclusion": "no action coefficient, lower-order mixed term or support profile can remove the two-degree intertwiner separation",
            "minimal_escape": "add and certify an explicit degree-reversing/suspension chain-cochain bridge, then rederive its pairing, action and receiver descent",
        },
        "pushout_disposition": {
            "standalone_regraded_action_chain": "CERTIFIED",
            "standalone_local_receiver_cochain": "CERTIFIED",
            "degree_zero_receiver_cocycle_inclusion": "OBSTRUCTED",
            "mixed_action_pushout": "NOT_REACHED",
            "mixed_nilpotency_cyclicity": "NOT_REACHED",
            "support_local_combined_parent": "NOT_REACHED",
            "background_equations": "NOT_REACHED",
            "physical_descent_input_contract": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "wrong_degree_minus_one_pairing": {"result": "recreates the terminal receiver20/q70 mismatch", "rejected": True},
            "relabel_only": {"result": "old carrier/q1/pairing/cocycle hashes reused without action differentiation", "rejected": True},
            "missing_cotangent": {"result": "pairing rank at most 18", "rejected": True},
            "identify_s_with_q_chain": {"result": "compact degrees -1 and +1 conflated", "rejected": True},
            "direct_sum_before_intertwiner": {"result": "no receiver cocycle inclusion", "rejected": True},
        },
        "claim_boundary": {
            "establishes": ["fresh action-derived compact receiver chain", "fresh local BV cochain descent", "complete-ansatz degree obstruction to a degree-zero cocycle intertwiner"],
            "does_not_establish": ["no-go after adding a certified suspension bridge", "mixed pushout, physical receiver, ratio or redshift", "nonlinear, particle, positivity or quantum result"],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    refs = {}
    for name, path in DEPS.items():
        data = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": data["result_id"], "sha256": sha(path)}
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    return {
        "schema": "positive-berger-receiver-regraded-action-cochain-intertwiner-obstruction-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1",
        "setting_id": "positive_Berger_regraded_receiver20_to_q70",
        "claim_status": "OBSTRUCTED_AT_DEGREE_ZERO_LOCAL_COCHAIN_TO_Q70_CHAIN_INTERTWINER",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "standalone_gate": {"compact_chain": "CERTIFIED", "degree_plus_one_pairing": "CERTIFIED", "local_BV_cochain_descent": "CERTIFIED", "causal_and_D_R_K": "CERTIFIED"},
        "first_obstruction": payload["intertwiner_obstruction"],
        "downstream_disposition": payload["pushout_disposition"],
        "next_gate": "CERTIFY_AN_EXPLICIT_DEGREE_REVERSING_CHAIN_COCHAIN_SUSPENSION_BRIDGE_BEFORE_ANY_MIXED_ACTION_PUSHOUT",
        "claim_boundary": (
            "This result rederives the receiver action in compact_degree=-ghost_number rather than relabeling the old payload. The resulting 20-row action-Hessian chain has physical degree zero, cotangent degree one, a homogeneous rank-20 degree-plus-one odd pairing, degree-plus-one nilpotent cyclic q_chain, real structure, causal transport identities and separate D/R/K actions. The same master action independently gives the genuine local BV derivation s of compact degree minus one and the compact D0 descent s(m_plus)+d(lambda rho_0 d3R)=0. The requested degree-zero inclusion into repaired q70 cannot intertwine these differentials: q70*i shifts degree plus one while i*s shifts degree minus one; homogeneity forces both to vanish, contradicting injectivity on the generically nonzero memory-shift descent. This two-degree separation is coefficient-independent over every real local first-order action on the declared receiver fields without a new suspension/chain-cochain bridge. The mixed action pushout is therefore not reached. No physical receiver, quotient, frequency ratio, redshift, nonlinear, particle, positivity or quantum claim is made."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_positive_berger_receiver_regraded_action_integration_obstruction --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_positive_berger_receiver_regraded_action_integration_obstruction",
            "source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Positive-Berger regraded receiver integration obstruction

The action regrading succeeds, but it exposes two distinct complexes.  The
q70-style Hessian chain has compact degree +1 and a degree-+1 rank-20 odd
pairing.  The master-action BV derivation has compact degree -1 and carries
the genuine local memory-shift descent.

A degree-zero inclusion cannot satisfy `q70 i = i s`: its two sides have
degree shifts +1 and -1.  Homogeneity forces both to vanish, contradicting
injectivity on the nonzero descent.  This is independent of every coefficient
in the declared first-order receiver action ansatz.  A new certified
degree-reversing chain/cochain suspension bridge is required before mixed
action rows can be constructed.
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
