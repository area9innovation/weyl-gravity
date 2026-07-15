from __future__ import annotations

import unittest

from d_quotient_classical.scalar_clock import ScalarClockVerticalSlice


class ScalarClockVerticalSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = ScalarClockVerticalSlice.build().payload

    def test_local_but_not_global_clock(self) -> None:
        clock = self.payload["homogeneous_clock"]
        self.assertTrue(self.payload["flags"]["local_monotone_charts_exist"])
        self.assertFalse(clock["nontrivial_global_monotone_solution_exists"])
        self.assertEqual(clock["maximum_monotone_interval_length"], "pi")

    def test_exact_cylinder_background_is_obstructed(self) -> None:
        coupled = self.payload["coupled_background_test"]
        self.assertEqual(coupled["cylinder_bach_tensor"], "ZERO")
        self.assertFalse(coupled["nonzero_homogeneous_clock_on_exact_vacuum_cylinder_exists"])
        self.assertFalse(coupled["linearized_scalar_fixes_D_at_T_bar_zero"])

    def test_test_field_charge_is_not_promoted(self) -> None:
        self.assertEqual(
            self.payload["improved_charge"]["unrestricted_test_field_verdict"],
            "D_CHARGED",
        )
        self.assertIsNone(self.payload["scientific_verdict"])
        self.assertEqual(self.payload["claim_status"], "CERTIFIED_OBSTRUCTION")

    def test_relational_fixture_is_exact_and_scoped(self) -> None:
        fixture = self.payload["local_relational_fixture"]
        self.assertEqual(fixture["gauge_invariance"], "PASS")
        self.assertEqual(fixture["nontrivial_tau_evolution"], "PASS")
        self.assertEqual(fixture["scope"], "REDUCED_MODE_OFF_SHELL_FIXTURE")


if __name__ == "__main__":
    unittest.main()
