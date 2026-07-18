from __future__ import annotations

from fractions import Fraction
import json
import unittest

from spectral.euclidean.round_s4_negative_scalar_phase import OUTPUT, build, phase_ledger
from spectral.euclidean.verify_round_s4_negative_scalar_phase import verify


class RoundS4NegativeScalarPhaseTests(unittest.TestCase):
    def test_two_spectral_cuts_have_opposite_gamma_phase(self) -> None:
        phase = phase_ledger()
        self.assertEqual(phase["upper_cut_Gamma_phase_in_units_of_i_pi"], {"numerator": -1, "denominator": 2})
        self.assertEqual(phase["lower_cut_Gamma_phase_in_units_of_i_pi"], {"numerator": 1, "denominator": 2})
        self.assertEqual(Fraction(**phase["phase_jump_in_units_of_i_pi"]), -1)

    def test_local_and_global_status_are_separate(self) -> None:
        value = build()
        self.assertTrue(value["claim_flags"]["PHASE_IRRELEVANT_TO_LOCAL_SLAVNOV_BREAKING_ON_FIXED_SIGN_CHAMBER"])
        self.assertFalse(value["claim_flags"]["GLOBAL_DETERMINANT_BRANCH_SELECTED"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
