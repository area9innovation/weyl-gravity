"""Fail-closed readiness theorem for the retained zero-frequency ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFLIGHT = HERE / "certificates/BERGER_RETAINED_26_STATIONARY_SPECTRAL_PREFLIGHT.json"
A104 = HERE / "certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json"
MASK = HERE / "generated/berger_a104_global_partial_assembly/global_A104_known_entry_mask.json"
PARTIAL = HERE / "generated/berger_a104_global_partial_assembly/global_A104_partial.json"
HADAMARD_LIFT = HERE / "certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json"
CAUSAL = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"

DEPENDENCIES = {
    "stationary_spectral_preflight": PREFLIGHT,
    "global_A104_partial": A104,
    "known_entry_mask": MASK,
    "partial_A104_payload": PARTIAL,
    "Hadamard_lift": HADAMARD_LIFT,
    "causal_chain": CAUSAL,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    identity = payload.get("result_id") or payload.get("schema") or path.name
    return {
        "artifact_id": str(identity),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _load() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if (
        values["stationary_spectral_preflight"].get("result_state")
        != "HYBRID_STATIONARY_PENCIL_AND_FREQUENCY_CONVENTION_CERTIFIED_COEFFICIENTWISE_A104_OPEN"
        or values["global_A104_partial"].get("result_state")
        != "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN"
        or values["Hadamard_lift"].get("result_state")
        != "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN"
        or values["causal_chain"].get("result_state")
        != "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN"
    ):
        raise ValueError("zero-frequency dependency boundary drifted")
    mask = values["known_entry_mask"]
    if (
        mask.get("shape") != [104, 104]
        or mask.get("unknown_coordinate_count") != 288
        or mask.get("unknown_blocks") != ["ghost_A12", "identity_A12"]
        or mask.get("known_coordinate_count") != 10_528
        or mask.get("sha256")
        != _canonical_hash({key: value for key, value in mask.items() if key != "sha256"})
    ):
        raise ValueError("A104 known-entry mask drifted")
    partial = values["partial_A104_payload"]
    if partial.get("shape") != [104, 104] or partial.get("sha256") != _canonical_hash(
        {key: value for key, value in partial.items() if key != "sha256"}
    ):
        raise ValueError("partial A104 payload drifted")
    flags = values["global_A104_partial"].get("claim_flags", {})
    if (
        flags.get("BERGER_GLOBAL_PARTIAL_A104") is not True
        or flags.get("BERGER_FULL_A104_CAUCHY_OPERATOR") is not False
        or flags.get("BERGER_Q_CAUCHY_104") is not False
        or flags.get("BERGER_CAUCHY_KREIN_FORM") is not False
    ):
        raise ValueError("partial A104 claim boundary drifted")
    return values


def build() -> dict[str, Any]:
    values = _load()
    ordering = values["stationary_spectral_preflight"]["Cauchy_ordering"]
    result = {
        "schema": "quantum-weyl-berger-zero-frequency-ledger-readiness-v1",
        "result_id": "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS",
        "result_state": "EXACT_MASK_NONIDENTIFIABILITY_CERTIFIED_FULL_STATIONARY_CARRIER_REQUIRED",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "Cauchy_contract": {
            "configuration_rank": 52,
            "Cauchy_rank": 104,
            "ordering": ordering["ordering"],
            "configuration_blocks": ordering["configuration_blocks"],
            "velocity_offset": 52,
        },
        "known_entry_audit": {
            "total_coordinates": 10_816,
            "known_coordinates": 10_528,
            "unknown_coordinates": 288,
            "unknown_fraction": "9/338",
            "unknown_blocks": [
                {"block_id": "ghost_A12", "shape": [12, 12], "coordinates": 144},
                {"block_id": "identity_A12", "shape": [12, 12], "coordinates": 144},
            ],
            "all_unknown_coordinates_are_confined_to_two_degree_diagonal_blocks": True,
        },
        "nonidentifiability_witness": {
            "scope": "formal exact completions of the exported known-entry mask; not physical endpoint claims",
            "completion_A": "set both unknown A12 blocks to the zero matrix",
            "completion_B": "set both unknown A12 blocks to the identity matrix",
            "agreement_on_all_exported_coordinates": True,
            "completion_A_endpoint_zero_eigenspace_dimension": 24,
            "completion_B_endpoint_zero_eigenspace_dimension": 0,
            "zero_eigenspace_dimension_difference": 24,
            "conclusion": "the exported mask and partial operator do not determine ker(A104), hence cannot determine the generalized zero eigenspace or its Jordan structure",
        },
        "minimal_stationary_carrier_contract": {
            "required_result_id": "BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            "required_artifacts": [
                {"artifact_id": "A104", "shape": [104, 104], "content": "complete exact stationary Cauchy generator"},
                {"artifact_id": "q_Cauchy_104", "shape": [104, 104], "content": "degree-plus-one nilpotent BRST prolongation"},
                {"artifact_id": "G_Cauchy_104", "shape": [104, 104], "content": "nondegenerate graded Cauchy/Krein form"},
                {"artifact_id": "real_structure_104", "shape": [104, 104], "content": "antilinear involution in the frozen ordering"},
            ],
            "required_exact_checks": [
                "all_104_rows_and_columns_ledgered",
                "A104_has_no_unknown_coordinates",
                "q_Cauchy_squared_zero",
                "A104_supercommutes_with_q_Cauchy",
                "G_Cauchy_is_nondegenerate_and_BRST_compatible",
                "real_structure_is_an_involution_and_intertwines_A104_q_Cauchy_G_Cauchy",
                "zero_is_isolated_or_a_precise_nonisolated_verdict_is_proved",
            ],
            "analytic_followup": [
                "choose a closed graded/Krein realization",
                "compute the Riesz generalized zero space when zero is isolated",
                "restrict q_Cauchy, causal form, pairing and real structure",
                "solve finite-dimensional graded CCR/Ward/reality/K_Berger equations",
                "test positivity only on ghost-number-zero BRST observables or state the Krein substitute",
            ],
        },
        "current_disposition": {
            "classical_causal_chain": "CERTIFIED",
            "local_Hadamard_singularities": "CERTIFIED",
            "covariance_lift_26_to_54": "CERTIFIED_CONDITIONAL_ON_RETAINED_COVARIANCE",
            "retained_generalized_zero_space": "NOT_COMPUTABLE_FROM_CURRENT_EXPORTS",
            "global_BRST_Hadamard_covariance": "NOT_CONSTRUCTED",
        },
        "claim_flags": {
            "ZERO_FREQUENCY_INPUT_NONIDENTIFIABILITY_CERTIFIED": True,
            "STATIONARY_GENERATOR_RECEIVING_CONTRACT_FROZEN": True,
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
        "claim_boundary": (
            "This exact readiness theorem proves that the current 104-row known-entry mask "
            "does not determine the zero-frequency spectral carrier: two mask-compatible "
            "exact completions differ by 24 endpoint zero modes. It freezes the minimal full "
            "A104, q_Cauchy, Cauchy/Krein form and real-structure receiving contract. It does "
            "not claim either formal completion is physical, compute the generalized zero "
            "space, construct a BRST Hadamard covariance, prove positivity, define renormalized "
            "products, restore a QME or make a quantum claim."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS"
        or result.get("result_state")
        != "EXACT_MASK_NONIDENTIFIABILITY_CERTIFIED_FULL_STATIONARY_CARRIER_REQUIRED"
        or result.get("next_gate")
        != "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1"
    ):
        raise ValueError("zero-frequency readiness identity drifted")
    witness = result.get("nonidentifiability_witness", {})
    if (
        witness.get("agreement_on_all_exported_coordinates") is not True
        or witness.get("zero_eigenspace_dimension_difference") != 24
    ):
        raise ValueError("zero-frequency nonidentifiability witness dropped")
    flags = result.get("claim_flags", {})
    expected_true = {
        "ZERO_FREQUENCY_INPUT_NONIDENTIFIABILITY_CERTIFIED",
        "STATIONARY_GENERATOR_RECEIVING_CONTRACT_FROZEN",
    }
    if {key for key, value in flags.items() if value is True} != expected_true:
        raise ValueError("zero-frequency or quantum result was over-promoted")
