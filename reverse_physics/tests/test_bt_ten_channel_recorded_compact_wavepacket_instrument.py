import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_ten_channel_recorded_compact_wavepacket_instrument import CERT, verify


class TenChannelRecordedCompactWavepacketInstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_changed_channel_order(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["ten_channel_residue_algebra"]["channel_masks"][0:2] = reversed(mutation["ten_channel_residue_algebra"]["channel_masks"][0:2])
        self.assert_rejected(mutation)

    def test_rejects_changed_residue_entry(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["ten_channel_residue_algebra"]["residues"][4]["matrix"][1][2] = "0"
        self.assert_rejected(mutation)

    def test_rejects_non_square_partition(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_square_partition"]["identity"] = "sum_B chi_B=1"
        self.assert_rejected(mutation)

    def test_rejects_soft_zero_admission(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_square_partition"]["acceptance"] = mutation["compact_square_partition"]["acceptance"].replace("excluding every soft q_B=0 point", "including soft q_B=0 points")
        self.assert_rejected(mutation)

    def test_rejects_wrong_amplitude_bound(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["recorded_packet_instrument"]["amplitude_bound"] = "||A_rec||^2<=10"
        self.assert_rejected(mutation)

    def test_rejects_wrong_source_probability(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["declared_scalar_source_probability"]["click"] = "q_click=256*lambda^8"
        self.assert_rejected(mutation)

    def test_rejects_coherent_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["unobserved_coherent_BT_probability"] = "CONSTRUCTED"
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
