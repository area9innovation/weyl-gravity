"""Tests for the repaired a/d polynomial zero locus."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus import OUTPUT, build


class ADPolynomialZeroLocusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_exact_ideal(self) -> None:
        self.assertEqual(
            self.value["polynomial_zero_locus"]["complex_zero_locus"],
            "a*z_ax1=a*z_ax2=a*z_pol1=a*z_pol2=d*z_pol2=0",
        )

    def test_old_cone_survives(self) -> None:
        self.assertEqual(self.value["old_cone_reconciliation"]["status"], "CERTIFIED_UNCHANGED")
        self.assertTrue(self.value["classification"]["old_nonzero_extra_common_zero_cone_survives_repair"])

    def test_fail_closed_resonance(self) -> None:
        self.assertFalse(self.value["classification"]["constant_resonance_zero_locus_solved_on_repaired_branches"])
        self.assertFalse(self.value["classification"]["complete_bounded_cone_solved"])


if __name__ == "__main__":
    unittest.main()
