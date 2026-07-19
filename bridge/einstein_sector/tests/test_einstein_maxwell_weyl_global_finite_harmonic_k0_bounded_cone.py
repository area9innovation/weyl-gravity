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

    def test_corrected_union(self) -> None:
        cone = self.value["complete_bounded_cone"]
        self.assertFalse(cone["union_is_necessary_and_sufficient"])
        self.assertIn("A=B=0", cone["certified_wave_subcone"])
        self.assertTrue(cone["nonzero_A_wave_stratum"].startswith("OPEN"))

    def test_cross_ell_is_included(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["arbitrary_finite_generic_ell_global_bounded_cone_classified"])
        self.assertTrue(classification["cross_ell_wave_superpositions_classified"])
        self.assertTrue(classification["A_arbitrary_wave_branch_withdrawn"])
        self.assertTrue(classification["A_zero_wave_subcone_certified"])

    def test_minus_channel_isolated(self) -> None:
        separation = self.value["global_wave_separation"]
        self.assertIn("distinct from every other primary shell", separation["selected_channel"])
        self.assertIn("constant A is excluded", separation["other_global_columns"])
        self.assertIn("forces a=b=d=0", separation["consequence"])

    def test_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["infinite_harmonic_completion_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertFalse(classification["exceptional_wave_inputs_classified"])


if __name__ == "__main__":
    unittest.main()
