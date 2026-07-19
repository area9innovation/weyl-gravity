from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from relative.einstein_weyl_qme_readiness import POLAR_LIFT, _polar_exact_replay, validate
from relative.einstein_weyl_qme_readiness_certificate import HERE, OUTPUT, build_certificate
from relative.verify_einstein_weyl_qme_readiness import verify


class EinsteinWeylQMEReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads((HERE / "schema/einstein-weyl-qme-readiness-v1.schema.json").read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_shared_row_is_complete_and_fail_closed(self) -> None:
        row = self.certificate["shared_relative_row"]
        self.assertEqual(
            set(row),
            {"setting", "map_iota", "cofiber", "relative_pairing", "O2", "residual_action", "observable_map", "quantum_lift"},
        )
        self.assertEqual(
            row["map_iota"],
            "COMPLETE_ALL_ROW_SUPPORT_LOCAL_NONCYCLIC_LINEAR_TRIANGLE_IMPORTED",
        )
        self.assertEqual(
            row["cofiber"],
            "SUPPORT_LOCAL_MAPPING_COFIBER_AND_EXACT_EXTRA_DETECTORS_IMPORTED",
        )
        self.assertEqual(
            row["observable_map"],
            "SUPPORT_LOCAL_LINEAR_BRST_DGA_PULLBACK_IMPORTED",
        )
        self.assertEqual(row["quantum_lift"], "ANALYTIC_FRAMEWORK_MISSING")

    def test_complete_linear_triangle_and_observable_functor_are_imported(self) -> None:
        gate = self.certificate["classical_import_gate"]
        self.assertEqual(
            gate["current_map_disposition"],
            "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED",
        )
        self.assertEqual(
            self.certificate["dependency_refs"]["relative_linear_triangle"]["artifact_id"],
            "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
        )
        self.assertEqual(
            self.certificate["dependency_refs"]["relative_observable_functor"]["artifact_id"],
            "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
        )
        self.assertTrue(
            self.certificate["claim_flags"]["CLASSICAL_RELATIVE_TRIANGLE_IMPORTED"]
        )
        self.assertTrue(
            self.certificate["claim_flags"]["RELATIVE_OBSERVABLE_PULLBACK_IMPORTED"]
        )
        self.assertTrue(
            self.certificate["claim_flags"]["RELATIVE_EQUIVARIANCE_IMPORTED"]
        )

    def test_polar_noether_lift_is_pinned_and_replayed_exactly(self) -> None:
        polar = json.loads(POLAR_LIFT.read_text())
        replay = _polar_exact_replay(polar)
        self.assertEqual(replay["exact_check_count"], 14)
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(
            self.certificate["polar_exact_replay"]["local_Green_time_term_count"],
            184,
        )
        self.assertFalse(
            self.certificate["polar_exact_replay"]["cyclic_BV_chain_map_certified"]
        )
        self.assertTrue(
            self.certificate["claim_flags"]["POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED"]
        )

    def test_background_stabilizer_authority_forbids_automatic_quotient(self) -> None:
        authority = self.certificate["background_stabilizer_authority"]
        self.assertEqual(
            authority["connected_algebra"], "R_H_direct_sum_R_Px_direct_sum_so3"
        )
        self.assertTrue(authority["full_SO42_stabilizer_rejected"])
        self.assertTrue(authority["universal_stabilizer_nullity_refuted"])
        self.assertFalse(authority["common_Taub_zero_derived_sector_complete"])
        self.assertFalse(authority["absolute_residual_gauge_quotient_certified"])
        self.assertTrue(
            self.certificate["claim_flags"][
                "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED"
            ]
        )

    def test_post_linear_gap_ledger_is_exact_and_fail_closed(self) -> None:
        ledger = self.certificate["relative_linear_triangle_gap_ledger"]
        self.assertEqual(len(ledger["established"]), 4)
        remaining = {row["sector"]: row["missing"] for row in ledger["remaining_beyond_V1"]}
        self.assertEqual(
            set(remaining),
            {
                "cyclic_relative_structure",
                "nonlinear_relative_morphism",
                "quantum_relative_lift",
            },
        )
        self.assertIn(
            "standard_pairing_cyclic_map_or_replacement",
            remaining["cyclic_relative_structure"],
        )
        self.assertIn(
            "arity_three_relative_identity",
            remaining["nonlinear_relative_morphism"],
        )
        self.assertIn(
            "matched_Einstein_and_Weyl_QME_dispositions",
            remaining["quantum_relative_lift"],
        )

    def test_only_nonlinear_classical_spine_input_remains(self) -> None:
        gate = self.certificate["classical_import_gate"]
        self.assertEqual(gate["status"], "LINEAR_GATE_SATISFIED_NONLINEAR_GATE_OPEN")
        self.assertEqual(len(gate["received_result_ids"]), 2)
        self.assertEqual(
            gate["remaining_result_ids"],
            ["EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE"],
        )
        self.assertIn("do not reconstruct", gate["forbidden_fallback"])

    def test_relative_anomaly_is_a_contract_not_a_claim(self) -> None:
        anomaly = self.certificate["relative_anomaly_contract"]
        self.assertEqual(anomaly["formal_expression"], "[A_rel]=[A_Weyl-iota_* A_Einstein]")
        self.assertEqual(
            anomaly["status"],
            "CLASSICAL_PULLBACK_AVAILABLE_QUANTUM_CLASS_UNDEFINED",
        )
        self.assertNotIn("off_shell_BV_chain_map_iota", anomaly["required_before_definition"])
        self.assertIn("antifield", anomaly["separate_ledgers"])
        self.assertIn("boundary_corner", anomaly["separate_ledgers"])

    def test_frameworks_and_qme_are_not_conflated(self) -> None:
        ledger = self.certificate["framework_ledger"]
        self.assertEqual(set(ledger), {"LOCAL_ALGEBRAIC", "EUCLIDEAN_SPECTRAL", "REDUCED_MODE", "LORENTZIAN_CAUSAL"})
        self.assertEqual(ledger["LORENTZIAN_CAUSAL"]["status"], "ANALYTIC_FRAMEWORK_MISSING")
        self.assertFalse(self.certificate["qme_and_transfer_gate"]["residual_quantum_transfer_authorized"])

    def test_overclaims_are_rejected(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["RELATIVE_ANOMALY_CLASS_DEFINED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["shared_relative_row"]["quantum_lift"] = "QME_RESTORED"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
