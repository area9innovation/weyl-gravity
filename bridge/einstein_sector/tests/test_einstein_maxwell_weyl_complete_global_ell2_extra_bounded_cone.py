"""Tests for the complete global plus ell2-extra bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone import OUTPUT, build


class CompleteGlobalEll2ExtraBoundedConeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_cone_equals_standard_global(self) -> None:
        theorem = self.value["complete_bounded_theorem"]
        self.assertTrue(theorem["equality_with_standard_global_cone"])
        self.assertIn("(c,d,W_x,A)", theorem["tangent_cone"])

    def test_extra_is_excluded(self) -> None:
        self.assertTrue(self.value["classification"]["all_nonzero_ell2_extra_directions_bounded_obstructed"])
        self.assertIn("no nonzero ell=2", self.value["complete_bounded_theorem"]["extra_intersection"])

    def test_fail_closed_beyond_scope(self) -> None:
        self.assertFalse(self.value["classification"]["other_harmonics_classified"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
