#!/usr/bin/env python3
"""Independent exact verifier for the Candidate A/B NEITHER comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-candidate-ab-neither-comparison-v1.schema.json"
)
EXPECTED_IMPORTS = {
    "candidate_A": {
        "result_id": "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1",
        "scientific_commit": "5c642e2ad14d45f6074b1327c69707b7b9b08f5d",
        "lifecycle_commit": "218cd5ad90cb9df537eb368a9312cb745a21044f",
        "certificate_sha256": "889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6",
        "report_sha256": "0b35a367f70f4215df25c9c3dbe97f5805199ecd21175c7b1cb9f02609bad826",
        "receipt_sha256": "2d2e6b54dafe41e4551362a3f05dc54cf76a80bd35856635f0d250ebc2662d94",
    },
    "candidate_B": {
        "result_id": "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1",
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


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if (
        payload["result_state"] != "NEITHER_MINIMAL_REPAIR_SELECTED"
        or payload["terminal_selection"] != "NEITHER"
    ):
        raise AssertionError("comparison terminal state drifted")

    imported_payloads = {}
    for name, row in payload["imports"].items():
        for field, expected in EXPECTED_IMPORTS[name].items():
            if row[field] != expected:
                raise AssertionError(f"{name} pinned {field} drift")
        for kind in ("certificate", "report", "receipt"):
            path = ROOT / row[kind]
            if _sha(path) != row[f"{kind}_sha256"]:
                raise AssertionError(f"{name} {kind} hash drift")
        imported = json.loads((ROOT / row["certificate"]).read_text())
        receipt = json.loads((ROOT / row["receipt"]).read_text())
        if (
            imported["result_id"] != row["result_id"]
            or imported["result_state"] != "OBSTRUCTED"
            or receipt["claim_id"] != imported["result_id"]
        ):
            raise AssertionError(f"{name} terminal import mismatch")
        imported_payloads[name] = imported

    candidate_a = imported_payloads["candidate_A"]
    candidate_b = imported_payloads["candidate_B"]
    expected_common = {
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
    if payload["common_conventions"] != expected_common:
        raise AssertionError("declared common convention ledger drifted")
    for name in (
        "action_preflight",
        "positive_Berger_clock",
        "strict_tau_obstruction",
    ):
        if candidate_a["dependencies"][name] != candidate_b["dependencies"][name]:
            raise AssertionError(f"Candidate A/B {name} import drifted")
    if (
        not (
            candidate_a["action_identity"]["manifest"]["M_P_squared"]
            == candidate_b["action_and_BV"]["manifest"]["couplings"][
                "M_P_squared"
            ]
            == "1/6"
        )
        or not (
            candidate_a["action_identity"]["manifest"]["V0"]
            == candidate_b["action_and_BV"]["manifest"]["couplings"]["V0"]
            == "1/4"
        )
        or candidate_b["domain"]["signature"] != "(-,+,+,+)"
        or candidate_b["domain"]["boundaries"]
        != "closed S3 Cauchy surfaces; no timelike boundary"
        or candidate_b["unit_cylinder_background_obstruction"]["background"][
            "metric"
        ]
        != "g_hat_bar=-dt^2+dOmega_3^2"
        or candidate_b["unit_cylinder_background_obstruction"]["background"]["R"]
        != "6"
        or candidate_b["Berger_gate"]["raw_D_action"]
        != "L_D A_3_bar=vol_Berger"
    ):
        raise AssertionError("imported common fixture fields drifted")
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
    if payload["action_hashes"] != {
        "candidate_A": candidate_a["action_identity"]["action_sha256"],
        "candidate_B": candidate_b["action_and_BV"]["action_sha256"],
    }:
        raise AssertionError("comparison action hashes drifted")
    if len(set(payload["action_hashes"].values())) != 2:
        raise AssertionError("candidate actions were conflated")

    gates = payload["seven_gate_matrix"]
    if [row["gate"] for row in gates] != list(range(1, 8)):
        raise AssertionError("comparison gate numbering drifted")
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
    if a_fail != [3, 5, 6, 7] or b_fail != [2, 3, 5, 6, 7]:
        raise AssertionError("decisive gate sets drifted")

    selection_hash = _digest(
        {
            "action_hashes": payload["action_hashes"],
            "common_conventions": payload["common_conventions"],
            "gates": payload["seven_gate_matrix"],
            "selection_input": payload["selection_rule"],
        }
    )
    if selection_hash != payload["selection_hash"]:
        raise AssertionError("selection hash drifted")
    if not payload["selection_rule"]["partial_scores_forbidden"]:
        raise AssertionError("partial-score selection enabled")
    if not payload["selection_rule"]["hybrid_forbidden"]:
        raise AssertionError("hybrid selection enabled")

    downstream = payload["strict_downstream_disposition"]
    if (
        downstream["selected_action"] is not None
        or downstream["selected_action_hash"] is not None
        or downstream["selected_carrier"] is not None
        or downstream["hybrid_authorized"]
        or len(downstream["retire_or_do_not_activate"]) != 4
    ):
        raise AssertionError("downstream selected-repair work was authorized")
    flags = payload["claim_flags"]
    if (
        flags["CANDIDATE_A_SELECTED"]
        or flags["CANDIDATE_B_SELECTED"]
        or not flags["NEITHER_SELECTED"]
        or flags["UNIVERSAL_COMPENSATOR_NO_GO"]
        or flags["DOWNSTREAM_SELECTED_ACTION_WORK_AUTHORIZED"]
        or flags["HADAMARD_OR_QUANTUM_RESULT"]
        or flags["PARTICLE_SCATTERING_POSITIVITY_UNITARITY"]
    ):
        raise AssertionError("comparison claim boundary drifted")


if __name__ == "__main__":
    verify()
    print(
        "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1 "
        "INDEPENDENT REPLAY: PASS"
    )
