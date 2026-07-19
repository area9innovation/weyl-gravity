from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class CompleteK0EllipseNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.json").read_text())

    def test_complete_inventory(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["complete_declared_k0_carrier_covered"])
        self.assertTrue(classification["all_finite_k0_nonminus_oscillators_covered"])

    def test_taub_requires_minus(self) -> None:
        self.assertIn("at least one", self.value["taub_reduction"]["necessity"])

    def test_minus_shell_is_isolated(self) -> None:
        self.assertIn("only d*C_parity", self.value["complete_minus_shell_isolation"]["remaining_source"])

    def test_bounded_cone_is_empty(self) -> None:
        self.assertTrue(self.value["classification"]["bounded_tangent_cone_intersection_empty_over_nonzero_ellipse"])
        self.assertEqual(self.value["correction_classes"]["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"], "OBSTRUCTED")

    def test_higher_lifecycles_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
