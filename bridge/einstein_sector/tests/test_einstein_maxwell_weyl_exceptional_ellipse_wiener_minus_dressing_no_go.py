from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class WienerMinusNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json").read_text())

    def test_declared_topology_is_strong_and_explicit(self) -> None:
        topology = self.value["declared_topology"]
        self.assertEqual(topology["name"], "smooth spatial Wiener-Bohr minus class")
        self.assertIn("absolutely and uniformly", topology["consequences"][0])

    def test_projection_is_coefficientwise(self) -> None:
        lemma = self.value["coefficientwise_fredholm_lemma"]
        self.assertIn("Bohr coefficient", lemma["projection"])
        self.assertIn("forces every minus coefficient", lemma["conclusion"])

    def test_bounded_class_is_obstructed(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"], "OBSTRUCTED")

    def test_infinite_secular_and_causal_classes_fail_closed(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["SMOOTH_INFINITE_SECULAR"]["status"], "OPEN")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_maximal_completion_is_not_claimed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["maximal_finite_energy_or_sobolev_completion_classified"])
        self.assertFalse(classification["additional_nonminus_carriers_classified"])


if __name__ == "__main__":
    unittest.main()
