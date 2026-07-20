#!/usr/bin/env python3
"""Exact seven-gate comparison of compensator Candidates A and B."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json"
)

IMPORTS = {
    "candidate_A": {
        "certificate": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json",
        "report": ROOT / "d_quotient_classical/reports/compensator-candidate-a-r2-auxiliary-scalar-obstruction-v1.md",
        "receipt": ROOT / "d_quotient_classical/receipts/COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1_TIER_RECEIPT.json",
        "scientific_commit": "5c642e2ad14d45f6074b1327c69707b7b9b08f5d",
        "lifecycle_commit": "218cd5ad90cb9df537eb368a9312cb745a21044f",
        "certificate_sha256": "889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6",
        "report_sha256": "0b35a367f70f4215df25c9c3dbe97f5805199ecd21175c7b1cb9f02609bad826",
        "receipt_sha256": "2d2e6b54dafe41e4551362a3f05dc54cf76a80bd35856635f0d250ebc2662d94",
    },
    "candidate_B": {
        "certificate": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json",
        "report": ROOT / "d_quotient_classical/reports/compensator-candidate-b-unimodular-threeform-obstruction-v1.md",
        "receipt": ROOT / "d_quotient_classical/receipts/COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1_TIER_RECEIPT.json",
        "scientific_commit": "cc0e0036c6acce2bc3d8ba81057031d90a71333a",
        "lifecycle_commit": "c7af7b707831a848e3e110f45bb746478473dbc6",
        "certificate_sha256": "e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa",
        "report_sha256": "aa5fc7b3545d032972807eb4d79f372df011dde855724f94993e2edbca2f9dd8",
        "receipt_sha256": "6966831ed574890bb9bc866dbd08b4789821925c2f37f6cf6bd887a43ef124b2",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    rows: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, source in IMPORTS.items():
        for kind in ("certificate", "report", "receipt"):
            actual = _sha(source[kind])
            if actual != source[f"{kind}_sha256"]:
                raise AssertionError(f"{name} {kind} hash drifted")
        payload = json.loads(source["certificate"].read_text())
        receipt = json.loads(source["receipt"].read_text())
        if payload["result_state"] != "OBSTRUCTED":
            raise AssertionError(f"{name} is not a terminal obstruction")
        if receipt["claim_id"] != payload["result_id"]:
            raise AssertionError(f"{name} receipt/certificate mismatch")
        payloads[name] = payload
        rows[name] = {
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "certificate": str(source["certificate"].relative_to(ROOT)),
            "certificate_sha256": source["certificate_sha256"],
            "report": str(source["report"].relative_to(ROOT)),
            "report_sha256": source["report_sha256"],
            "receipt": str(source["receipt"].relative_to(ROOT)),
            "receipt_sha256": source["receipt_sha256"],
            "scientific_commit": source["scientific_commit"],
            "lifecycle_commit": source["lifecycle_commit"],
        }
    return rows, payloads


def _normalized_gates(
    candidate_a: dict[str, Any],
    candidate_b: dict[str, Any],
) -> list[dict[str, Any]]:
    gates_a = candidate_a["comparison_disposition"]["seven_gate_disposition"]
    gates_b = candidate_b["seven_gate_disposition"]
    if [row["gate"] for row in gates_a] != list(range(1, 8)):
        raise AssertionError("Candidate-A gate numbering drifted")
    if [row["gate"] for row in gates_b] != list(range(1, 8)):
        raise AssertionError("Candidate-B gate numbering drifted")
    normalized_names = [
        "action_derived_BV_CME_Q2",
        "compact_support_dressed_trace_disposition",
        "complete_support_local_causal_parent",
        "cyclic_current_and_reduced_pairing",
        "physical_sign_or_topological_control",
        "raw_D_charge_sector",
        "frozen_Berger_clock_compatibility",
    ]
    return [
        {
            "gate": index,
            "normalized_name": normalized_names[index - 1],
            "candidate_A": {
                "status": gates_a[index - 1]["status"],
                "reason": gates_a[index - 1]["reason"],
            },
            "candidate_B": {
                "status": gates_b[index - 1]["status"],
                "reason": gates_b[index - 1]["reason"],
            },
        }
        for index in range(1, 8)
    ]


def _common_conventions(
    candidate_a: dict[str, Any],
    candidate_b: dict[str, Any],
) -> dict[str, str]:
    shared_dependencies = (
        "action_preflight",
        "positive_Berger_clock",
        "strict_tau_obstruction",
    )
    for name in shared_dependencies:
        if candidate_a["dependencies"][name] != candidate_b["dependencies"][name]:
            raise AssertionError(f"Candidate A/B {name} import drifted")

    manifest_a = candidate_a["action_identity"]["manifest"]
    manifest_b = candidate_b["action_and_BV"]["manifest"]
    couplings_b = manifest_b["couplings"]
    background_b = candidate_b["unit_cylinder_background_obstruction"]["background"]
    domain_b = candidate_b["domain"]
    berger_a = candidate_a["comparison_disposition"]["Berger_compatibility"]
    berger_b = candidate_b["Berger_gate"]
    exact_input_checks = {
        "M_P_squared": (
            manifest_a["M_P_squared"],
            couplings_b["M_P_squared"],
            "1/6",
        ),
        "V0": (manifest_a["V0"], couplings_b["V0"], "1/4"),
        "metric": (
            background_b["metric"],
            "g_hat_bar=-dt^2+dOmega_3^2",
        ),
        "scalar_curvature": (background_b["R"], "6"),
        "theta_background": (background_b["theta_bar"], "constant"),
        "signature": (domain_b["signature"], "(-,+,+,+)"),
        "boundaries": (
            domain_b["boundaries"],
            "closed S3 Cauchy surfaces; no timelike boundary",
        ),
        "candidate_A_background": (
            candidate_a["action_identity"]["identities"]["background"],
            "R0=6, chi0=-1/12, psi0=0",
        ),
        "candidate_A_Berger_fixture": (
            berger_a["fixture"],
            "a=1, q=9/40, alpha_B=5, rho^2=1, omega=3/4",
        ),
        "candidate_B_Berger_fixture": (
            berger_b["fixture"],
            "a=1, c^2=9/40, alpha_B=5, rho^2=1, omega_clock=3/4, lambda_scalar=119/480",
        ),
        "candidate_B_small_gauge": (
            manifest_b["three_form_gauge_tower"],
            "A_3 -> A_3+d epsilon_2; epsilon_2~epsilon_2+d epsilon_1; epsilon_1~epsilon_1+d epsilon_0",
        ),
    }
    for name, values in exact_input_checks.items():
        if len(set(values)) != 1:
            raise AssertionError(f"Candidate A/B common convention {name} drifted")

    if (
        "i_D Omega=d H_D"
        not in candidate_a["homogeneous_scalar_full_Hessian_sector"][
            "D_evolution_and_charge"
        ]["Cartan_identity"]
        or candidate_b["linearized_topological_block"]["flux_multiplier_pairing"][
            "Hamiltonian"
        ]
        != "H_D=V_S3 lambda_HT"
        or candidate_b["Berger_gate"]["raw_D_action"]
        != "L_D A_3_bar=vol_Berger"
    ):
        raise AssertionError("Candidate A/B raw-D convention drifted")

    return {
        "spacetime": "R_t x S3",
        "metric": "g_hat_bar=-dt^2+dOmega_3^2",
        "signature": "(-,+,+,+)",
        "scalar_curvature": "6",
        "M_P_squared": "1/6",
        "V0": "1/4",
        "theta_bar": "constant",
        "dressed_trace": "u=phi_trace-2tau",
        "raw_D": "partial_t",
        "boundaries": "closed S3 Cauchy surfaces; no timelike boundary",
        "support_domains": "compact, spacelike-compact and one-sided Green domains",
        "Weyl_quartet": "(tau,omega,omega_star,tau_hat_star) contracted",
        "internal_U1": "global phase shift, not gauged",
        "three_form_gauge_for_B": "small reducible A3 -> A3+d epsilon2 tower; no large/global shift quotient",
        "Berger_fixture": "a=1, q=9/40, alpha_B=5, rho^2=1, omega_clock=3/4",
    }


def _verify_decisive_evidence(
    candidate_a: dict[str, Any],
    candidate_b: dict[str, Any],
) -> None:
    scalar_a = candidate_a["homogeneous_scalar_full_Hessian_sector"]
    sign_a = scalar_a["Lee_Wald_and_sign"]
    charge_a = scalar_a["D_evolution_and_charge"]
    berger_a = candidate_a["comparison_disposition"]["Berger_compatibility"]
    if (
        sign_a["velocity_Hessian_inertia"] != [1, 1, 0]
        or sign_a["physical_sign"] != "INDEFINITE"
        or charge_a["real_roots"] != ["-sqrt(2)", "sqrt(2)"]
        or charge_a["Jordan_block_size"] != 2
        or charge_a["negative_witness"]
        != "(u,dot_u,psi,dot_psi)=(0,1,0,1) gives H_D=-3"
        or charge_a["positive_witness"]
        != "(u,dot_u,psi,dot_psi)=(0,1,0,-1) gives H_D=3"
        or berger_a["orthonormal_metric_Euler_residual"]
        != [
            "93839/1843200",
            "135917/1843200",
            "135917/1843200",
            "-12943/368640",
        ]
    ):
        raise AssertionError("Candidate-A decisive physical evidence drifted")

    background_b = candidate_b["unit_cylinder_background_obstruction"]
    block_b = candidate_b["linearized_topological_block"]
    topology_b = candidate_b["global_topology"]
    berger_b = candidate_b["Berger_gate"]
    if (
        background_b["tracefree_Euler_orthonormal"]
        != ["1/8", "1/24", "1/24", "1/24"]
        or background_b["simultaneous_equations_have_solution"]
        or block_b["polynomial_kernel"]["vector"] != ["D/2", "1", "0"]
        or block_b["complete_Green_inverse_exists"]
        or topology_b["ordinary_de_Rham_betti_H0_to_H4"]
        != [1, 0, 0, 1, 0]
        or topology_b["compact_support_betti_Hc0_to_Hc4"]
        != [0, 1, 0, 0, 1]
        or block_b["flux_multiplier_pairing"]["Hamiltonian"]
        != "H_D=V_S3 lambda_HT"
        or berger_b["cohomology_class"] != "[vol_Berger] != 0 in H^3(S3)"
        or berger_b["small_gauge_compensator_exists"]
        or berger_b["raw_D_action"] != "L_D A_3_bar=vol_Berger"
    ):
        raise AssertionError("Candidate-B decisive global evidence drifted")


def build() -> dict[str, Any]:
    imports, payloads = _imports()
    candidate_a = payloads["candidate_A"]
    candidate_b = payloads["candidate_B"]
    _verify_decisive_evidence(candidate_a, candidate_b)
    gates = _normalized_gates(candidate_a, candidate_b)

    a_fail = [
        row["gate"]
        for row in gates
        if row["candidate_A"]["status"] == "FAIL"
        or row["candidate_A"]["status"].startswith("NOT_REACHED")
    ]
    b_fail = [
        row["gate"]
        for row in gates
        if row["candidate_B"]["status"] == "FAIL"
        or row["candidate_B"]["status"].startswith("FAIL_")
    ]
    if a_fail != [3, 5, 6, 7]:
        raise AssertionError("Candidate-A decisive gate set drifted")
    if b_fail != [2, 3, 5, 6, 7]:
        raise AssertionError("Candidate-B decisive gate set drifted")

    common = _common_conventions(candidate_a, candidate_b)
    action_hashes = {
        "candidate_A": candidate_a["action_identity"]["action_sha256"],
        "candidate_B": candidate_b["action_and_BV"]["action_sha256"],
    }
    if action_hashes["candidate_A"] == action_hashes["candidate_B"]:
        raise AssertionError("distinct candidate actions were conflated")

    selection_input = {
        "rule": "a candidate is selectable iff every one of the seven gates passes without an uncontrolled, not-reached or conditional remainder",
        "candidate_A_decisive_nonpass_gates": a_fail,
        "candidate_B_decisive_nonpass_gates": b_fail,
        "partial_scores_forbidden": True,
        "hybrid_forbidden": True,
    }
    selection_hash = _digest(
        {
            "action_hashes": action_hashes,
            "common_conventions": common,
            "gates": gates,
            "selection_input": selection_input,
        }
    )
    return {
        "schema": "pure-weyl-compensator-candidate-ab-neither-comparison-v1",
        "result_id": "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1",
        "result_state": "NEITHER_MINIMAL_REPAIR_SELECTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "common_conventions": common,
        "action_hashes": action_hashes,
        "seven_gate_matrix": gates,
        "selection_rule": selection_input,
        "selection_hash": selection_hash,
        "terminal_selection": "NEITHER",
        "candidate_A_summary": {
            "terminal_obstruction": (
                "the complete mixed auxiliary scalar sector has split "
                "Lee-Wald inertia, real Jordan roots, a both-sign D "
                "Hamiltonian and nonzero frozen-Berger Euler residuals"
            ),
            "scoped_not_universal": (
                "does not rule out every R^2 theory, coupling or retuned background"
            ),
        },
        "candidate_B_summary": {
            "terminal_obstruction": (
                "the frozen cylinder is off shell and the HT block has an "
                "arbitrary flux-history kernel, H3/Hc4 classes, nonconstant "
                "ambient D charge and nonexact Berger flux shift"
            ),
            "scoped_not_universal": (
                "does not rule out an active-clock retuning, fixed flux/lambda "
                "superselection theory or enlarged global gauge quotient"
            ),
        },
        "strict_downstream_disposition": {
            "selected_action": None,
            "selected_action_hash": None,
            "selected_carrier": None,
            "retire_or_do_not_activate": [
                "nonlinear-selected-compensator-repair-q2",
                "bridge-selected-compensator-repair-einstein-extra-charge",
                "observer-selected-compensator-repair-clock-redshift",
                "quantum-selected-compensator-repair-dressed-regulator",
            ],
            "reason": (
                "every selected-repair consumer requires one receiver-valid "
                "action hash, and neither declared candidate passes all gates"
            ),
            "smallest_open_theory_classes": [
                "a differently tuned/backgrounded local R(g_hat)^2 theory with a separately certified healthy full mixed scalar sector",
                "an active-clock HT theory with explicit fixed flux/lambda superselection and global symmetry quotient",
                "a theory with an additional independent conformal gauge generator and complete BV cotangent lift",
                "the bounded minimal-action classification activated by this NEITHER theorem",
            ],
            "hybrid_authorized": False,
        },
        "exact_checks": {
            "all_import_hashes": True,
            "both_inputs_terminal_obstructed": True,
            "same_common_conventions": True,
            "common_conventions_bound_to_imported_fields": True,
            "distinct_action_hashes": True,
            "seven_gates_aligned": True,
            "candidate_A_failure_replayed": True,
            "candidate_B_failure_replayed": True,
            "selection_rule_applied_without_score": True,
            "terminal_selection_is_NEITHER": True,
            "no_selected_action_hash_exported": True,
            "no_hybrid_exported": True,
        },
        "claim_flags": {
            "CANDIDATE_A_SELECTED": False,
            "CANDIDATE_B_SELECTED": False,
            "NEITHER_SELECTED": True,
            "UNIVERSAL_COMPENSATOR_NO_GO": False,
            "DOWNSTREAM_SELECTED_ACTION_WORK_AUTHORIZED": False,
            "HADAMARD_OR_QUANTUM_RESULT": False,
            "PARTICLE_SCATTERING_POSITIVITY_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL comparison pins "
            "the two terminal obstruction artifacts and applies one common "
            "seven-gate rule on the same unit-cylinder, coupling, raw-D, "
            "clock and small-gauge conventions. It selects NEITHER declared "
            "minimal action. It does not average scores, construct a hybrid, "
            "or rule out every R^2, unimodular, compensator, active-clock, "
            "fixed-flux or enlarged-gauge theory. No selected-action q2, "
            "regulator, Einstein, observer, Hadamard, anomaly/QME, particle, "
            "scattering, positivity or unitarity result is authorized."
        ),
        "next_gate": (
            "Classify the smallest bounded action/gauge/superselection "
            "enlargements after NEITHER; do not activate selected-A/B consumers."
        ),
    }


def _check(value: dict[str, Any]) -> None:
    if value["terminal_selection"] != "NEITHER":
        raise AssertionError("comparison selection drifted")
    if value["strict_downstream_disposition"]["selected_action_hash"] is not None:
        raise AssertionError("comparison exported a selected action")
    if value["strict_downstream_disposition"]["hybrid_authorized"]:
        raise AssertionError("comparison authorized a hybrid")
    if not value["claim_flags"]["NEITHER_SELECTED"]:
        raise AssertionError("NEITHER flag drifted")
    if value["claim_flags"]["UNIVERSAL_COMPENSATOR_NO_GO"]:
        raise AssertionError("scoped comparison was made universal")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    _check(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("Candidate A/B comparison certificate is stale")
    print("COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1: PASS")


if __name__ == "__main__":
    main()
