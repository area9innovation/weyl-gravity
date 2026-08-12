import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_positive_sector_physical_detector_effect import CERT, verify


class PositiveSectorPhysicalDetectorEffectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_physical_auxiliary_probability_and_scalar_boundary(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["normalized_two_outcome_probability_jet"], "CONSTRUCTED_ON_DECLARED_POSITIVE_INTERVAL")
        self.assertEqual(result["transported_perfect_square_scalar_source"], "NOT_CONSTRUCTED")

    def test_rejects_residue_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["fixed_shell_transition_effect"]["R_plus"][0][0] = "1/2"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_spectrum_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["fixed_shell_transition_effect"]["spectrum"][-1] = "(3+sqrt(3))/8"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_survival_sign_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["pseudo_unitary_survival_coefficient"]["leading_survival_probability_coefficient"] = "+G"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_scalar_source_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["transported_perfect_square_scalar_source"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_complete_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_finite_time_probability"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["Eq19_all_orders"] = "PROVED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
