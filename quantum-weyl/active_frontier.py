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
    "antifield_import": HERE / "classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
    "classical_snapshot_compatibility_receiver": HERE / "classical_import/certificates/CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS.json",
    "minimal_KT_collapse": HERE / "local_bv/certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
    "minimal_BV_H14": HERE / "local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
    "general_nonminimal_gauge_fixed": HERE / "local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "background_coefficients": HERE / "spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "full_BV_multiplicity_preflight": HERE / "spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json",
    "scalar_ghost_reduction": HERE / "spectral/euclidean/certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json",
    "york_hodge_berezinian": HERE / "spectral/euclidean/certificates/YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCH.json",
    "TT_hessian_normalization_readiness": HERE / "spectral/euclidean/certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json",
    "round_S4_standard_zero_modes": HERE / "spectral/euclidean/certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json",
    "standard_TT_auxiliary_contour": HERE / "spectral/euclidean/certificates/STANDARD_TT_AUXILIARY_CONTOUR_PHASE.json",
    "standard_Euclidean_integration_slice": HERE / "spectral/euclidean/certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
    "TT_hessian_dictionary_receiver": HERE / "spectral/euclidean/certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_RECEIVER_READINESS.json",
    "full_BV_ledger_composer": HERE / "spectral/euclidean/certificates/REPOSITORY_FULL_BV_LEDGER_COMPOSER_READINESS.json",
    "physical_TT_hessian_dictionary": HERE / "spectral/euclidean/certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json",
    "full_BV_multiplicity_ledger": HERE / "spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "repository_round_S4_Euler_coefficient": HERE / "spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json",
    "Slavnov_breaking_assembly": HERE / "anomalies/certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json",
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
    "retained_36_branch_projector_obstruction": HERE / "transfer/certificates/BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT.json",
    "branch_carrier_architecture_preflight": HERE / "transfer/certificates/BERGER_BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT.json",
    "retained_46_STF2_carrier_import": HERE / "transfer/certificates/BERGER_RETAINED_46_STF2_CARRIER_IMPORT.json",
    "causal_chain": HERE / "lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "base_Hadamard_parametrix": HERE / "lorentzian/certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json",
    "typed_companion": HERE / "lorentzian/certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json",
    "Hadamard_lift": HERE / "lorentzian/certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json",
    "zero_frequency_readiness": HERE / "lorentzian/certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json",
    "A104_partial": HERE / "lorentzian/certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json",
    "Hadamard_existence_audit": HERE / "lorentzian/certificates/BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT.json",
    "stationary_generator_import_readiness": HERE / "lorentzian/certificates/BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS.json",
    "curvature_image_CCR": HERE / "lorentzian/certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json",
    "curvature_observable_propagator": HERE / "lorentzian/certificates/CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR.json",
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
        "antifield_import": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_IMPORTED_INDEPENDENTLY_REPLAYED",
        "classical_snapshot_compatibility_receiver": "CONTENT_HASH_COMPATIBILITY_RECEIVER_READY_PHYSICAL_BRIDGE_NOT_SUPPLIED",
        "minimal_KT_collapse": "MINIMAL_KT_COLLAPSE_PROVED_AFN0_WEYL_QUOTIENTS_LIFT_DIFF_MIXED_TOTAL_COMPLEX_OPEN",
        "minimal_BV_H14": "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS_NONMINIMAL_OPEN",
        "general_nonminimal_gauge_fixed": "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN",
        "full_BV_multiplicity_preflight": "STANDARD_FACTOR_AND_COVARIANT_FIELD_RANKS_MATCHED_SCALAR_GHOST_AND_ANALYTIC_ROW_MAP_OPEN",
        "scalar_ghost_reduction": "SCALAR_FP_RANK_TWO_TO_ONE_DIFFERENTIAL_FACTOR_VERIFIED_FULL_BV_MEASURE_MAP_OPEN",
        "york_hodge_berezinian": "NONZERO_MODE_YORK_HODGE_AND_BRST_QUARTET_MEASURE_MATCHED_PHYSICAL_HESSIAN_ZERO_MODES_CONTOUR_OPEN",
        "TT_hessian_normalization_readiness": "ACTION_NORMALIZATION_AND_NEARBY_FACTORIZATIONS_VERIFIED_ROUND_S4_TT_DICTIONARY_NOT_SUPPLIED",
        "round_S4_standard_zero_modes": "STANDARD_ROUND_S4_FOUR_FACTOR_ZERO_MODES_COMPLETE_REPOSITORY_GLOBAL_LEDGER_OPEN",
        "standard_TT_auxiliary_contour": "STANDARD_AUXILIARY_POSITIVE_IMAGINARY_THIMBLE_AND_MODEWISE_PHASE_FIXED_REPOSITORY_MATCH_OPEN",
        "standard_Euclidean_integration_slice": "STANDARD_LOCAL_B4_FACTOR_MEASURE_ZERO_MODE_AND_CONTOUR_SLICE_COMPLETE_REPOSITORY_TT_MAP_OPEN",
        "TT_hessian_dictionary_receiver": "SEMANTIC_RECEIVER_READY_PHYSICAL_TT_DICTIONARY_INPUT_NOT_SUPPLIED",
        "full_BV_ledger_composer": "ALL_STANDARD_ROWS_BOUND_COMPOSER_READY_PHYSICAL_TT_INPUT_NOT_SUPPLIED",
        "physical_TT_hessian_dictionary": "REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED",
        "full_BV_multiplicity_ledger": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "repository_round_S4_Euler_coefficient": "REPOSITORY_EUCLIDEAN_S4_EULER_COEFFICIENT_MATCHED_C_COEFFICIENT_OPEN",
        "Slavnov_breaking_assembly": "FULL_BV_QUOTIENT_STANDARD_VECTOR_AND_LEDGER_COMPOSER_BOUND_REGULATED_BV_INSERTION_OPEN",
        "coupled_q2": "COUPLED_64_Q2_IMPORTED_STRUCTURAL_AND_K_REPLAY_COMPLETE_Q1Q2_AND_CYCLICITY_BLOCKED",
        "coupled_36_transfer_replay": "TRANSFER_AND_Q1Q2_REPLAYED_CYCLICITY_OBSTRUCTION_FOUND",
        "coupled_cyclicity_atlas": "EXACT_DEFECT_LOCALIZED_FACTOR_TWO_PARTIAL_REPAIR_IDENTIFIED",
        "coupled_cyclicity_repair": "CORRECTED_CLASSICAL_REPAIR_ACCEPTED_MIXED_Q3_INPUT_UNBLOCKED",
        "mixed_q3_acceptance": "TYPED_MIXED_Q3_INDEPENDENTLY_ACCEPTED_RETAINED_ELL3_TRANSFER_OPEN",
        "retained_mixed_ell3_acceptance": "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED_RESIDUAL_BRANCH_PROJECTION_OPEN",
        "retained_mixed_ell3_physical_cyclicity": "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_ACCEPTED_FULL_BV_CYCLICITY_OPEN",
        "retained_mixed_ell3_full_BV_cyclicity": "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_ACCEPTED",
        "residual_ell3_projection_readiness": "CONSUMER_READY_EXACT_SPLIT_FIELD_CONTRACT_BRANCH_BASIS_INPUT_NOT_SUPPLIED",
        "retained_36_branch_projector_obstruction": "RETAINED_36_CANONICAL_SAME_BUNDLE_ROUTE_OBSTRUCTED_ENLARGED_CARRIER_REQUIRED",
        "branch_carrier_architecture_preflight": "ARCHITECTURES_COMPARED_ACCEPTANCE_CONTRACT_READY_NO_BRANCH_PROJECTOR_ACCEPTED",
        "retained_46_STF2_carrier_import": "PINNED_EXACT_CYCLIC_GRAPH_SDR_IMPORTED_PROJECTOR_OPEN",
        "causal_chain": "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN",
        "base_Hadamard_parametrix": "LOCAL_STATIONARY_HADAMARD_PARAMETRICES_CERTIFIED_GLOBAL_BISOLUTION_OPEN",
        "typed_companion": "TYPED_MOLLER_ALGEBRA_CERTIFIED_MICROLOCAL_KERNEL_ACTION_OPEN",
        "Hadamard_lift": "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN",
        "zero_frequency_readiness": "EXACT_MASK_NONIDENTIFIABILITY_CERTIFIED_FULL_STATIONARY_CARRIER_REQUIRED",
        "A104_partial": "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN",
        "Hadamard_existence_audit": "DECOMPOSABILITY_CERTIFIED_EXISTENCE_NOT_IMPLIED_STATIONARY_POSITIVITY_CARRIER_OPEN",
        "stationary_generator_import_readiness": "CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED",
        "curvature_image_CCR": "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_CERTIFIED_DIRECT_KERNEL_AND_STATE_OPEN",
        "curvature_observable_propagator": "GAUGE_INVARIANT_CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED_AUTONOMOUS_GREEN_AND_HADAMARD_OPEN",
        "relative_readiness": "G0_DEPENDENCY_LEDGER_READY_CLASSICAL_TRIANGLE_AND_QME_MISSING",
    }
    for name, state in states.items():
        if values[name].get("result_state") != state:
            raise ValueError(f"active frontier dependency state drifted: {name}")
    antifield = values["antifield_import"]
    antifield_flags = antifield.get("claim_flags", {})
    if (
        antifield_flags.get("ANTIFIELD_EXPORT_V2_RECEIVER_READY") is not True
        or antifield_flags.get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED") is not True
        or antifield_flags.get("CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT") is not True
        or antifield_flags.get("FILTERED_COMPLEX_ADAPTER_REPLAYED") is not True
        or antifield_flags.get("FULL_BV_G2_COMPLETE") is not False
        or antifield.get("next_gate")
        != "MINIMAL_BV_H04_H14_WITH_KOSZUL_TATE_ROWS"
    ):
        raise ValueError("antifield v2 receiving frontier drifted")
    compatibility = values["classical_snapshot_compatibility_receiver"]
    compatibility_flags = compatibility.get("claim_flags", {})
    compatibility_contract = compatibility.get("accepted_contract", {})
    if (
        compatibility_flags.get("CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY")
        is not True
        or compatibility_flags.get(
            "GENERATOR_ATOM_DIFFERENTIAL_DEPENDENCY_SCOPE_HASHES_ENFORCED"
        )
        is not True
        or compatibility_flags.get("DISTINCT_COMMITS_REQUIRE_CONTENT_PROOF")
        is not True
        or compatibility_flags.get("PHYSICAL_COMPATIBILITY_BRIDGE_SUPPLIED")
        is not False
        or compatibility_contract.get("required_result_id")
        != "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY"
        or compatibility.get("next_gate")
        != "SUPPLY_REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_IF_ANALYTIC_COMMIT_DIFFERS"
    ):
        raise ValueError("classical snapshot compatibility receiver frontier drifted")
    kt = values["minimal_KT_collapse"]
    kt_flags = kt.get("claim_flags", {})
    if (
        kt_flags.get("MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC") is not True
        or kt_flags.get("H04_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT") is not True
        or kt_flags.get("H14_WEYL_AFN0_CLASSES_LIFT_THROUGH_MINIMAL_KT") is not True
        or kt_flags.get("PURE_DIFF_H14_COMPUTED") is not False
        or kt_flags.get("MIXED_DIFF_WEYL_H14_COMPUTED") is not False
        or kt_flags.get("FULL_BV_G2_COMPLETE") is not False
        or kt.get("next_gate")
        != "AFN0_DIFF_MIXED_TOTAL_COMPLEX_AND_MINIMAL_BV_H14"
    ):
        raise ValueError("minimal Koszul--Tate collapse frontier drifted")
    minimal_h14 = values["minimal_BV_H14"]
    minimal_h14_flags = minimal_h14.get("claim_flags", {})
    if (
        minimal_h14_flags.get("AFN0_DIFF_MIXED_TOTAL_COMPLEX_COMPLETE") is not True
        or minimal_h14_flags.get("PURE_DIFF_H14_ZERO") is not True
        or minimal_h14_flags.get("INDEPENDENT_MIXED_DIFF_WEYL_H14_ZERO") is not True
        or minimal_h14_flags.get("MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS") is not True
        or minimal_h14_flags.get("GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE") is not False
        or minimal_h14_flags.get("FULL_G2_PROMOTED") is not False
        or minimal_h14.get("next_gate")
        != "GENERAL_LOCAL_NONMINIMAL_DOUBLETS_AND_GAUGE_FIXED_CONTRACTION"
    ):
        raise ValueError("minimal-BV H14 frontier drifted")
    g2 = values["general_nonminimal_gauge_fixed"]
    g2_flags = g2.get("claim_flags", {})
    if (
        g2_flags.get("GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED") is not True
        or g2_flags.get("LOCAL_CANONICAL_GAUGE_FIXING_INVARIANCE_PROVED") is not True
        or g2_flags.get("H04_GAUGE_FIXED_BV_COMPLETE") is not True
        or g2_flags.get("H14_GAUGE_FIXED_BV_COMPLETE") is not True
        or g2_flags.get("FULL_BV_G2_COMPLETE") is not True
        or g2_flags.get("REGULATED_SLAVNOV_BREAKING_COMPUTED") is not False
        or g2_flags.get("QME_RESTORED") is not False
        or g2.get("next_gate") != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
    ):
        raise ValueError("general nonminimal/gauge-fixed G2 frontier drifted")
    coefficient_flags = values["background_coefficients"].get("claim_flags", {})
    if (
        values["background_coefficients"].get("result_stage") != "COEFFICIENT_COMPUTED"
        or coefficient_flags.get("STANDARD_BACKGROUND_A_AND_C_COMPUTED") is not True
        or coefficient_flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or coefficient_flags.get("REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED")
        is not False
        or coefficient_flags.get("QME_RESTORED") is not False
    ):
        raise ValueError("background coefficient boundary drifted")
    assembly = values["Slavnov_breaking_assembly"]
    assembly_flags = assembly.get("claim_flags", {})
    multiplicity_flags = values["full_BV_multiplicity_preflight"].get(
        "claim_flags", {}
    )
    if (
        multiplicity_flags.get("STANDARD_FACTOR_MULTIPLICITIES_COMPLETE") is not True
        or multiplicity_flags.get("COVARIANT_MINIMAL_COMPONENT_RANKS_COMPLETE")
        is not True
        or multiplicity_flags.get("SCALAR_GHOST_GAP_LOCALIZED_TO_RANK_ONE")
        is not True
        or multiplicity_flags.get("MULTIPLICITY_EXPORT_SEMANTIC_RECEIVER_READY")
        is not True
        or multiplicity_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
    ):
        raise ValueError("full-BV multiplicity frontier drifted")
    scalar_ghost_flags = values["scalar_ghost_reduction"].get("claim_flags", {})
    scalar_ghost_target = values["scalar_ghost_reduction"].get("target_match", {})
    if (
        scalar_ghost_flags.get("DIFF_WEYL_SCALAR_FP_MATRIX_DERIVED") is not True
        or scalar_ghost_flags.get("SCALAR_GHOST_DIFFERENTIAL_RANK_TWO_TO_ONE")
        is not True
        or scalar_ghost_flags.get("STANDARD_SCALAR_GHOST_OPERATOR_MATCHED")
        is not True
        or scalar_ghost_flags.get("NONMINIMAL_BEREZINIAN_MATCHED") is not False
        or scalar_ghost_flags.get("FULL_REPOSITORY_HESSIAN_MATCHED") is not False
        or scalar_ghost_flags.get(
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
        )
        is not False
        or scalar_ghost_target.get("standard_factor_id") != "ghost_depth_0"
        or scalar_ghost_target.get("differential_input_rank") != 2
        or scalar_ghost_target.get("differential_output_factor_rank") != 1
    ):
        raise ValueError("Diff-Weyl scalar ghost reduction frontier drifted")
    measure_flags = values["york_hodge_berezinian"].get("claim_flags", {})
    measure_match = values["york_hodge_berezinian"].get(
        "standard_ghost_factor_match", {}
    )
    if (
        measure_flags.get("YORK_GRAM_OPERATORS_DERIVED") is not True
        or measure_flags.get("HODGE_SUPERJACOBIAN_DELTA0_CANCELLATION") is not True
        or measure_flags.get("NONZERO_MODE_BRST_QUARTET_SUPERDETERMINANT_ONE")
        is not True
        or measure_flags.get("STANDARD_GHOST_OPERATOR_RANK_AND_EXPONENTS_MATCHED")
        is not True
        or measure_flags.get("GLOBAL_ZERO_MODE_LEDGER_COMPLETE") is not False
        or measure_flags.get("REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED") is not False
        or measure_flags.get("AUXILIARY_CONTOUR_AND_PHASE_FIXED") is not False
        or measure_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
        or measure_match.get("status")
        != "EXACT_NONZERO_MODE_OPERATOR_RANK_AND_EXPONENT_MATCH"
    ):
        raise ValueError("York/Hodge nonminimal Berezinian frontier drifted")
    tt_readiness_flags = values["TT_hessian_normalization_readiness"].get(
        "claim_flags", {}
    )
    tt_missing = values["TT_hessian_normalization_readiness"].get(
        "minimal_missing_carrier_theorem", {}
    )
    if (
        tt_readiness_flags.get("REPOSITORY_ACTION_NORMALIZATION_VERIFIED")
        is not True
        or tt_readiness_flags.get(
            "CONFORMALLY_FLAT_C1_ADJOINT_C1_HESSIAN_VERIFIED"
        )
        is not True
        or tt_readiness_flags.get("CYLINDER_TT_BACH_FACTORIZATION_IMPORTED")
        is not True
        or tt_readiness_flags.get("NARIAI_ENDPOINT_ELIGIBILITY_AUDITED")
        is not True
        or tt_readiness_flags.get("REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED")
        is not False
        or tt_missing.get("missing_artifact")
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
    ):
        raise ValueError("repository TT Hessian readiness frontier drifted")
    zero_mode_flags = values["round_S4_standard_zero_modes"].get("claim_flags", {})
    zero_mode_match = values["round_S4_standard_zero_modes"].get(
        "reducibility_match", {}
    )
    if (
        zero_mode_flags.get("STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE")
        is not True
        or zero_mode_flags.get("FIFTEEN_CONFORMAL_REDUCIBILITY_MODES_MATCHED")
        is not True
        or zero_mode_flags.get("REPOSITORY_SCALAR_FP_KERNEL_MATCHED")
        is not True
        or zero_mode_flags.get("REPOSITORY_GLOBAL_ZERO_MODE_LEDGER_COMPLETE")
        is not False
        or zero_mode_match.get("total_conformal_Killing_modes") != 15
    ):
        raise ValueError("round-S4 standard zero-mode frontier drifted")
    contour_flags = values["standard_TT_auxiliary_contour"].get("claim_flags", {})
    contour_data = values["standard_TT_auxiliary_contour"].get(
        "oriented_normalized_contour", {}
    )
    if (
        contour_flags.get("STANDARD_AUXILIARY_CONTOUR_FIXED") is not True
        or contour_flags.get("STANDARD_AUXILIARY_MODEWISE_PHASE_FIXED") is not True
        or contour_flags.get("STANDARD_AUXILIARY_BACKGROUND_LOG_COEFFICIENT_ZERO")
        is not True
        or contour_flags.get("REPOSITORY_AUXILIARY_CONTOUR_MATCHED") is not False
        or contour_flags.get("INFINITE_DIMENSIONAL_REGULATOR_FIXED") is not False
        or contour_data.get("residual_modewise_phase")
        != "PLUS_ONE_BY_ORIENTED_NORMALIZED_MEASURE"
    ):
        raise ValueError("standard TT auxiliary contour frontier drifted")
    slice_flags = values["standard_Euclidean_integration_slice"].get(
        "claim_flags", {}
    )
    slice_checks = values["standard_Euclidean_integration_slice"].get(
        "aggregate_checks", {}
    )
    if (
        slice_flags.get("STANDARD_LOCAL_B4_INTEGRATION_SLICE_COMPLETE") is not True
        or slice_flags.get("STANDARD_LOCAL_ANOMALY_VECTOR_REPRODUCED") is not True
        or slice_flags.get("REPOSITORY_TT_HESSIAN_MATCHED") is not False
        or slice_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
        or slice_checks.get("signed_effective_bundle_rank") != 6
        or slice_checks.get("zero_mode_dimension") != 15
    ):
        raise ValueError("standard Euclidean integration-slice frontier drifted")
    tt_receiver_flags = values["TT_hessian_dictionary_receiver"].get(
        "claim_flags", {}
    )
    tt_contract = values["TT_hessian_dictionary_receiver"].get(
        "accepted_contract", {}
    )
    if (
        tt_receiver_flags.get("TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY")
        is not True
        or tt_receiver_flags.get("KAPPA_HALF_AND_FACTOR_SHIFTS_ENFORCED")
        is not True
        or tt_receiver_flags.get("PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED")
        is not False
        or tt_contract.get("required_result_id")
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
        or tt_contract.get("required_kappa") != {"numerator": 1, "denominator": 2}
    ):
        raise ValueError("TT Hessian dictionary receiver frontier drifted")
    composer = values["full_BV_ledger_composer"]
    composer_flags = composer.get("claim_flags", {})
    composer_contract = composer.get("accepted_contract", {})
    if (
        composer_flags.get("FULL_BV_LEDGER_COMPOSER_READY") is not True
        or composer_flags.get("ALL_NON_TT_STANDARD_ROWS_BOUND") is not True
        or composer_flags.get(
            "COMPOSER_EXACT_EXPONENT_AND_ZERO_MODE_POLICY_ENFORCED"
        )
        is not True
        or composer_flags.get("PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED") is not False
        or composer_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
        or composer_contract.get("required_input_result_id")
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
        or composer_contract.get("standard_factor_operators")
        != [
            "Delta_2_perp(4)",
            "Delta_0(-4)",
            "Delta_2_perp(2)",
            "Delta_1_perp(-3)",
        ]
    ):
        raise ValueError("full-BV ledger composer frontier drifted")
    physical_tt = values["physical_TT_hessian_dictionary"]
    physical_tt_flags = physical_tt.get("claim_flags", {})
    physical_tt_operator = physical_tt.get("operator_dictionary", {})
    if (
        physical_tt_flags.get("REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_SUPPLIED")
        is not True
        or physical_tt_flags.get("REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED")
        is not True
        or physical_tt_flags.get("REPOSITORY_ELLIPTIC_TT_BLOCK_CERTIFIED")
        is not True
        or physical_tt_flags.get("REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED")
        is not False
        or physical_tt_operator.get("repository_Hessian")
        != "(1/2) Delta_2_perp(2) Delta_2_perp(4)"
        or physical_tt.get("zero_modes", {}).get("Hessian_kernel_dimension") != 0
    ):
        raise ValueError("physical round-S4 TT Hessian dictionary frontier drifted")
    physical_ledger = values["full_BV_multiplicity_ledger"]
    physical_factors = physical_ledger.get("repository_factors", [])
    if (
        physical_ledger.get("analytic_route") != "EUCLIDEAN_ELLIPTIC"
        or physical_ledger.get("classical_commit") != physical_tt.get("classical_commit")
        or [row.get("operator") for row in physical_factors]
        != [
            "Delta_2_perp(4)",
            "Delta_0(-4)",
            "Delta_2_perp(2)",
            "Delta_1_perp(-3)",
        ]
        or [row.get("component_rank") for row in physical_factors] != [5, 1, 5, 3]
        or physical_ledger.get("cancellations", {}).get("factor_coverage_status")
        != "VERIFIED"
        or physical_ledger.get("cancellations", {}).get(
            "integration_row_coverage_status"
        )
        != "VERIFIED"
    ):
        raise ValueError("physical full-BV multiplicity ledger frontier drifted")
    repository_euler = values["repository_round_S4_Euler_coefficient"]
    repository_euler_flags = repository_euler.get("claim_flags", {})
    if (
        repository_euler_flags.get(
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED"
        )
        is not True
        or repository_euler_flags.get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not False
        or repository_euler_flags.get(
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED"
        )
        is not False
        or repository_euler.get("coefficient_result", {}).get("a") != "87/20"
        or repository_euler.get("coefficient_result", {}).get("c")
        != "NOT_DETERMINED_ON_ROUND_S4"
    ):
        raise ValueError("repository round-S4 Euler coefficient frontier drifted")
    if (
        assembly_flags.get("FULL_GAUGE_FIXED_BV_H14_BOUND") is not True
        or assembly_flags.get("STANDARD_BACKGROUND_EVEN_VECTOR_REDUCED") is not True
        or assembly_flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or assembly_flags.get("STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND") is not True
        or assembly_flags.get("FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND") is not True
        or assembly_flags.get("FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_BOUND")
        is not True
        or assembly_flags.get("FULL_BV_LEDGER_COMPOSER_READY") is not True
        or assembly_flags.get(
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND"
        )
        is not True
        or assembly_flags.get("REGULATED_BV_INSERTION_V2_RECEIVER_READY")
        is not True
        or assembly_flags.get("ANALYTIC_SLAVNOV_EXPORT_RECEIVER_READY") is not True
        or assembly_flags.get("REGULATED_SLAVNOV_BREAKING_COMPUTED") is not False
        or assembly_flags.get("QME_OBSTRUCTED") is not False
        or assembly_flags.get("QME_RESTORED") is not False
        or assembly.get("next_gate")
        != "MATCH_REPOSITORY_ANALYTIC_REGULATOR_MEASURE_AND_COMPUTE_SLAVNOV_BREAKING"
    ):
        raise ValueError("Slavnov-breaking assembly frontier drifted")
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
    projector_obstruction = values["retained_36_branch_projector_obstruction"]
    projector_flags = projector_obstruction.get("claim_flags", {})
    if (
        projector_flags.get("CLASSICAL_OBSTRUCTION_INDEPENDENTLY_IMPORTED")
        is not True
        or projector_flags.get(
            "RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTED"
        )
        is not True
        or projector_flags.get(
            "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_UNAFFECTED"
        )
        is not True
        or projector_flags.get("RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED")
        is not True
        or projector_flags.get("RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED")
        is not False
        or projector_flags.get("RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED")
        is not False
        or projector_flags.get("RESIDUAL_ELL3_MIXING_TABLE_COMPUTED")
        is not False
        or projector_flags.get("QUANTUM_CLAIM") is not False
        or projector_obstruction.get("next_gate")
        != "CONSTRUCT_BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1"
        or projector_obstruction.get("carrier_enlargement", {}).get(
            "natural_candidate_retained_rank"
        )
        != 46
        or projector_obstruction.get("carrier_enlargement", {}).get(
            "candidate_projector_certified"
        )
        is not False
    ):
        raise ValueError("retained-36 branch-projector obstruction frontier drifted")
    architecture = values["branch_carrier_architecture_preflight"]
    architecture_flags = architecture.get("claim_flags", {})
    architecture_selection = architecture.get("selection_verdict", {})
    architecture_quantum_path = architecture.get("quantum_critical_path", {})
    if (
        architecture_flags.get("ARCHITECTURE_PREFLIGHT_COMPLETE") is not True
        or architecture_flags.get("RANK_46_FIRST_ATTEMPT_SELECTED") is not True
        or architecture_flags.get("COVARIANT_MAPPING_CYLINDER_REUSE_AUDITED")
        is not True
        or architecture_flags.get("RANK_46_CARRIER_IMPORTED") is not True
        or architecture_flags.get("BRANCH_PROJECTOR_ACCEPTED") is not False
        or architecture_flags.get("ELL3_BRANCH_MIXING_AUTHORIZED") is not False
        or architecture_flags.get("RANK_46_IS_QUANTUM_PREREQUISITE") is not False
        or architecture_flags.get("QUANTUM_CLAIM") is not False
        or architecture_selection.get("preferred_first_attempt")
        != "rank_46_STF2_graph_carrier"
        or architecture_selection.get("rank_46_is_quantum_prerequisite")
        is not False
        or architecture_quantum_path.get("ordered_gates", [None])[0]
        != "MATCH_REPOSITORY_ANALYTIC_REGULATOR_MEASURE_AND_COMPUTE_SLAVNOV_BREAKING"
        or architecture.get("next_gate")
        != "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1"
    ):
        raise ValueError("branch-carrier architecture preflight frontier drifted")
    carrier = values["retained_46_STF2_carrier_import"]
    carrier_flags = carrier.get("claim_flags", {})
    if (
        carrier_flags.get("RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED") is not True
        or carrier_flags.get("RANK_46_GRAPH_SDR_INDEPENDENTLY_REPLAYED") is not True
        or carrier_flags.get("RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED") is not False
        or carrier_flags.get("ELL3_BRANCH_MIXING_AUTHORIZED") is not False
        or carrier_flags.get("RANK_46_IS_QUANTUM_PREREQUISITE") is not False
        or carrier_flags.get("QUANTUM_CLAIM") is not False
        or carrier.get("independent_replay", {}).get("all_checks_pass") is not True
        or carrier.get("next_gate")
        != "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1"
    ):
        raise ValueError("retained rank-46 carrier import frontier drifted")
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
    curvature_ccr = values["curvature_image_CCR"]
    curvature_ccr_flags = curvature_ccr.get("claim_flags", {})
    if (
        curvature_ccr_flags.get("CURVATURE_IMAGE_PRESYMPLECTIC_ALGEBRA_DEFINED")
        is not True
        or curvature_ccr_flags.get(
            "CURVATURE_PRESENTATION_MATCHES_FREE_BV_OBSERVABLE_COHOMOLOGY"
        )
        is not True
        or curvature_ccr_flags.get("DIRECT_CURVATURE_CAUSAL_PROPAGATOR_CONSTRUCTED")
        is not False
        or curvature_ccr_flags.get("CURVATURE_HADAMARD_STATE_CONSTRUCTED")
        is not False
        or curvature_ccr_flags.get("INTERACTING_QUANTUM_THEORY") is not False
        or curvature_ccr.get("next_gate")
        != "DIRECT_CURVATURE_GREEN_KERNEL_OR_BRST_HADAMARD_COVARIANCE"
    ):
        raise ValueError("curvature-image CCR frontier drifted")
    curvature_propagator = values["curvature_observable_propagator"]
    curvature_propagator_flags = curvature_propagator.get("claim_flags", {})
    if (
        curvature_propagator_flags.get(
            "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED"
        )
        is not True
        or curvature_propagator_flags.get(
            "CURVATURE_OBSERVABLE_GAUGE_INVARIANCE_CERTIFIED"
        )
        is not True
        or curvature_propagator_flags.get(
            "AUTONOMOUS_CURVATURE_GREEN_OPERATORS_CONSTRUCTED"
        )
        is not False
        or curvature_propagator_flags.get("CURVATURE_HADAMARD_STATE_CONSTRUCTED")
        is not False
        or curvature_propagator_flags.get("INTERACTING_QUANTUM_THEORY") is not False
        or curvature_propagator.get("next_gate")
        != "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE"
    ):
        raise ValueError("curvature observable propagator frontier drifted")
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
        "result_state": "G2_LOCAL_BV_AND_SLAVNOV_ASSEMBLY_READY_GLOBAL_HADAMARD_QME_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "promotion_ladder": {
            "G0": "PASSED",
            "G1": "PASSED_AFN0_LOCAL_QUOTIENT",
            "G2": "PASSED_LOCAL_BV_COHOMOLOGY_REGULAR_BACH_LOCUS",
            "G3": "REPOSITORY_FULL_BV_LEDGER_ACCEPTED_REGULATED_SLAVNOV_INSERTION_AND_GLOBAL_PHASE_OPEN",
            "G4": "BLOCKED_QME_NOT_RESTORED",
            "G5": "BLOCKED_GLOBAL_BRST_HADAMARD_AND_RENORMALIZED_PRODUCTS",
        },
        "active_rows": {
            "classical_interacting_input": {
                "status": "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED_RANK_46_CYCLIC_GRAPH_CARRIER_IMPORTED_PROJECTOR_OPEN_OPTIONAL_FOLLOWUP",
                "next_gate": "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
            },
            "local_obstruction_space": {
                "status": "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN",
                "next_gate": "MATCH_REPOSITORY_ANALYTIC_REGULATOR_MEASURE_AND_COMPUTE_SLAVNOV_BREAKING",
            },
            "coefficient_and_QME": {
                "status": "ROUND_S4_REPOSITORY_EULER_COEFFICIENT_MATCHED_C2_AND_REGULATED_SLAVNOV_INSERTION_OPEN",
                "next_gate": "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION",
            },
            "free_Lorentzian_state": {
                "status": "STATIONARY_IMPORT_CONSUMER_READY_INPUT_ABSENT_ANALYTIC_ZERO_ISOLATION_SEPARATE",
                "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
            },
            "free_Lorentzian_algebra": {
                "status": "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_DEFINED_AND_GAUGE_INVARIANT_OBSERVABLE_CAUSAL_PROPAGATOR_DEFINED_AUTONOMOUS_GREEN_AND_HADAMARD_STATE_OPEN",
                "next_gate": "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE",
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
                "historical_result_id": "ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT",
                "active_result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
                "disposition": "SUPERSEDED_AS_IMPORT_STATUS_SOURCE_HISTORY_RETAINED_VALID_RECEIVER_CONTRACT",
            },
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
            {
                "historical_result_id": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2",
                "active_result_id": "BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT",
                "disposition": "SUPERSEDED_AS_NEXT_GATE_STATUS_SOURCE_HISTORY_RETAINED_VALID_CONSUMER_CONTRACT",
            },
            {
                "historical_result_id": "BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT",
                "active_result_id": "BERGER_BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT",
                "disposition": "SUPERSEDED_AS_NEXT_GATE_STATUS_SOURCE_HISTORY_RETAINED_VALID_OBSTRUCTION",
            },
        ],
        "claim_flags": {
            "ACTIVE_FRONTIER_LEDGER": True,
            "AFN0_G1_COMPLETE": True,
            "ANTIFIELD_EXPORT_V2_RECEIVER_READY": True,
            "CLASSICAL_ANTIFIELD_EXPORT_IMPORTED": True,
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY": True,
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND": True,
            "REGULATED_BV_INSERTION_V2_RECEIVER_READY": True,
            "MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC": True,
            "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS": True,
            "GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE": True,
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
            "RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTION_IMPORTED": True,
            "RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED": True,
            "BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT_COMPLETE": True,
            "COMPANION_DECOMPOSABILITY_CERTIFIED": True,
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY": True,
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED": True,
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED": True,
            "HADAMARD_EXISTENCE_THEOREM_APPLIES": False,
            "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED": False,
            "RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED": True,
            "RANK_46_IS_QUANTUM_PREREQUISITE": False,
            "FULL_BV_G2_COMPLETE": True,
            "SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT_READY": True,
            "SLAVNOV_BV_INSERTION_GAP_ISOLATED": True,
            "STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED": True,
            "STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND": True,
            "FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND": True,
            "FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_READY": True,
            "DIFF_WEYL_SCALAR_GHOST_REDUCTION_VERIFIED": True,
            "YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCHED_NONZERO_MODES": True,
            "REPOSITORY_TT_HESSIAN_MISSING_CARRIER_ISOLATED": True,
            "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE": True,
            "STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED": True,
            "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE": True,
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY": True,
            "FULL_BV_LEDGER_COMPOSER_READY": True,
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED": True,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": True,
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED": True,
            "CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED": True,
            "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "GLOBAL_BRST_HADAMARD_STATE": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "ordered_next_gates": [
            "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION",
            "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
            "BERGER_TYPED_COMPANION_MICROLOCAL_COMPOSITION_AND_GLOBAL_COVARIANCE",
            "QME_RESTORATION_OR_OBSTRUCTION",
            "QUANTUM_RESIDUAL_TRANSFER",
            "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        ],
        "claim_boundary": (
            "This machine-generated frontier selects current status artifacts without "
            "invalidating historical receipts. It establishes G1 AFN0 local quotients, "
            "an accepted classical minimal-BV antifield v2 export with independent exact "
            "delta/gamma/Q and scope-bounded FilteredLocalComplex replay, while the actual "
            "positive-antifield Koszul--Tate sector now contracts on the regular Bach locus; "
            "the pure-Diff and independent mixed H14 sectors vanish by the total-form "
            "comparison and exact degree-three invariant-polynomial calculation, leaving "
            "the minimal-BV H14 quotient complete with even/odd dimensions 2/1 while the "
            "general nonminimal doublets contract pointwise and the contraction transports "
            "under arbitrary invertible local BV-canonical gauge fixing, so the gauge-fixed "
            "H04 and H14 quotients are complete with the same 2/1 dimensions on that locus, "
            "and the exact 3-by-4 breaking reduction binds the standard even background "
            "coordinates 199/30 and -87/20 while keeping the repository matching open. "
            "A cross-commit classical-snapshot receiver is now ready: if the later analytic "
            "operator export and frozen local-BV import come from distinct commits, it "
            "requires exact equality of the generator, atom, differential, dependency and "
            "scope hashes plus role-specific content-addressed import/export proofs. No "
            "physical cross-commit bridge has yet been supplied. The v2 regulated-BV "
            "insertion receiver additionally requires explicit action, total-derivative, "
            "gauge-dependence, regularization-dependence and antifield-completion ledgers, "
            "each bound to the exact coefficient hash; no physical insertion is supplied. "
            "The standard determinant ranks 5,1,5,3 reproduce signed rank six. The exact "
            "longitudinal-Diff/Weyl Faddeev--Popov matrix now reduces its two scalar ghost "
            "inputs to the single differential factor Delta_0-R/3, matching the standard "
            "rank-one scalar ghost row. On the common nonzero-mode domain, the York/Hodge "
            "super-Jacobians cancel the unwanted Delta_0 factor and every gauge/nonminimal "
            "quartet has unit superdeterminant, leaving exactly the standard vector and scalar "
            "ghost exponents. The action normalization and flat TT symbol now combine with the "
            "independent round-S4 spin-two factor specialization to fix the physical repository "
            "Hessian as one half Delta_2_perp(2) Delta_2_perp(4). A separate verifier replays the "
            "factor shifts, normalization, proof digest, ellipticity, and zero kernel. The four "
            "standard round-S4 factors now "
            "have a complete zero-mode ledger: no physical TT zeros, ten Killing-vector ghost "
            "zeros, and five proper-conformal scalar ghost zeros matching the classical fifteen. "
            "The standard algebraic TT auxiliary now also has a convergent oriented +iR thimble, "
            "normalized +1 phase per real mode, and zero background-dependent logarithmic "
            "coefficient. The standard factor, exponent, measure, zero-mode, contour, and "
            "local-b4 regulator data are now consolidated in one integration-slice manifest "
            "reproducing (199/30,-87/20,0). The accepted TT dictionary has been composed with "
            "all non-TT fourth-order rows into a physical full-BV multiplicity ledger, and an "
            "independent consumer verifies complete row/factor coverage, ranks 5,1,5,3, exact "
            "determinant exponents, scalar-map consistency, nested proof hashes, and priming "
            "0,5,0,10. Matching an auxiliary row remains optional for the auxiliary formulation. "
            "The global determinant phase and regulated BV insertion remain open; neither the "
            "standard coefficient vector nor the accepted multiplicity ledger alone decides the "
            "QME. The round-S4 factor sum now promotes the repository Euler coefficient a=87/20, "
            "but C2 vanishes on that background, so c=199/30 remains a standard cross-check until "
            "a non-conformally-flat or Ricci-flat repository operator/measure match lands. The "
            "frontier also contains "
            "a complete classical causal chain, local Hadamard parametrices and a covariance "
            "lift. The support-local curvature graph, completed causal quasi-isomorphism, and "
            "transported pairing define a universal presymplectic graded CCR algebra on the "
            "curvature-image free BV observable classes. Exact transport through the curvature "
            "map and its formal adjoint also constructs the gauge-invariant curvature-observable "
            "Pauli-Jordan operator. This is not an autonomous curvature Green inverse, a "
            "Hadamard state, positivity, or an interacting quantum theory. The "
            "repaired Maxwell transfer now replays coefficientwise with 1,890 full "
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
            "that omits the degree-two polarization exposes 132 defects on seven rows. The former "
            "36-row V2 branch-basis request is now closed by a pinned, independently replayed "
            "LOCAL-ALGEBRAIC obstruction. For the canonical rough-tensor-wave Einstein image, all "
            "92 degree-two entries of the exact remainder are nondivisible by the scalar wave "
            "polynomial, so no finite-order support-local same-bundle complementary projector is "
            "authorized on that carrier. The historical V2 consumer remains an immutable valid "
            "contract, and the retained full-BV ell3 theorem is unaffected, but its 36-row success "
            "artifact and branch-space mixing table must not be produced. The exact lower bound is "
            "four added BV rows. The natural STF2 prolongation plus cyclic dual has now landed as "
            "a pinned, independently replayed finite-order rank-46 cyclic graph carrier. Its exact "
            "46-to-36 SDR preserves retained cohomology, but it is not yet a certified branch "
            "projector. Filtered or mapping-cylinder projectors remain open, and any nonlocal split "
            "must remain REDUCED-MODE. The topological o direction remains outside the dynamical "
            "branch list. A separate architecture preflight selects the rank-46 STF2 graph carrier "
            "as the preferred minimal setting-specific route, imports its exact carrier, and imports the established "
            "386=356+30 covariant curvature mapping cylinder only as a certified reuse library and "
            "fallback. Neither route currently supplies a Berger branch projector or authorizes "
            "mixing. Rank-46 resolution is an optional Paper 11 interpretation follow-up, not a "
            "quantum prerequisite: full local BV cohomology has reached G2 and the exact Slavnov "
            "assembly/receiver is ready; repository regulator, measure and Slavnov matching is now "
            "the analytic critical path, while stationary/Hadamard construction is "
            "parallel. This is a classical LOCAL-ALGEBRAIC acceptance, not a quantum result. "
            "The companion is null-cone decomposable, but this does not imply existence of a "
            "Hadamard state: the bosonic analytic hypothesis failure and the later full-BV "
            "BRST/Krein and physical-positivity gate are recorded separately. "
            "The exact stationary-carrier import consumer is ready, but no classical manifest "
            "has been supplied and finite PBW data do not decide spectral isolation of zero. "
            "The relative Einstein-Weyl rail imports exact generic axial and generic polar "
            "ungauged off-shell preflights plus the correct five-generator stabilizer "
            "authority, but polar cyclic/stabilizer descent and exceptional/global rows "
            "still block the all-sector classical triangle. "
            "It does not establish repository Slavnov coefficients, a global BRST Hadamard state, "
            "renormalized products, QME restoration, "
            "residual quantum transfer or a Lorentzian quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "QUANTUM_WEYL_ACTIVE_FRONTIER"
        or result.get("result_state")
        != "G2_LOCAL_BV_AND_SLAVNOV_ASSEMBLY_READY_GLOBAL_HADAMARD_QME_OPEN"
    ):
        raise ValueError("active frontier identity drifted")
    ladder = result.get("promotion_ladder", {})
    if (
        ladder.get("G1") != "PASSED_AFN0_LOCAL_QUOTIENT"
        or ladder.get("G2") != "PASSED_LOCAL_BV_COHOMOLOGY_REGULAR_BACH_LOCUS"
        or ladder.get("G3")
        != "REPOSITORY_FULL_BV_LEDGER_ACCEPTED_REGULATED_SLAVNOV_INSERTION_AND_GLOBAL_PHASE_OPEN"
        or any(
            not str(ladder.get(level, "")).startswith(("BLOCKED", "PARTIAL"))
            for level in ("G4", "G5")
        )
    ):
        raise ValueError("quantum promotion ladder was over-promoted")
    flags = result.get("claim_flags", {})
    if (
        flags.get("ACTIVE_FRONTIER_LEDGER") is not True
        or flags.get("AFN0_G1_COMPLETE") is not True
        or flags.get("ANTIFIELD_EXPORT_V2_RECEIVER_READY") is not True
        or flags.get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED") is not True
        or flags.get("CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY") is not True
        or flags.get("CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND")
        is not True
        or flags.get("REGULATED_BV_INSERTION_V2_RECEIVER_READY") is not True
        or flags.get("MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC") is not True
        or flags.get("MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS") is not True
        or flags.get("GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE") is not True
        or flags.get("FULL_BV_G2_COMPLETE") is not True
        or flags.get("SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT_READY") is not True
        or flags.get("SLAVNOV_BV_INSERTION_GAP_ISOLATED") is not True
        or flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or flags.get("STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND") is not True
        or flags.get("FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND") is not True
        or flags.get("FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_READY") is not True
        or flags.get("DIFF_WEYL_SCALAR_GHOST_REDUCTION_VERIFIED") is not True
        or flags.get("YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCHED_NONZERO_MODES")
        is not True
        or flags.get("REPOSITORY_TT_HESSIAN_MISSING_CARRIER_ISOLATED")
        is not True
        or flags.get("STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE") is not True
        or flags.get("STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED") is not True
        or flags.get("STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE")
        is not True
        or flags.get("TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY") is not True
        or flags.get("FULL_BV_LEDGER_COMPOSER_READY") is not True
        or flags.get("REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED")
        is not True
        or flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not True
        or flags.get("REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED")
        is not True
        or flags.get("CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED")
        is not True
        or flags.get("CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED")
        is not True
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
        or flags.get("RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTION_IMPORTED")
        is not True
        or flags.get("RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED") is not True
        or flags.get("BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT_COMPLETE") is not True
        or flags.get("RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED") is not True
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
            "ANTIFIELD_EXPORT_V2_RECEIVER_READY",
            "CLASSICAL_ANTIFIELD_EXPORT_IMPORTED",
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY",
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND",
            "REGULATED_BV_INSERTION_V2_RECEIVER_READY",
            "MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC",
            "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS",
            "GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE",
            "FULL_BV_G2_COMPLETE",
            "SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT_READY",
            "SLAVNOV_BV_INSERTION_GAP_ISOLATED",
            "STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED",
            "STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND",
            "FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND",
            "FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_READY",
            "DIFF_WEYL_SCALAR_GHOST_REDUCTION_VERIFIED",
            "YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCHED_NONZERO_MODES",
            "REPOSITORY_TT_HESSIAN_MISSING_CARRIER_ISOLATED",
            "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE",
            "STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED",
            "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE",
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY",
            "FULL_BV_LEDGER_COMPOSER_READY",
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED",
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED",
            "CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED",
            "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED",
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
            "RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTION_IMPORTED",
            "RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED",
            "BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT_COMPLETE",
            "RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED",
            "COMPANION_DECOMPOSABILITY_CERTIFIED",
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY",
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED",
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED",
        }
    ):
        raise ValueError("active frontier quantum claim was over-promoted")
    if len(result.get("supersession_ledger", [])) != 14:
        raise ValueError("active frontier supersession ledger drifted")
