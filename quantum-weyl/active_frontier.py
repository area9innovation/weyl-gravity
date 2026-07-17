"""Canonical active frontier for the quantum Weyl programme.

Historical certificates remain valid receipts, but many record blockers that
later certificates close.  This module imports the current authoritative
artifacts, verifies their claim boundaries, and emits a single fail-closed
frontier without rewriting or deleting history.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEPENDENCIES = {
    "H04_AFN0": HERE / "local_bv/certificates/AFN0_H04_CANONICAL_QUOTIENT.json",
    "H14_AFN0_even": HERE / "local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "H14_AFN0_odd": HERE / "local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "antifield_contract": HERE / "classical_import/certificates/ANTIFIELD_EXPORT_CONTRACT.json",
    "background_coefficients": HERE / "spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "Cartan_comparison": HERE / "cartan/certificates/LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json",
    "coupled_q2": HERE / "transfer/certificates/BERGER_COUPLED_64_Q2_IMPORT_REPLAY.json",
    "coupled_36_transfer_replay": HERE / "transfer/certificates/BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY.json",
    "classical_Maxwell_transfer": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "classical_transferred_mixed_q2": ROOT / "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json",
    "causal_chain": HERE / "lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "base_Hadamard_parametrix": HERE / "lorentzian/certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json",
    "typed_companion": HERE / "lorentzian/certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json",
    "Hadamard_lift": HERE / "lorentzian/certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json",
    "zero_frequency_readiness": HERE / "lorentzian/certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json",
    "A104_partial": HERE / "lorentzian/certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json",
    "relative_readiness": HERE / "relative/certificates/QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json",
    "Paper09_boundary": HERE / "cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    states = {
        "H04_AFN0": "COMPLETE_AFN0_COVARIANT_COUNTERTERM_CANDIDATE_QUOTIENT",
        "H14_AFN0_even": "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT",
        "H14_AFN0_odd": "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT",
        "antifield_contract": "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT",
        "coupled_q2": "COUPLED_64_Q2_IMPORTED_STRUCTURAL_AND_K_REPLAY_COMPLETE_Q1Q2_AND_CYCLICITY_BLOCKED",
        "coupled_36_transfer_replay": "TRANSFER_AND_Q1Q2_REPLAYED_CYCLICITY_OBSTRUCTION_FOUND",
        "causal_chain": "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN",
        "base_Hadamard_parametrix": "LOCAL_STATIONARY_HADAMARD_PARAMETRICES_CERTIFIED_GLOBAL_BISOLUTION_OPEN",
        "typed_companion": "TYPED_MOLLER_ALGEBRA_CERTIFIED_MICROLOCAL_KERNEL_ACTION_OPEN",
        "Hadamard_lift": "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN",
        "zero_frequency_readiness": "EXACT_MASK_NONIDENTIFIABILITY_CERTIFIED_FULL_STATIONARY_CARRIER_REQUIRED",
        "A104_partial": "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN",
        "relative_readiness": "G0_DEPENDENCY_LEDGER_READY_CLASSICAL_TRIANGLE_AND_QME_MISSING",
    }
    for name, state in states.items():
        if values[name].get("result_state") != state:
            raise ValueError(f"active frontier dependency state drifted: {name}")
    coefficient_flags = values["background_coefficients"].get("claim_flags", {})
    if (
        values["background_coefficients"].get("result_stage") != "COEFFICIENT_COMPUTED"
        or coefficient_flags.get("STANDARD_BACKGROUND_A_AND_C_COMPUTED") is not True
        or coefficient_flags.get("REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED")
        is not False
        or coefficient_flags.get("QME_RESTORED") is not False
    ):
        raise ValueError("background coefficient boundary drifted")
    if (
        values["Cartan_comparison"].get("result_state")
        != "LOCAL_D_PULLBACK_COMPUTED_TARGET_CHAIN_MAP_UNDEFINED"
    ):
        raise ValueError("Cartan comparison boundary drifted")
    q2_flags = values["coupled_q2"].get("claim_flags", {})
    if (
        q2_flags.get("K_BERGER_EQUIVARIANCE_INDEPENDENTLY_REPLAYED") is not True
        or q2_flags.get("RAW_D_CARTAN_CERTIFIED") is not False
        or q2_flags.get("MAXWELL_UNARY_CONTRACTION_IMPORTED") is not False
    ):
        raise ValueError("coupled q2 frontier drifted")
    transfer_replay_flags = values["coupled_36_transfer_replay"].get("claim_flags", {})
    if (
        transfer_replay_flags.get("CLASSICAL_MIXED_Q2_TRANSFER_INDEPENDENTLY_REPLAYED") is not True
        or transfer_replay_flags.get("RETAINED_Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED") is not True
        or transfer_replay_flags.get("RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED") is not False
        or transfer_replay_flags.get("EXACT_CYCLICITY_OBSTRUCTION_WITNESS") is not True
        or values["coupled_36_transfer_replay"]["cyclicity_obstruction"]["retained_36_defect_coefficient_count"] != 953
    ):
        raise ValueError("coupled 36-row transfer replay frontier drifted")
    transfer_flags = values["classical_Maxwell_transfer"].get("flags", {})
    if (
        values["classical_Maxwell_transfer"].get("claim_status")
        != "CERTIFIED_MAXWELL_CAUSAL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_Q2"
        or transfer_flags.get("BERGER_MAXWELL_UNARY_CONTRACTION") is not True
        or transfer_flags.get("BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING")
        is not True
        or transfer_flags.get("BERGER_HADAMARD_DATA") is not False
        or transfer_flags.get("QUANTUM_CLAIM") is not False
        or values["classical_transferred_mixed_q2"].get("shape") != [36, 36, 36]
    ):
        raise ValueError("classical Maxwell transfer frontier drifted")
    hadamard_flags = values["Hadamard_lift"].get("claim_flags", {})
    if (
        hadamard_flags.get("BERGER_COVARIANCE_LIFT_26_TO_54") is not True
        or hadamard_flags.get("BERGER_HADAMARD_DATA") is not False
        or hadamard_flags.get("LORENTZIAN_QME_RESTORED") is not False
    ):
        raise ValueError("Hadamard frontier drifted")
    return values


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    identity = payload.get("result_id") or payload.get("schema")
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"dependency identity missing: {path}")
    return {
        "artifact_id": identity,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    values = _load()
    result = {
        "schema": "quantum-weyl-active-frontier-v1",
        "result_id": "QUANTUM_WEYL_ACTIVE_FRONTIER",
        "result_state": "G1_LOCAL_AFN0_AND_CLASSICAL_CAUSAL_CHAIN_READY_GLOBAL_HADAMARD_FULL_BV_QME_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "promotion_ladder": {
            "G0": "PASSED",
            "G1": "PASSED_AFN0_LOCAL_QUOTIENT",
            "G2": "BLOCKED_FULL_ANTIFIELD_BV_COHOMOLOGY",
            "G3": "PARTIAL_LOCAL_PARAMETRIX_AND_BACKGROUND_COEFFICIENTS_ONLY",
            "G4": "BLOCKED_QME_NOT_RESTORED",
            "G5": "BLOCKED_GLOBAL_BRST_HADAMARD_AND_RENORMALIZED_PRODUCTS",
        },
        "active_rows": {
            "classical_interacting_input": {
                "status": "TRANSFER_FORMULA_AND_Q1Q2_REPLAY_PASS_CYCLICITY_HAS_953_TERM_RETAINED_OBSTRUCTION",
                "next_gate": "REPAIR_CLASSICAL_COUPLED_Q2_OR_PAIRING_UNTIL_CYCLICITY_REPLAYS",
            },
            "local_obstruction_space": {
                "status": "AFN0_H04_H14_EVEN_ODD_COMPLETE_FULL_BV_OPEN",
                "next_gate": "IMPORT_KOSZUL_TATE_ROWS_AND_COMPUTE_MINIMAL_BV_H04_H14",
            },
            "coefficient_and_QME": {
                "status": "STANDARD_BACKGROUND_A_C_ONLY_REPOSITORY_SLAVNOV_BREAKING_OPEN",
                "next_gate": "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
            },
            "free_Lorentzian_state": {
                "status": "CAUSAL_CHAIN_AND_LOCAL_PARAMETRIX_READY_ZERO_SPECTRUM_NONIDENTIFIABLE_FROM_PARTIAL_A104",
                "next_gate": "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            },
            "relative_Einstein_Weyl": {
                "status": "PRINCIPAL_AND_GENERIC_AXIAL_PREFLIGHT_GLOBAL_V1_OPEN",
                "next_gate": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            },
            "quantum_transfer": {
                "status": "FORBIDDEN_BEFORE_QME_RESTORED",
                "next_gate": "QME_RESTORED",
            },
        },
        "supersession_ledger": [
            {
                "historical_result_id": "BERGER_54_ROW_Q2_ARRIVAL_READINESS",
                "active_result_id": "BERGER_COUPLED_64_Q2_IMPORT_REPLAY",
                "disposition": "SUPERSEDED_AS_STATUS_SOURCE_HISTORY_RETAINED",
            },
            {
                "historical_result_id": "BERGER_54_ROW_Q2_REPLAY_ENGINE",
                "active_result_id": "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY",
                "disposition": "SUPERSEDED_AS_STATUS_SOURCE_HISTORY_RETAINED",
            },
            {
                "historical_result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS",
                "active_result_id": "BERGER_CAUSAL_CHAIN_V2_IMPORT",
                "disposition": "SUPERSEDED_AS_STATUS_SOURCE_HISTORY_RETAINED",
            },
            {
                "historical_result_id": "BERGER_ENDPOINT_FACTOR_INPUT_IMPORT",
                "active_result_id": "BERGER_CAUSAL_CHAIN_V2_IMPORT",
                "disposition": "SUPERSEDED_AS_GLOBAL_STATUS_SOURCE_HISTORY_RETAINED_VALID_INPUT_RECEIPT",
            },
            {
                "historical_result_id": "BERGER_HADAMARD_CONSTRUCTION_GATE",
                "active_result_id": "BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT",
                "disposition": "SUPERSEDED_AS_STATUS_SOURCE_HISTORY_RETAINED",
            },
        ],
        "claim_flags": {
            "ACTIVE_FRONTIER_LEDGER": True,
            "AFN0_G1_COMPLETE": True,
            "CLASSICAL_MAXWELL_TRANSFER_LANDED": True,
            "MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM": True,
            "MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM": False,
            "FULL_BV_G2_COMPLETE": False,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "GLOBAL_BRST_HADAMARD_STATE": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "ordered_next_gates": [
            "REPAIR_CLASSICAL_COUPLED_Q2_OR_PAIRING_UNTIL_CYCLICITY_REPLAYS",
            "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
            "BERGER_TYPED_COMPANION_MICROLOCAL_COMPOSITION_AND_GLOBAL_COVARIANCE",
            "MINIMAL_BV_H04_H14_WITH_KOSZUL_TATE_ROWS",
            "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
            "QME_RESTORATION_OR_OBSTRUCTION",
            "QUANTUM_RESIDUAL_TRANSFER",
        ],
        "claim_boundary": (
            "This machine-generated frontier selects current status artifacts without "
            "invalidating historical receipts. It establishes G1 AFN0 local quotients, "
            "a complete classical causal chain, local Hadamard parametrices and a covariance "
            "lift. The first Maxwell transfer formula and q1/q2 identities replay, "
            "but the exported cyclicity claim has an exact 953-coefficient retained defect. "
            "The mixed interaction is therefore blocked pending a classical tensor or convention repair. "
            "It does not establish full antifield BV cohomology, repository Slavnov coefficients, "
            "a global BRST Hadamard state, renormalized products, QME restoration, "
            "residual quantum transfer or a Lorentzian quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "QUANTUM_WEYL_ACTIVE_FRONTIER"
        or result.get("result_state")
        != "G1_LOCAL_AFN0_AND_CLASSICAL_CAUSAL_CHAIN_READY_GLOBAL_HADAMARD_FULL_BV_QME_OPEN"
    ):
        raise ValueError("active frontier identity drifted")
    ladder = result.get("promotion_ladder", {})
    if ladder.get("G1") != "PASSED_AFN0_LOCAL_QUOTIENT" or any(
        not str(ladder.get(level, "")).startswith(("BLOCKED", "PARTIAL"))
        for level in ("G2", "G3", "G4", "G5")
    ):
        raise ValueError("quantum promotion ladder was over-promoted")
    flags = result.get("claim_flags", {})
    if (
        flags.get("ACTIVE_FRONTIER_LEDGER") is not True
        or flags.get("AFN0_G1_COMPLETE") is not True
        or flags.get("CLASSICAL_MAXWELL_TRANSFER_LANDED") is not True
        or flags.get("MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM") is not True
    ):
        raise ValueError("active frontier positive flags dropped")
    if any(
        value is not False
        for key, value in flags.items()
        if key
        not in {
            "ACTIVE_FRONTIER_LEDGER",
            "AFN0_G1_COMPLETE",
            "CLASSICAL_MAXWELL_TRANSFER_LANDED",
            "MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM",
        }
    ):
        raise ValueError("active frontier quantum claim was over-promoted")
    if len(result.get("supersession_ledger", [])) != 5:
        raise ValueError("active frontier supersession ledger drifted")
