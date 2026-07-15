from __future__ import annotations

import unittest

from d_quotient_classical.scalar_clock.homogeneous_stealth_clock import (
    HomogeneousPositiveConformalStealthClock,
)


class HomogeneousPositiveConformalStealthClockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = HomogeneousPositiveConformalStealthClock.build().payload

    def test_stress_and_family_are_exact(self) -> None:
        stress = self.payload["stress_classification"]
        family = self.payload["complete_nonzero_family"]
        self.assertEqual(stress["pressure_on_shell"], "p=rho/3")
        self.assertTrue(family["scalar_equation_exact"])
        self.assertTrue(family["stress_tensor_zero"])
        self.assertTrue(family["family_exhaustive_on_connected_nonzero_real_branches"])

    def test_nonnegative_quartic_has_no_nonzero_stealth(self) -> None:
        stress = self.payload["stress_classification"]
        self.assertFalse(stress["kappa_nonnegative_nonzero_stealth_exists"])
        self.assertTrue(stress["kappa_negative_required_for_nonzero_homogeneous_stealth"])

    def test_local_secant_branch_is_not_a_global_clock(self) -> None:
        health = self.payload["clock_and_health"]
        self.assertTrue(health["local_monotone_clock_charts"])
        self.assertTrue(health["finite_time_singularity"])
        self.assertFalse(health["globally_regular_on_R_times_S3"])
        self.assertFalse(health["globally_monotone_clock"])

    def test_parent_gate_remains_open(self) -> None:
        gate = self.payload["gate_result"]
        self.assertEqual(gate["parent_gate_status"], "OPEN")
        self.assertFalse(self.payload["flags"]["inhomogeneous_stealth_clock_ruled_out"])
        self.assertFalse(
            self.payload["flags"]["nonconformally_flat_backreacted_clock_ruled_out"]
        )


if __name__ == "__main__":
    unittest.main()
