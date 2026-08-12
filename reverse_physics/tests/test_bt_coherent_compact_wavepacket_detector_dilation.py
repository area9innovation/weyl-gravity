import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_coherent_compact_wavepacket_detector_dilation import CERT, verify


class CoherentCompactWavepacketDetectorDilationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_changed_Gram_entry(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["coherent_residue_interference"]["matrix"][1][2] = "7/16"
        self.assert_rejected(mutation)

    def test_rejects_wrong_coherent_bound(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["coherent_packet_effect"]["operator_bound"] = "||A_coh||^2<=144"
        self.assert_rejected(mutation)

    def test_rejects_wrong_source_probability(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["declared_scalar_source"]["click_probability"] = "q_click=144*lambda^8"
        self.assert_rejected(mutation)

    def test_rejects_non_adjoint_square_click(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["coherent_packet_effect"]["click"] = "E_click=A_coh"
        self.assert_rejected(mutation)

    def test_rejects_BT_virtual_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["BT_virtual_coefficient_boundary"]["public_BT_order_lambda8_virtual_graph"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_dynamical_affiliation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["BT_virtual_coefficient_boundary"]["disposition"] = "BT_DYNAMICALLY_AFFILIATED"
        self.assert_rejected(mutation)

    def test_rejects_missing_object_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["missing_object_ledger"].pop()
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
