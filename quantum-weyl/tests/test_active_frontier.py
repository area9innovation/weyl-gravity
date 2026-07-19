from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from active_frontier import build, validate
from active_frontier_certificate import HERE, OUTPUT, build_certificate
from verify_active_frontier import verify


class ActiveFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_frontier_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads((HERE / "schema/active-frontier-v1.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)

    def test_g2_local_bv_cohomology_is_complete(self) -> None:
        ladder = self.payload["promotion_ladder"]
        self.assertEqual(ladder["G1"], "PASSED_AFN0_LOCAL_QUOTIENT")
        self.assertTrue(self.payload["claim_flags"]["ANTIFIELD_EXPORT_V2_RECEIVER_READY"])
        self.assertTrue(self.payload["claim_flags"]["CLASSICAL_ANTIFIELD_EXPORT_IMPORTED"])
        self.assertTrue(
            self.payload["claim_flags"][
                "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REGULATED_BV_INSERTION_V2_RECEIVER_READY"]
        )
        self.assertTrue(self.payload["claim_flags"]["MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC"])
        self.assertTrue(
            self.payload["claim_flags"]["MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS"]
        )
        self.assertEqual(ladder["G2"], "PASSED_LOCAL_BV_COHOMOLOGY_REGULAR_BACH_LOCUS")
        self.assertTrue(
            self.payload["claim_flags"]["GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE"]
        )
        self.assertTrue(self.payload["claim_flags"]["FULL_BV_G2_COMPLETE"])
        self.assertEqual(
            ladder["G3"],
            "PASSED_REPOSITORY_EUCLIDEAN_COEFFICIENT_AND_SLAVNOV_BREAKING",
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REPOSITORY_TT_HESSIAN_HISTORICAL_MISSING_CARRIER_CLOSED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["STANDARD_TT_AUXILIARY_CONTOUR_AND_PHASE_FIXED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE_COMPLETE"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["FULL_BV_LEDGER_COMPOSER_READY"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REPOSITORY_C2_COEFFICIENT_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REGULATED_SLAVNOV_BREAKING_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["QME_OBSTRUCTED_STRICT_FIELD_CONTENT"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED"
            ]
        )
        self.assertTrue(self.payload["claim_flags"]["WZ_AFN0_PRIMITIVE_CERTIFIED"])
        self.assertTrue(
            self.payload["claim_flags"]["WZ_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["WZ_TAU_ADIC_EXTENDED_H04_H14_COMPLETE"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["WZ_LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "ANOMALY_INDUCED_NONLOCAL_GAMMA1_REPRESENTATIVE_SUPPLIED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "FLAT_TT_UNIVERSAL_LOG_GAMMA1_FORM_FACTOR_FIXED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "FV_CONFORMIZED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED"
            ]
        )
        self.assertTrue(self.payload["claim_flags"]["FV_ANOMALY_ACTION_FIXED"])
        self.assertTrue(
            self.payload["claim_flags"]["RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED"]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_BACKGROUND_GHOST_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION"
            ]
        )
        self.assertTrue(self.payload["claim_flags"]["SCHUR_CORRECTION_S3_CLASS_PROVED"])
        self.assertTrue(self.payload["claim_flags"]["CANONICAL_DET3_TAIL_DEFINED"])
        self.assertTrue(
            self.payload["claim_flags"]["CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"]
        )
        self.assertTrue(self.payload["claim_flags"]["WODZICKI_RESIDUE_K_COMPUTED"])
        self.assertTrue(
            self.payload["claim_flags"]["WODZICKI_RESIDUE_LOG_S_COMPUTED"]
        )
        self.assertFalse(self.payload["claim_flags"]["RENORMALIZED_R_K_COMPUTED"])
        self.assertFalse(self.payload["claim_flags"]["FINITE_PART_R_K2_COMPUTED"])
        self.assertTrue(self.payload["claim_flags"]["ZETA_SCALE_COEFFICIENT_COMPUTED"])
        self.assertTrue(self.payload["claim_flags"]["ROUND_S4_SCHUR_R_K_COMPUTED"])
        self.assertTrue(
            self.payload["claim_flags"]["ROUND_S4_SCHUR_FINITE_R_K2_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["ROUND_S4_SCHUR_DET3_TAIL_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "ROUND_S4_SCHUR_MODIFIED_DETERMINANT_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["GENERIC_SCHUR_FINITE_ROWS_REQUIRE_GLOBAL_CARRIER"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N3_TEN_POLE3_INTEGRATED_FUNCTIONS_COMPUTED"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N3_CORNER_ANGULAR_FLUXES_EVALUATED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "GENERIC_GHOST_LONGITUDINAL_DW_CARRIERS_EVALUATED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"][
                "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"
            ]
        )
        self.assertFalse(
            self.payload["claim_flags"]["FV_AND_WZ_DRESSED_METRICS_IDENTIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["RAW_ZETA_BOXR_COEFFICIENT_COMPUTED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["NONLOCAL_R2_FORM_FACTOR_COMPUTED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED"]
        )
        self.assertFalse(self.payload["claim_flags"]["A_L_BRANCHES_POSITIVE"])
        self.assertFalse(
            self.payload["claim_flags"]["FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED"]
        )
        self.assertFalse(self.payload["claim_flags"]["BERGER_BRIDGE4_CERTIFIED"])
        self.assertFalse(
            self.payload["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["FINITE_R2_NORMALIZATION_FIXED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        )
        self.assertFalse(
            self.payload["claim_flags"]["FULL_EXTENDED_BV_QME_RESTORED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT_READY"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["SLAVNOV_BV_INSERTION_GAP_ISOLATED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_READY"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["DIFF_WEYL_SCALAR_GHOST_REDUCTION_VERIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"][
                "YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCHED_NONZERO_MODES"
            ]
        )
        self.assertTrue(
            self.payload["claim_flags"]["STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED"]
        )
        self.assertTrue(
            self.payload["claim_flags"]["STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND"]
        )
        self.assertEqual(
            ladder["G4"],
            "DISPOSITION_COMPLETE_STRICT_OBSTRUCTED_TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED",
        )
        self.assertEqual(
            ladder["G5"],
            "PARTIAL_REDUCED_VACUUM_CYLINDER_BRIDGE4_CERTIFIED_FULL_BV_BRST_HADAMARD_AND_RENORMALIZED_PRODUCTS_OPEN",
        )

    def test_supersession_does_not_delete_history(self) -> None:
        for row in self.payload["supersession_ledger"]:
            self.assertIn("HISTORY_RETAINED", row["disposition"])

    def test_retained_mixed_ell3_is_independently_accepted(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM"])
        self.assertTrue(flags["MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM"])
        self.assertTrue(flags["COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED"])
        self.assertTrue(flags["MIXED_Q3_INPUT_UNBLOCKED"])
        self.assertTrue(flags["MIXED_Q3_INDEPENDENTLY_ACCEPTED"])
        self.assertTrue(flags["RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED"])
        self.assertTrue(flags["RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY_ACCEPTED"])
        self.assertTrue(flags["RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_ACCEPTED"])
        self.assertTrue(flags["RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY"])
        self.assertTrue(
            flags["RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTION_IMPORTED"]
        )
        self.assertTrue(flags["RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED"])
        self.assertTrue(flags["BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT_COMPLETE"])
        self.assertFalse(flags["RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED"])
        self.assertTrue(flags["RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED"])
        self.assertFalse(flags["RANK_46_IS_QUANTUM_PREREQUISITE"])
        row = self.payload["active_rows"]["classical_interacting_input"]
        self.assertIn("FULL_BV_CYCLICITY_ACCEPTED", row["status"])
        self.assertIn("RANK_46_CYCLIC_GRAPH_CARRIER_IMPORTED", row["status"])
        self.assertIn("PROJECTOR_OPEN", row["status"])
        self.assertEqual(
            row["next_gate"],
            "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        )
        self.assertEqual(
            self.payload["ordered_next_gates"][0],
            "CONSTRUCT_EXACT_RELATIVE_SIMPLEX_IBP_PRIMITIVES_WITH_PUNCTURED_CORNER_FLUX_AND_I10_EDGE_BUBBLE_DISPOSITION",
        )
        self.assertEqual(
            self.payload["ordered_next_gates"][-1],
            "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        )

    def test_reduced_bridge4_and_full_bv_hadamard_boundaries_are_authoritative(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED"])
        self.assertTrue(flags["CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED"])
        self.assertTrue(flags["COMPANION_DECOMPOSABILITY_CERTIFIED"])
        self.assertTrue(flags["TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"])
        self.assertTrue(flags["STATIONARY_GENERATOR_IMPORT_CONSUMER_READY"])
        self.assertFalse(flags["HADAMARD_EXISTENCE_THEOREM_APPLIES"])
        self.assertTrue(flags["VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED"])
        self.assertTrue(flags["REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"])
        self.assertFalse(flags["FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"])
        row = self.payload["active_rows"]["free_Lorentzian_state"]
        self.assertIn(
            "VACUUM_CYLINDER_REDUCED_BRIDGE4_KREIN_HADAMARD_CARRIER_CERTIFIED",
            row["status"],
        )
        self.assertEqual(
            row["next_gate"],
            "FULL_BV_BRST_HADAMARD_EXTENSION_OR_SAME_BACKGROUND_BERGER_STATIONARY_MODE_IMPORT",
        )
        algebra_row = self.payload["active_rows"]["free_Lorentzian_algebra"]
        self.assertIn("PRESYMPLECTIC_GRADED_CCR_ALGEBRA_DEFINED", algebra_row["status"])
        self.assertIn("OBSERVABLE_CAUSAL_PROPAGATOR_DEFINED", algebra_row["status"])
        self.assertIn("HADAMARD_STATE_OPEN", algebra_row["status"])
        self.assertEqual(
            algebra_row["next_gate"],
            "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE",
        )

    def test_relative_frontier_imports_polar_but_not_global_triangle(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED"])
        self.assertTrue(flags["PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED"])
        row = self.payload["active_rows"]["relative_Einstein_Weyl"]
        self.assertEqual(
            row["status"],
            "PRINCIPAL_GENERIC_AXIAL_AND_GENERIC_POLAR_UNGAUGED_PREFLIGHTS_GLOBAL_V1_OPEN",
        )
        self.assertEqual(
            row["next_gate"], "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        )

    def test_quantum_overclaim_is_rejected(self) -> None:
        mutant = json.loads(json.dumps(self.payload))
        mutant["claim_flags"]["QME_RESTORED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate())


if __name__ == "__main__":
    unittest.main()
