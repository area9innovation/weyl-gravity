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
    "coupled_cyclicity_atlas": HERE / "transfer/certificates/BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS.json",
    "coupled_cyclicity_repair": HERE / "transfer/certificates/BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS.json",
    "mixed_q3_acceptance": HERE / "transfer/certificates/BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE.json",
    "retained_mixed_ell3_acceptance": HERE / "transfer/certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json",
    "retained_mixed_ell3_physical_cyclicity": HERE / "transfer/certificates/BERGER_RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY.json",
    "retained_mixed_ell3_full_BV_cyclicity": HERE / "transfer/certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json",
    "residual_ell3_projection_readiness": HERE / "transfer/certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2.json",
    "causal_chain": HERE / "lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "base_Hadamard_parametrix": HERE / "lorentzian/certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json",
    "typed_companion": HERE / "lorentzian/certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json",
    "Hadamard_lift": HERE / "lorentzian/certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json",
    "zero_frequency_readiness": HERE / "lorentzian/certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json",
    "A104_partial": HERE / "lorentzian/certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json",
    "Hadamard_existence_audit": HERE / "lorentzian/certificates/BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT.json",
    "stationary_generator_import_readiness": HERE / "lorentzian/certificates/BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS.json",
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
        "coupled_cyclicity_atlas": "EXACT_DEFECT_LOCALIZED_FACTOR_TWO_PARTIAL_REPAIR_IDENTIFIED",
        "coupled_cyclicity_repair": "CORRECTED_CLASSICAL_REPAIR_ACCEPTED_MIXED_Q3_INPUT_UNBLOCKED",
        "mixed_q3_acceptance": "TYPED_MIXED_Q3_INDEPENDENTLY_ACCEPTED_RETAINED_ELL3_TRANSFER_OPEN",
        "retained_mixed_ell3_acceptance": "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED_RESIDUAL_BRANCH_PROJECTION_OPEN",
        "retained_mixed_ell3_physical_cyclicity": "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_ACCEPTED_FULL_BV_CYCLICITY_OPEN",
        "retained_mixed_ell3_full_BV_cyclicity": "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_ACCEPTED",
        "residual_ell3_projection_readiness": "CONSUMER_READY_EXACT_SPLIT_FIELD_CONTRACT_BRANCH_BASIS_INPUT_NOT_SUPPLIED",
        "causal_chain": "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN",
        "base_Hadamard_parametrix": "LOCAL_STATIONARY_HADAMARD_PARAMETRICES_CERTIFIED_GLOBAL_BISOLUTION_OPEN",
        "typed_companion": "TYPED_MOLLER_ALGEBRA_CERTIFIED_MICROLOCAL_KERNEL_ACTION_OPEN",
        "Hadamard_lift": "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN",
        "zero_frequency_readiness": "EXACT_MASK_NONIDENTIFIABILITY_CERTIFIED_FULL_STATIONARY_CARRIER_REQUIRED",
        "A104_partial": "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN",
        "Hadamard_existence_audit": "DECOMPOSABILITY_CERTIFIED_EXISTENCE_NOT_IMPLIED_STATIONARY_POSITIVITY_CARRIER_OPEN",
        "stationary_generator_import_readiness": "CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED",
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
    atlas_flags = values["coupled_cyclicity_atlas"].get("claim_flags", {})
    if (
        atlas_flags.get("EXACT_RETAINED_CYCLICITY_DEFECT_ATLAS") is not True
        or atlas_flags.get("PHYSICAL_HAA_FACTOR_TWO_SEAM") is not True
        or atlas_flags.get("UNIFORM_MAXWELL_OUTPUT_X2_PRESERVES_Q1Q2") is not True
        or atlas_flags.get("COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND") is not False
        or values["coupled_cyclicity_atlas"]["retained_atlas"][
            "total_defect_coefficients"
        ]
        != 953
    ):
        raise ValueError("coupled cyclicity atlas frontier drifted")
    repair = values["coupled_cyclicity_repair"]
    repair_flags = repair.get("claim_flags", {})
    repair_diagnostics = repair.get("accepted_candidate", {}).get("diagnostics", {})
    if (
        repair_flags.get("CORRECTED_CLASSICAL_INPUT_AVAILABLE") is not True
        or repair_flags.get("COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED") is not True
        or repair_flags.get("MIXED_Q3_UNBLOCKED") is not True
        or repair_flags.get("QUANTUM_CLAIM") is not False
        or repair.get("next_gate") != "IMPORT_OR_COMPUTE_MIXED_Q3_WITH_REPAIRED_Q2"
        or repair.get("accepted_candidate", {}).get("verdict")
        != "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR"
        or repair_diagnostics.get("full_overlay_coefficient_count") != 1890
        or repair_diagnostics.get("retained_transfer_coefficient_count") != 1474
        or any(
            repair_diagnostics.get(key) != 0
            for key in (
                "full_q1_q2_defect_count",
                "full_cyclicity_defect_count",
                "transfer_missing_coefficient_count",
                "transfer_extra_coefficient_count",
                "transfer_changed_coefficient_count",
                "retained_q1_q2_defect_count",
                "retained_cyclicity_defect_count",
            )
        )
    ):
        raise ValueError("coupled cyclicity repair frontier drifted")
    mixed_q3 = values["mixed_q3_acceptance"]
    mixed_q3_flags = mixed_q3.get("claim_flags", {})
    mixed_q3_diagnostics = mixed_q3.get("exact_replay", {}).get("diagnostics", {})
    if (
        mixed_q3_flags.get("TYPED_MIXED_Q3_PORTABLE_IMPORT_ACCEPTED") is not True
        or mixed_q3_flags.get("MIXED_ARITY_THREE_IDENTITY_INDEPENDENTLY_REPLAYED") is not True
        or mixed_q3_flags.get("RETAINED_MIXED_ELL3_TRANSFER") is not False
        or mixed_q3_flags.get("QUANTUM_CLAIM") is not False
        or mixed_q3.get("next_gate") != "BERGER_RETAINED_MIXED_ELL3_TRANSFER_AND_EXCHANGE"
        or mixed_q3_diagnostics.get("mixed_q3_coefficient_count") != 59598
        or mixed_q3_diagnostics.get("mixed_q3_nonzero_rows") != 21
        or mixed_q3_diagnostics.get("mixed_arity_three_defect_count") != 0
        or mixed_q3_diagnostics.get("typed_q3_graded_symmetry_defect_count") != 0
        or mixed_q3_diagnostics.get("localized_mutation_defect_count", 0) <= 0
    ):
        raise ValueError("mixed q3 acceptance frontier drifted")
    retained_ell3 = values["retained_mixed_ell3_acceptance"]
    retained_ell3_flags = retained_ell3.get("claim_flags", {})
    retained_ell3_diagnostics = retained_ell3.get("exact_replay", {}).get("diagnostics", {})
    if (
        retained_ell3_flags.get("RETAINED_MIXED_ELL3_PORTABLE_IMPORT_ACCEPTED") is not True
        or retained_ell3_flags.get("RETAINED_MIXED_ELL3_CONTACT_INDEPENDENTLY_REPLAYED") is not True
        or retained_ell3_flags.get("RETAINED_MIXED_ELL3_ALL_EXCHANGE_SECTORS_ZERO") is not True
        or retained_ell3_flags.get("RETAINED_MIXED_ARITY_THREE_IDENTITY_INDEPENDENTLY_REPLAYED") is not True
        or retained_ell3_flags.get("EINSTEIN_EXTRA_WEYL_BRANCH_MIXING_COMPUTED") is not False
        or retained_ell3_flags.get("QUANTUM_CLAIM") is not False
        or retained_ell3.get("next_gate") != "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_AND_MIXING_TABLE"
        or retained_ell3_diagnostics.get("retained_ell3_coefficient_count") != 25_950
        or retained_ell3_diagnostics.get("exchange_outer_inner_pair_counts", {}).get("gravity_outer_mixed_inner") != 144
        or retained_ell3_diagnostics.get("exchange_full_coefficient_counts", {}).get("gravity_outer_mixed_inner") != 342
        or any(retained_ell3_diagnostics.get("exchange_final_coefficient_counts", {}).values())
        or retained_ell3_diagnostics.get("retained_arity_three_defect_count") != 0
        or retained_ell3_diagnostics.get("mutation_defect_count", 0) <= 0
    ):
        raise ValueError("retained mixed ell3 acceptance frontier drifted")
    physical_cyclicity = values["retained_mixed_ell3_physical_cyclicity"]
    physical_cyclicity_flags = physical_cyclicity.get("claim_flags", {})
    physical_cyclicity_diagnostics = physical_cyclicity.get("exact_replay", {}).get(
        "diagnostics", {}
    )
    if (
        physical_cyclicity_flags.get(
            "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_REPLAYED"
        )
        is not True
        or physical_cyclicity_flags.get(
            "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"
        )
        is not False
        or physical_cyclicity_flags.get("QME_RESTORED") is not False
        or physical_cyclicity_flags.get("QUANTUM_CLAIM") is not False
        or physical_cyclicity_diagnostics.get("physical_quartic_coefficient_count")
        != 25_662
        or physical_cyclicity_diagnostics.get(
            "physical_quartic_cyclicity_defect_count"
        )
        != 0
        or physical_cyclicity_diagnostics.get(
            "Maxwell_pairing_weight_mutation_defect_count"
        )
        != 17_108
        or physical_cyclicity_diagnostics.get(
            "nonphysical_ghost_antifield_completion_coefficient_count"
        )
        != 288
        or physical_cyclicity_diagnostics.get("physical_pairing_weight_ledger")
        != {
            "gravity": {
                "signed_odd_pairing_entries": ["-1"],
                "absolute_field_equation_weights": ["1"],
                "row_count": 10,
            },
            "Maxwell": {
                "signed_odd_pairing_entries": ["2"],
                "absolute_field_equation_weights": ["2"],
                "row_count": 4,
            },
        }
    ):
        raise ValueError("retained mixed ell3 physical cyclicity frontier drifted")
    full_BV_cyclicity = values["retained_mixed_ell3_full_BV_cyclicity"]
    full_BV_cyclicity_flags = full_BV_cyclicity.get("claim_flags", {})
    full_BV_cyclicity_diagnostics = full_BV_cyclicity.get("exact_replay", {}).get(
        "diagnostics", {}
    )
    if (
        full_BV_cyclicity_flags.get(
            "GHOST_ANTIFIELD_COMPLETION_CYCLICITY_INDEPENDENTLY_REPLAYED"
        )
        is not True
        or full_BV_cyclicity_flags.get(
            "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"
        )
        is not True
        or full_BV_cyclicity_flags.get("QME_RESTORED") is not False
        or full_BV_cyclicity_flags.get("QUANTUM_CLAIM") is not False
        or full_BV_cyclicity_diagnostics.get("retained_ell3_coefficient_count")
        != 25_950
        or full_BV_cyclicity_diagnostics.get(
            "ghost_antifield_completion_coefficient_count"
        )
        != 288
        or full_BV_cyclicity_diagnostics.get("full_BV_cyclicity_defect_count")
        != 0
        or full_BV_cyclicity_diagnostics.get(
            "omitted_degree_two_polarization_mutation_defect_count"
        )
        != 132
    ):
        raise ValueError("retained mixed ell3 full-BV cyclicity frontier drifted")
    projection_readiness = values["residual_ell3_projection_readiness"]
    projection_flags = projection_readiness.get("claim_flags", {})
    if (
        projection_flags.get("RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY") is not True
        or projection_flags.get("RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE") is not False
        or projection_flags.get("RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED") is not False
        or projection_flags.get("RESIDUAL_ELL3_MIXING_TABLE_COMPUTED") is not False
        or projection_flags.get("RESIDUAL_QUANTUM_TRANSFERRED") is not False
        or projection_flags.get("QUANTUM_CLAIM") is not False
        or projection_flags.get(
            "INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS"
        )
        is not True
        or projection_flags.get("OPERATOR_FIELD_REMAINS_Q_SQRT10") is not True
        or projection_flags.get("DEFORMATION_FIELD_EXTENDED_EXACTLY") is not True
        or projection_readiness.get("next_gate")
        != "SUPPLY_COMMITTED_BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2_MANIFEST"
        or projection_readiness.get("input_contract", {}).get(
            "Maxwell_branch_carrier_required"
        )
        is not True
        or projection_readiness.get("input_contract", {}).get(
            "required_dynamical_gravity_branch_ids"
        )
        != ["Einstein_like", "extra_Weyl"]
        or projection_readiness.get("input_contract", {}).get(
            "required_deformation_vertex_basis_ids"
        )
        != ["e_C2_dynamical", "o_C_dual_C_topological"]
    ):
        raise ValueError("residual ell3 projection readiness frontier drifted")
    hadamard_flags = values["Hadamard_lift"].get("claim_flags", {})
    if (
        hadamard_flags.get("BERGER_COVARIANCE_LIFT_26_TO_54") is not True
        or hadamard_flags.get("BERGER_HADAMARD_DATA") is not False
        or hadamard_flags.get("LORENTZIAN_QME_RESTORED") is not False
    ):
        raise ValueError("Hadamard frontier drifted")
    existence = values["Hadamard_existence_audit"]
    existence_flags = existence.get("claim_flags", {})
    if (
        existence_flags.get("BERGER_COMPANION_NULL_CONE_DECOMPOSABLE") is not True
        or existence_flags.get("FEWSTER_GENERAL_EXISTENCE_THEOREM_APPLIES")
        is not False
        or existence_flags.get("BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION")
        is not False
        or existence.get("next_gate")
        != "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1"
    ):
        raise ValueError("Hadamard existence criterion frontier drifted")
    stationary = values["stationary_generator_import_readiness"]
    stationary_flags = stationary.get("claim_flags", {})
    if (
        stationary_flags.get("STATIONARY_GENERATOR_IMPORT_CONSUMER_READY") is not True
        or stationary_flags.get("STATIONARY_GENERATOR_INPUT_AVAILABLE") is not False
        or stationary_flags.get("STATIONARY_GENERATOR_ACCEPTED") is not False
        or stationary.get("next_gate")
        != "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST"
    ):
        raise ValueError("stationary-generator import readiness frontier drifted")
    relative = values["relative_readiness"]
    relative_flags = relative.get("claim_flags", {})
    relative_gate = relative.get("classical_import_gate", {})
    if (
        relative_flags.get("POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED") is not True
        or relative_flags.get("PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED")
        is not True
        or relative_flags.get("CLASSICAL_RELATIVE_TRIANGLE_IMPORTED") is not False
        or relative_flags.get("QUANTUM_RELATIVE_LIFT") is not False
        or relative_gate.get("status") != "NOT_SATISFIED"
        or relative_gate.get("current_map_disposition")
        != "PARTIAL_GENERIC_AXIAL_AND_POLAR_UNGAUGED_OFFSHELL_PREFLIGHT"
    ):
        raise ValueError("relative Einstein-Weyl frontier drifted")
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
                "status": "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED_BRANCH_PROJECTION_CONSUMER_READY_INPUT_ABSENT",
                "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2_MANIFEST",
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
                "status": "STATIONARY_IMPORT_CONSUMER_READY_INPUT_ABSENT_ANALYTIC_ZERO_ISOLATION_SEPARATE",
                "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
            },
            "relative_Einstein_Weyl": {
                "status": "PRINCIPAL_GENERIC_AXIAL_AND_GENERIC_POLAR_UNGAUGED_PREFLIGHTS_GLOBAL_V1_OPEN",
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
                "active_result_id": "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT",
                "disposition": "SUPERSEDED_AS_STATUS_SOURCE_HISTORY_RETAINED",
            },
            {
                "historical_result_id": "BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX",
                "active_result_id": "BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS",
                "disposition": "SUPERSEDED_AS_INTERACTION_STATUS_SOURCE_HISTORY_RETAINED_CAUSAL_UNARY_RECEIPT_VALID",
            },
            {
                "historical_result_id": "BERGER_COMPANION_STATIONARY_DECOMPOSABILITY",
                "active_result_id": "BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT",
                "disposition": "SUPERSEDED_AS_HADAMARD_STATUS_SOURCE_HISTORY_RETAINED_VALID_DECOMPOSABILITY_INPUT",
            },
            {
                "historical_result_id": "BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS",
                "active_result_id": "BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS",
                "disposition": "SUPERSEDED_AS_INTERACTION_STATUS_SOURCE_HISTORY_RETAINED_VALID_NEGATIVE_CONTROL",
            },
            {
                "historical_result_id": "BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS",
                "active_result_id": "BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE",
                "disposition": "SUPERSEDED_AS_INTERACTION_STATUS_SOURCE_HISTORY_RETAINED_VALID_Q2_ACCEPTANCE",
            },
            {
                "historical_result_id": "BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE",
                "active_result_id": "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE",
                "disposition": "SUPERSEDED_AS_INTERACTION_STATUS_SOURCE_HISTORY_RETAINED_VALID_FULL_Q3_ACCEPTANCE",
            },
            {
                "historical_result_id": "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE",
                "active_result_id": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS",
                "disposition": "SUPERSEDED_AS_NEXT_GATE_STATUS_SOURCE_HISTORY_RETAINED_VALID_ELL3_ACCEPTANCE",
            },
        ],
        "claim_flags": {
            "ACTIVE_FRONTIER_LEDGER": True,
            "AFN0_G1_COMPLETE": True,
            "CLASSICAL_MAXWELL_TRANSFER_LANDED": True,
            "MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM": True,
            "MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM": True,
            "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED": True,
            "MIXED_Q3_INPUT_UNBLOCKED": True,
            "MIXED_Q3_INDEPENDENTLY_ACCEPTED": True,
            "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED": True,
            "RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY_ACCEPTED": True,
            "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED": True,
            "RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY": True,
            "COMPANION_DECOMPOSABILITY_CERTIFIED": True,
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY": True,
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED": True,
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED": True,
            "HADAMARD_EXISTENCE_THEOREM_APPLIES": False,
            "FULL_BV_G2_COMPLETE": False,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "GLOBAL_BRST_HADAMARD_STATE": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "ordered_next_gates": [
            "SUPPLY_COMMITTED_BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2_MANIFEST",
            "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
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
            "lift. The repaired Maxwell transfer now replays coefficientwise with 1,890 full "
            "and 1,474 retained coefficients, zero full and retained q1/q2 defects, zero full "
            "and retained cyclicity defects, and preserved causal unary flags. The historical "
            "953-term obstruction remains a valid negative control. The typed 59,598-term mixed "
            "q3 is independently replayed with zero graded-symmetry and all-row arity-three "
            "defects, while a localized coefficient mutation is rejected. The retained ell3 "
            "contact is independently replayed coefficientwise with 25,950 terms. Exact PBW "
            "construction finds 144 gravity-outer/mixed-inner coefficient pairs and 342 full-complex "
            "exchange coefficients, but none survives retained output projection; the other two "
            "exchange sectors have no outer/inner pairs. All three retained exchange sectors therefore "
            "vanish, all 36 retained arity-three rows close, and a mutation is rejected. Exact "
            "cyclic transposition independently reproduces all 25,662 physical quartic coefficients "
            "with zero defects. The signed odd-pairing orientations are -1 in gravity and +2 in "
            "Maxwell, while the physical field-equation transpose uses their absolute weights 1 and "
            "2; changing the Maxwell weight to one produces 17,108 defects. The remaining 288 "
            "ghost/antifield coefficients are also independently replayed. Their suspended-Darboux "
            "transpose has 120 positive and 168 negative signs, zero full-BV defects, and a mutation "
            "that omits the degree-two polarization exposes 132 defects on seven rows. Residual "
            "Einstein-like/extra-Weyl dynamical branch projection and separate e/o deformation-vertex "
            "action remain open. The fail-closed consumer contract is ready and requires exact "
            "gravity plus Maxwell carriers over Q(sqrt(10)); normalized deformation data use the "
            "exact extension Q(sqrt(2),sqrt(10)). This versioned repair keeps the topological o direction out of the "
            "dynamical branch list, but no "
            "branch-basis manifest has been supplied. This is a classical LOCAL-ALGEBRAIC "
            "acceptance, not a quantum result. "
            "The companion is null-cone decomposable, but this does not imply existence of a "
            "Hadamard state: the bosonic analytic hypothesis failure and the later full-BV "
            "BRST/Krein and physical-positivity gate are recorded separately. "
            "The exact stationary-carrier import consumer is ready, but no classical manifest "
            "has been supplied and finite PBW data do not decide spectral isolation of zero. "
            "The relative Einstein-Weyl rail imports exact generic axial and generic polar "
            "ungauged off-shell preflights plus the correct five-generator stabilizer "
            "authority, but polar cyclic/stabilizer descent and exceptional/global rows "
            "still block the all-sector classical triangle. "
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
        or flags.get("MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM") is not True
        or flags.get("COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED") is not True
        or flags.get("MIXED_Q3_INPUT_UNBLOCKED") is not True
        or flags.get("MIXED_Q3_INDEPENDENTLY_ACCEPTED") is not True
        or flags.get("RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED") is not True
        or flags.get("RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY_ACCEPTED") is not True
        or flags.get("RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED") is not True
        or flags.get("RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY") is not True
        or flags.get("COMPANION_DECOMPOSABILITY_CERTIFIED") is not True
        or flags.get("STATIONARY_GENERATOR_IMPORT_CONSUMER_READY") is not True
        or flags.get("POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED") is not True
        or flags.get("PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED") is not True
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
            "MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM",
            "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED",
            "MIXED_Q3_INPUT_UNBLOCKED",
            "MIXED_Q3_INDEPENDENTLY_ACCEPTED",
            "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED",
            "RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY_ACCEPTED",
            "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED",
            "RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY",
            "COMPANION_DECOMPOSABILITY_CERTIFIED",
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY",
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED",
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED",
        }
    ):
        raise ValueError("active frontier quantum claim was over-promoted")
    if len(result.get("supersession_ledger", [])) != 11:
        raise ValueError("active frontier supersession ledger drifted")
