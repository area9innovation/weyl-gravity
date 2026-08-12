import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_finite_time_shell_column import CERT, verify


class FiniteTimeShellColumnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_constructed_local_column_and_open_global_gate(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["normalized_local_survival_plus_history_column"], "EXACTLY_CONSTRUCTED")
        self.assertEqual(result["finite_inclusive_BT_probability"], "NOT_CONSTRUCTED")

    def test_rejects_nonnull_momentum(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_physical_shell"]["intermediate_momentum"][1] = "1/2"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_norm_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["local_history_column"]["Q_T"] = "pi*T/E"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_global_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["normalized_survival_completion"]["status"] = "GLOBAL_BT_MOLLER_OPERATOR"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["finite_inclusive_BT_probability"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
