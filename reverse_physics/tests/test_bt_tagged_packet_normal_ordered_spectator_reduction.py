import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_packet_normal_ordered_spectator_reduction import CERT, verify


class NormalOrderedSpectatorReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_unclassified_lifecycle(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["lifecycle_state"] = "CLASSIFIED"
        self.assert_rejected(mutation)

    def test_rejects_non_tadpole_topology(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["auxiliary_graph_classification"]["order_lambda2_solution"]["topology"] = "SUNSET"
        self.assert_rejected(mutation)

    def test_rejects_extra_order_two_topology(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["auxiliary_graph_classification"]["other_order_lambda2_two_point_topologies"] = "BUBBLE"
        self.assert_rejected(mutation)

    def test_rejects_momentum_dependent_tadpole(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_and_counterterm_ledger"]["external_momentum_degree"] = 2
        self.assert_rejected(mutation)

    def test_rejects_incomplete_counterterm_basis(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_and_counterterm_ledger"]["two_point_basis"] = ["Omega*Upsilon"]
        self.assert_rejected(mutation)

    def test_rejects_missing_normal_order_condition(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_and_counterterm_ledger"]["normal_ordering"] = "UNDECLARED"
        self.assert_rejected(mutation)

    def test_rejects_nonzero_spectator_block(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_and_counterterm_ledger"]["renormalized_order_lambda2_two_point_block"] = "S2_spectator!=0"
        self.assert_rejected(mutation)

    def test_rejects_spectator_cross_reinstatement(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["reduced_probability_ledger"]["spectator_cross"] = "MISSING"
        self.assert_rejected(mutation)

    def test_rejects_active_loop_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["reduced_probability_ledger"]["active_loop_cross"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_complete_q6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_public_scheme_overclaim(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["frame_boundary"]["status"] = "PUBLICLY_FORCED_UNIQUE_SCHEME"
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
