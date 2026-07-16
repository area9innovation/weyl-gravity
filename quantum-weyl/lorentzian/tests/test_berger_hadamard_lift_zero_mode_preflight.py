from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_hadamard_lift_zero_mode_preflight import (
    covariance_lift_replay,
    validate,
)
from lorentzian.berger_hadamard_lift_zero_mode_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_hadamard_lift_zero_mode_preflight import verify


class BergerHadamardLiftZeroModePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-hadamard-lift-zero-mode-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_actual_pairing_and_all_exchange_signs_are_replayed(self) -> None:
        audit = self.certificate["rowwise_Koszul_audit"]
        self.assertEqual(len(audit["row_ledger"]), 54)
        self.assertEqual(len(audit["Darboux_pairs"]), 27)
        self.assertEqual(
            audit["ordered_parity_sector_counts"],
            {
                "even_even": 729,
                "even_odd": 729,
                "odd_even": 729,
                "odd_odd": 729,
            },
        )
        self.assertTrue(all(audit["checks"].values()))

    def test_algebraic_homotopy_cancels_from_causal_difference(self) -> None:
        lift = covariance_lift_replay()
        self.assertEqual(lift["replay_coefficients"]["Delta54"], [0, 1, -1])
        self.assertTrue(
            lift["checks"][
                "contractible_28_rows_add_no_independent_singular_covariance"
            ]
        )

    def test_D_Cartan_and_q2_are_imported_without_quantum_promotion(self) -> None:
        compatibility = self.certificate["D_and_interaction_compatibility"]
        self.assertEqual(
            compatibility["causal_cyclic_arity_two_D_Cartan"], "CERTIFIED"
        )
        self.assertEqual(compatibility["state_stationarity_status"], "NOT_COMPUTED")
        self.assertFalse(self.certificate["claim_flags"]["QUANTUM_CLAIM"])

    def test_minimal_missing_carrier_is_exactly_named(self) -> None:
        theorem = self.certificate["zero_frequency_carrier_theorem"]
        self.assertEqual(theorem["status"], "MINIMAL_MISSING_CARRIER")
        self.assertIn("generalized zero eigenspace", theorem["missing_carrier"])
        self.assertEqual(theorem["algebraic_complement_rows"], 28)
        self.assertEqual(theorem["retained_candidate_rows"], 26)

    def test_covariance_and_state_overclaims_fail_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["zero_frequency_carrier_theorem"]["status"] = "COMPLETE"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
