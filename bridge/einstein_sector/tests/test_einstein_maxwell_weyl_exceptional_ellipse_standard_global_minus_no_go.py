from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class StandardGlobalMinusNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json").read_text())

    def test_global_polynomial_reduction(self) -> None:
        self.assertEqual(self.value["standard_global_reduction"]["universal_bounded_polynomial_ideal"], "b=0, B=0, Q_e*a=0")
        self.assertIn("Wiener-Bohr completion", self.value["standard_global_reduction"]["completion_extension"])

    def test_all_spectator_transports_are_named(self) -> None:
        self.assertEqual(set(self.value["standard_global_reduction"]["spectators"]), {"W_x", "Q_e", "c", "A"})

    def test_triangular_pivots_remove_a_then_d(self) -> None:
        reduction = self.value["triangular_resonant_reduction"]
        self.assertIn("forces a=0", reduction["first_step"])
        self.assertIn("d!=0", reduction["second_step"])

    def test_bounded_class_is_obstructed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"], "OBSTRUCTED")

    def test_oscillatory_nonminus_gate_remains_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["genuinely_oscillatory_nonminus_carriers_classified"])
        self.assertFalse(classification["smooth_infinite_secular_extension_classified"])


if __name__ == "__main__":
    unittest.main()
