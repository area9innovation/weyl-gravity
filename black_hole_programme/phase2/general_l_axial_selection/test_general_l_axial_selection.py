import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class SelectionCounterexampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((HERE / "certificate.json").read_text())

    def test_fail_closed_disposition(self):
        self.assertFalse(self.payload["claim_flags"]["generic_l_axial_einstein_selection_certified"])
        self.assertTrue(self.payload["claim_flags"]["first_exact_counterexample_certified"])
        self.assertEqual(self.payload["disposition"]["X2"],
                         "unclassified after the first exact counterexample stop condition fired")

    def test_current_is_finite(self):
        self.assertEqual(self.payload["literal_current"]["E0|X0"]["leading_power"], -2)
        self.assertTrue(self.payload["literal_current"]["X0|X0"]["finite"])


if __name__ == "__main__":
    unittest.main()
