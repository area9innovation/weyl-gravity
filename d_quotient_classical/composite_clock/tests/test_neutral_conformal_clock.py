from __future__ import annotations

import unittest

from d_quotient_classical.composite_clock import NeutralConformalClockPair


class NeutralConformalClockPairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = NeutralConformalClockPair.build().payload

    def test_exact_nonzero_cylinder_background(self) -> None:
        stress = self.payload["stress_cancellation"]
        self.assertTrue(stress["stress_vanishes_on_neutral_constraint"])
        self.assertTrue(stress["coupled_metric_equation_satisfied"])
        self.assertTrue(stress["exact_nonzero_clock_background_exists"])

    def test_clock_is_global_only_in_declared_compact_sense(self) -> None:
        gauge = self.payload["gauge_slice"]
        self.assertTrue(gauge["global_compact_D_clock"])
        self.assertTrue(gauge["clock_velocity_never_zero_on_regular_sector"])
        self.assertFalse(gauge["global_real_lift_on_universal_cover"])

    def test_diff_weyl_slice_is_transverse(self) -> None:
        gauge = self.payload["gauge_slice"]
        self.assertEqual(
            gauge["incidence_determinant"],
            "W=T_1*dot(T_2)-T_2*dot(T_1)",
        )
        self.assertTrue(gauge["full_rank_on_regular_sector"])

    def test_scoped_d_verdict_and_health_caveat(self) -> None:
        self.assertEqual(self.payload["scientific_verdict"], "D_GAUGE")
        self.assertEqual(
            self.payload["phase_space_id"],
            "compact_neutral_clock_pair_homogeneous",
        )
        self.assertTrue(
            self.payload["health_and_scope"]["opposite_sign_reference_scalar_present"]
        )
        self.assertFalse(self.payload["flags"]["healthy_positive_matter_completion"])


if __name__ == "__main__":
    unittest.main()
