from __future__ import annotations

import unittest

from d_quotient_classical.composite_clock.neutral_clock_bv_health import (
    NeutralClockBVHealthAudit,
)


class NeutralClockBVHealthAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = NeutralClockBVHealthAudit.build().payload

    def test_local_scalar_incidence_is_still_useful(self) -> None:
        incidence = self.payload["brst_incidence"]
        self.assertTrue(incidence["field_ghost_incidence_invertible_on_W_nonzero"])
        self.assertTrue(incidence["inverse_support_local"])

    def test_ratio_mode_survives_weyl_reduction(self) -> None:
        reduction = self.payload["local_field_reduction"]
        self.assertTrue(reduction["remaining_angle_has_derivative_action"])
        self.assertFalse(reduction["ratio_mode_weyl_contractible"])

    def test_every_clock_orbit_crosses_kinetic_null_cone(self) -> None:
        obstruction = self.payload["neutral_orbit_obstruction"]
        self.assertEqual(obstruction["norm_zero_count_per_2pi"], 4)
        self.assertTrue(obstruction["kinetic_degeneracy_crossed_by_every_regular_clock_orbit"])
        self.assertFalse(obstruction["kinetic_sign_definite_on_full_clock_orbit"])

    def test_homogeneous_clock_survives_but_health_does_not(self) -> None:
        gate = self.payload["gate_result"]
        self.assertTrue(gate["homogeneous_clock_theorem_retained"])
        self.assertEqual(
            gate["status"],
            "OBSTRUCTED_AS_GLOBALLY_REGULAR_HEALTHY_CLOCK",
        )
        self.assertFalse(
            self.payload["degree_of_freedom_audit"][
                "opposite_sign_reference_sector_entirely_contractible"
            ]
        )


if __name__ == "__main__":
    unittest.main()
