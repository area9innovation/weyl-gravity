import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_complete_tagged_q6_physical_probability import CERT, verify


class CompleteTaggedQ6PhysicalProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def mutate(self, path, value):
        mutation = copy.deepcopy(self.certificate)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        self.assert_rejected(mutation)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_lifecycle_mutation(self):
        self.mutate(("lifecycle_state",), "CLASSIFIED")

    def test_rejects_leading_coefficient_mutation(self):
        self.mutate(("complete_probability", "leading_term"), "wrong")

    def test_rejects_tree_ratio_mutation(self):
        self.mutate(("complete_probability", "relative_q6_coefficient"), "tree omitted")

    def test_rejects_loop_omission(self):
        self.mutate(("complete_probability", "relative_q6_coefficient"), "loop omitted")

    def test_rejects_wrong_remainder(self):
        self.mutate(("complete_probability", "assembled_probability"), "O(lambda7)")

    def test_rejects_spectator_reinstatement(self):
        self.mutate(("complete_probability", "spectator_cross"), "nonzero")

    def test_rejects_incomplete_ledger(self):
        self.mutate(("completeness_audit", "status"), "INCOMPLETE")

    def test_rejects_sign_wall_mutation(self):
        self.mutate(("sign_and_bounds", "zero_wall"), "R6 never vanishes")

    def test_rejects_universal_sign(self):
        self.mutate(("interpretation", "universal_q6_sign"), "POSITIVE")

    def test_rejects_all_order_promotion(self):
        self.mutate(("interpretation", "all_order_positivity"), "PROVED")

    def test_rejects_eq19_promotion(self):
        self.mutate(("interpretation", "general_Eq19"), "PROVED")

    def test_rejects_all_time_promotion(self):
        self.mutate(("interpretation", "all_time_scattering"), "CONSTRUCTED")

    def test_rejects_gravity_promotion(self):
        self.mutate(("interpretation", "gravity_or_BV_BRST_transfer"), "CONSTRUCTED")

    def test_rejects_lorentzian_promotion(self):
        self.mutate(("interpretation", "Lorentzian_causal_claim"), "ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
