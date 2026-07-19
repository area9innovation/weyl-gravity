from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone import build


class FixedEllConstantTwistBoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_both_neighbors_are_uniformly_invertible(self) -> None:
        self.assertEqual(set(self.value["neighbor_output_ledger"]), {"L=ell-1", "L=ell+1"})
        for neighbor in self.value["neighbor_output_ledger"].values():
            self.assertTrue(neighbor["all_input_shells_invertible"])

    def test_product_formula_is_complete(self) -> None:
        locus = self.value["complete_bounded_zero_locus"]
        self.assertTrue(locus["necessity_and_sufficiency"])
        self.assertIn("R_A^3", locus["formula"])

    def test_all_qp_primaries_are_included(self) -> None:
        self.assertTrue(self.value["classification"]["all_m_both_parities_all_qp_primaries_included"])

    def test_larger_scopes_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["finite_multi_ell_twist_cone_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])

    def test_causal_gate_is_fail_closed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
