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

from classical_import.classical_snapshot_compatibility_receiver import (
    validate_classical_snapshot_compatibility,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEPENDENCIES = {
    "H04_AFN0": HERE / "local_bv/certificates/AFN0_H04_CANONICAL_QUOTIENT.json",
    "H14_AFN0_even": HERE / "local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "H14_AFN0_odd": HERE / "local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "antifield_import": HERE / "classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
    "classical_snapshot_compatibility_receiver": HERE / "classical_import/certificates/CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS.json",
    "physical_classical_snapshot_compatibility": HERE / "classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json",
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
    "nonconformal_coefficient_match_receiver": HERE / "spectral/euclidean/certificates/REPOSITORY_NONCONFORMAL_COEFFICIENT_MATCH_READINESS.json",
    "Euclidean_elliptic_complex_receiver": HERE / "spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_READINESS.json",
    "regulator_measure_receiver": HERE / "spectral/euclidean/certificates/REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_READINESS.json",
    "Slavnov_breaking_assembly": HERE / "anomalies/certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json",
    "physical_Euclidean_elliptic_complex": HERE / "spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "physical_nonconformal_coefficient_match": HERE / "spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
    "regulated_repository_Slavnov_breaking": HERE / "anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "unitary_matter_cancellation_no_go": HERE / "anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "WZ_compensator_preflight": HERE / "anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "WZ_minimal_BV_cotangent_lift": HERE / "anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "WZ_extended_local_BV": HERE / "anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "one_loop_Slavnov_Q1_disposition": HERE / "transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_nonlocal_Gamma1": HERE / "transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_TT_logarithmic_Gamma1": HERE / "transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "curvature_squared_covariant_log_Gamma1": HERE / "transfer/certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "FV_conformized_C2_log_Gamma1": HERE / "transfer/certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
    "FV_anomaly_action_Ricci_sector": HERE / "transfer/certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json",
    "algebraic_cubic_Weyl_carriers": HERE / "transfer/certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json",
    "third_curvature_Weyl_manifest": HERE / "transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "CPT_universal_third_curvature_kernels": HERE / "transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
    "generic_physical_hessian_linear_curvature": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "generic_physical_hessian_n3_triangle_fixture": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json",
    "generic_physical_hessian_n3_five_carrier_projection": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_physical_hessian_n3_integration_obstruction": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json",
    "generic_physical_hessian_curvature_squared": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "generic_physical_hessian_mixed_H1_H2_corner_fixture": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json",
    "generic_physical_hessian_mellin_subtraction_scale_row": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json",
    "generic_physical_hessian_covariant_Volterra_carrier": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json",
    "generic_physical_hessian_H1_H2_contact_residue_projection": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json",
    "generic_physical_hessian_symmetric_mixed_boundary_incidence": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_triangle_corner_residues": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json",
    "generic_physical_hessian_full_boundary_incidence": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_H1_H2_contact_finite_rows": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json",
    "generic_physical_hessian_triangle_master_completeness": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json",
    "generic_physical_hessian_triangle_renormalized_master_values": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json",
    "generic_physical_hessian_triangle_six_master_coordinates": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json",
    "generic_physical_hessian_triangle_relative_IBP_boundary_flux": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json",
    "generic_physical_hessian_third_curvature_form_factors": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json",
    "generic_physical_plus_ghost_n3_third_curvature_form_factors": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS.json",
    "generic_ghost_n1_n2_vector_integrated_functions": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS.json",
    "generic_partial_BV_third_curvature_form_factors": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS.json",
    "generic_background_ghost_CPT_obstruction": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "generic_ghost_Endo_Duhamel_reduction": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json",
    "generic_ghost_n1_n2_Hodge_resolvent_reduction": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "generic_ghost_n1_n2_vector_CPT_projection": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json",
    "generic_ghost_longitudinal_Schur_resummation": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "generic_ghost_Schur_Schatten_split": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
    "generic_ghost_Schur_Wodzicki_residue": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
    "generic_ghost_Schur_weighted_trace_scale": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_ghost_Schur_finite_weighted_traces": HERE / "spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
    "round_S4_ghost_Schur_zeta_factorization": HERE / "spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json",
    "product_S2_S2_ghost_Schur_spectral_carrier": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json",
    "product_S2_S2_ghost_Schur_det3_enclosure": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json",
    "product_S2_S2_ghost_Schur_weighted_rows": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json",
    "product_S2_S2_ghost_Schur_modified_determinant": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_SCHUR_MODIFIED_DETERMINANT_PRECERTIFICATE.json",
    "product_S2_S2_ghost_minimal_vector_carrier": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_CARRIER.json",
    "product_S2_S2_ghost_minimal_vector_determinant": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE.json",
    "product_S2_S2_full_BV_join_boundary": HERE / "spectral/euclidean/certificates/PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY.json",
    "generic_ghost_Schur_weight_raised_zeta_factorization": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json",
    "generic_ghost_n3_adiabatic_carrier": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json",
    "generic_ghost_n3_triangle_kernel": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "scalar_flat_K_Ricci_crosswalk": HERE / "transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
    "generic_ghost_n3_five_carrier_projection": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_ghost_n3_barycentric_factorization": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json",
    "generic_ghost_n3_pole3_relative_IBP": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json",
    "scalar_triangle_differential_system": HERE / "spectral/euclidean/certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json",
    "generic_ghost_n3_pole3_integrated_functions": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json",
    "generic_ghost_n3_I29_integrated_function": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json",
    "generic_ghost_n3_symmetric_point_simplex_integration": HERE / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json",
    "BoxR_scheme_conversion": HERE / "spectral/euclidean/certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json",
    "vacuum_cylinder_reduced_Bridge4": HERE / "lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json",
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
    "Hadamard_regular_morphism_boundary": HERE / "lorentzian/certificates/BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY.json",
    "temporal_cutoff_companion_Green_family": HERE / "lorentzian/certificates/BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY.json",
    "cutoff_companion_microlocal_response_preflight": HERE / "lorentzian/certificates/BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT.json",
    "cutoff_companion_Hermitian_dilation": HERE / "lorentzian/certificates/BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION.json",
    "cutoff_Volterra_microlocal_orientation_reduction": HERE / "lorentzian/certificates/BERGER_CUTOFF_VOLTERRA_MICROLOCAL_ORIENTATION_REDUCTION.json",
    "cutoff_Volterra_normal_topology_convergence": HERE / "lorentzian/certificates/BERGER_CUTOFF_VOLTERRA_NORMAL_TOPOLOGY_CONVERGENCE.json",
    "free_dilation_Hadamard_bisolution_seed": HERE / "lorentzian/certificates/BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED.json",
    "free_dilation_Krein_CCR_covariance": HERE / "lorentzian/certificates/BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE.json",
    "full_dilation_Hadamard_Krein_CCR_covariance": HERE / "lorentzian/certificates/BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE.json",
    "dilation_retained26_restriction_audit": HERE / "lorentzian/certificates/BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT.json",
    "typed_biwave_Volterra_theorem": HERE / "lorentzian/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json",
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
        "physical_classical_snapshot_compatibility": "LOCAL_BV_CONTENT_HASHES_EQUAL_ACROSS_DISTINCT_COMMITS",
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
        "nonconformal_coefficient_match_receiver": "RECEIVER_READY_CURRENT_CANDIDATES_FAIL_COMPLEMENTARY_GATES",
        "Euclidean_elliptic_complex_receiver": "SYMBOL_EXACTNESS_RECEIVER_READY_PHYSICAL_COMPLEX_NOT_SUPPLIED",
        "regulator_measure_receiver": "COMPOSITIONAL_RECEIVER_READY_PHYSICAL_LEDGER_NOT_SUPPLIED",
        "Slavnov_breaking_assembly": "FULL_BV_QUOTIENT_PHYSICAL_ROUND_S4_LEDGER_EULER_AND_SNAPSHOT_COMPATIBILITY_BOUND_REGULATED_BV_INSERTION_OPEN",
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
        "Hadamard_existence_audit": "DECOMPOSABILITY_CERTIFIED_DIRECT_CAUSAL_AND_STATIONARY_COMPLETIONS_OPEN",
        "Hadamard_regular_morphism_boundary": "FINITE_WAVEFRONT_MAPS_CERTIFIED_CUTOFF_REGULAR_MORPHISM_AND_SEED_COVARIANCE_OPEN",
        "temporal_cutoff_companion_Green_family": "NONSTATIONARY_CUTOFF_GREEN_FAMILY_CERTIFIED_MICROLOCAL_PROPAGATION_AND_SEED_COVARIANCE_OPEN",
        "cutoff_companion_microlocal_response_preflight": "CUTOFF_FACTORWISE_NULL_KERNEL_AND_REGULAR_TIMESLICE_SOURCE_MAP_CERTIFIED_ORIENTATION_AND_GREENHYP_RESPONSE_OPEN",
        "cutoff_companion_Hermitian_dilation": "METRIC_COMPANION_RFHGHO_DILATION_AND_TWO_REGULAR_CAUCHY_MORPHISMS_CERTIFIED_CONE_ACTION_AND_STATE_OPEN",
        "cutoff_Volterra_microlocal_orientation_reduction": "FINITE_VOLTERRA_TERMS_ORIENTED_SINGLE_HORMANDER_CONVERGENCE_GATE_OPEN",
        "cutoff_Volterra_normal_topology_convergence": "CUTOFF_NORMAL_CONVERGENCE_DECOMPOSABILITY_AND_DILATED_CONE_MAPPING_CERTIFIED_COVARIANCE_TRANSPORT_OPEN",
        "free_dilation_Hadamard_bisolution_seed": "GLOBAL_FREE_DILATION_HADAMARD_BISOLUTION_EXISTS_POSITIVE_STATE_AND_BV_RESTRICTION_OPEN",
        "free_dilation_Krein_CCR_covariance": "FREE_DILATION_GLOBAL_HADAMARD_KREIN_COVARIANCE_CCR_NORMALIZED_POSITIVE_STATE_AND_BV_TRANSPORT_OPEN",
        "full_dilation_Hadamard_Krein_CCR_covariance": "FULL_METRIC_DILATION_GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE_TRANSPORTED_GRADED_BV_AND_POSITIVITY_OPEN",
        "dilation_retained26_restriction_audit": "CANONICAL_SUMMAND_RESTRICTION_OBSTRUCTED_GRAPH_INTERTWINER_OR_DIRECT_RETAINED26_COVARIANCE_REQUIRED",
        "typed_biwave_Volterra_theorem": "CONDITIONAL_TYPED_BIWAVE_GREEN_THEOREM_IMPORTED_HADAMARD_AND_PHYSICAL_NORMAL_FORM_OPEN",
        "stationary_generator_import_readiness": "CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED",
        "curvature_image_CCR": "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_CERTIFIED_DIRECT_KERNEL_AND_STATE_OPEN",
        "curvature_observable_propagator": "GAUGE_INVARIANT_CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED_AUTONOMOUS_GREEN_AND_HADAMARD_OPEN",
        "BoxR_scheme_conversion": "RAW_ZETA_BOX_R_COEFFICIENT_AND_REPOSITORY_BOXR_ZERO_R2_CONVERSION_CERTIFIED_NONLOCAL_R2_FORM_FACTOR_OPEN",
        "algebraic_cubic_Weyl_carriers": "ALGEBRAIC_C3_CARRIERS_COMPLETE_NONLOCAL_CUBIC_FORM_FACTORS_OPEN",
        "third_curvature_Weyl_manifest": "PARITY_EVEN_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST_COMPLETE_COEFFICIENT_FUNCTIONS_OPEN",
        "CPT_universal_third_curvature_kernels": "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED_REPOSITORY_CONFORMAL_GRAVITON_TRACE_SUBSTITUTION_OPEN",
        "generic_physical_hessian_linear_curvature": "SAME_GAUGE_TRACELESS_PHYSICAL_HESSIAN_LINEAR_CURVATURE_IMPORTED_N3_THREE_LINEAR_VERTEX_READY",
        "generic_physical_hessian_n3_triangle_fixture": "PHYSICAL_THREE_LINEAR_HESSIAN_TRIANGLE_OPERATIONAL_EXACT_INTERIOR_FIXTURE",
        "generic_physical_hessian_n3_five_carrier_projection": "PHYSICAL_THREE_H1_COMMON_NUMERATOR_AND_FIVE_CARRIER_PROJECTION_EXACT",
        "generic_physical_hessian_n3_integration_obstruction": "ISOLATED_PHYSICAL_THREE_H1_TRIANGLE_HAS_LOGARITHMIC_SIMPLEX_CORNER_OBSTRUCTION",
        "generic_physical_hessian_curvature_squared": "ALGEBRAIC_CURVATURE_SQUARED_PHYSICAL_HESSIAN_IMPORTED_GAUGE_ORDERING_CROSSWALKED",
        "generic_physical_hessian_mixed_H1_H2_corner_fixture": "RAW_MIXED_PHYSICAL_LOG_COEFFICIENT_NONZERO_SUBTRACTION_REQUIRED",
        "generic_physical_hessian_mellin_subtraction_scale_row": "FIXTURE_MELLIN_MINIMAL_SUBTRACTION_SCALE_ROW_COMPUTED_GENERIC_COVARIANT_LIFT_OPEN",
        "generic_physical_hessian_covariant_Volterra_carrier": "GENERIC_COVARIANT_VOLTERRA_SUBTRACTION_CARRIER_CONSTRUCTED_MIXED_ROWS_OPEN",
        "generic_physical_hessian_H1_H2_contact_residue_projection": "GENERIC_H1_H2_CONTACT_ENDPOINT_RESIDUES_PROJECTED_TO_FIVE_CARRIER_QUOTIENT",
        "generic_physical_hessian_symmetric_mixed_boundary_incidence": "SYMMETRIC_POINT_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED_H2_CANCELLATION_REFUTED",
        "generic_physical_hessian_triangle_corner_residues": "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED",
        "generic_physical_hessian_full_boundary_incidence": "GENERIC_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED_M14_NONZERO_RENORMALIZED",
        "generic_physical_hessian_H1_H2_contact_finite_rows": "GENERIC_H1_H2_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED",
        "generic_physical_hessian_triangle_master_completeness": "ALL_ELEVEN_PHYSICAL_TRIANGLE_ROWS_REDUCED_TO_SIX_MASTER_RELATIVE_IBP_SPAN",
        "generic_physical_hessian_triangle_renormalized_master_values": "THREE_NEW_PHYSICAL_TRIANGLE_MASTER_VALUES_EVALUATED_IN_COMMON_MELLIN_SCHEME",
        "generic_physical_hessian_triangle_six_master_coordinates": "ALL_ELEVEN_PHYSICAL_TRIANGLE_SIX_MASTER_COORDINATE_FUNCTIONS_COMPUTED",
        "generic_physical_hessian_triangle_relative_IBP_boundary_flux": "ALL_ELEVEN_PHYSICAL_TRIANGLE_BOUNDARY_FLUXES_AND_INTEGRATED_MASTER_DECOMPOSITIONS_COMPUTED",
        "generic_physical_hessian_third_curvature_form_factors": "FIVE_CARRIER_LABELLED_PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED",
    "generic_physical_plus_ghost_n3_third_curvature_form_factors": "COEFFICIENT_COMPUTED",
        "generic_ghost_n1_n2_vector_integrated_functions": "COEFFICIENT_COMPUTED",
        "generic_partial_BV_third_curvature_form_factors": "COEFFICIENT_COMPUTED",
        "generic_background_ghost_CPT_obstruction": "GENERIC_GHOST_OPERATOR_NONMINIMAL_AND_HODGE_MIXED_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED",
        "generic_ghost_Endo_Duhamel_reduction": "NONMINIMAL_GHOST_EXACTLY_REDUCED_TO_ENDO_BASE_PLUS_LOCAL_RICCI_DUHAMEL_SERIES",
        "generic_ghost_n1_n2_Hodge_resolvent_reduction": "CURVED_ENDO_N1_N2_REDUCED_EXACTLY_TO_FIVE_MINIMAL_VECTOR_SCALAR_RESOLVENT_CARRIERS",
        "generic_ghost_n1_n2_vector_CPT_projection": "PURE_VECTOR_N1_PLUS_N2_PROJECTED_TO_SCALAR_FLAT_CPT_CARRIER_QUOTIENT",
        "generic_ghost_longitudinal_Schur_resummation": "THREE_LONGITUDINAL_DW_CARRIERS_RESUMMED_TO_ONE_NORMALIZED_SCALAR_SCHUR_FACTOR_WITH_REGULATOR_BOUNDARY",
        "generic_ghost_Schur_Schatten_split": "SCHUR_CORRECTION_IN_S3_WITH_CANONICAL_DET3_TAIL_AND_EXACT_CRITICAL_K2_RESIDUE",
        "generic_ghost_Schur_Wodzicki_residue": "SCHUR_K_AND_LOGARITHM_WODZICKI_RESIDUES_COMPUTED",
        "generic_ghost_Schur_weighted_trace_scale": "ORDER_TWO_WEIGHTED_TRACE_POLE_AND_SCALE_RESPONSE_COMPUTED",
        "round_S4_ghost_Schur_finite_weighted_traces": "ROUND_S4_SCHUR_REFERENCE_MODIFIED_DETERMINANT_COMPUTED",
        "round_S4_ghost_Schur_zeta_factorization": "ROUND_S4_ZETA_TO_WEIGHTED_SCHUR_FACTORIZATION_DEFECT_COMPUTED",
        "product_S2_S2_ghost_Schur_spectral_carrier": "NON_EINSTEIN_PRODUCT_SPECTRUM_AND_MATCHED_ZERO_POLE_POLICY_COMPUTED",
        "product_S2_S2_ghost_Schur_det3_enclosure": "PRODUCT_S2_S2_REGULAR_SCHUR_DET3_RIGOROUSLY_ENCLOSED",
        "product_S2_S2_ghost_Schur_weighted_rows": "PRODUCT_WEIGHTED_ROWS_RIGOROUS_ENCLOSURES_COEFFICIENT_COMPUTED",
        "product_S2_S2_ghost_Schur_modified_determinant": "COUPLED_SCHUR_FACTOR_RIGOROUS_ENCLOSURE_COEFFICIENT_COMPUTED",
        "product_S2_S2_ghost_minimal_vector_carrier": "MINIMAL_VECTOR_EXACT_COEXACT_SPECTRUM_AND_PRIMING_COMPUTED",
        "product_S2_S2_ghost_minimal_vector_determinant": "MINIMAL_VECTOR_AND_FULL_WEIGHTED_GHOST_ENCLOSURES_COEFFICIENT_COMPUTED",
        "product_S2_S2_full_BV_join_boundary": "PRODUCT_GHOST_COEFFICIENT_COMPUTED_FULL_BV_JOIN_BLOCKED_BY_SAME_BACKGROUND_PHYSICAL_CARRIER",
        "generic_ghost_Schur_weight_raised_zeta_factorization": "GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_LOCAL_DEFECT_COMPUTED",
        "scalar_flat_K_Ricci_crosswalk": "K_EQUALS_RICCI_MODULO_QUADRATIC_CURVATURE_ON_SCALAR_FLAT_DOMAIN",
        "generic_ghost_n3_five_carrier_projection": "N3_GHOST_TRIANGLE_PROJECTED_TO_SCALAR_FLAT_FIVE_CARRIER_QUOTIENT",
        "generic_ghost_n3_barycentric_factorization": "GENERIC_N3_BARYCENTRIC_DENOMINATOR_AND_BOUNDARY_FACTORIZATION_COMPUTED",
        "generic_ghost_n3_pole3_relative_IBP": "GENERIC_N3_TEN_POLE3_ROWS_REDUCED_TO_TRIANGLE_DERIVATIVE_MASTERS",
        "scalar_triangle_differential_system": "COEFFICIENT_COMPUTED",
        "generic_ghost_n3_pole3_integrated_functions": "COEFFICIENT_COMPUTED",
        "generic_ghost_n3_I29_integrated_function": "COEFFICIENT_COMPUTED",
        "generic_ghost_n3_symmetric_point_simplex_integration": "COEFFICIENT_COMPUTED",
        "vacuum_cylinder_reduced_Bridge4": "BRIDGE4_CERTIFIED_ON_REDUCED_VACUUM_CYLINDER_KREIN_CARRIER_FULL_BV_EXTENSION_OPEN",
        "relative_readiness": "LINEAR_RELATIVE_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED_NONLINEAR_QME_OPEN",
    }
    for name, state in states.items():
        if values[name].get("result_state") != state:
            raise ValueError(f"active frontier dependency state drifted: {name}")
    physical_elliptic = values["physical_Euclidean_elliptic_complex"]
    physical_coefficient = values["physical_nonconformal_coefficient_match"]
    physical_breaking = values["regulated_repository_Slavnov_breaking"]
    matter_no_go = values["unitary_matter_cancellation_no_go"]
    wz_preflight = values["WZ_compensator_preflight"]
    wz_lift = values["WZ_minimal_BV_cotangent_lift"]
    wz_extended = values["WZ_extended_local_BV"]
    q1_disposition = values["one_loop_Slavnov_Q1_disposition"]
    anomaly_induced_gamma1 = values["anomaly_induced_nonlocal_Gamma1"]
    flat_tt_logarithmic_gamma1 = values["flat_TT_logarithmic_Gamma1"]
    curvature_squared_log_gamma1 = values["curvature_squared_covariant_log_Gamma1"]
    fv_conformized_log_gamma1 = values["FV_conformized_C2_log_Gamma1"]
    fv_anomaly_ricci = values["FV_anomaly_action_Ricci_sector"]
    cubic_weyl = values["algebraic_cubic_Weyl_carriers"]
    third_curvature_weyl = values["third_curvature_Weyl_manifest"]
    cpt_third_curvature = values["CPT_universal_third_curvature_kernels"]
    generic_physical_hessian_linear = values[
        "generic_physical_hessian_linear_curvature"
    ]
    generic_physical_hessian_n3_fixture = values[
        "generic_physical_hessian_n3_triangle_fixture"
    ]
    generic_physical_hessian_n3_projection = values[
        "generic_physical_hessian_n3_five_carrier_projection"
    ]
    generic_physical_hessian_n3_obstruction = values[
        "generic_physical_hessian_n3_integration_obstruction"
    ]
    generic_physical_hessian_curvature_squared = values[
        "generic_physical_hessian_curvature_squared"
    ]
    generic_physical_hessian_mixed = values[
        "generic_physical_hessian_mixed_H1_H2_corner_fixture"
    ]
    generic_physical_hessian_mellin = values[
        "generic_physical_hessian_mellin_subtraction_scale_row"
    ]
    generic_physical_hessian_volterra = values[
        "generic_physical_hessian_covariant_Volterra_carrier"
    ]
    generic_physical_hessian_contacts = values[
        "generic_physical_hessian_H1_H2_contact_residue_projection"
    ]
    generic_physical_hessian_incidence = values[
        "generic_physical_hessian_symmetric_mixed_boundary_incidence"
    ]
    generic_physical_hessian_triangle_residues = values[
        "generic_physical_hessian_triangle_corner_residues"
    ]
    generic_physical_hessian_full_incidence = values[
        "generic_physical_hessian_full_boundary_incidence"
    ]
    generic_physical_hessian_contact_finite = values[
        "generic_physical_hessian_H1_H2_contact_finite_rows"
    ]
    generic_physical_hessian_triangle_masters = values[
        "generic_physical_hessian_triangle_master_completeness"
    ]
    generic_physical_hessian_triangle_master_values = values[
        "generic_physical_hessian_triangle_renormalized_master_values"
    ]
    generic_physical_hessian_triangle_master_coordinates = values[
        "generic_physical_hessian_triangle_six_master_coordinates"
    ]
    generic_physical_hessian_triangle_boundary_flux = values[
        "generic_physical_hessian_triangle_relative_IBP_boundary_flux"
    ]
    generic_physical_hessian_form_factors = values[
        "generic_physical_hessian_third_curvature_form_factors"
    ]
    generic_physical_plus_ghost_n3 = values[
        "generic_physical_plus_ghost_n3_third_curvature_form_factors"
    ]
    generic_ghost_vector_integrated = values[
        "generic_ghost_n1_n2_vector_integrated_functions"
    ]
    generic_partial_bv = values[
        "generic_partial_BV_third_curvature_form_factors"
    ]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_longitudinal_schur = values["generic_ghost_longitudinal_Schur_resummation"]
    generic_ghost_schur_schatten = values["generic_ghost_Schur_Schatten_split"]
    generic_ghost_schur_wodzicki = values["generic_ghost_Schur_Wodzicki_residue"]
    generic_ghost_schur_scale = values["generic_ghost_Schur_weighted_trace_scale"]
    round_s4_ghost_schur_finite = values["round_S4_ghost_Schur_finite_weighted_traces"]
    round_s4_ghost_schur_zeta = values["round_S4_ghost_Schur_zeta_factorization"]
    product_s2_s2_ghost_schur = values["product_S2_S2_ghost_Schur_spectral_carrier"]
    product_s2_s2_ghost_schur_det3 = values["product_S2_S2_ghost_Schur_det3_enclosure"]
    product_s2_s2_ghost_schur_weighted = values["product_S2_S2_ghost_Schur_weighted_rows"]
    product_s2_s2_ghost_schur_modified = values["product_S2_S2_ghost_Schur_modified_determinant"]
    product_s2_s2_ghost_minimal_carrier = values["product_S2_S2_ghost_minimal_vector_carrier"]
    product_s2_s2_ghost_minimal_determinant = values["product_S2_S2_ghost_minimal_vector_determinant"]
    product_s2_s2_full_bv_join = values["product_S2_S2_full_BV_join_boundary"]
    generic_ghost_schur_weight_raised = values["generic_ghost_Schur_weight_raised_zeta_factorization"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n3_barycentric = values["generic_ghost_n3_barycentric_factorization"]
    generic_ghost_n3_relative_ibp = values["generic_ghost_n3_pole3_relative_IBP"]
    scalar_triangle_system = values["scalar_triangle_differential_system"]
    generic_ghost_n3_integrated = values["generic_ghost_n3_pole3_integrated_functions"]
    generic_ghost_n3_i29 = values["generic_ghost_n3_I29_integrated_function"]
    generic_ghost_n3_symmetric = values["generic_ghost_n3_symmetric_point_simplex_integration"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    reduced_bridge4 = values["vacuum_cylinder_reduced_Bridge4"]
    if (
        physical_elliptic.get("result_id") != "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX"
        or physical_elliptic.get("result_state")
        != "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC"
        or physical_elliptic.get("claim_flags", {}).get(
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"
        )
        is not True
    ):
        raise ValueError("physical Euclidean elliptic complex frontier drifted")
    coefficient_result = physical_coefficient.get("coefficient_result", {})
    coefficient_values = coefficient_result.get("coefficients", {})
    if (
        physical_coefficient.get("result_id")
        != "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH"
        or physical_coefficient.get("result_state")
        != "C2_VISIBLE_FULL_BV_LOCAL_COEFFICIENT_MATCHED"
        or physical_coefficient.get("claim_flags", {}).get(
            "REPOSITORY_C2_COEFFICIENT_COMPUTED"
        )
        is not True
        or coefficient_values.get("C2") != {"numerator": 199, "denominator": 30}
        or coefficient_values.get("E4") != {"numerator": -87, "denominator": 20}
        or coefficient_values.get("CdualC") != {"numerator": 0, "denominator": 1}
    ):
        raise ValueError("physical nonconformal coefficient frontier drifted")
    if (
        physical_breaking.get("result_id")
        != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
        or physical_breaking.get("analytic_route") != "EUCLIDEAN_ELLIPTIC"
        or physical_breaking.get("classification", {}).get("status") != "NONTRIVIAL"
        or physical_breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or physical_breaking.get("coefficients", {}).get("ANOM_OMEGA_C2")
        != {"numerator": 199, "denominator": 30}
        or physical_breaking.get("coefficients", {}).get("ANOM_OMEGA_E4")
        != {"numerator": -87, "denominator": 20}
    ):
        raise ValueError("regulated repository Slavnov breaking frontier drifted")
    if (
        matter_no_go.get("result_id") != "UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO"
        or matter_no_go.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or matter_no_go.get("classification", {}).get("solution_set") != "EMPTY"
        or matter_no_go.get("classification", {}).get("qme_status")
        != "REMAINS_OBSTRUCTED_IN_DECLARED_MATTER_CLASS"
    ):
        raise ValueError("unitary matter cancellation frontier drifted")
    if (
        wz_preflight.get("result_state")
        != "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN"
        or wz_preflight.get("cohomology_comparison", {}).get(
            "extended_quotient_dimension"
        )
        != 0
        or wz_preflight.get("qme_lifecycle", {}).get(
            "extended_AFN0_one_loop_breaking"
        )
        != "EXACT_REMOVABLE"
        or wz_preflight.get("qme_lifecycle", {}).get("full_extended_BV_QME")
        != "NOT_CERTIFIED"
        or wz_preflight.get("qme_lifecycle", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("Wess-Zumino compensator preflight frontier drifted")
    if (
        wz_lift.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or wz_lift.get("exact_checks", {}).get("Q_squared_zero_on_all_atoms")
        is not True
        or wz_lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
    ):
        raise ValueError("Wess-Zumino minimal-BV cotangent lift frontier drifted")
    if (
        wz_extended.get("result_state")
        != "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        or wz_extended.get("H04", {}).get("even_quotient_dimension") != 3
        or wz_extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or wz_extended.get("H14", {}).get("even_quotient_dimension") != 0
        or wz_extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or wz_extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or wz_extended.get("lifecycle", {}).get("residual_transfer")
        != "FORBIDDEN_EXTENDED_CLASSICAL_CONTRACTION_NOT_SUPPLIED"
    ):
        raise ValueError("Wess-Zumino extended local-BV frontier drifted")
    if (
        q1_disposition.get("result_state")
        != "LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED_COMPLETE_Q1_UNDERDETERMINED_RESIDUAL_TRANSFER_FORBIDDEN"
        or q1_disposition.get("finite_counterterm_ambiguity", {}).get(
            "bulk_response_rank"
        )
        != 2
        or q1_disposition.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or q1_disposition.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("one-loop Slavnov Q1 frontier drifted")
    if (
        anomaly_induced_gamma1.get("result_state")
        != "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN"
        or anomaly_induced_gamma1.get("exact_coefficient_solve", {}).get("rank") != 3
        or anomaly_induced_gamma1.get("decision", {}).get(
            "anomaly_induced_nonlocal_Gamma1"
        )
        != "CERTIFIED_CONDITIONAL_EUCLIDEAN_REPRESENTATIVE"
        or anomaly_induced_gamma1.get("decision", {}).get(
            "complete_finite_nonlocal_Gamma1"
        )
        != "NO_CERTIFIED_FUNCTIONAL"
        or anomaly_induced_gamma1.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or anomaly_induced_gamma1.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("anomaly-induced nonlocal Gamma1 frontier drifted")
    if (
        flat_tt_logarithmic_gamma1.get("result_state")
        != "FLAT_TT_UNIVERSAL_LOGARITHMIC_GAMMA1_FORM_FACTOR_CERTIFIED_FINITE_CONSTANT_AND_CURVED_COMPLETION_OPEN"
        or flat_tt_logarithmic_gamma1.get("exact_logarithmic_form_factor", {}).get(
            "logarithmic_coefficient"
        )
        != {"numerator": -199, "denominator": 60}
        or flat_tt_logarithmic_gamma1.get("exact_logarithmic_form_factor", {}).get(
            "RG_scale_response"
        )
        != {"numerator": 199, "denominator": 30}
        or flat_tt_logarithmic_gamma1.get("decision", {}).get(
            "complete_Weyl_invariant_remainder"
        )
        != "NO_CERTIFIED_FUNCTIONAL"
        or flat_tt_logarithmic_gamma1.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or flat_tt_logarithmic_gamma1.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("flat-TT logarithmic Gamma1 frontier drifted")
    if (
        curvature_squared_log_gamma1.get("result_state")
        != "COVARIANT_CURVATURE_SQUARED_C2_LOG_CERTIFIED_CUBIC_COMPLETION_AND_FINITE_NORMALIZATIONS_OPEN"
        or curvature_squared_log_gamma1.get(
            "covariant_curvature_squared_form_factor", {}
        ).get("logarithmic_coefficient")
        != {"numerator": -199, "denominator": 60}
        or curvature_squared_log_gamma1.get("operator_choice_independence", {}).get(
            "first_difference_order"
        )
        != 3
        or curvature_squared_log_gamma1.get("claim_flags", {}).get(
            "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"
        )
        is not False
        or curvature_squared_log_gamma1.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("curvature-squared covariant-log Gamma1 frontier drifted")
    if (
        fv_conformized_log_gamma1.get("result_state")
        != "FV_CONFORMIZED_C2_LOG_CARRIER_EXACTLY_WEYL_COMPLETED_INDEPENDENT_CUBIC_R2_AND_NORMALIZATION_DATA_OPEN"
        or fv_conformized_log_gamma1.get("conformized_C2_log", {}).get(
            "logarithmic_coefficient"
        )
        != {"numerator": -199, "denominator": 60}
        or fv_conformized_log_gamma1.get("decision", {}).get(
            "selected_C2_log_local_Weyl_completion"
        )
        != "CERTIFIED"
        or fv_conformized_log_gamma1.get("carrier_crosswalk", {}).get(
            "identity_status"
        )
        != "DISTINCT_CARRIERS_NO_IDENTIFICATION"
        or fv_conformized_log_gamma1.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
        )
        is not False
        or fv_conformized_log_gamma1.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("FV-conformized C2-log Gamma1 frontier drifted")
    if (
        fv_anomaly_ricci.get("result_state")
        != "FV_ANOMALY_ACTION_FIXED_RICCI_SECTOR_NOT_INDEPENDENT_CUBIC_WEYL_AND_FINITE_NORMALIZATIONS_OPEN"
        or fv_anomaly_ricci.get("decision", {}).get("FV_anomaly_action")
        != "CERTIFIED"
        or fv_anomaly_ricci.get("decision", {}).get(
            "Ricci_scalar_sector_dependence"
        )
        != "CERTIFIED"
        or fv_anomaly_ricci.get("decision", {}).get(
            "independent_nonlocal_R2_form_factor"
        )
        != "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION"
        or fv_anomaly_ricci.get("claim_flags", {}).get(
            "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"
        )
        is not False
        or fv_anomaly_ricci.get("decision", {}).get("complete_Gamma1")
        != "NO_CERTIFIED_FUNCTIONAL"
        or fv_anomaly_ricci.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
    ):
        raise ValueError("FV anomaly-action/Ricci-sector frontier drifted")
    if (
        cubic_weyl.get("decision", {}).get("zero_derivative_algebraic_C3_carriers")
        != "CERTIFIED_COMPLETE"
        or cubic_weyl.get("tensor_carriers", {}).get("parity_dimensions")
        != {"even": 1, "odd": 1}
        or cubic_weyl.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED"
        )
        is not False
    ):
        raise ValueError("algebraic cubic-Weyl carrier frontier drifted")
    if (
        third_curvature_weyl.get("raw_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 11
        or third_curvature_weyl.get("quotient_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 10
        or third_curvature_weyl.get("claim_flags", {}).get(
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "SCALAR_FLAT_I29_REVERSAL_IDENTITY_REPLAYED"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
    ):
        raise ValueError("third-curvature Weyl carrier manifest frontier drifted")
    if (
        [row.get("carrier_id") for row in cpt_third_curvature.get("universal_kernels", [])]
        != ["I10", "I24", "I25", "I28", "I29"]
        or cpt_third_curvature.get("universal_kernels", [])[-1].get("stabilizer")
        != "S3"
        or cpt_third_curvature.get("claim_flags", {}).get(
            "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED"
        )
        is not True
        or cpt_third_curvature.get("claim_flags", {}).get(
            "SOURCE_SCALAR_FIXTURE_COEFFICIENTS_COMPUTED"
        )
        is not True
        or cpt_third_curvature.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or cpt_third_curvature.get("repository_matching_audit", {}).get("verdict")
        != "NO_REPOSITORY_FORM_FACTOR_COEFFICIENT_CAN_BE_INFERRED_FROM_THE_CURRENT_SPECIAL_BACKGROUND_LEDGER"
    ):
        raise ValueError("universal CPT third-curvature kernel frontier drifted")
    physical_linear_rows = generic_physical_hessian_linear.get(
        "source_operator", {}
    ).get("coefficient_rows", {})
    physical_linear_flags = generic_physical_hessian_linear.get("claim_flags", {})
    if (
        generic_physical_hessian_linear.get("gauge_crosswalk", {}).get("same_gauge")
        is not True
        or generic_physical_hessian_linear.get("traceless_projector", {}).get(
            "projected_traceless_rank"
        )
        != 9
        or {name: len(rows) for name, rows in physical_linear_rows.items()}
        != {"N_lambda": 8, "U": 5, "V_rho_sigma": 9}
        or generic_physical_hessian_linear.get("repository_normalization", {}).get(
            "repository_functional_Hessian"
        )
        != "H_repository=(1/2)H_source"
        or generic_physical_hessian_linear.get("scalar_flat_restriction", {}).get(
            "surviving_term_counts"
        )
        != {"N_lambda": 6, "U": 3, "V_rho_sigma": 7}
        or generic_physical_hessian_linear.get(
            "round_S4_linear_crosscheck", {}
        ).get("missing_curvature_squared_fixture")
        != "source monic +8 K^2, equivalently repository functional-Hessian +4 K^2"
        or generic_physical_hessian_linear.get(
            "third_curvature_applicability", {}
        ).get("status")
        != "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"
        or physical_linear_flags.get("SAME_GAUGE_CROSSWALK_CERTIFIED") is not True
        or physical_linear_flags.get("LINEAR_CURVATURE_V_N_U_IMPORTED") is not True
        or physical_linear_flags.get(
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"
        )
        is not True
        or physical_linear_flags.get("FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED")
        is not False
        or physical_linear_flags.get(
            "CURVATURE_SQUARED_ZERO_ORDER_LAYER_SUPPLIED"
        )
        is not False
        or physical_linear_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED") is not False
    ):
        raise ValueError("generic physical-Hessian linear-curvature frontier drifted")
    physical_n3_fixture_flags = generic_physical_hessian_n3_fixture.get(
        "claim_flags", {}
    )
    physical_n3_fixture = generic_physical_hessian_n3_fixture.get(
        "exact_interior_fixture", {}
    )
    if (
        physical_n3_fixture_flags.get("PHYSICAL_H1_MOMENTUM_VERTEX_CONSTRUCTED")
        is not True
        or physical_n3_fixture_flags.get(
            "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED"
        )
        is not True
        or physical_n3_fixture_flags.get(
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED"
        )
        is not True
        or physical_n3_fixture_flags.get("PHYSICAL_N3_FULL_ALPHA_POLYNOMIAL_COMPUTED")
        is not False
        or physical_n3_fixture_flags.get("PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED")
        is not False
        or physical_n3_fixture_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED")
        is not False
        or physical_n3_fixture.get("Delta")
        != {"numerator": 104, "denominator": 45}
        or physical_n3_fixture.get("formal_adjoint_check", {}).get(
            "completed_vertex_defect_count"
        )
        != 0
        or physical_n3_fixture.get("loop_trace", {}).get("monomial_count") != 210
        or physical_n3_fixture.get("nonzero") is not True
    ):
        raise ValueError("generic physical-Hessian n=3 fixture frontier drifted")
    physical_n3_projection_flags = generic_physical_hessian_n3_projection.get(
        "claim_flags", {}
    )
    physical_n3_interpolation = generic_physical_hessian_n3_projection.get(
        "interpolation_certificate", {}
    )
    if (
        physical_n3_projection_flags.get(
            "PHYSICAL_N3_FULL_ALPHA_POLYNOMIAL_COMPUTED"
        )
        is not True
        or physical_n3_projection_flags.get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or physical_n3_projection_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED")
        is not False
        or physical_n3_projection_flags.get("CURVATURE_SQUARED_H2_IMPORTED")
        is not False
        or physical_n3_interpolation.get("training_fixture_count") != 28
        or physical_n3_interpolation.get("degree_six_box_evaluation_rank_mod_prime")
        != 28
        or physical_n3_interpolation.get("unseen_fixture_count") != 2
    ):
        raise ValueError("generic physical-Hessian n=3 projection frontier drifted")
    if (
        generic_physical_hessian_n3_obstruction.get("relative_quotient", {}).get(
            "symmetric_point_relative_IBP_plus_master_rank"
        )
        != 49
        or generic_physical_hessian_n3_obstruction.get("relative_quotient", {}).get(
            "M14_augmented_rank"
        )
        != 50
        or generic_physical_hessian_n3_obstruction.get("corner_asymptotic", {}).get(
            "total_log_1_over_epsilon_coefficient"
        )
        != {"numerator": 1, "denominator": 2}
        or len(
            generic_physical_hessian_n3_obstruction.get(
                "nonzero_obstruction_channels", []
            )
        )
        != 8
        or generic_physical_hessian_n3_obstruction.get("claim_flags", {}).get(
            "H2_CANCELLATION_OF_CORNER_CLASS_PROVED"
        )
        is not False
    ):
        raise ValueError("physical-Hessian n=3 integration obstruction frontier drifted")
    physical_h2_flags = generic_physical_hessian_curvature_squared.get(
        "claim_flags", {}
    )
    if (
        physical_h2_flags.get("ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED")
        is not True
        or physical_h2_flags.get("GAUGE_ORDERING_COMMUTATOR_CROSSWALK_CERTIFIED")
        is not True
        or physical_h2_flags.get("ROUND_S4_H2_COMMUTATOR_SPLIT_CERTIFIED")
        is not True
        or physical_h2_flags.get("PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED")
        is not False
        or generic_physical_hessian_curvature_squared.get(
            "scalar_flat_restriction", {}
        ).get("effective_term_count")
        != 9
        or generic_physical_hessian_curvature_squared.get(
            "round_S4_crosscheck", {}
        ).get("sum")
        != "+24 K^2-16 K^2=+8 K^2"
    ):
        raise ValueError("physical-Hessian curvature-squared frontier drifted")
    physical_mixed_flags = generic_physical_hessian_mixed.get("claim_flags", {})
    if (
        physical_mixed_flags.get(
            "OPERATIONAL_SCALAR_FLAT_H2_POLARIZATION_CONSTRUCTED"
        )
        is not True
        or physical_mixed_flags.get(
            "RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE"
        )
        is not True
        or physical_mixed_flags.get("RENORMALIZED_SUBTRACTION_FIXED") is not False
        or physical_mixed_flags.get("PHYSICAL_M14_CORNER_CLASS_DISPOSED")
        is not False
        or generic_physical_hessian_mixed.get("combined_raw_logarithm", {}).get(
            "sum"
        )
        != {"numerator": 15707, "denominator": 216}
    ):
        raise ValueError("physical-Hessian mixed H1-H2 frontier drifted")
    mellin_flags = generic_physical_hessian_mellin.get("claim_flags", {})
    if (
        mellin_flags.get("FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED")
        is not True
        or mellin_flags.get("FIXTURE_SCALE_ROW_COMPUTED") is not True
        or mellin_flags.get("GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED")
        is not False
        or mellin_flags.get("PHYSICAL_M14_CORNER_CLASS_DISPOSED") is not False
        or generic_physical_hessian_mellin.get("renormalization_scale_row", {}).get(
            "coefficient"
        )
        != {"numerator": 15707, "denominator": 216}
    ):
        raise ValueError("physical-Hessian Mellin subtraction frontier drifted")
    volterra_flags = generic_physical_hessian_volterra.get("claim_flags", {})
    if (
        volterra_flags.get("GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED")
        is not True
        or volterra_flags.get("COMMON_MELLIN_BOUNDARY_EXTENSION_DEFINED")
        is not True
        or volterra_flags.get("GENERIC_TENSOR_KERNELS_EVALUATED") is not False
        or volterra_flags.get("RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED")
        is not False
        or volterra_flags.get("PHYSICAL_M14_CORNER_CLASS_DISPOSED") is not False
        or generic_physical_hessian_volterra.get("decorated_carrier", {}).get(
            "ordered_triangle_cell_count"
        )
        != 6
        or generic_physical_hessian_volterra.get("decorated_carrier", {}).get(
            "mixed_contact_cell_count"
        )
        != 3
    ):
        raise ValueError("physical-Hessian covariant Volterra frontier drifted")
    contact_flags = generic_physical_hessian_contacts.get("claim_flags", {})
    if (
        contact_flags.get("GENERIC_H1_H2_CONTACT_ENDPOINT_KERNELS_EVALUATED")
        is not True
        or contact_flags.get("ALL_THREE_CONTACT_CELLS_PROJECTED") is not True
        or contact_flags.get("LEFT_RIGHT_ENDPOINT_EQUALITY_CERTIFIED") is not True
        or contact_flags.get("SYMMETRIC_I28_QUOTIENT_SECTION_PRESERVED")
        is not True
        or contact_flags.get("RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED")
        is not False
        or contact_flags.get("PHYSICAL_M14_CORNER_CLASS_DISPOSED") is not False
        or generic_physical_hessian_contacts.get("interpolation", {}).get(
            "row_count"
        )
        != 33
        or generic_physical_hessian_contacts.get("equal_box_regression", {}).get(
            "combined_all_contacts"
        )
        != {"numerator": 2704, "denominator": 27}
    ):
        raise ValueError("physical-Hessian H1-H2 contact frontier drifted")
    incidence_flags = generic_physical_hessian_incidence.get("claim_flags", {})
    if (
        incidence_flags.get("SYMMETRIC_POINT_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED")
        is not True
        or incidence_flags.get("SYMMETRIC_POINT_H2_CANCELLATION_OF_M14_REFUTED")
        is not True
        or incidence_flags.get("GENERIC_BOX_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED")
        is not False
        or incidence_flags.get("GENERIC_PHYSICAL_M14_DISPOSED") is not False
        or generic_physical_hessian_incidence.get(
            "equal_box_tensor_reconstruction", {}
        ).get("combined_log_mu2_coefficient")
        != {"numerator": 15707, "denominator": 216}
        or generic_physical_hessian_incidence.get("M14_disposition", {}).get(
            "generic_box_disposition"
        )
        != "NOT_COMPUTED"
    ):
        raise ValueError("physical-Hessian symmetric mixed incidence frontier drifted")
    triangle_residue_flags = generic_physical_hessian_triangle_residues.get("claim_flags", {})
    full_incidence_flags = generic_physical_hessian_full_incidence.get("claim_flags", {})
    if (
        triangle_residue_flags.get("GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED")
        is not True
        or triangle_residue_flags.get("FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED")
        is not False
        or generic_physical_hessian_triangle_residues.get("regressions", {}).get(
            "symmetric_obstruction_rows_matched"
        )
        != 11
        or full_incidence_flags.get("FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED")
        is not True
        or full_incidence_flags.get("GENERIC_PHYSICAL_M14_DISPOSED") is not True
        or full_incidence_flags.get("GENERIC_PHYSICAL_M14_NONZERO_SCALE_ROW")
        is not True
        or full_incidence_flags.get("FINITE_LOCAL_MIXED_ROWS_FIXED") is not False
        or generic_physical_hessian_full_incidence.get("generic_disposition", {}).get("M14")
        != "NONZERO_SCALE_ROW_RENORMALIZED_BY_COMMON_MELLIN_EXTENSION"
        or generic_physical_hessian_full_incidence.get("exact_fixture_replay", {}).get("combined")
        != {"numerator": 15707, "denominator": 216}
    ):
        raise ValueError("physical-Hessian full generic incidence frontier drifted")
    contact_finite_flags = generic_physical_hessian_contact_finite.get(
        "claim_flags", {}
    )
    if (
        contact_finite_flags.get(
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED"
        )
        is not True
        or contact_finite_flags.get("ALL_THREE_CONTACT_FINITE_ROWS_PROJECTED")
        is not True
        or contact_finite_flags.get("GENERIC_I28_QUOTIENT_RELATION_PRESERVED")
        is not True
        or contact_finite_flags.get("FINITE_COUNTERTERM_NORMALIZATION_FIXED")
        is not False
        or contact_finite_flags.get("RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED")
        is not False
        or generic_physical_hessian_contact_finite.get("interpolation", {}).get(
            "row_count"
        )
        != 33
        or generic_physical_hessian_contact_finite.get(
            "equal_box_regression", {}
        ).get("combined_contact_finite_value")
        != {"numerator": 3188, "denominator": 27}
    ):
        raise ValueError("physical-Hessian finite H1-H2 contact frontier drifted")
    triangle_master_flags = generic_physical_hessian_triangle_masters.get(
        "claim_flags", {}
    )
    if (
        triangle_master_flags.get("M14_SINGLET_REQUIRED") is not True
        or triangle_master_flags.get("STANDARD_S3_MASTER_PAIR_REQUIRED")
        is not True
        or triangle_master_flags.get("ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN")
        is not True
        or triangle_master_flags.get("GENERIC_MASTER_SPAN_RANK_52") is not True
        or triangle_master_flags.get("RENORMALIZED_SIX_MASTER_VALUES_COMPUTED")
        is not False
        or [row.get("generic_augmented_rank") for row in generic_physical_hessian_triangle_masters.get("physical_channel_rows", [])]
        != [52] * 11
    ):
        raise ValueError("physical-Hessian triangle master-completeness frontier drifted")
    triangle_master_value_flags = generic_physical_hessian_triangle_master_values.get(
        "claim_flags", {}
    )
    if (
        triangle_master_value_flags.get("RENORMALIZED_M14_SINGLET_VALUE_COMPUTED")
        is not True
        or triangle_master_value_flags.get(
            "RENORMALIZED_STANDARD_S3_PAIR_VALUES_COMPUTED"
        )
        is not True
        or triangle_master_value_flags.get("RENORMALIZED_SIX_MASTER_VALUES_COMPUTED")
        is not True
        or triangle_master_value_flags.get(
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        )
        is not False
        or triangle_master_value_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED")
        is not False
        or len(generic_physical_hessian_triangle_master_values.get("master_rows", []))
        != 3
    ):
        raise ValueError("physical-Hessian renormalized triangle-master frontier drifted")
    triangle_coordinate_flags = generic_physical_hessian_triangle_master_coordinates.get(
        "claim_flags", {}
    )
    if (
        triangle_coordinate_flags.get(
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        )
        is not True
        or triangle_coordinate_flags.get("ALL_ELEVEN_CHANNELS_COORDINATED")
        is not True
        or triangle_coordinate_flags.get(
            "PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"
        )
        is not False
        or triangle_coordinate_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED")
        is not False
        or len(generic_physical_hessian_triangle_master_coordinates.get("channel_rows", []))
        != 11
    ):
        raise ValueError("physical-Hessian triangle-coordinate frontier drifted")
    triangle_flux_flags = generic_physical_hessian_triangle_boundary_flux.get(
        "claim_flags", {}
    )
    if (
        triangle_flux_flags.get("PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED")
        is not True
        or triangle_flux_flags.get("PHYSICAL_N3_TRIANGLE_INTEGRATED") is not True
        or triangle_flux_flags.get(
            "PHYSICAL_N3_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED"
        )
        is not True
        or triangle_flux_flags.get("ALL_ELEVEN_CHANNELS_INTEGRATED") is not True
        or triangle_flux_flags.get("REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED")
        is not False
        or len(generic_physical_hessian_triangle_boundary_flux.get("channel_rows", []))
        != 11
    ):
        raise ValueError("physical-Hessian triangle boundary-flux frontier drifted")
    form_factor_flags = generic_physical_hessian_form_factors.get("claim_flags", {})
    if (
        form_factor_flags.get("FIVE_PHYSICAL_CARRIER_FUNCTIONS_ASSEMBLED") is not True
        or form_factor_flags.get(
            "PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED"
        )
        is not True
        or form_factor_flags.get("ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED") is not False
        or form_factor_flags.get("FULL_BV_FORM_FACTORS_COMPUTED") is not False
        or generic_physical_hessian_form_factors.get("quotient_ledger", {}).get(
            "quotient_dimension"
        )
        != 10
    ):
        raise ValueError("physical-Hessian form-factor frontier drifted")
    partial_bv_flags = generic_physical_plus_ghost_n3.get("claim_flags", {})
    if (
        partial_bv_flags.get(
            "PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED"
        )
        is not True
        or partial_bv_flags.get("GHOST_N1_INSERTION_TRACE_COMPUTED") is not False
        or partial_bv_flags.get("GHOST_N2_INSERTION_TRACE_COMPUTED") is not False
        or partial_bv_flags.get("GENERIC_FINITE_SCHUR_ROWS_COMPUTED") is not False
        or partial_bv_flags.get("FULL_BV_FORM_FACTORS_COMPUTED") is not False
        or generic_physical_plus_ghost_n3.get("quotient_ledger", {}).get(
            "quotient_dimension"
        )
        != 10
    ):
        raise ValueError("physical-plus-ghost-n3 frontier drifted")
    ghost_vector_flags = generic_ghost_vector_integrated.get("claim_flags", {})
    if (
        ghost_vector_flags.get(
            "GENERIC_GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED"
        )
        is not True
        or ghost_vector_flags.get("NO_NEW_TRANSCENDENTAL_MASTER_REQUIRED")
        is not True
        or ghost_vector_flags.get("GENERIC_GHOST_LONGITUDINAL_CARRIERS_EVALUATED")
        is not False
        or generic_ghost_vector_integrated.get("identity_ledger", {}).get(
            "nonzero_channel_count"
        )
        != 6
        or generic_ghost_vector_integrated.get("identity_ledger", {}).get(
            "zero_channel_count"
        )
        != 5
    ):
        raise ValueError("integrated ghost-vector n1+n2 frontier drifted")
    generic_partial_bv_flags = generic_partial_bv.get("claim_flags", {})
    if (
        generic_partial_bv_flags.get(
            "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED"
        )
        is not True
        or generic_partial_bv_flags.get("GHOST_VECTOR_N1_N2_INCLUDED") is not True
        or generic_partial_bv_flags.get("GHOST_LONGITUDINAL_CARRIERS_INCLUDED")
        is not False
        or generic_partial_bv_flags.get("FULL_BV_FORM_FACTORS_COMPUTED")
        is not False
        or generic_partial_bv.get("quotient_ledger", {}).get("quotient_dimension")
        != 10
    ):
        raise ValueError("partial-BV third-curvature frontier drifted")
    if (
        generic_ghost_cpt.get("CPT_applicability_decision", {}).get("verdict")
        != "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED"
        or generic_ghost_cpt.get("algebraic_Weyl_ghost_elimination", {}).get(
            "effective_vector_operator"
        )
        != "M_eff xi_mu=Box xi_mu+Ric_mu_nu xi^nu+(1/2)nabla_mu div(xi)"
        or generic_ghost_cpt.get("nonminimal_principal_symbol", {}).get("Laplace_type")
        is not False
        or generic_ghost_cpt.get("generic_Hodge_mixing", {}).get(
            "longitudinal_subspace_preserved"
        )
        is not False
        or generic_ghost_cpt.get("generic_Hodge_mixing", {}).get(
            "Einstein_scalar_factor_reproduced"
        )
        != "Delta_0-R/3"
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic-background ghost CPT obstruction frontier drifted")
    if (
        generic_ghost_endo.get("exact_Endo_split", {}).get("local_perturbation")
        != "W=-2 Ric"
        or generic_ghost_endo.get("exact_Endo_heat_kernel", {}).get(
            "proper_time_upper_multiplier"
        )
        != {"numerator": 3, "denominator": 2}
        or generic_ghost_endo.get("Duhamel_expansion", {}).get(
            "maximum_W_insertions_through_cubic_order"
        )
        != 3
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED"
        )
        is not True
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED"
        )
        is not False
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost Endo-Duhamel reduction frontier drifted")
    if (
        generic_ghost_n1_n2.get("proper_time_to_resolvent", {}).get(
            "resolvent_identity"
        )
        != "G_H0=G_F-(1/3)d Delta_0^-2 delta"
        or generic_ghost_n1_n2.get("log_determinant_expansion", {}).get(
            "carrier_count"
        )
        != 5
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED"
        )
        is not True
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED"
        )
        is not True
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=1/n=2 Hodge-resolvent frontier drifted")
    if (
        generic_ghost_n1_n2_vector.get("minimal_operator_sign_flip", {}).get(
            "surviving_rows"
        )
        != [1, 3, 14]
        or generic_ghost_n1_n2_vector.get("minimal_operator_sign_flip", {}).get(
            "n1_plus_n2_formula"
        )
        != "6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14"
        or generic_ghost_n1_n2_vector.get(
            "minimal_missing_carrier_theorem", {}
        ).get("missing_carriers")
        != [
            "N1_LONGITUDINAL_SCALAR",
            "N2_VECTOR_LONGITUDINAL",
            "N2_LONGITUDINAL_LONGITUDINAL",
        ]
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"
        )
        is not False
    ):
        raise ValueError("generic ghost vector n=1/n=2 CPT projection frontier drifted")
    if (
        generic_ghost_longitudinal_schur.get(
            "exact_determinant_factorization", {}
        ).get("normalized_scalar_Schur_operator")
        != "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d"
        or generic_ghost_longitudinal_schur.get(
            "regularization_boundary", {}
        ).get("zeta_multiplicative_anomaly")
        != "LOCAL_TERM_NOT_EVALUATED"
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED"
        )
        is not True
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION"
        )
        is not True
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "GENERIC_LONGITUDINAL_SCHUR_FORM_FACTORS_COMPUTED"
        )
        is not False
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED"
        )
        is not False
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED"
        )
        is not False
    ):
        raise ValueError("generic ghost longitudinal Schur frontier drifted")
    if (
        generic_ghost_schur_schatten.get("sharp_ideal_classification", {}).get(
            "minimal_modified_determinant_order"
        )
        != 3
        or generic_ghost_schur_schatten.get("critical_local_residue", {}).get(
            "Ricci_basis"
        )
        != "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "SCHUR_CORRECTION_S3_CLASS_PROVED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "CANONICAL_DET3_TAIL_DEFINED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"
        )
        is not False
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost Schur Schatten frontier drifted")
    if (
        generic_ghost_schur_wodzicki.get("exact_residues", {}).get(
            "K_Ricci_basis"
        )
        != "Wres(K)=(4 pi)^-2 integral[R^2+4 Ric_mn Ric^mn]/9"
        or generic_ghost_schur_wodzicki.get("exact_residues", {}).get(
            "log_S_Ricci_basis"
        )
        != "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "WODZICKI_RESIDUE_K_COMPUTED"
        )
        is not True
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "WODZICKI_RESIDUE_LOG_S_COMPUTED"
        )
        is not True
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "RENORMALIZED_R_K_COMPUTED"
        )
        is not False
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "FINITE_PART_R_K2_COMPUTED"
        )
        is not False
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "ZETA_SCALE_COEFFICIENT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost Schur Wodzicki frontier drifted")
    if (
        generic_ghost_schur_scale.get("Schur_determinant_scale_row", {}).get(
            "Ricci_basis"
        )
        != "d/dlog(mu) log Det_(3,R_mu)(S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
        or generic_ghost_schur_scale.get("exact_conversion", {}).get(
            "scale_to_weight_order_ratio"
        )
        != {"numerator": 1, "denominator": 1}
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "SCHUR_SCALE_COEFFICIENT_COMPUTED"
        )
        is not True
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "REFERENCE_FINITE_R_K_COMPUTED"
        )
        is not False
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "REFERENCE_FINITE_R_K2_COMPUTED"
        )
        is not False
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost Schur weighted-trace scale frontier drifted")
    if (
        round_s4_ghost_schur_finite.get("exact_finite_rows", {})
        .get("Delta_weighted_finite_rows", {})
        .get("R_Delta_K", {})
        .get("exact")
        != "-20/9-(8/3)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]"
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "ROUND_S4_R_DELTA_K_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "ROUND_S4_FINITE_R_DELTA_K2_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "FULL_ROUND_S4_DET3_TAIL_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "FULL_ROUND_S4_MODIFIED_DETERMINANT_COMPUTED"
        )
        is not True
        or not round_s4_ghost_schur_finite.get("exact_finite_rows", {})
        .get("canonical_det3_tail", {})
        .get("certified_common_decimal_prefix", "")
        .startswith("0.4981635654196290984312532999414818723861")
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "GENERIC_BACKGROUND_R_K_COMPUTED"
        )
        is not False
        or round_s4_ghost_schur_finite.get("generic_missing_input_theorem", {}).get(
            "status"
        )
        != "MINIMAL_MISSING_GLOBAL_CARRIER_THEOREM"
    ):
        raise ValueError("round-S4 ghost Schur finite weighted-trace frontier drifted")
    if (
        round_s4_ghost_schur_zeta.get("local_residue_derivation", {}).get(
            "exact_factorization_defect"
        )
        != {"numerator": 5, "denominator": 3}
        or not round_s4_ghost_schur_zeta.get("factorization_result", {}).get(
            "zeta_determinant_ratio_decimal", ""
        ).startswith("-2.311478818948744960808728888139320253")
        or round_s4_ghost_schur_zeta.get("claim_flags", {}).get(
            "ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_zeta.get("claim_flags", {}).get(
            "GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("round-S4 ghost Schur zeta-factorization frontier drifted")
    if (
        product_s2_s2_ghost_schur.get("primed_mode_policy", {}).get(
            "total_exceptional_correction"
        )
        != "3^-6"
        or product_s2_s2_ghost_schur.get("finite_cutoff_fixture", {}).get(
            "exceptional_matched_dimension"
        )
        != 6
        or product_s2_s2_ghost_schur.get("residue_crosscheck", {}).get(
            "fixture_value"
        )
        != {"numerator": 28, "denominator": 27}
        or product_s2_s2_ghost_schur.get("claim_flags", {}).get(
            "PRODUCT_SPECTRAL_MEASURE_SUPPLIED"
        )
        is not True
        or product_s2_s2_ghost_schur.get("claim_flags", {}).get(
            "FULL_COUPLED_GHOST_DETERMINANT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("product-S2xS2 ghost Schur spectral frontier drifted")
    if (
        not product_s2_s2_ghost_schur_det3.get("det3_enclosure", {}).get(
            "certified_common_decimal_prefix", ""
        ).startswith("0.3263039")
        or product_s2_s2_ghost_schur_det3.get("claim_flags", {}).get(
            "PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"
        )
        is not True
        or product_s2_s2_ghost_schur_det3.get("claim_flags", {}).get(
            "PRODUCT_WEIGHTED_R_K_COMPUTED"
        )
        is not False
        or product_s2_s2_ghost_schur_det3.get("claim_flags", {}).get(
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("product-S2xS2 ghost Schur det3 frontier drifted")
    if (
        not product_s2_s2_ghost_schur_weighted.get("weighted_rows", {}).get(
            "R_Delta_K", {}
        ).get("lower", "").startswith("-2.2406602690")
        or not product_s2_s2_ghost_schur_weighted.get("weighted_rows", {}).get(
            "FP_R_Delta_K2", {}
        ).get("upper", "").startswith("1.9669718542")
        or product_s2_s2_ghost_schur_weighted.get("claim_flags", {}).get(
            "PRODUCT_WEIGHTED_ROW_RIGOROUS_ENCLOSURES_DERIVED"
        )
        is not True
        or product_s2_s2_ghost_schur_weighted.get("claim_flags", {}).get(
            "PRODUCT_WEIGHTED_R_K_COMPUTED"
        )
        is not True
        or product_s2_s2_ghost_schur_weighted.get("claim_flags", {}).get(
            "PRODUCT_FINITE_PART_R_K2_COMPUTED"
        )
        is not True
        or product_s2_s2_ghost_schur_weighted.get(
            "tier3_promotion_receipt", {}
        ).get("tests_run")
        != 850
    ):
        raise ValueError("product-S2xS2 ghost Schur weighted-row frontier drifted")
    if (
        not product_s2_s2_ghost_schur_modified.get("directed_enclosures", {}).get(
            "coupled_schur_log", {}
        ).get("lower", "").startswith("-9.4895160141")
        or product_s2_s2_ghost_schur_modified.get("claim_flags", {}).get(
            "MATCHED_EXCEPTIONAL_COUPLED_SCHUR_ENCLOSURE_DERIVED"
        )
        is not True
        or product_s2_s2_ghost_schur_modified.get(
            "tier3_promotion_receipt", {}
        ).get("status")
        != "PASSED"
    ):
        raise ValueError("product-S2xS2 ghost Schur assembly frontier drifted")
    if (
        product_s2_s2_ghost_minimal_carrier.get("claim_flags", {}).get(
            "PRODUCT_MINIMAL_VECTOR_MODE_CARRIER_SUPPLIED"
        )
        is not True
        or product_s2_s2_ghost_minimal_carrier.get("claim_flags", {}).get(
            "MINIMAL_VECTOR_ZETA_WEIGHTED_LOCAL_DEFECT_COMPUTED"
        )
        is not True
        or not product_s2_s2_ghost_minimal_determinant.get(
            "directed_enclosures", {}
        ).get("full_vector_plus_schur_weighted", {}).get("lower", "").startswith(
            "19.0791598956"
        )
        or product_s2_s2_ghost_minimal_determinant.get("claim_flags", {}).get(
            "FULL_VECTOR_PLUS_SCHUR_WEIGHTED_ENCLOSURE_DERIVED"
        )
        is not True
        or product_s2_s2_ghost_minimal_determinant.get("claim_flags", {}).get(
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"
        )
        is not True
        or product_s2_s2_ghost_minimal_determinant.get(
            "tier3_promotion_receipt", {}
        ).get("status")
        != "PASSED"
    ):
        raise ValueError("product-S2xS2 ghost minimal-vector determinant frontier drifted")
    if (
        product_s2_s2_full_bv_join.get("scope_comparison", {}).get("same_background")
        is not False
        or product_s2_s2_full_bv_join.get("join_decision", {}).get(
            "round_full_BV_rows_can_be_reused_on_product"
        )
        is not False
        or product_s2_s2_full_bv_join.get("claim_flags", {}).get(
            "PRODUCT_FULL_BV_DETERMINANT_COMPUTED"
        )
        is not False
        or product_s2_s2_full_bv_join.get("minimal_missing_carrier", {}).get(
            "primary"
        )
        != "PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER"
    ):
        raise ValueError("product-S2xS2 full-BV join boundary drifted")
    if (
        generic_ghost_schur_weight_raised.get("generic_local_result", {}).get(
            "coefficient_of_(4pi)^-2_integral_R2"
        )
        != {"numerator": -1, "denominator": 108}
        or generic_ghost_schur_weight_raised.get("generic_local_result", {}).get(
            "coefficient_of_(4pi)^-2_integral_Ric2"
        )
        != {"numerator": -1, "denominator": 54}
        or generic_ghost_schur_weight_raised.get("round_S4_crosscheck", {}).get(
            "weight_raised_defect"
        )
        != {"numerator": -1, "denominator": 3}
        or generic_ghost_schur_weight_raised.get("factorization_convention_crosswalk", {}).get(
            "difference_of_defects"
        )
        != {"numerator": 2, "denominator": 1}
        or generic_ghost_schur_weight_raised.get("claim_flags", {}).get(
            "GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost weight-raised zeta-factorization frontier drifted")
    if (
        generic_ghost_n3.get("angular_average", {}).get("coefficients", {}).get(
            "tr_R3"
        )
        != {"numerator": 503, "denominator": 648}
        or generic_ghost_n3.get("three_insertion_log_term", {}).get(
            "coefficients", {}
        ).get("tr_R3")
        != {"numerator": -503, "denominator": 243}
        or generic_ghost_n3.get("radial_and_momentum_status", {}).get(
            "full_nonzero_external_momentum_triangle"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3.get("carrier_crosswalk", {}).get(
            "repository_I10_normalization_map"
        )
        != "NO_CERTIFIED_MAP"
        or generic_ghost_n3.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED"
        )
        is not True
        or generic_ghost_n3.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 adiabatic carrier frontier drifted")
    if (
        generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "sector_count"
        )
        != 8
        or generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "total_Wick_rows"
        )
        != 20
        or generic_ghost_n3_triangle.get("carrier_projection", {}).get(
            "repository_five_carrier_projection"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3_triangle.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"
        )
        is not True
        or generic_ghost_n3_triangle.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 triangle kernel frontier drifted")
    if (
        scalar_flat_k_ricci.get("linear_crosswalk", {}).get("identity")
        != "K_munu=Ric_munu+O(curvature^2)"
        or scalar_flat_k_ricci.get("cubic_order_counting", {}).get(
            "first_replacement_error_order"
        )
        != 4
        or scalar_flat_k_ricci.get("five_carrier_target", {}).get("carrier_ids")
        != ["I10", "I24", "I25", "I28", "I29"]
        or scalar_flat_k_ricci.get("five_carrier_target", {}).get(
            "projection_status"
        )
        != "NOT_COMPUTED"
        or scalar_flat_k_ricci.get("claim_flags", {}).get(
            "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED"
        )
        is not True
        or scalar_flat_k_ricci.get("claim_flags", {}).get(
            "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED"
        )
        is not True
    ):
        raise ValueError("scalar-flat K/Ricci crosswalk frontier drifted")
    if (
        generic_ghost_n3_projection.get("quotient_section", {}).get(
            "raw_effective_channel_count"
        )
        != 11
        or generic_ghost_n3_projection.get("quotient_section", {}).get(
            "quotient_dimension"
        )
        != 10
        or len(generic_ghost_n3_projection.get("projection_rows", [])) != 11
        or generic_ghost_n3_projection.get("coefficient_disposition", {}).get(
            "ghost_n3_five_carrier_parametric_contribution"
        )
        != "COMPUTED"
        or generic_ghost_n3_projection.get("coefficient_disposition", {}).get(
            "ghost_n1_curved_Endo_trace"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3_projection.get("coefficient_disposition", {}).get(
            "ghost_n2_curved_Endo_trace"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 five-carrier projection frontier drifted")
    if (
        generic_ghost_n3_symmetric.get("scope", {}).get("kinematic_point")
        != {"x1": 1, "x2": 1, "x3": 1}
        or len(generic_ghost_n3_symmetric.get("channel_rows", [])) != 11
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED"
        )
        is not True
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 symmetric-point integration frontier drifted")
    if (
        generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_exact_Delta_factor"
        )
        != 10
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_nonzero_direct_open_edge_restriction"
        )
        != ["I10_123"]
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "minimum_vertex_integrability_margin"
        )
        != 1
        or generic_ghost_n3_barycentric.get("claim_flags", {}).get(
            "GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 barycentric factorization frontier drifted")
    if (
        len(generic_ghost_n3_relative_ibp.get("channel_rows", [])) != 10
        or generic_ghost_n3_relative_ibp.get("rank_ledger", {}).get(
            "open_edge_tangent_plus_master_and_targets_rank"
        )
        != 30
        or generic_ghost_n3_relative_ibp.get("rank_ledger", {}).get(
            "corner_zero_tangent_plus_master_rank"
        )
        != 26
        or any(
            row.get("augmented_rank") != 27
            for row in generic_ghost_n3_relative_ibp.get("rank_ledger", {}).get(
                "corner_zero_augmented_ranks", []
            )
        )
        or generic_ghost_n3_relative_ibp.get("claim_flags", {}).get(
            "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS"
        )
        is not True
        or generic_ghost_n3_relative_ibp.get("claim_flags", {}).get(
            "I29_POLE4_REDUCED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 pole-three relative-IBP frontier drifted")
    if (
        scalar_triangle_system.get("claim_flags", {}).get(
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"
        )
        is not True
        or scalar_triangle_system.get("claim_flags", {}).get(
            "TWO_LOG_MASTER_REDUCTION_COMPUTED"
        )
        is not True
        or scalar_triangle_system.get("claim_flags", {}).get(
            "EQUAL_WEIGHT_CORNER_ANGULAR_SUM_COMPUTED"
        )
        is not True
        or len(generic_ghost_n3_integrated.get("channel_rows", [])) != 10
        or generic_ghost_n3_integrated.get("identity_ledger", {}).get(
            "symmetric_point_regression_status"
        )
        != "ALL_EXACT_MATCH"
        or generic_ghost_n3_integrated.get("claim_flags", {}).get(
            "TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED"
        )
        is not True
        or generic_ghost_n3_integrated.get("claim_flags", {}).get(
            "CORNER_ANGULAR_FLUXES_EVALUATED"
        )
        is not True
        or generic_ghost_n3_integrated.get("claim_flags", {}).get(
            "I29_POLE4_REDUCED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 pole-three integrated-function frontier drifted")
    if (
        generic_ghost_n3_i29.get("rank_ledger", {}).get("tangent_rank") != 46
        or generic_ghost_n3_i29.get("rank_ledger", {}).get(
            "tangent_plus_masters_rank"
        )
        != 49
        or generic_ghost_n3_i29.get("rank_ledger", {}).get(
            "tangent_plus_masters_and_target_rank"
        )
        != 49
        or generic_ghost_n3_i29.get("exact_reconstruction", {}).get(
            "full_55_row_symbolic_relative_IBP_defect"
        )
        != "ZERO"
        or generic_ghost_n3_i29.get("claim_flags", {}).get("I29_POLE4_REDUCED")
        is not True
        or generic_ghost_n3_i29.get("claim_flags", {}).get(
            "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"
        )
        is not True
        or generic_ghost_n3_i29.get("claim_flags", {}).get(
            "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("generic ghost n=3 I29 integrated-function frontier drifted")
    if (
        box_r_scheme_conversion.get("decision", {}).get(
            "raw_zeta_BoxR_coefficient"
        )
        != "COEFFICIENT_COMPUTED"
        or box_r_scheme_conversion.get("decision", {}).get(
            "repository_BoxR_zero_scheme_conversion"
        )
        != "CERTIFIED"
        or box_r_scheme_conversion.get("decision", {}).get(
            "nonlocal_R2_form_factor"
        )
        != "NOT_COMPUTED"
        or box_r_scheme_conversion.get("decision", {}).get(
            "absolute_dressed_Rhat2_normalization"
        )
        != "NOT_FIXED"
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED"
        )
        is not False
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED"
        )
        is not False
    ):
        raise ValueError("BoxR scheme-conversion frontier drifted")
    if (
        reduced_bridge4.get("decision", {}).get(
            "Bridge_4_reduced_vacuum_cylinder"
        )
        != "CERTIFIED"
        or reduced_bridge4.get("decision", {}).get("Bridge_4_full_BV")
        != "NO_CERTIFIED_MAP"
        or reduced_bridge4.get("decision", {}).get("Bridge_4_Berger")
        != "NO_CERTIFIED_MAP"
        or reduced_bridge4.get("claim_flags", {}).get(
            "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"
        )
        is not True
        or reduced_bridge4.get("claim_flags", {}).get(
            "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"
        )
        is not False
    ):
        raise ValueError("vacuum-cylinder reduced Bridge-4 frontier drifted")
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
    physical_compatibility = values["physical_classical_snapshot_compatibility"]
    physical_analytic_commit = values["physical_TT_hessian_dictionary"].get(
        "classical_commit"
    )
    physical_compatibility_receipt = validate_classical_snapshot_compatibility(
        physical_compatibility,
        repository_root=ROOT,
        expected_local_commit=antifield["classical_commit"],
        expected_local_hashes=antifield["independent_replay"]["canonical_hashes"],
        expected_analytic_commit=physical_analytic_commit,
    )
    if (
        physical_compatibility_receipt.get("status")
        != "SEMANTIC_RECEIVER_ACCEPTED"
        or physical_compatibility_receipt.get("matched_hash_count") != 5
    ):
        raise ValueError("physical classical snapshot compatibility frontier drifted")
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
    nonconformal = values["nonconformal_coefficient_match_receiver"]
    nonconformal_flags = nonconformal.get("claim_flags", {})
    if (
        nonconformal_flags.get("NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY")
        is not True
        or nonconformal_flags.get("CURRENT_CANDIDATES_AUDITED") is not True
        or nonconformal_flags.get("PHYSICAL_C2_CARRIER_SUPPLIED") is not False
        or nonconformal_flags.get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not False
        or nonconformal.get("next_gate")
        != "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH"
    ):
        raise ValueError("nonconformal coefficient receiver frontier drifted")
    elliptic = values["Euclidean_elliptic_complex_receiver"]
    elliptic_flags = elliptic.get("claim_flags", {})
    if (
        elliptic_flags.get("EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY")
        is not True
        or elliptic_flags.get("EXACT_SPARSE_SYMBOL_REPLAY_READY") is not True
        or elliptic_flags.get("REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED")
        is not False
        or elliptic.get("next_gate") != "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX"
    ):
        raise ValueError("Euclidean elliptic-complex receiver frontier drifted")
    regulator = values["regulator_measure_receiver"]
    regulator_flags = regulator.get("claim_flags", {})
    if (
        regulator_flags.get("REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY")
        is not True
        or regulator_flags.get("NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND") is not True
        or regulator_flags.get("CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND")
        is not True
        or regulator_flags.get(
            "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED"
        )
        is not False
        or regulator.get("next_gate")
        != "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER"
    ):
        raise ValueError("regulator/zero-mode/measure receiver frontier drifted")
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
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED"
        )
        is not True
        or assembly_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not True
        or assembly_flags.get("REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED")
        is not True
        or assembly_flags.get(
            "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED"
        )
        is not True
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
        != "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION"
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
        != "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT_OR_Q26_COMPATIBLE_CAUCHY_LIFT"
    ):
        raise ValueError("Hadamard existence criterion frontier drifted")
    regular_boundary = values["Hadamard_regular_morphism_boundary"]
    regular_flags = regular_boundary.get("claim_flags", {})
    if (
        regular_flags.get("BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY") is not True
        or regular_flags.get("BERGER_LOCAL_GHOST_HADAMARD_FACTORS_INCLUDED")
        is not True
        or regular_flags.get("BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY")
        is not False
        or regular_flags.get("BERGER_REGULAR_GREENHYP_MORPHISM") is not False
        or regular_flags.get("BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION")
        is not False
        or regular_boundary.get("classical_import_request", {}).get("status")
        != "NOT_SUPPLIED"
    ):
        raise ValueError("Hadamard regular-morphism frontier drifted")
    cutoff_family = values["temporal_cutoff_companion_Green_family"]
    cutoff_flags = cutoff_family.get("claim_flags", {})
    if (
        cutoff_flags.get("BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY")
        is not True
        or cutoff_flags.get("BERGER_CUTOFF_COMPANION_BOTH_INVERSE_IDENTITIES")
        is not True
        or cutoff_flags.get("BERGER_CUTOFF_COMPANION_CAUSAL_SUPPORT") is not True
        or cutoff_flags.get("BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL")
        is not True
        or cutoff_flags.get("BERGER_CUTOFF_COMPANION_WAVEFRONT_THEOREM")
        is not False
        or cutoff_flags.get("BERGER_REGULAR_GREENHYP_MORPHISM") is not False
        or cutoff_flags.get("BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION")
        is not False
        or cutoff_family.get("next_gate")
        != "BERGER_CUTOFF_COMPANION_MICROLOCAL_PROPAGATION_AND_REGULAR_RESPONSE_MORPHISM"
    ):
        raise ValueError("temporal-cutoff companion Green-family frontier drifted")
    cutoff_microlocal = values["cutoff_companion_microlocal_response_preflight"]
    cutoff_microlocal_flags = cutoff_microlocal.get("claim_flags", {})
    if (
        cutoff_microlocal_flags.get(
            "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND"
        )
        is not True
        or cutoff_microlocal_flags.get(
            "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR"
        )
        is not True
        or cutoff_microlocal_flags.get(
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        )
        is not False
        or cutoff_microlocal_flags.get("BERGER_REGULAR_GREENHYP_MORPHISM")
        is not False
        or cutoff_microlocal_flags.get(
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
        )
        is not False
        or cutoff_microlocal.get("next_gate")
        != "BERGER_CUTOFF_ORIENTATION_EXCLUSION_AND_GRADED_GREENHYP_REALIZATION_THEN_GLOBAL_SEED_COVARIANCE"
    ):
        raise ValueError("cutoff companion microlocal-response frontier drifted")
    dilation = values["cutoff_companion_Hermitian_dilation"]
    dilation_flags = dilation.get("claim_flags", {})
    if (
        dilation_flags.get("BERGER_METRIC_COMPANION_RFHGHO_DILATION") is not True
        or dilation_flags.get(
            "BERGER_DILATED_FREE_CUTOFF_REGULAR_CAUCHY_MORPHISM"
        )
        is not True
        or dilation_flags.get(
            "BERGER_DILATED_CUTOFF_FULL_REGULAR_CAUCHY_MORPHISM"
        )
        is not True
        or dilation_flags.get("BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING")
        is not False
        or dilation_flags.get("BERGER_FULL_GRADED_GREENHYP_REALIZATION")
        is not False
        or dilation_flags.get("BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION")
        is not False
        or dilation.get("next_gate")
        != "BERGER_DILATED_MORPHISM_CONE_MAPPING_AND_CUTOFF_ORIENTATION_EXCLUSION_THEN_FREE_SEED_COVARIANCE"
    ):
        raise ValueError("cutoff companion Hermitian-dilation frontier drifted")
    orientation_reduction = values[
        "cutoff_Volterra_microlocal_orientation_reduction"
    ]
    orientation_flags = orientation_reduction.get("claim_flags", {})
    if (
        orientation_flags.get(
            "BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED"
        )
        is not True
        or orientation_flags.get(
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED"
        )
        is not True
        or orientation_flags.get(
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED"
        )
        is not False
        or orientation_flags.get(
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        )
        is not False
        or orientation_flags.get(
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING"
        )
        is not False
        or orientation_flags.get(
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
        )
        is not False
        or orientation_reduction.get("next_gate")
        != "PROVE_COMPACT_SLAB_VOLTERRA_CONVERGENCE_IN_DPRIME_GAMMA_NORMAL_TOPOLOGY_THEN_CONSTRUCT_FREE_SEED_COVARIANCE"
    ):
        raise ValueError("cutoff Volterra microlocal orientation reduction drifted")
    free_seed = values["free_dilation_Hadamard_bisolution_seed"]
    free_seed_flags = free_seed.get("claim_flags", {})
    if (
        free_seed_flags.get("BERGER_FREE_DILATION_NORMALLY_HYPERBOLIC")
        is not True
        or free_seed_flags.get(
            "BERGER_FREE_DILATION_GLOBAL_FEYNMAN_PROPAGATOR_EXISTS"
        )
        is not True
        or free_seed_flags.get(
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED"
        )
        is not True
        or free_seed_flags.get(
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"
        )
        is not False
        or free_seed_flags.get(
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED"
        )
        is not False
        or free_seed_flags.get(
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
        )
        is not False
        or free_seed.get("next_gate")
        != "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_FREE_BISOLUTION_AND_NORMALIZE_KREIN_CCR"
    ):
        raise ValueError("free-dilation Hadamard-bisolution frontier drifted")
    free_covariance = values["free_dilation_Krein_CCR_covariance"]
    free_covariance_flags = free_covariance.get("claim_flags", {})
    if (
        free_covariance_flags.get(
            "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR"
        )
        is not True
        or free_covariance_flags.get(
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED"
        )
        is not True
        or free_covariance_flags.get(
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"
        )
        is not False
        or free_covariance_flags.get(
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
        )
        is not False
        or free_covariance.get("next_gate")
        != "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_NORMALIZED_KREIN_COVARIANCE_TO_FULL_DILATION"
    ):
        raise ValueError("free-dilation Krein-CCR covariance frontier drifted")
    normal_convergence = values["cutoff_Volterra_normal_topology_convergence"]
    normal_convergence_flags = normal_convergence.get("claim_flags", {})
    if (
        normal_convergence.get("result_state")
        != "CUTOFF_NORMAL_CONVERGENCE_DECOMPOSABILITY_AND_DILATED_CONE_MAPPING_CERTIFIED_COVARIANCE_TRANSPORT_OPEN"
        or normal_convergence_flags.get(
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED"
        )
        is not True
        or normal_convergence_flags.get(
            "BERGER_CUTOFF_VOLTERRA_TRANSPOSE_NORMAL_CONVERGENCE"
        )
        is not True
        or normal_convergence_flags.get(
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        )
        is not True
        or normal_convergence_flags.get(
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE"
        )
        is not True
        or normal_convergence_flags.get(
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING"
        )
        is not True
        or normal_convergence_flags.get("BERGER_REGULAR_GREENHYP_MORPHISM")
        is not True
        or normal_convergence_flags.get(
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"
        )
        is not False
        or normal_convergence.get("next_gate")
        != "TRANSPORT_NORMALIZED_FREE_KREIN_COVARIANCE_ACROSS_THE_TWO_REGULAR_CAUCHY_MORPHISMS_AND_VERIFY_EXACT_CCR"
    ):
        raise ValueError("cutoff Volterra normal-topology frontier drifted")
    full_covariance = values["full_dilation_Hadamard_Krein_CCR_covariance"]
    full_covariance_flags = full_covariance.get("claim_flags", {})
    if (
        full_covariance.get("result_state")
        != "FULL_METRIC_DILATION_GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE_TRANSPORTED_GRADED_BV_AND_POSITIVITY_OPEN"
        or full_covariance_flags.get(
            "BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE"
        )
        is not True
        or full_covariance_flags.get(
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"
        )
        is not True
        or full_covariance_flags.get("BERGER_FULL_DILATION_EXACT_CCR")
        is not True
        or full_covariance_flags.get(
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
        )
        is not False
        or full_covariance_flags.get("BERGER_54_ROW_BRST_HADAMARD")
        is not False
        or full_covariance_flags.get(
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"
        )
        is not False
        or full_covariance.get("next_gate")
        != "CONSTRUCT_RAW_COMPANION_OR_GRADED_BV_RESTRICTION_OF_FULL_DILATION_COVARIANCE_AND_VERIFY_BRST_WARD_IDENTITY"
    ):
        raise ValueError("full-dilation Hadamard Krein covariance frontier drifted")
    restriction_audit = values["dilation_retained26_restriction_audit"]
    restriction_flags = restriction_audit.get("claim_flags", {})
    if (
        restriction_audit.get("result_state")
        != "CANONICAL_SUMMAND_RESTRICTION_OBSTRUCTED_GRAPH_INTERTWINER_OR_DIRECT_RETAINED26_COVARIANCE_REQUIRED"
        or restriction_flags.get(
            "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR"
        )
        is not False
        or restriction_flags.get(
            "BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY"
        )
        is not True
        or restriction_flags.get(
            "BERGER_DILATION_GRAPH_INTERTWINER_SUPPLIED"
        )
        is not False
        or restriction_flags.get(
            "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE"
        )
        is not False
        or restriction_flags.get("BERGER_COVARIANCE_LIFT_26_TO_54")
        is not True
        or restriction_flags.get("BERGER_54_ROW_BRST_HADAMARD") is not False
        or restriction_audit.get("next_gate")
        != "SUPPLY_SUPPORT_LOCAL_GRAPH_INTERTWINER_OR_CONSTRUCT_DIRECT_RETAINED26_GRADED_COVARIANCE_THEN_APPLY_CERTIFIED_26_TO_54_LIFT"
    ):
        raise ValueError("dilation-to-retained-26 restriction frontier drifted")
    typed_biwave = values["typed_biwave_Volterra_theorem"]
    typed_flags = typed_biwave.get("claim_flags", {})
    if (
        typed_flags.get("TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED")
        is not True
        or typed_flags.get("HADAMARD_STATE") is not False
        or typed_flags.get("QUANTUM_THEORY") is not False
        or typed_biwave.get("next_gate")
        != "APPLY_THEOREM_ONLY_AFTER_EXACT_PHYSICAL_NORMAL_FORM_AND_ENERGY_HYPOTHESES_ARE_CERTIFIED"
    ):
        raise ValueError("typed biwave Volterra theorem frontier drifted")
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
        or relative_flags.get("CLASSICAL_RELATIVE_TRIANGLE_IMPORTED") is not True
        or relative_flags.get("RELATIVE_OBSERVABLE_PULLBACK_IMPORTED") is not True
        or relative_flags.get("RELATIVE_EQUIVARIANCE_IMPORTED") is not True
        or relative_flags.get("QUANTUM_RELATIVE_LIFT") is not False
        or relative_gate.get("status")
        != "LINEAR_GATE_SATISFIED_NONLINEAR_GATE_OPEN"
        or relative_gate.get("current_map_disposition")
        != "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED"
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
        "result_state": "STRICT_QME_OBSTRUCTED_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED_REDUCED_BRIDGE4_CERTIFIED_FULL_BV_LORENTZIAN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "promotion_ladder": {
            "G0": "PASSED",
            "G1": "PASSED_AFN0_LOCAL_QUOTIENT",
            "G2": "PASSED_LOCAL_BV_COHOMOLOGY_REGULAR_BACH_LOCUS",
            "G3": "PASSED_REPOSITORY_EUCLIDEAN_COEFFICIENT_AND_SLAVNOV_BREAKING",
            "G4": "DISPOSITION_COMPLETE_STRICT_OBSTRUCTED_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED",
            "G5": "PARTIAL_REDUCED_VACUUM_CYLINDER_BRIDGE4_CERTIFIED_FULL_BV_BRST_HADAMARD_AND_RENORMALIZED_PRODUCTS_OPEN",
        },
        "active_rows": {
            "classical_interacting_input": {
                "status": "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED_RANK_46_CYCLIC_GRAPH_CARRIER_IMPORTED_PROJECTOR_OPEN_OPTIONAL_FOLLOWUP",
                "next_gate": "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
            },
            "local_obstruction_space": {
                "status": "STRICT_G2_COMPLETE_TAU_ADIC_EXTENDED_H04_DIMENSIONS_3_1_AND_H14_ZERO",
                "next_gate": "REPOSITORY_PARITY_EVEN_THIRD_CURVATURE_FORM_FACTOR_FUNCTIONS_AND_COEFFICIENTS_FINITE_C2_ABSOLUTE_RHAT2_NORMALIZATION_AND_SAME_BACKGROUND_EXTENDED_CLASSICAL_CONTRACTION",
            },
            "coefficient_and_QME": {
                "status": "STRICT_ONE_LOOP_LOCAL_EUCLIDEAN_QME_OBSTRUCTED_TAU_ADIC_COMPENSATOR_EXTENDED_ONE_LOOP_QME_RESTORED_PHYSICAL_GHOST_N3_AND_VECTOR_N1_N2_FIVE_CARRIER_MELLIN_MS_REPRESENTATIVE_ASSEMBLED_LONGITUDINAL_SCHUR_RESUMMED_NON_EINSTEIN_PRODUCT_WEIGHTED_GHOST_DETERMINANT_COEFFICIENT_COMPUTED_CROSS_BACKGROUND_FULL_BV_JOIN_REJECTED_Q1_UNDERDETERMINED",
                "next_gate": "CONSTRUCT_PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER_AND_SAME_BACKGROUND_BV_MEASURE_LEDGER",
            },
            "free_Lorentzian_state": {
                "status": "VACUUM_CYLINDER_REDUCED_BRIDGE4_KREIN_HADAMARD_CARRIER_CERTIFIED_BERGER_FULL_METRIC_DILATION_GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE_TRANSPORTED_CANONICAL_SUMMAND_RESTRICTION_OBSTRUCTED_GRAPH_OR_DIRECT_RETAINED26_ROUTE_OPEN",
                "next_gate": "SUPPLY_SUPPORT_LOCAL_GRAPH_INTERTWINER_OR_CONSTRUCT_DIRECT_RETAINED26_GRADED_COVARIANCE_THEN_APPLY_CERTIFIED_26_TO_54_LIFT",
            },
            "free_Lorentzian_algebra": {
                "status": "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_DEFINED_AND_GAUGE_INVARIANT_OBSERVABLE_CAUSAL_PROPAGATOR_DEFINED_AUTONOMOUS_GREEN_AND_HADAMARD_STATE_OPEN",
                "next_gate": "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE",
            },
            "relative_Einstein_Weyl": {
                "status": "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_OBSERVABLE_PULLBACK_AND_COFIBER_DETECTORS_IMPORTED_NONLINEAR_QME_OPEN",
                "next_gate": "EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_AND_MATCHED_QME",
            },
            "quantum_transfer": {
                "status": "FORBIDDEN_PHYSICAL_GHOST_N3_AND_VECTOR_N1_N2_FIVE_CARRIER_REPRESENTATIVE_ASSEMBLED_LONGITUDINAL_SCHUR_PRODUCT_WEIGHTED_GHOST_DETERMINANT_COEFFICIENT_COMPUTED_SAME_BACKGROUND_PRODUCT_PHYSICAL_BV_LEDGER_FINITE_NORMALIZATIONS_RENORMALIZED_PRODUCTS_AND_EXTENDED_CLASSICAL_CONTRACTION_NOT_SUPPLIED",
                "next_gate": "CONSTRUCT_PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER_AND_SAME_BACKGROUND_BV_MEASURE_LEDGER",
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
            "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED": True,
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
            "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY": True,
            "BERGER_LOCAL_GHOST_HADAMARD_FACTORS_INCLUDED": True,
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY": True,
            "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND": True,
            "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR": True,
            "BERGER_METRIC_COMPANION_RFHGHO_DILATION": True,
            "BERGER_DILATED_REGULAR_CAUCHY_MORPHISM_LEGS": True,
            "BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED": True,
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED": True,
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED": True,
            "BERGER_CUTOFF_VOLTERRA_TRANSPOSE_NORMAL_CONVERGENCE": True,
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": True,
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE": True,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": True,
            "BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE": True,
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE": True,
            "BERGER_FULL_DILATION_EXACT_CCR": True,
            "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR": False,
            "BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY": True,
            "BERGER_DILATION_GRAPH_INTERTWINER_SUPPLIED": False,
            "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE": False,
            "BERGER_COVARIANCE_LIFT_26_TO_54": True,
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED": True,
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE": False,
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED": True,
            "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR": True,
            "BERGER_REGULAR_GREENHYP_MORPHISM": True,
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED": True,
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY": True,
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED": True,
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED": True,
            "CLASSICAL_RELATIVE_TRIANGLE_IMPORTED": True,
            "RELATIVE_OBSERVABLE_PULLBACK_IMPORTED": True,
            "RELATIVE_EQUIVARIANCE_IMPORTED": True,
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
            "REPOSITORY_TT_HESSIAN_HISTORICAL_MISSING_CARRIER_CLOSED": True,
            "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE": True,
            "STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED": True,
            "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE": True,
            "FIVE_UNIVERSAL_CPT_THIRD_CURVATURE_KERNELS_IMPORTED": True,
            "GENERIC_PHYSICAL_HESSIAN_LINEAR_CURVATURE_IMPORTED": True,
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY": True,
            "PHYSICAL_H1_FORMAL_ADJOINT_MOMENTUM_VERTEX_VERIFIED": True,
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED": True,
            "GENERIC_H1_H2_CONTACT_ENDPOINT_RESIDUES_PROJECTED": True,
            "SYMMETRIC_PHYSICAL_MIXED_INCIDENCE_ASSEMBLED": True,
            "SYMMETRIC_H2_CANCELLATION_OF_M14_REFUTED": True,
            "GENERIC_BOX_TRIANGLE_CORNER_RESIDUES_COMPUTED": True,
            "GENERIC_PHYSICAL_MIXED_ROWS_ASSEMBLED": True,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": True,
            "PHYSICAL_M14_NONZERO_SCALE_ROW_RENORMALIZED": True,
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED": True,
            "PHYSICAL_TRIANGLE_SIX_MASTER_SPAN_COMPLETE": True,
            "RENORMALIZED_PHYSICAL_TRIANGLE_MASTER_VALUES_COMPUTED": True,
            "PHYSICAL_TRIANGLE_SIX_MASTER_COORDINATES_COMPUTED": True,
            "PHYSICAL_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX_COMPUTED": True,
            "PHYSICAL_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED": True,
            "PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED": True,
            "PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED": True,
            "GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED": True,
            "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED": True,
            "FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED": False,
            "CURVATURE_SQUARED_PHYSICAL_HESSIAN_LAYER_SUPPLIED": False,
            "PHYSICAL_N3_THREE_LINEAR_TRIANGLE_COMPUTED": True,
            "GENERIC_BACKGROUND_GHOST_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED": True,
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED": True,
            "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED": True,
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED": True,
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED": True,
            "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED": True,
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION": True,
            "SCHUR_CORRECTION_S3_CLASS_PROVED": True,
            "CANONICAL_DET3_TAIL_DEFINED": True,
            "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED": True,
            "WODZICKI_RESIDUE_LOG_S_COMPUTED": True,
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED": False,
            "WODZICKI_RESIDUE_K_COMPUTED": True,
            "RENORMALIZED_R_K_COMPUTED": False,
            "FINITE_PART_R_K2_COMPUTED": False,
            "ZETA_SCALE_COEFFICIENT_COMPUTED": True,
            "ROUND_S4_SCHUR_R_K_COMPUTED": True,
            "ROUND_S4_SCHUR_FINITE_R_K2_COMPUTED": True,
            "ROUND_S4_SCHUR_DET3_TAIL_COMPUTED": True,
            "ROUND_S4_SCHUR_MODIFIED_DETERMINANT_COMPUTED": True,
            "GENERIC_SCHUR_FINITE_ROWS_REQUIRE_GLOBAL_CARRIER": True,
            "GENERIC_WEIGHT_RAISED_LOCAL_ZETA_FACTORIZATION_DEFECT_COMPUTED": True,
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED": False,
            "ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED": False,
            "ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED": False,
            "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED": True,
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED": True,
            "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED": True,
            "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED": True,
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE": True,
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED": True,
            "GENERIC_GHOST_N3_POLE3_RELATIVE_IBP_COMPUTED": True,
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED": True,
            "GENERIC_GHOST_N3_TEN_POLE3_INTEGRATED_FUNCTIONS_COMPUTED": True,
            "GENERIC_GHOST_N3_CORNER_ANGULAR_FLUXES_EVALUATED": True,
            "GENERIC_GHOST_N3_I29_POLE4_REDUCED": True,
            "GENERIC_GHOST_N3_ALL_ELEVEN_FUNCTIONS_COMPUTED": True,
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED": False,
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED": False,
            "GENERIC_GHOST_LONGITUDINAL_DW_CARRIERS_EVALUATED": False,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "REPOSITORY_GENERIC_BACKGROUND_CPT_TRACE_SUBSTITUTION_SUPPLIED": False,
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY": True,
            "FULL_BV_LEDGER_COMPOSER_READY": True,
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED": True,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": True,
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED": True,
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED": True,
            "REPOSITORY_C2_COEFFICIENT_COMPUTED": True,
            "NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY": True,
            "EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY": True,
            "REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY": True,
            "NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND": True,
            "CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND": True,
            "CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED": True,
            "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": True,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": True,
            "QME_OBSTRUCTED_STRICT_FIELD_CONTENT": True,
            "STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED": True,
            "WZ_AFN0_PRIMITIVE_CERTIFIED": True,
            "WZ_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED": True,
            "WZ_TAU_ADIC_EXTENDED_H04_H14_COMPLETE": True,
            "TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED": True,
            "WZ_LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED": True,
            "FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO": True,
            "ANOMALY_INDUCED_NONLOCAL_GAMMA1_REPRESENTATIVE_SUPPLIED": True,
            "FLAT_TT_UNIVERSAL_LOG_GAMMA1_FORM_FACTOR_FIXED": True,
            "CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED": True,
            "FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE": True,
            "FV_CONFORMIZED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED": True,
            "FV_ANOMALY_ACTION_FIXED": True,
            "RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED": True,
            "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED": False,
            "ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE": True,
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE": True,
            "PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE": False,
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED": False,
            "FV_AND_WZ_DRESSED_METRICS_IDENTIFIED": False,
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED": True,
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED": True,
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED": True,
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED": False,
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED": False,
            "VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED": True,
            "REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED": True,
            "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED": True,
            "E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED": True,
            "A_L_BRANCHES_POSITIVE": False,
            "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED": False,
            "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED": False,
            "BERGER_BRIDGE4_CERTIFIED": False,
            "FINITE_C2_NORMALIZATION_FIXED": False,
            "FINITE_R2_NORMALIZATION_FIXED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "FULL_EXTENDED_BV_QME_RESTORED": False,
            "GLOBAL_BRST_HADAMARD_STATE": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "ordered_next_gates": [
            "CONSTRUCT_PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER_AND_SAME_BACKGROUND_BV_MEASURE_LEDGER",
            "SUPPLY_GENERIC_PRIMED_GREEN_OR_SPECTRAL_MEASURE_THEN_COMPUTE_FINITE_SCHUR_ROWS_AND_REPOSITORY_FORM_FACTORS",
            "SUPPLY_SUPPORT_LOCAL_GRAPH_INTERTWINER_OR_CONSTRUCT_DIRECT_RETAINED26_GRADED_COVARIANCE_THEN_APPLY_CERTIFIED_26_TO_54_LIFT",
            "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
            "BERGER_REGULAR_GREENHYP_RESPONSE_MORPHISM_AND_GLOBAL_SEED_COVARIANCE",
            "RESTORE_QME_IN_A_CERTIFIED_EXTENDED_THEORY",
            "QUANTUM_RESIDUAL_TRANSFER_ONLY_AFTER_QME_RESTORATION",
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
            "and the exact 3-by-4 breaking reduction binds the even coordinates 199/30 "
            "and -87/20. A complete repository Euclidean principal-symbol complex is exact, "
            "and a local Ricci-flat C2-visible carrier fixes c=199/30 while the round-S4 "
            "carrier independently fixes a=87/20. Their regulated Slavnov insertion has "
            "nonzero coordinates in the complete H14 quotient, so the strict fixed-field-content "
            "local Euclidean QME is obstructed at one loop. "
            "The same exact c coordinate fixes the nonzero-momentum flat-TT logarithmic "
            "form-factor coefficient -199/60 and its scheme-independent momentum "
            "difference. A spectral covariantization now fixes <C,log(Delta_C/mu^2)C> "
            "through curvature order two; the resolvent filtration proves that admissible "
            "Laplace-type operator choices first differ at curvature order three. A normalized "
            "Fradkin--Vilkovisky scalar-flat representative now supplies an exact local-Weyl "
            "completion of that selected coefficient-bearing carrier and identifies its first "
            "forced cubic correction through the Frechet derivative of the spectral logarithm. "
            "This nonlocal strict-metric representative is not the local tau-adic dressed metric. "
            "The zero-derivative algebraic C3 carrier basis is complete with one even and "
            "one odd direction. The parity-even third-curvature conformal carrier manifest "
            "is also complete in the declared scalar-flat Euclidean scope: five carrier labels "
            "retain their source stabilizers while scalar-flat transversality enhances I29 "
            "to effective S3, leaving eleven raw effective label channels; the single "
            "four-dimensional symmetric functional relation leaves ten. This is not ten "
            "computed form factors. The five exact universal CPT alpha kernels have now been "
            "imported and symmetrized; they are coefficient-bearing for the rank-one minimal "
            "scalar-Laplacian source fixture. At this point the repository tensor and ghost "
            "trace substitutions were not yet supplied by those universal kernels alone, "
            "and the special-background determinant ranks cannot determine them. The exact "
            "generic Diff--Weyl ghost Schur complement is beta-independent but nonminimal, "
            "with principal spectrum (3/2,1,1,1), and generic tracefree Ricci curvature mixes "
            "its Hodge sectors. It reproduces the accepted scalar factor only on Einstein "
            "backgrounds. Direct substitution of the current ghost ledger into the imported "
            "minimal-Laplace CPT kernels is therefore obstructed; a matched nonminimal-vector "
            "ghost determinant or an exact determinant/Jacobian-equivalent local extension is "
            "required. This is an architecture obstruction, not an anomaly or Lorentzian no-go. "
            "The positive ghost operator is now exactly split as H=H0-2Ric, where "
            "H0 is the nondegenerate Endo vector operator with alpha=-1/2. Its heat "
            "kernel reduces on a finite proper-time interval to one minimal vector and "
            "one scalar heat kernel, and its nonzero-mode determinant differs from the "
            "minimal vector determinant only by the local zeta scaling "
            "zeta_Delta0(0)log(3/2). Through third curvature order the remaining "
            "generic ghost contribution is a finite list of one-, two- and three-Ricci "
            "insertions. The flat-Endo three-insertion row now has an exact adiabatic "
            "angular numerator: before the W/log factors its scalar-flat tr(Ric^3) "
            "coefficient is 503/648, and the n=3 Tr-log coefficient is -503/243. "
            "Its generic nonexceptional-momentum continuation is now an exact eight-sector "
            "Feynman-simplex/Wick kernel with twenty rational Wick rows. The labelled-Ricci "
            "triangle is now projected exactly onto the eleven raw I10/I24/I25/I28/I29 "
            "orientations and the ten-dimensional scalar-flat quotient section, with the "
            "common Delta^-4 numerators stored as exact alpha/box polynomials. Ten generic "
            "numerators cancel one Delta exactly; only I10 has a nonzero direct open-edge "
            "restriction, every vertex margin is positive, and the I28 relation holds "
            "pointwise. All ten pole-three rows now have exact relative-IBP reductions to "
            "the scalar triangle and two first kinematic derivatives. Four explicit "
            "open-edge tangent primitives cover every orientation. The corner-zero "
            "tangent-plus-master span has rank 26 and every target raises it to 27, with "
            "normalized rank-stable dual witnesses, so punctured-corner flux is unavoidable. "
            "The scalar-triangle differential system is now exact, S3-covariant, homogeneous "
            "and integrable. Its two derivative masters reduce to J and two bubble-log ratios. "
            "For all four canonical primitives the only nonzero corner has equal angular "
            "weights, so its exact oriented integral is rational rather than a new logarithmic "
            "master. Combining these facts gives complete generic J-plus-two-log functions "
            "for all ten pole-three rows, with exact symmetric-point regressions. The sole "
            "pole-four I29 row is now reduced by a full 55-row symbolic identity to the same "
            "three masters; its three finite corner numerators are linear, its flux is rational, "
            "and all six permutations and the symmetric-point value replay exactly. Thus all "
            "eleven generic ghost n=3 functions are complete. The same-gauge traceless "
            "metric Hessian has now been imported through first curvature order as exact "
            "V, N and U ledgers with 9, 8 and 5 source rows, respectively. The repository "
            "functional Hessian is one half of the source operator, while the normalized "
            "trace-log insertion is unchanged. On the scalar-flat domain 7, 6 and 3 rows "
            "survive, and the round-S4 restriction reproduces the complete linear layer. "
            "The scalar-flat rank-nine momentum vertex is now completed by formal adjunction. "
            "Its full physical +(1/6)Tr[(H0^-1 H1)^3] alpha numerator is projected exactly "
            "onto all eleven raw channels of the five-carrier quotient using 28 training "
            "and two unseen fixtures. At the symmetric point its isolated simplex integral "
            "contains a logarithmic M14 corner class: the exact relative rank jumps 49 to 50, "
            "a normalized dual witness certifies non-membership, and the total corner coefficient "
            "is 1/2. The algebraic curvature-squared H2 block is now imported from the projected "
            "monic source operator with an exact gauge-ordering crosswalk. Nine nonzero rows survive "
            "on the scalar-flat carrier, while the round-S4 split +24K^2-16K^2=+8K^2 replays the "
            "known factorization. The scalar-flat H2 block is now polarized operationally on a rational "
            "equal-box TT fixture. Comparing all six labelled H1-cubed orderings with both endpoints "
            "of all three mixed H1-H2 bubbles gives the nonzero raw logarithmic coefficient 15707/216. "
            "Thus a universal algebraic H2 cancellation is refuted on this fixture. A common Mellin "
            "minimal-subtraction extension on the resolved equal-box carrier promotes 15707/216 to "
            "the exact log(mu^2) scale row. A generic covariant Volterra carrier now joins all six "
            "ordered triangle cells to the three local H1-H2 contact cells under that common Mellin "
            "extension. All three generic H1-H2 logarithmic endpoint residues are now projected to "
            "33 exact raw five-carrier rows with two unseen-fixture replays and the symmetric I28 "
            "quotient relation preserved. At the symmetric point, the six ordered triangle corner "
            "rows and all six contact endpoints are now assembled coefficientwise: their exact "
            "TT-carrier values are -1975/72 and 2704/27, giving the nonzero combined scale row "
            "15707/216. Thus algebraic H2 cancellation of the symmetric M14 divergence is refuted. "
            "The three generic-box triangle corner residues are now integrated for all eleven raw "
            "channels as exact rational box functions and replay every symmetric obstruction row. "
            "Their full incidence with all six contact endpoints is exact and generically nonzero. "
            "Thus algebraic H2 cancellation is refuted generically and M14 is disposed as a nonzero "
            "scale row renormalized by the common Mellin extension. The finite parts of all three "
            "H1-H2 contact cells are now reconstructed from their quadratic parameter densities and "
            "projected to 33 exact rational rows; their equal-box TT sum is 3188/27. The renormalized "
            "H1-cubed triangle carrier span is now exact: the rank-49 tangent-plus-scalar-master system "
            "grows through the M14 singlet and a standard-S3 pair to rank 52, and all eleven physical "
            "rows lie in it. The M14 singlet and standard-S3 pair are now evaluated as exact "
            "sector-decomposed rational/logarithmic functions in the common Mellin scheme, including "
            "their scale derivatives. All 66 reduced rational six-master coordinate functions of the eleven physical "
            "channels are now exact; their selected minor factors into chart terms times lambda^5. Their relative-IBP "
            "boundary fluxes and seven-function structured decompositions are exact for all eleven channels: 33 quadratic "
            "corner moments reduce to two logarithm ratios and one rational corner term, and two exact holdouts independently "
            "replay the tangent primitives, angular integrations and scale recipes. Optional finite-counterterm normalization, "
            "global carrier and five repository form-factor assembly remain open. At the "
            "normalized symmetric point all eleven coordinates are integrated exactly in "
            "terms of one Clausen master. This is not the generic five repository functions; "
            "the n=1/n=2 pure-vector sum is now evaluated exactly from CPT rows 1, 3 and 14 as "
            "6 Gamma1 S1-2 Gamma3 S3-2 Gamma14 S14 and projected to the scalar-flat carrier quotient. "
            "The other three carriers contain the anisotropic principal-symbol insertion D_W=delta W d; "
            "minimal-P kernels cannot evaluate them separately. They are now resummed exactly into one "
            "normalized scalar Schur trace-log series. Its order-minus-two correction lies in S_3, so the "
            "canonical det_3 tail exists. The canonical local residues are "
            "Wres(K)=(4 pi)^-2 integral(R^2+4 Ric^2)/9, "
            "Wres(K^2)=(4 pi)^-2 integral(R^2+2 Ric^2)/27, and "
            "Wres(log S_L)=(4 pi)^-2 integral(5R^2+22Ric^2)/54. "
            "For the declared order-two scalar weight Q_mu=(Delta_0+Pi_0)/mu^2, the weighted-trace pole and scale conversion are exact: d/dlog(mu) log Det_(3,R_mu)(S_L)=Wres(log S_L). Generic reference-scale finite rows remain open. For the canonical weight-raised comparison A=S_L Q, B=Q, the order-minus-three/four BCH carrier is now exact: its weighted trace vanishes through four-dimensional residue order and the local defect is -(1/4)Wres(K^2)=-(4 pi)^-2 integral(R^2+2 Ric^2)/108. On the round unit S4 fixture, after deleting the absent ell=0 gradient and five ell=1 conformal-Killing zero modes, both reference finite rows are exact digamma/trigamma values, the canonical det_3 tail has an exact rational enclosure of width below 5.8e-48, and their selected weighted modified determinant is -3.9781454856154116... . The Einstein numerator/denominator factorization defect is 5/3, while the distinct generic weight-raised convention specializes to -1/3; the exact difference 2 is a factorization-convention effect. The corresponding zeta ratios are -2.3114788189487449608... and -4.3114788189487449608... . On S2(k1)xS2(k2), closed mode and degeneracy formulas now supply a complete non-Einstein spectral measure for the same Schur kernel. Six minimal-vector zeros are matched Schur poles and contribute the finite coupled correction 3^-6, so they cannot be primed independently. The product Wres(K^2) replay is exact. On S2(1)xS2(2), the regular-complement det_3, weighted R(K), finite-part R(K^2), matched exceptional Schur factor, both exact/coexact minimal-vector determinants and their combined vector-plus-Schur weighted logarithm are rigorously enclosed. The last lies in [19.0791598956...,19.0791630891...]. After receipt reconciliation, the full 850-test Tier-3 suite passes and these selected special-background weighted-row and determinant results are COEFFICIENT_COMPUTED. A finite-rank smoothing witness still proves that the full primed Green kernel or spectral measure is necessary for arbitrary generic-background finite values. "
            "The five repository form-factor functions and their "
            "coefficients, the parity-odd derivative-decorated manifest and the additive C2 "
            "normalization remain open. The imported raw "
            "zeta/proper-time BoxR coefficient is independently replayed as "
            "(7/2)log(3/2)-159/80. The exact strict-metric R2 counterterm "
            "(7/24)log(3/2)-53/320 converts it to the repository BoxR=0 convention "
            "and reproduces the anomaly-induced local R2 coefficient 29/120. This fixes "
            "only a relative one-loop strict-metric scheme conversion. The exact FV anomaly "
            "action and conformal decomposition now prove that the Ricci-scalar sector is "
            "structurally dependent: a generic-basis nonlocal R F(Box) R term can appear after "
            "re-expansion, but it is fixed by the anomaly action and conformized Weyl sector, "
            "not a separately specifiable form factor. The absolute dressed R(g_hat)^2 "
            "normalization remains open. "
            "An exact dual-cone witness further proves that no nonnegative collection of "
            "standard-sign free conformal scalars, Weyl or Dirac fermions, and gauge vectors "
            "cancels the C2/E4 vector. "
            "A separate compensator preflight adjoins Q tau=L_xi tau+omega, verifies the "
            "finite-jet Weyl-doublet contraction and dressed-metric Weyl cancellation, and "
            "constructs the exact coefficient-bearing Wess--Zumino primitive on the two "
            "certified even AFN0 anomaly coordinates. This makes the displayed breaking exact "
            "only in the declared AFN0 extended sector. The tau-antifield cotangent row and "
            "full extended H04/H14 quotient are now constructed in the formal tau-adic local "
            "analytic algebra. The canonical cotangent lift verifies delta squared, the "
            "delta-gamma anticommutator and Q squared on all extended atoms, and the dressed "
            "Weyl quartet contracts. The remaining pure-Diff quotient has H04 dimensions "
            "three even and one odd, including R(g_hat)^2, while H14 vanishes. The displayed "
            "counterterm therefore restores the compensator-extended local Euclidean QME at "
            "one loop. The coefficient-bearing local Hamiltonian contribution Q1^WZ is fixed, "
            "and an exact Paneitz/Riegert solve now supplies one anomaly-induced Euclidean "
            "Gamma1 representative with coefficients (199/120,-87/160,29/120). Its local "
            "R^2 term exactly restores the certified BoxR=0 convention. The result is "
            "conditional on an invertible boundary problem or compatible source sector and "
            "does not discard Paneitz kernel/global data. An exact flat-momentum response "
            "matrix still has rank two on the allowed C(g_hat)^2 and R(g_hat)^2 finite-counterterm "
            "directions. Two of the five n=1/n=2 Hodge carriers have now been combined and evaluated "
            "in their physical pure-vector sum. The three longitudinal D_W trace-log towers are now "
            "resummed exactly into the single normalized scalar Schur operator "
            "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1d. Its order-minus-two correction is in every S_p for p>2, "
            "so det_3(I+K) gives a canonical trace-class tail. The exact local residues are "
            "Wres(K)=(4 pi)^-2 integral(R^2+4 Ric^2)/9, "
            "Wres(K^2)=(4 pi)^-2 integral(R^2+2 Ric^2)/27, and "
            "Wres(log S_L)=(4 pi)^-2 integral(5R^2+22Ric^2)/54. Ordinary trace-class "
            "determinacy is not implied. The selected order-two weight fixes the pole and scale normalization, and the round-S4 spectrum fixes both reference finite constants after the certified zero-mode deletion. Exact rational alternating-series and Euler--Maclaurin bounds also fix the round-S4 det_3 tail and selected weighted modified determinant. The commuting Einstein-ratio round-S4 zeta-to-weighted factorization defect is exactly 5/3. For the separately frozen generic weight-raised convention A=S_L Q, B=Q, the noncommuting BCH trace is exact through residue order and gives -(1/4)Wres(K^2); it specializes to -1/3 on round S4. The exact S2(k1)xS2(k2) spectrum is now supplied and detects anisotropic tracefree Ricci curvature. Its six exceptional exact-vector zeros are Schur poles whose coupled product is 3^-6; independent deletion is invalid. On S2(1)xS2(2), rigorous product-heat and rational-tail enclosures now determine the weighted Schur rows and the exact/coexact minimal-vector blocks, including the selected combined vector-plus-Schur weighted logarithm [19.0791598956...,19.0791630891...]. The passing 850-test Tier-3 receipt promotes these selected special-background rows to COEFFICIENT_COMPUTED, while a finite-rank smoothing witness proves that arbitrary generic finite constants still require the full primed Green/spectral carrier. "
            "The five parity-even third-curvature repository functions and "
            "coefficients, the parity-odd derivative manifest, renormalized "
            "BV Laplacian or time-ordered product, finite normalization conditions, and global Green data "
            "are absent, so no unique complete Gamma1 or Q1 is supplied. This does not "
            "establish an all-loop or Lorentzian QME. The frozen classical residual contraction "
            "has no compensator rows, so residual transfer remains forbidden. The positive-Berger "
            "34-to-26 SDR does not fill that gap: its tau row is the temporal diffeomorphism "
            "ghost on a different background, not the Wess-Zumino scalar compensator. "
            "A cross-commit classical-snapshot receiver is now ready: if the later analytic "
            "operator export and frozen local-BV import come from distinct commits, it "
            "requires exact equality of the generator, atom, differential, dependency and "
            "scope hashes plus role-specific content-addressed import/export proofs. Exact "
            "Git-tree attribution now supplies and independently replays that physical "
            "cross-commit bridge for the accepted round-S4 analytic producer. The v2 regulated-BV "
            "insertion receiver additionally requires explicit action, total-derivative, "
            "gauge-dependence, regularization-dependence and antifield-completion ledgers, "
            "each bound to the exact coefficient hash; the physical insertion supplies and "
            "passes all of them. "
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
            "The global determinant phase remains open but is locally irrelevant to the b4 "
            "density used here. The round-S4 factor sum fixes a=87/20, and the local Ricci-flat "
            "operator/measure carrier independently fixes c=199/30. The "
            "frontier also contains "
            "a complete classical causal chain, local Hadamard parametrices and a covariance "
            "lift. The support-local curvature graph, completed causal quasi-isomorphism, and "
            "transported pairing define a universal presymplectic graded CCR algebra on the "
            "curvature-image free BV observable classes. Exact transport through the curvature "
            "map and its formal adjoint also constructs the gauge-invariant curvature-observable "
            "Pauli-Jordan operator. This is not an autonomous curvature Green inverse, a "
            "Hadamard state, positivity, or an interacting quantum theory. Independently, "
            "the same-background normalized E/A/L modes, reduced causal Green carrier and "
            "transported pairing on the vacuum conformal cylinder now define a compatible "
            "complex structure and microlocal Hadamard two-point distribution. The E branch "
            "is positive, while A and L have negative Krein sign. This closes Bridge 4 only "
            "on that free reduced carrier; it is not a full-BV kernel, a positive graviton "
            "Hilbert space, a Berger-space crosswalk, or an interacting quantum theory. The "
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
            "the analytic critical path, while the Berger/full-BV stationary-Hadamard "
            "construction is parallel. This is a classical LOCAL-ALGEBRAIC acceptance, not "
            "a quantum result. The Berger companion is null-cone decomposable, but this does "
            "not imply existence of a Hadamard state there: the bosonic analytic hypothesis "
            "failure and the later full-BV "
            "BRST/Krein and physical-positivity gate are recorded separately. The finite "
            "companion graph maps are wavefront-safe and the ghost local parametrices are "
            "included. The pinned typed Volterra theorem permits smooth time dependence, "
            "so its Berger specialization now certifies the full nonstationary temporal-cutoff "
            "Green family, two-sided inverse identities, causal support and adjoint reversal. "
            "The cutoff Pauli--Jordan kernel now has a Schwartz kernel, two-sided bisolution "
            "identity, no one-sided zero covectors and a factorwise metric-null wavefront "
            "bound. Its compact-slab time-slice source representative is regular as a linear "
            "map. A canonical off-diagonal indefinite Hermitian dilation now turns the free, "
            "cutoff and full metric companions into RFHGHO objects, and the two endpoint "
            "agreement regions supply regular Cauchy GreenHyp morphism legs. Every finite "
            "same-sided Volterra term has the correct oriented canonical relation, and the "
            "compact-slab Volterra series and its formal transpose now converge in the fixed "
            "D'_Gamma normal topologies by an exact polynomial-times-factorial seminorm "
            "majorant. This certifies cutoff null-cone decomposability, Pauli--Jordan "
            "same-orientation exclusion, and the two regular morphisms' cone action. "
            "Independently, the free "
            "rank-40 Hermitian dilation now satisfies the hypotheses of the global "
            "normally-hyperbolic Feynman theorem, so an exact formally self-adjoint "
            "Hadamard bisolution seed exists. Transpose symmetrization and the explicit "
            "source-to-project sign map now fix its antisymmetric part exactly to i times "
            "the project Pauli--Jordan operator, giving a normalized free Krein covariance. "
            "Its fibre form has signature (20,20), and "
            "the companion Jordan incidence rules out a positive-definite symmetrizer on "
            "that same auxiliary carrier. The quotient-inverse morphisms now transport this "
            "covariance across both regular Cauchy legs to the cutoff and full rank-40 metric "
            "dilations, preserving the Hadamard wavefront relation and exact CCR. The off-diagonal "
            "Hermitian form makes each canonical 20-row summand isotropic, so direct summand "
            "restriction is exactly rejected. A support-local graph intertwiner or a direct "
            "retained-26 covariance, including six ghost/identity rows, remains required; the "
            "conditional 26-to-54 lift is already certified. The BRST Ward identity and "
            "physical-cohomology positivity remain open. "
            "The exact stationary-carrier import consumer is ready, but no classical manifest "
            "has been supplied and finite PBW data do not decide spectral isolation of zero. "
            "The relative Einstein-Weyl rail imports the final all-row support-local "
            "noncyclic linear triangle, exact mapping cofiber, H_product equivariance and "
            "contravariant linear BRST-DGA observable pullback. The three action-derived "
            "forms remain distinct; cyclic replacement, f2/arity three and matched QME "
            "dispositions remain open. "
            "It does not establish a global BRST Hadamard state, renormalized Lorentzian "
            "products, a Lorentzian QME, residual quantum transfer, or rule out cancellation "
            "by nonstandard added matter."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "QUANTUM_WEYL_ACTIVE_FRONTIER"
        or result.get("result_state")
        != "STRICT_QME_OBSTRUCTED_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED_REDUCED_BRIDGE4_CERTIFIED_FULL_BV_LORENTZIAN_OPEN"
    ):
        raise ValueError("active frontier identity drifted")
    ladder = result.get("promotion_ladder", {})
    if (
        ladder.get("G1") != "PASSED_AFN0_LOCAL_QUOTIENT"
        or ladder.get("G2") != "PASSED_LOCAL_BV_COHOMOLOGY_REGULAR_BACH_LOCUS"
        or ladder.get("G3")
        != "PASSED_REPOSITORY_EUCLIDEAN_COEFFICIENT_AND_SLAVNOV_BREAKING"
        or ladder.get("G4")
        != "DISPOSITION_COMPLETE_STRICT_OBSTRUCTED_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        or ladder.get("G5")
        != "PARTIAL_REDUCED_VACUUM_CYLINDER_BRIDGE4_CERTIFIED_FULL_BV_BRST_HADAMARD_AND_RENORMALIZED_PRODUCTS_OPEN"
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
        or flags.get("REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED")
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
        or flags.get("REPOSITORY_TT_HESSIAN_HISTORICAL_MISSING_CARRIER_CLOSED")
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
        or flags.get("REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED") is not True
        or flags.get("REPOSITORY_C2_COEFFICIENT_COMPUTED") is not True
        or flags.get("REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED") is not True
        or flags.get("REGULATED_SLAVNOV_BREAKING_COMPUTED") is not True
        or flags.get("QME_OBSTRUCTED_STRICT_FIELD_CONTENT") is not True
        or flags.get("STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED") is not True
        or flags.get("WZ_AFN0_PRIMITIVE_CERTIFIED") is not True
        or flags.get("WZ_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED") is not True
        or flags.get("WZ_TAU_ADIC_EXTENDED_H04_H14_COMPLETE") is not True
        or flags.get("TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED") is not True
        or flags.get("WZ_LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED") is not True
        or flags.get("FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO") is not True
        or flags.get("ANOMALY_INDUCED_NONLOCAL_GAMMA1_REPRESENTATIVE_SUPPLIED")
        is not True
        or flags.get("FLAT_TT_UNIVERSAL_LOG_GAMMA1_FORM_FACTOR_FIXED") is not True
        or flags.get("CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED") is not True
        or flags.get("FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE") is not True
        or flags.get("FV_CONFORMIZED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED") is not True
        or flags.get("FV_ANOMALY_ACTION_FIXED") is not True
        or flags.get("RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED") is not True
        or flags.get("SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED") is not False
        or flags.get("ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE") is not True
        or flags.get("PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE") is not True
        or flags.get("PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE") is not False
        or flags.get("INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED") is not False
        or flags.get("FV_AND_WZ_DRESSED_METRICS_IDENTIFIED") is not False
        or flags.get("RAW_ZETA_BOXR_COEFFICIENT_COMPUTED") is not True
        or flags.get("RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED") is not True
        or flags.get("REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED") is not True
        or flags.get("NONLOCAL_R2_FORM_FACTOR_COMPUTED") is not False
        or flags.get("ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED") is not False
        or flags.get("BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND")
        is not True
        or flags.get("BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR") is not True
        or flags.get("BERGER_METRIC_COMPANION_RFHGHO_DILATION") is not True
        or flags.get("BERGER_DILATED_REGULAR_CAUCHY_MORPHISM_LEGS") is not True
        or flags.get("BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED")
        is not True
        or flags.get("BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED")
        is not True
        or flags.get("BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED")
        is not True
        or flags.get("BERGER_CUTOFF_VOLTERRA_TRANSPOSE_NORMAL_CONVERGENCE")
        is not True
        or flags.get(
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        )
        is not True
        or flags.get("BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE")
        is not True
        or flags.get("BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING")
        is not True
        or flags.get("BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE")
        is not True
        or flags.get("BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE")
        is not True
        or flags.get("BERGER_FULL_DILATION_EXACT_CCR") is not True
        or flags.get(
            "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR"
        )
        is not False
        or flags.get("BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY")
        is not True
        or flags.get("BERGER_DILATION_GRAPH_INTERTWINER_SUPPLIED") is not False
        or flags.get("BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE")
        is not False
        or flags.get("BERGER_COVARIANCE_LIFT_26_TO_54") is not True
        or flags.get("BERGER_REGULAR_GREENHYP_MORPHISM") is not True
        or flags.get("BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED")
        is not True
        or flags.get("BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE")
        is not False
        or flags.get("BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED")
        is not True
        or flags.get(
            "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR"
        )
        is not True
        or flags.get("VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED") is not True
        or flags.get("REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED") is not True
        or flags.get("REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED") is not True
        or flags.get("E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED") is not True
        or flags.get("A_L_BRANCHES_POSITIVE") is not False
        or flags.get("FULL_BV_BRST_HADAMARD_STATE_CERTIFIED") is not False
        or flags.get("POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED") is not False
        or flags.get("BERGER_BRIDGE4_CERTIFIED") is not False
        or flags.get("FINITE_C2_NORMALIZATION_FIXED") is not False
        or flags.get("FINITE_R2_NORMALIZATION_FIXED") is not False
        or flags.get("COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED") is not False
        or flags.get("COMPLETE_RENORMALIZED_Q1_SUPPLIED") is not False
        or flags.get("FULL_EXTENDED_BV_QME_RESTORED") is not False
        or flags.get("NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY") is not True
        or flags.get("EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY") is not True
        or flags.get("REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY") is not True
        or flags.get("NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND") is not True
        or flags.get("CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND") is not True
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
        or flags.get("TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED") is not True
        or flags.get("STATIONARY_GENERATOR_IMPORT_CONSUMER_READY") is not True
        or flags.get("POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED") is not True
        or flags.get("PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED") is not True
        or flags.get("CLASSICAL_RELATIVE_TRIANGLE_IMPORTED") is not True
        or flags.get("RELATIVE_OBSERVABLE_PULLBACK_IMPORTED") is not True
        or flags.get("RELATIVE_EQUIVARIANCE_IMPORTED") is not True
        or flags.get("FIVE_UNIVERSAL_CPT_THIRD_CURVATURE_KERNELS_IMPORTED")
        is not True
        or flags.get("GENERIC_PHYSICAL_HESSIAN_LINEAR_CURVATURE_IMPORTED")
        is not True
        or flags.get("PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY")
        is not True
        or flags.get("PHYSICAL_H1_FORMAL_ADJOINT_MOMENTUM_VERTEX_VERIFIED")
        is not True
        or flags.get("PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED")
        is not True
        or flags.get("SYMMETRIC_PHYSICAL_MIXED_INCIDENCE_ASSEMBLED") is not True
        or flags.get("SYMMETRIC_H2_CANCELLATION_OF_M14_REFUTED") is not True
        or flags.get("GENERIC_BOX_TRIANGLE_CORNER_RESIDUES_COMPUTED") is not True
        or flags.get("GENERIC_PHYSICAL_MIXED_ROWS_ASSEMBLED") is not True
        or flags.get("PHYSICAL_M14_CORNER_CLASS_DISPOSED") is not True
        or flags.get("PHYSICAL_M14_NONZERO_SCALE_ROW_RENORMALIZED") is not True
        or flags.get("GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED")
        is not True
        or flags.get("PHYSICAL_TRIANGLE_SIX_MASTER_SPAN_COMPLETE") is not True
        or flags.get("RENORMALIZED_PHYSICAL_TRIANGLE_MASTER_VALUES_COMPUTED")
        is not True
        or flags.get("PHYSICAL_TRIANGLE_SIX_MASTER_COORDINATES_COMPUTED")
        is not True
        or flags.get("PHYSICAL_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX_COMPUTED")
        is not True
        or flags.get("PHYSICAL_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED")
        is not True
        or flags.get("PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED")
        is not True
        or flags.get("PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED")
        is not True
        or flags.get("GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED")
        is not True
        or flags.get("PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED")
        is not True
        or flags.get("FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED") is not False
        or flags.get("CURVATURE_SQUARED_PHYSICAL_HESSIAN_LAYER_SUPPLIED")
        is not False
        or flags.get("PHYSICAL_N3_THREE_LINEAR_TRIANGLE_COMPUTED") is not True
        or flags.get("GENERIC_BACKGROUND_GHOST_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED")
        is not True
        or flags.get("GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED")
        is not True
        or flags.get("GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED")
        is not True
        or flags.get("GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED")
        is not True
        or flags.get("GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED")
        is not True
        or flags.get("GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED")
        is not True
        or flags.get(
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION"
        )
        is not True
        or flags.get("SCHUR_CORRECTION_S3_CLASS_PROVED") is not True
        or flags.get("CANONICAL_DET3_TAIL_DEFINED") is not True
        or flags.get("CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED") is not True
        or flags.get("FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED") is not False
        or flags.get("WODZICKI_RESIDUE_K_COMPUTED") is not True
        or flags.get("WODZICKI_RESIDUE_LOG_S_COMPUTED") is not True
        or flags.get("RENORMALIZED_R_K_COMPUTED") is not False
        or flags.get("FINITE_PART_R_K2_COMPUTED") is not False
        or flags.get("ZETA_SCALE_COEFFICIENT_COMPUTED") is not True
        or flags.get("ROUND_S4_SCHUR_R_K_COMPUTED") is not True
        or flags.get("ROUND_S4_SCHUR_FINITE_R_K2_COMPUTED") is not True
        or flags.get("ROUND_S4_SCHUR_DET3_TAIL_COMPUTED") is not True
        or flags.get("ROUND_S4_SCHUR_MODIFIED_DETERMINANT_COMPUTED") is not True
        or flags.get("GENERIC_SCHUR_FINITE_ROWS_REQUIRE_GLOBAL_CARRIER") is not True
        or flags.get("GENERIC_WEIGHT_RAISED_LOCAL_ZETA_FACTORIZATION_DEFECT_COMPUTED")
        is not True
        or flags.get("ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED") is not False
        or flags.get("GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED")
        is not True
        or flags.get("GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED")
        is not True
        or flags.get("SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED") is not True
        or flags.get("CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED") is not True
        or flags.get("GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE") is not True
        or flags.get("GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED") is not True
        or flags.get("GENERIC_GHOST_N3_POLE3_RELATIVE_IBP_COMPUTED") is not True
        or flags.get("SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED") is not True
        or flags.get("GENERIC_GHOST_N3_TEN_POLE3_INTEGRATED_FUNCTIONS_COMPUTED")
        is not True
        or flags.get("GENERIC_GHOST_N3_CORNER_ANGULAR_FLUXES_EVALUATED")
        is not True
        or flags.get("GENERIC_GHOST_N3_I29_POLE4_REDUCED") is not True
        or flags.get("GENERIC_GHOST_N3_ALL_ELEVEN_FUNCTIONS_COMPUTED") is not True
        or flags.get("GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED")
        is not False
        or flags.get("GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED")
        is not False
        or flags.get("GENERIC_GHOST_LONGITUDINAL_DW_CARRIERS_EVALUATED")
        is not False
        or flags.get("ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED")
        is not False
        or flags.get("ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED")
        is not False
        or flags.get("GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED")
        is not False
        or flags.get("REPOSITORY_GENERIC_BACKGROUND_CPT_TRACE_SUBSTITUTION_SUPPLIED")
        is not False
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
            "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED",
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
            "REPOSITORY_TT_HESSIAN_HISTORICAL_MISSING_CARRIER_CLOSED",
            "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE",
            "STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED",
            "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE",
            "GENERIC_PHYSICAL_HESSIAN_LINEAR_CURVATURE_IMPORTED",
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY",
            "PHYSICAL_H1_FORMAL_ADJOINT_MOMENTUM_VERTEX_VERIFIED",
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED",
            "FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED",
            "CURVATURE_SQUARED_PHYSICAL_HESSIAN_LAYER_SUPPLIED",
            "PHYSICAL_N3_THREE_LINEAR_TRIANGLE_COMPUTED",
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY",
            "FULL_BV_LEDGER_COMPOSER_READY",
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED",
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED",
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED",
            "REPOSITORY_C2_COEFFICIENT_COMPUTED",
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
            "REGULATED_SLAVNOV_BREAKING_COMPUTED",
            "QME_OBSTRUCTED_STRICT_FIELD_CONTENT",
            "STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED",
            "WZ_AFN0_PRIMITIVE_CERTIFIED",
            "WZ_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED",
            "WZ_TAU_ADIC_EXTENDED_H04_H14_COMPLETE",
            "TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED",
            "WZ_LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED",
            "FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO",
            "ANOMALY_INDUCED_NONLOCAL_GAMMA1_REPRESENTATIVE_SUPPLIED",
            "FLAT_TT_UNIVERSAL_LOG_GAMMA1_FORM_FACTOR_FIXED",
            "CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED",
            "FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE",
            "FV_CONFORMIZED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED",
            "FV_ANOMALY_ACTION_FIXED",
            "RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED",
            "ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE",
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE",
            "FIVE_UNIVERSAL_CPT_THIRD_CURVATURE_KERNELS_IMPORTED",
            "GENERIC_BACKGROUND_GHOST_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED",
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED",
            "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED",
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED",
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED",
            "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED",
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION",
            "SCHUR_CORRECTION_S3_CLASS_PROVED",
            "CANONICAL_DET3_TAIL_DEFINED",
            "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED",
            "WODZICKI_RESIDUE_K_COMPUTED",
            "WODZICKI_RESIDUE_LOG_S_COMPUTED",
            "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED",
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED",
            "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED",
            "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED",
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE",
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED",
            "GENERIC_GHOST_N3_POLE3_RELATIVE_IBP_COMPUTED",
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED",
            "GENERIC_GHOST_N3_TEN_POLE3_INTEGRATED_FUNCTIONS_COMPUTED",
            "GENERIC_GHOST_N3_CORNER_ANGULAR_FLUXES_EVALUATED",
            "GENERIC_GHOST_N3_I29_POLE4_REDUCED",
            "GENERIC_GHOST_N3_ALL_ELEVEN_FUNCTIONS_COMPUTED",
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED",
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED",
            "GENERIC_GHOST_LONGITUDINAL_DW_CARRIERS_EVALUATED",
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED",
            "REPOSITORY_GENERIC_BACKGROUND_CPT_TRACE_SUBSTITUTION_SUPPLIED",
            "PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE",
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED",
            "FV_AND_WZ_DRESSED_METRICS_IDENTIFIED",
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED",
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED",
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED",
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
            "VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED",
            "REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED",
            "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED",
            "E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED",
            "A_L_BRANCHES_POSITIVE",
            "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED",
            "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED",
            "BERGER_BRIDGE4_CERTIFIED",
            "FINITE_C2_NORMALIZATION_FIXED",
            "FINITE_R2_NORMALIZATION_FIXED",
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY",
            "EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY",
            "REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY",
            "NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND",
            "CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND",
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
            "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY",
            "BERGER_LOCAL_GHOST_HADAMARD_FACTORS_INCLUDED",
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY",
            "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND",
            "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR",
            "BERGER_METRIC_COMPANION_RFHGHO_DILATION",
            "BERGER_DILATED_REGULAR_CAUCHY_MORPHISM_LEGS",
            "BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED",
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED",
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED",
            "BERGER_CUTOFF_VOLTERRA_TRANSPOSE_NORMAL_CONVERGENCE",
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION",
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE",
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING",
            "BERGER_REGULAR_GREENHYP_MORPHISM",
            "BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE",
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE",
            "BERGER_FULL_DILATION_EXACT_CCR",
            "BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY",
            "BERGER_COVARIANCE_LIFT_26_TO_54",
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED",
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED",
            "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR",
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED",
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY",
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED",
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED",
            "CLASSICAL_RELATIVE_TRIANGLE_IMPORTED",
            "RELATIVE_OBSERVABLE_PULLBACK_IMPORTED",
            "RELATIVE_EQUIVARIANCE_IMPORTED",
            "ZETA_SCALE_COEFFICIENT_COMPUTED",
            "ROUND_S4_SCHUR_R_K_COMPUTED",
            "ROUND_S4_SCHUR_FINITE_R_K2_COMPUTED",
            "ROUND_S4_SCHUR_DET3_TAIL_COMPUTED",
            "ROUND_S4_SCHUR_MODIFIED_DETERMINANT_COMPUTED",
            "GENERIC_SCHUR_FINITE_ROWS_REQUIRE_GLOBAL_CARRIER",
            "GENERIC_WEIGHT_RAISED_LOCAL_ZETA_FACTORIZATION_DEFECT_COMPUTED",
            "GENERIC_H1_H2_CONTACT_ENDPOINT_RESIDUES_PROJECTED",
            "SYMMETRIC_PHYSICAL_MIXED_INCIDENCE_ASSEMBLED",
            "SYMMETRIC_H2_CANCELLATION_OF_M14_REFUTED",
            "GENERIC_BOX_TRIANGLE_CORNER_RESIDUES_COMPUTED",
            "GENERIC_PHYSICAL_MIXED_ROWS_ASSEMBLED",
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED",
            "PHYSICAL_M14_NONZERO_SCALE_ROW_RENORMALIZED",
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED",
            "PHYSICAL_TRIANGLE_SIX_MASTER_SPAN_COMPLETE",
            "RENORMALIZED_PHYSICAL_TRIANGLE_MASTER_VALUES_COMPUTED",
            "PHYSICAL_TRIANGLE_SIX_MASTER_COORDINATES_COMPUTED",
            "PHYSICAL_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX_COMPUTED",
            "PHYSICAL_TRIANGLE_FUNCTION_BASIS_DECOMPOSITION_COMPUTED",
            "PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED",
            "PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED",
            "GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED",
            "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED",
        }
    ):
        raise ValueError("active frontier quantum claim was over-promoted")
    if len(result.get("supersession_ledger", [])) != 14:
        raise ValueError("active frontier supersession ledger drifted")
