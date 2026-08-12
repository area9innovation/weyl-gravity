import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_complete_connected_order4_packet_column import CERT, verify


class CompleteConnectedOrder4PacketColumnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_graph_type_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["connected_graph_classification"]["order4_types"][1]["loops"] = 1
        self.assert_rejected(mutation)

    def test_rejects_graph_row_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["connected_graph_classification"]["enumerated_graph_rows"][0]["I"] = 2
        self.assert_rejected(mutation)

    def test_rejects_negative_parity_leakage(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["positive_output_closure"]["status"] = "NEGATIVE_OUTPUT_PRESENT"
        self.assert_rejected(mutation)

    def test_rejects_square_partition_tree_weight(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["unpartitioned_compact_packet_column"]["tree_weight_rule"] = "SQUARE_PARTITION"
        self.assert_rejected(mutation)

    def test_rejects_wrong_amplitude_bound(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["unpartitioned_compact_packet_column"]["operator_bound"] = "||A_full,C||^2<=1296"
        self.assert_rejected(mutation)

    def test_rejects_global_soft_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["outside_leakage_reduction"]["global_kernel"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_disconnected_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["outside_leakage_reduction"]["disconnected_spectator_terms"] = "INCLUDED"
        self.assert_rejected(mutation)

    def test_rejects_missing_soft_object_removal(self):
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
