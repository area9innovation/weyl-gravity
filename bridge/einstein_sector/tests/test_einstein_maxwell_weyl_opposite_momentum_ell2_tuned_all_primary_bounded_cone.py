"""Tests for the tuned all-primary bounded cone."""

from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone import build


class TunedAllPrimaryBoundedConeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_all_primary_collision_census(self) -> None:
        census = self.payload["collision_census"]
        self.assertEqual(census["check_count"], 140)
        self.assertEqual(
            census["collisions"],
            [{"frequency": "two_minus", "momentum": "K_zero", "ell": "4", "target": "p"}],
        )

    def test_extra_branch_widens_balance_interval(self) -> None:
        interval = self.payload["nonzero_bounded_components"]["complete_imbalance_interval"]
        self.assertTrue(interval["strictly_contains_qplus_only_interval"])
        self.assertIn("r_e", interval["condition"])
        self.assertIn("omega_-/omega_e", self.payload["moment_polytope"]["strict_ratio_order"])

    def test_complete_only_in_declared_carrier(self) -> None:
        flags = self.payload["classification"]
        self.assertTrue(flags["complete_tuned_axisymmetric_all_primary_bounded_cone_classified"])
        self.assertTrue(flags["positive_branch_moment_polytope_complete"])
        self.assertFalse(flags["nonaxisymmetric_inputs_included"])
        self.assertFalse(flags["all_orders_integrability"])
        self.assertEqual(self.payload["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
