import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_scalar_dressed_positive_source_affiliation import CERT, verify


class ScalarDressedPositiveSourceAffiliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_scalar_probability_and_Eq19_boundary(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["leading_scalar_click_no_click_probability_jet"], "TRANSFERRED_WITHOUT_REFITTING")
        self.assertEqual(result["general_Eq19"], "NOT_PROVED")

    def test_rejects_charge_support_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["positive_BT_source"]["source_projector_charge_support"] = [-6, 6]
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_Laurent_branch_loss(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["formal_Rt_affiliation"]["scalar_Laurent_orbit_support"] = ["1", "Z^6"]
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_rate_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["transferred_scalar_detector_effect"]["declared_source_rate"] = "lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_standard_projector_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["standard_shift_invariant_P_chi"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_general_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_all_time_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["all_time_scalar_probability"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_fixture_as_public_Rt(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["formal_Rt_affiliation"]["fixture_role"] = "the public Rt matrix"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
