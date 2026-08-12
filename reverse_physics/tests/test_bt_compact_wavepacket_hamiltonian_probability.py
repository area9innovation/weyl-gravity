import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_compact_wavepacket_hamiltonian_probability import CERT, verify


class CompactWavepacketHamiltonianProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_wrong_phase_density(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["full_phase_space_measure"]["density_without_two_pi"] = "rho=1"
        self.assert_rejected(mutation)

    def test_rejects_singular_input_center(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_shell_geometry"]["incoming_center"][3] = "0"
        self.assert_rejected(mutation)

    def test_rejects_missing_denominator_margin(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["Hamiltonian_packet_operator"]["pointwise_bound"] = "|beta|<=T"
        self.assert_rejected(mutation)

    def test_rejects_missing_cutoff_normalization(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["assumptions"] = [row.replace(" obeys |chi|<=1 and", "") for row in mutation["assumptions"]]
        self.assert_rejected(mutation)

    def test_rejects_wrong_source_probability(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["positive_packet_probability"]["declared_source_click"] = "q_click=256*lambda^8*||K F||^2"
        self.assert_rejected(mutation)

    def test_rejects_missing_small_coupling_domain(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["positive_packet_probability"]["sufficient_positive_domain"] = "all lambda and T"
        self.assert_rejected(mutation)

    def test_rejects_global_ten_channel_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["ten_channel_global_probability"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_general_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
