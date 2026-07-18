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
        self.assertTrue(ladder["G5"].startswith("BLOCKED"))

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
            "EXTENDED_CLASSICAL_CONTRACTION_AND_ONE_LOOP_SLAVNOV_OPERATOR_Q1",
        )
        self.assertEqual(
            self.payload["ordered_next_gates"][-1],
            "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        )

    def test_hadamard_existence_boundary_is_authoritative(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA_DEFINED"])
        self.assertTrue(flags["CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED"])
        self.assertTrue(flags["COMPANION_DECOMPOSABILITY_CERTIFIED"])
        self.assertTrue(flags["TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"])
        self.assertTrue(flags["STATIONARY_GENERATOR_IMPORT_CONSUMER_READY"])
        self.assertFalse(flags["HADAMARD_EXISTENCE_THEOREM_APPLIES"])
        row = self.payload["active_rows"]["free_Lorentzian_state"]
        self.assertIn(
            "STATIONARY_IMPORT_CONSUMER_READY_INPUT_ABSENT",
            row["status"],
        )
        self.assertEqual(
            row["next_gate"],
            "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
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
