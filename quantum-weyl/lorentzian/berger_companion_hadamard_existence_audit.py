"""Audit whether the certified companion data imply a Hadamard state.

Fewster's decomposable Green-hyperbolic framework defines and propagates the
Hadamard class.  Decomposability alone is not a general existence theorem.
This consumer pins the current Berger inputs and records the exact missing
positivity and stationary carriers without constructing a state.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent

DEPENDENCIES = {
    "base_parametrix": HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json",
    "typed_moller": HERE / "certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json",
    "companion_principal": HERE / "certificates/BERGER_COMPANION_DECOMPOSABILITY_PREFLIGHT.json",
    "companion_decomposability": HERE / "certificates/BERGER_COMPANION_STATIONARY_DECOMPOSABILITY.json",
    "graded_state_space": HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json",
    "hadamard_lift": HERE / "certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json",
    "causal_26": HERE / "../../d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "full_A104": HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json",
    "graph_q_obstruction": HERE / "certificates/BERGER_CANONICAL_GRAPH_Q_CAUCHY_OBSTRUCTION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def evaluate() -> dict[str, Any]:
    data = _load()
    principal = data["companion_principal"]
    decomposable = data["companion_decomposability"]
    state_space = data["graded_state_space"]
    full_A104 = data["full_A104"]
    graph_q = data["graph_q_obstruction"]
    causal_26 = data["causal_26"]

    source_checks = {
        "base_local_parametrix_certified": data["base_parametrix"]["claim_flags"][
            "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"
        ]
        is True,
        "typed_moller_kernel_action_still_formal": data["typed_moller"][
            "claim_flags"
        ]["BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT"]
        is False,
        "companion_principal_symbol_not_scalar_normal_wave": principal[
            "principal_symbol_analysis"
        ]["null_symbol_replay"]["checks"][
            "nonzero_square_zero_symbol_is_not_diagonalizable"
        ]
        is True,
        "companion_decomposable": decomposable["claim_flags"][
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
        ]
        is True,
        "distributional_two_point_kernel_open": state_space["readiness_ledger"][
            "distributional_two_point_kernel"
        ]
        == "OPEN",
        "physical_positivity_policy_open": state_space["readiness_ledger"][
            "physical_positivity_or_covariant_Krein_policy"
        ]
        == "OPEN",
        "smooth_zero_mode_completion_open": state_space["readiness_ledger"][
            "smooth_spatial_zero_mode_completion"
        ]
        == "OPEN",
        "covariance_lift_ready_but_source_covariance_absent": data["hadamard_lift"][
            "claim_flags"
        ]["BERGER_COVARIANCE_LIFT_26_TO_54"]
        is True
        and data["hadamard_lift"]["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"]
        is False,
        "full_A104_complete": full_A104["claim_flags"][
            "BERGER_FULL_A104_CAUCHY_OPERATOR"
        ] is True
        and full_A104["coverage"]["unknown_coordinates"] == 0,
        "canonical_graph_q_Cauchy_lift_rejected": graph_q["claim_flags"][
            "BERGER_CANONICAL_GRAPH_Q_CAUCHY_LIFT_REJECTED"
        ] is True,
        "corrected_q_Cauchy_absent": graph_q["claim_flags"][
            "BERGER_Q_CAUCHY_104"
        ] is False,
        "Cauchy_Krein_form_absent": graph_q["claim_flags"][
            "BERGER_CAUCHY_KREIN_FORM"
        ] is False,
        "direct_26_row_causal_green_homotopy_certified": causal_26[
            "result_state"
        ] == "GREEN_CERTIFIED_HADAMARD_OPEN"
        and all(
            row["status"] == "VERIFIED"
            for row in causal_26["green_proof_checks"].values()
        ),
    }
    if not all(source_checks.values()):
        failed = [name for name, passed in source_checks.items() if not passed]
        raise ValueError(f"Hadamard existence input drifted: {failed}")

    return {
        "schema": "quantum-weyl-berger-companion-hadamard-existence-audit-v1",
        "result_id": "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT",
        "result_state": "DECOMPOSABILITY_CERTIFIED_DIRECT_CAUSAL_AND_STATIONARY_COMPLETIONS_OPEN",
        "lifecycle_layer": "LORENTZIAN_HADAMARD_EXISTENCE_AUDIT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "setting_id": decomposable["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in data.items()
        },
        "literature_criterion": {
            "source": "Christopher J. Fewster, Hadamard States for Decomposable Green-Hyperbolic Operators, Communications in Mathematical Physics 407:14 (2026)",
            "doi": "10.1007/s00220-025-05512-1",
            "arxiv": "2503.12537v3",
            "definition_5_2": "decomposability constrains the Pauli-Jordan wavefront set",
            "general_existence_from_decomposability_alone": False,
            "theorem_5_3_scope": "normally hyperbolic real formally hermitian Green-hyperbolic operator with positive-definite hermitian fibre metric",
            "theorem_5_3_applies_to_companion": False,
            "companion_analytic_obstruction": "C20 has a nonzero square-zero lower-left order-two principal symbol, so the normally-hyperbolic hypothesis fails already on the twenty-row bosonic companion",
            "full_BV_lift_obstruction": "after a companion covariance is constructed, the graded 26-to-54 lift separately requires BRST/Krein compatibility and positivity on physical cohomology",
        },
        "exact_input_checks": source_checks,
        "existence_disposition": {
            "decomposability_status": "CERTIFIED",
            "local_singular_parametrix_status": "CERTIFIED_ON_BASE_FACTORS",
            "direct_26_row_causal_green_homotopy_status": "CERTIFIED",
            "stationary_A104_status": "CERTIFIED_COEFFICIENTWISE",
            "canonical_stationary_q_Cauchy_lift_status": "REJECTED_WITH_EXACT_DEFECTS",
            "companion_distributional_transport_status": "OPEN",
            "positive_two_point_bisolution_status": "NOT_CONSTRUCTED",
            "BRST_covariance_status": "NOT_CONSTRUCTED",
            "global_Hadamard_state_status": "NOT_CONSTRUCTED",
            "inference": "DECOMPOSABILITY_DOES_NOT_IMPLY_EXISTENCE_FOR_THIS_OPERATOR",
        },
        "minimal_missing_carrier": {
            "typed_companion_distributional_transport": "REQUIRED_FOR_DIRECT_CAUSAL_ROUTE",
            "smooth_global_bisolution_completion": "REQUIRED_FOR_DIRECT_CAUSAL_ROUTE",
            "q26_compatible_q_Cauchy_104": "REQUIRED_FOR_STATIONARY_ROUTE",
            "Cauchy_Lagrange_Krein_form": "REQUIRED_FOR_STATIONARY_ROUTE",
            "real_structure_and_common_closed_realization": "REQUIRED_FOR_STATIONARY_ROUTE",
            "zero_frequency_Riesz_Jordan_ledger": "REQUIRED_FOR_STATIONARY_ROUTE",
            "positive_or_declared_Krein_covariance": "REQUIRED_EITHER_ROUTE",
            "BRST_Ward_identity_for_two_point_kernel": "REQUIRED_EITHER_ROUTE",
        },
        "claim_flags": {
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE": True,
            "FEWSTER_GENERAL_EXISTENCE_THEOREM_APPLIES": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT_OR_Q26_COMPATIBLE_CAUCHY_LIFT",
        "claim_boundary": (
            "This LORENTZIAN-CAUSAL criterion audit proves that the certified null-cone "
            "decomposability of the Berger companion does not by itself supply a Hadamard "
            "state. Fewster's general existence theorem for bosonic fields applies to normally "
            "hyperbolic operators with positive-definite hermitian fibre metric; the companion "
            "already fails the normally-hyperbolic hypothesis through its nonzero nilpotent "
            "order-two principal block. Separately, the full graded BV lift requires BRST/Krein "
            "compatibility and positivity on physical cohomology. The direct 26-row causal Green "
            "homotopy and full A104 coefficient table are ready, but the canonical stationary "
            "q_Cauchy graph lift is exactly rejected. The direct causal route still requires "
            "distributional companion transport and a global bisolution; the stationary route "
            "requires a corrected q-compatible lift, pairing/reality carrier and spectral "
            "ledger. Both still require a positive or declared Krein covariance and BRST Ward identity. "
            "No Hadamard state, positivity, renormalized product, QME or quantum theorem is claimed."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT"
        or result.get("result_state")
        != "DECOMPOSABILITY_CERTIFIED_DIRECT_CAUSAL_AND_STATIONARY_COMPLETIONS_OPEN"
        or result.get("next_gate")
        != "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT_OR_Q26_COMPATIBLE_CAUCHY_LIFT"
    ):
        raise ValueError("Hadamard existence audit identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("Hadamard existence input check failed")
    criterion = result.get("literature_criterion", {})
    if criterion.get("general_existence_from_decomposability_alone") is not False:
        raise ValueError("decomposability was over-promoted to existence")
    if criterion.get("theorem_5_3_applies_to_companion") is not False:
        raise ValueError("normally-hyperbolic existence theorem was over-applied")
    flags = result.get("claim_flags", {})
    true_flags = {name for name, value in flags.items() if value is True}
    if true_flags != {"BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"}:
        raise ValueError("Hadamard or quantum claim was over-promoted")
