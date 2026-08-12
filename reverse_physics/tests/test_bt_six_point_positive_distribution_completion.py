import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_positive_distribution_completion import CERT, verify


class PositiveDistributionCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_no_positive_extension_and_open_physical_gate(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["positive_exclusive_distributional_completion"], "EXACT_NO_GO")
        self.assertEqual(result["finite_inclusive_probability"], "NOT_CONSTRUCTED")

    def test_rejects_false_positive_completion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_distribution_theorem"]["conclusion"] = "POSITIVE_EXTENSION_EXISTS"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_physical_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["finite_inclusive_probability"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_type_conflation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["typed_candidate_audit"]["existing_NLO_support"] = mutation["typed_candidate_audit"]["new_singular_support"]
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
