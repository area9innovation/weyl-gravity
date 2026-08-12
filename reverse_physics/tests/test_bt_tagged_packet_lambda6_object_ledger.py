import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_packet_lambda6_object_ledger import CERT, verify


class TaggedPacketLambda6ObjectLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_lifecycle_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["lifecycle_state"] = "COEFFICIENT_COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_T3_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["fixed_BT_expansion"]["order_three_block"] = "Pout*T3*Pin!=0"
        self.assert_rejected(mutation)

    def test_rejects_q6_formula_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["probability_ledger"]["q6_formula"] = "q6=tree only"
        self.assert_rejected(mutation)

    def test_rejects_loop_completion_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["probability_ledger"]["active_loop_status"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_spectator_self_energy_omission(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["probability_ledger"]["spectator_self_energy_status"] = "ABSENT"
        self.assert_rejected(mutation)

    def test_rejects_survival_insertion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["probability_ledger"]["survival_term"] = "INCLUDED"
        self.assert_rejected(mutation)

    def test_rejects_dressing_double_count(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["probability_ledger"]["source_detector_terms"] = "ADDITIONAL_Q6_SUMMANDS"
        self.assert_rejected(mutation)

    def test_rejects_hard_log_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["active_loop_boundary_condition"]["status"] = "COMPLETE_PACKET_LOOP"
        self.assert_rejected(mutation)

    def test_rejects_complete_q6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
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
