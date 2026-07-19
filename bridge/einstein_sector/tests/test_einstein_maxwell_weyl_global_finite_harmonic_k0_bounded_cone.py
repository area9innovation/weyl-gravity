"""Tests for the global finite-harmonic k0 bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone import OUTPUT, build


class GlobalFiniteHarmonicK0BoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_complete_union(self) -> None:
        self.assertTrue(self.value["complete_bounded_cone"]["union_is_necessary_and_sufficient"])

    def test_cross_ell_is_included(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["arbitrary_finite_generic_ell_global_bounded_cone_classified"])
        self.assertTrue(classification["cross_ell_wave_superpositions_classified"])

    def test_minus_channel_isolated(self) -> None:
        separation = self.value["global_wave_separation"]
        self.assertIn("distinct from every other primary shell", separation["selected_channel"])
        self.assertIn("none contributes to the adjoint projection", separation["other_global_columns"])
        self.assertIn("forces a=b=d=0", separation["consequence"])

    def test_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["infinite_harmonic_completion_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertFalse(classification["exceptional_wave_inputs_classified"])


if __name__ == "__main__":
    unittest.main()
