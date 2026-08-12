import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_scalar_dressed_source_compact_wavepacket import CERT, verify


class ScalarDressedSourceCompactWavepacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_compact_source_and_domain_are_constructed(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["compact_continuum_scalar_source"], "CONSTRUCTED")
        self.assertEqual(result["common_closable_Gaussian_domain"], "CONSTRUCTED")

    def test_rejects_missing_support_gap(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_packet_carrier"]["support_hypotheses"] = "compact supports including p=0"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_dropped_reflected_annihilator(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_packet_carrier"]["Omega_creator_full"] = mutation["compact_packet_carrier"]["Omega_creator_on_declared_frame"]
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_packet_rate_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["packet_BT_Hamiltonian_strength"] = "COMPUTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_ordinary_Fock_IR_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["ordinary_massless_Fock_IR_limit"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_general_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_lost_trace_norm_control(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["finite_volume_approximation"]["rank_one_bound"] = "operator convergence assumed"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
