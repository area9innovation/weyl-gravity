"""Scoped tests for the horizon/two-sided projective successor."""
from __future__ import annotations

import unittest

from .rail_v2 import compute


class ProjectiveRiccatiV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_horizon_chart_and_step(self) -> None:
        horizon = self.result["horizon"]
        self.assertTrue(horizon["passed"])
        self.assertEqual(
            horizon["chart_gate"]["chart"],
            "q_H=(partial_x P_H)/P_H",
        )
        self.assertTrue(horizon["chart_gate"]["pivot_excludes_zero"])
        self.assertTrue(horizon["transport"]["post_normalization_finite"])

    def test_common_generator_and_mismatch(self) -> None:
        self.assertTrue(all(self.result["interface_gates"].values()))
        match = self.result["common_match"]
        self.assertTrue(match["passed"])
        self.assertTrue(match["mismatch"]["excludes_zero"])
        self.assertEqual(
            match["mismatch"]["formula"],
            "Delta=q_H-q_out+2*I*omega",
        )
        self.assertTrue(
            match["omega_sensitivity"]["equals_affine_slope"]
        )

    def test_fail_closed_scope(self) -> None:
        self.assertFalse(self.result["scope"]["full_closed_contour"])
        self.assertEqual(self.result["scope"]["common_match_panel_count"], 1)


if __name__ == "__main__":
    unittest.main()
