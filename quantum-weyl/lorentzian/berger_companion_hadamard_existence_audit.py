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
    "partial_A104": HERE / "certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json",
    "zero_frequency_readiness": HERE / "certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json",
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
    partial = data["partial_A104"]
    readiness = data["zero_frequency_readiness"]

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
        "full_A104_absent": partial["claim_flags"][
            "BERGER_FULL_A104_CAUCHY_OPERATOR"
        ]
        is False,
        "q_Cauchy_absent": partial["claim_flags"]["BERGER_Q_CAUCHY_104"] is False,
        "Cauchy_Krein_form_absent": partial["claim_flags"][
            "BERGER_CAUCHY_KREIN_FORM"
        ]
        is False,
        "zero_frequency_carrier_nonidentifiable": readiness["claim_flags"][
            "ZERO_FREQUENCY_INPUT_NONIDENTIFIABILITY_CERTIFIED"
        ]
        is True,
    }
    if not all(source_checks.values()):
        failed = [name for name, passed in source_checks.items() if not passed]
        raise ValueError(f"Hadamard existence input drifted: {failed}")

    return {
        "schema": "quantum-weyl-berger-companion-hadamard-existence-audit-v1",
        "result_id": "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT",
        "result_state": "DECOMPOSABILITY_CERTIFIED_EXISTENCE_NOT_IMPLIED_STATIONARY_POSITIVITY_CARRIER_OPEN",
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
            "reason": "C20 has a nonzero square-zero lower-left order-two principal symbol and the BV state-space carrier is an odd/Krein pairing, not the positive-definite fibre metric required by the theorem",
        },
        "exact_input_checks": source_checks,
        "existence_disposition": {
            "decomposability_status": "CERTIFIED",
            "local_singular_parametrix_status": "CERTIFIED_ON_BASE_FACTORS",
            "companion_distributional_transport_status": "OPEN",
            "positive_two_point_bisolution_status": "NOT_CONSTRUCTED",
            "BRST_covariance_status": "NOT_CONSTRUCTED",
            "global_Hadamard_state_status": "NOT_CONSTRUCTED",
            "inference": "DECOMPOSABILITY_DOES_NOT_IMPLY_EXISTENCE_FOR_THIS_OPERATOR",
        },
        "minimal_missing_carrier": {
            "complete_A104": "REQUIRED",
            "q_Cauchy_104": "REQUIRED",
            "Cauchy_Lagrange_Krein_form": "REQUIRED",
            "real_structure_104": "REQUIRED",
            "common_closed_realization": "REQUIRED",
            "zero_frequency_Riesz_Jordan_ledger": "REQUIRED",
            "positive_or_declared_Krein_covariance": "REQUIRED",
            "BRST_Ward_identity_for_two_point_kernel": "REQUIRED",
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
        "next_gate": "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
        "claim_boundary": (
            "This LORENTZIAN-CAUSAL criterion audit proves that the certified null-cone "
            "decomposability of the Berger companion does not by itself supply a Hadamard "
            "state. Fewster's general existence theorem for bosonic fields applies to normally "
            "hyperbolic operators with positive-definite hermitian fibre metric; the companion "
            "has a nonzero nilpotent order-two principal block and the BV carrier has an odd/Krein "
            "pairing. A local base-factor parametrix and a 26-to-54 covariance lift are ready, but "
            "the full stationary Cauchy/BRST/pairing/reality carrier, zero-frequency ledger, "
            "positive or declared Krein covariance and BRST Ward identity are not constructed. "
            "No Hadamard state, positivity, renormalized product, QME or quantum theorem is claimed."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT"
        or result.get("next_gate")
        != "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1"
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
