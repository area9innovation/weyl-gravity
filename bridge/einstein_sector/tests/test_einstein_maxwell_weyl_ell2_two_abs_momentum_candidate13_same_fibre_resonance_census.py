import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json"


class Candidate13SameFibreResonanceCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_complete_nonzero_channel_count(self) -> None:
        self.assertEqual(self.value["channel_count"], 18)
        self.assertEqual(self.value["nonzero_defect_count"], 144)
        self.assertTrue(all(defect["witness"]["excludes_zero"] for row in self.value["channels"] for defect in row["nonzero_shell_defects"]))
        differences = [row for row in self.value["channels"] if row["temporal_channel"] == "DIFFERENCE"]
        self.assertEqual(len(differences), 6)
        self.assertTrue(all("K=0 and Omega!=0" in row["ell0_disposition"] for row in differences))

    def test_zero_frequency_gate_remains_open(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["candidate_13_all_nonzero_same_fibre_channels_off_shell"])
        self.assertTrue(classification["ell0_homogeneous_nonzero_frequency_quotient_empty_imported"])
        self.assertFalse(classification["same_fibre_zero_frequency_source_matrices_classified"])
        self.assertFalse(classification["mixed_Einstein_extra_taub_intersection_classified"])
        self.assertEqual(self.value["zero_frequency_remainder"]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
