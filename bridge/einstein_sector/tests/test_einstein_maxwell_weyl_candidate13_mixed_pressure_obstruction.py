import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json"


class Candidate13MixedPressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independence_witness_is_explicit(self) -> None:
        theorem = self.value["independence_theorem"]
        self.assertEqual(theorem["five_moment_maps"], "zero")
        self.assertEqual(theorem["candidate_13_cross_fibre_functionals"], "zero")
        self.assertEqual(theorem["bounded_circle_pressure_functional"], "strictly negative")

    def test_zero_frequency_source_is_typed_pressure_pairing(self) -> None:
        source = self.value["zero_frequency_source"]
        self.assertIn("(1/2)D^2E_WM", source["typed_pairing"])
        self.assertNotEqual(source["value"], "0")
        self.assertIn("no componentwise E11", source["calibration_boundary"])

    def test_correction_classes_are_separate(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(classes["smooth_exponential_polynomial"]["status"], "CERTIFIED")
        self.assertEqual(classes["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_full_cone_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["complete_candidate13_mixed_cone_classified"])


if __name__ == "__main__":
    unittest.main()
