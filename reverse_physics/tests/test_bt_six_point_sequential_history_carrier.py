import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_sequential_history_carrier import CERT, verify


class SequentialHistoryCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_constructed_carrier_but_open_dynamics(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["on_shell_factorization_channel_carrier"], "EXACTLY_CONSTRUCTED")
        self.assertEqual(result["BT_dynamical_Moller_affiliation"], "NOT_CONSTRUCTED")

    def test_rejects_residue_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_channel_carrier"]["complete_channel_gram"][0][0] = "1"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_positive_interference_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["sequential_interference_boundary"]["connected_interference"] = "positive outcome Gram"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_moller_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["BT_dynamical_Moller_affiliation"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
