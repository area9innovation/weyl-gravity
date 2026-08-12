import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_history_incidence_isometry import CERT, verify


class HistoryIncidenceIsometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_finite_instrument_and_open_BT_gate(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["normalized_finite_channel_instrument_with_survival"], "EXACTLY_CONSTRUCTED")
        self.assertEqual(result["BT_affiliated_spacetime_detector_instrument"], "NOT_CONSTRUCTED")

    def test_rejects_forbidden_history(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["typed_history_carrier"]["allowed_histories"][0]["intermediate_channel"] = 0
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_false_isometry(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["typed_history_carrier"]["isometry_identity"] = "W_hist^T*W_hist=2*I10"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_spacetime_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["finite_channel_instrument"]["status"] = "BT_SPACETIME_INSTRUMENT"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["finite_inclusive_probability"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
