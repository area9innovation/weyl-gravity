from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class SobolevBohrNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.json").read_text())

    def test_domain_is_finite_order_sobolev_graph(self) -> None:
        domain = self.value["declared_sobolev_bohr_domain"]
        self.assertEqual(domain["regularity"], "integer s>=6")
        self.assertIn("0<=j<=4", domain["mode_space"])

    def test_domain_strictly_extends_wiener(self) -> None:
        self.assertTrue(self.value["classification"]["strict_extension_beyond_smooth_wiener_domain"])
        self.assertIn("c_ell=", self.value["declared_sobolev_bohr_domain"]["strictly_weaker_than_smooth_wiener"])

    def test_source_and_projection_are_continuous(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["continuous_quadratic_source_map_certified"])
        self.assertTrue(classification["continuous_bohr_adjoint_projection_certified"])

    def test_bounded_sobolev_bohr_class_is_obstructed(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["BOUNDED_UNIFORMLY_ALMOST_PERIODIC_SOBOLEV_GRAPH"]["status"], "OBSTRUCTED")

    def test_higher_lifecycles_fail_closed(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["SMOOTH_INFINITE_SECULAR"]["status"], "OPEN")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_maximal_energy_and_nonzero_k_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["maximal_finite_energy_or_low_regularity_completion_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
