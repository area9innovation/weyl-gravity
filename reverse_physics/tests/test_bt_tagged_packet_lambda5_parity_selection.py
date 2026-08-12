import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_packet_lambda5_parity_selection import CERT, verify


class TaggedPacketLambda5ParitySelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_parity_identification_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_covariance"]["distinction"] = "Pi_F is BT ghost parity"
        self.assert_rejected(mutation)

    def test_rejects_action_covariance_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_covariance"]["action"] = "S_lambda=S_lambda"
        self.assert_rejected(mutation)

    def test_rejects_probability_evenness_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_covariance"]["probability"] = "q(lambda)!=q(-lambda)"
        self.assert_rejected(mutation)

    def test_rejects_graph_identity_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["vertex_and_graph_selection"]["graph_identity"] = "E congruent d+1 mod 2"
        self.assert_rejected(mutation)

    def test_rejects_Krein_metric_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["finite_Krein_witness"]["metric"][0][2] = "1"
        mutation["finite_Krein_witness"]["metric"][2][0] = "1"
        self.assert_rejected(mutation)

    def test_rejects_output_parity_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["finite_Krein_witness"]["y3"] = ["1", "0", "5", "7"]
        self.assert_rejected(mutation)

    def test_rejects_lambda5_cross_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_output_selection"]["lambda5_coefficient"] = "q_tag^(5)=1"
        self.assert_rejected(mutation)

    def test_rejects_lambda5_interpretation_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["probability_order_lambda5"] = "UNKNOWN"
        self.assert_rejected(mutation)

    def test_rejects_remainder_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["tagged_probability_remainder_after_lambda4"] = "BEGINS_AT_LAMBDA5"
        self.assert_rejected(mutation)

    def test_rejects_complete_lambda6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_noncovariant_boundary_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("that a detector held noncovariantly fixed under lambda to minus lambda has an even probability")
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_gravity_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["gravity_or_BV_BRST_transfer"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["Lorentzian_causal_claim"] = "ESTABLISHED"
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
