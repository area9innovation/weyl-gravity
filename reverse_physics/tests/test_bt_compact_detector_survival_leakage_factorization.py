import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_compact_detector_survival_leakage_factorization import CERT, verify


class CompactDetectorSurvivalLeakageFactorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_changed_leakage_amplitude(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["two_completion_witness"]["leaky_amplitude"]["numerator"] = 1
        self.assert_rejected(mutation)

    def test_rejects_changed_virtual_coefficient(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["two_completion_witness"]["leaky_forward_Hermitian_coefficient"]["denominator"] = 10
        self.assert_rejected(mutation)

    def test_rejects_wrong_no_click_factorization(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["order_lambda8_identity"]["factorization"] = "detector no-click=true survival"
        self.assert_rejected(mutation)

    def test_rejects_zero_leakage_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_BT_disposition"]["outside_positive_transition_block"] = "ZERO"
        self.assert_rejected(mutation)

    def test_rejects_Julia_dynamical_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_BT_disposition"]["minimal_Julia_dilation"] = "BT_EVOLUTION"
        self.assert_rejected(mutation)

    def test_rejects_full_dynamics_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_BT_disposition"]["complete_BT_finite_time_evolution"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_missing_column_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["missing_object_ledger"].pop(0)
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("the standard scalar projector or general Eq. (19)")
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
