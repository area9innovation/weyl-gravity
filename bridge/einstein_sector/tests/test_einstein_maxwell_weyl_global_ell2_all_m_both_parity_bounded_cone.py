"""Tests for the global plus complete ell2 bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone import OUTPUT, build


class GlobalEll2AllMBothParityBoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_all_m_both_parity_scope(self) -> None:
        self.assertTrue(self.value["classification"]["all_m_both_parities_all_ell2_qp_branches_included"])

    def test_complete_union(self) -> None:
        cone = self.value["complete_bounded_cone"]
        self.assertTrue(cone["union_is_necessary_and_sufficient"])
        self.assertIn("mu_H=mu_J1=mu_J2=mu_J3=0", cone["wave_branch"])

    def test_zero_frequency_completion_is_constant(self) -> None:
        completion = self.value["bounded_zero_frequency_completion"]
        self.assertEqual(completion["constant_correction"], ["S0/2", "-S1/2", "0", "0"])
        self.assertEqual(completion["remainder"], ["0", "0", "0", "0"])

    def test_zero_frequency_L1_is_bounded(self) -> None:
        self.assertEqual(
            self.value["wave_cone"]["zero_frequency_L1_constant_correction"],
            ["S0/2", "-S1/2", "0", "0"],
        )
        self.assertIn("no secular/Jordan term", self.value["sufficiency"]["wave_self"])

    def test_fail_closed_beyond_ell2_k0(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["general_ell_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
