from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock import PositiveBergerClockBackground


class PositiveBergerClockBackgroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = PositiveBergerClockBackground.build().payload

    def test_exact_background_and_positive_interval(self) -> None:
        solution = self.payload["exact_solution_family"]
        self.assertTrue(solution["solution_interval_nonempty"])
        self.assertTrue(solution["rho_squared_positive"])
        self.assertTrue(solution["omega_squared_positive"])
        self.assertTrue(solution["lambda_positive"])
        self.assertEqual(solution["metric_equations"], "alpha_B B=T componentwise PASS")

    def test_clock_incidence_and_target_are_healthy(self) -> None:
        clock = self.payload["clock_ansatz"]
        health = self.payload["energy_health"]
        self.assertTrue(clock["incidence_full_rank"])
        self.assertEqual(clock["phase_kinetic_coefficient"], "+rho^2")
        self.assertTrue(health["scalar_target_positive_definite"])
        self.assertTrue(health["quartic_potential_bounded_below"])
        self.assertTrue(health["dominant_energy_condition"])

    def test_rational_fixture_is_human_auditable(self) -> None:
        fixture = self.payload["rational_fixture"]
        self.assertEqual(fixture["q"], "9/40")
        self.assertEqual(fixture["omega"], "3/4")
        self.assertEqual(fixture["lambda"], "119/480")
        self.assertEqual(fixture["three_independent_metric_equations"], "PASS")

    def test_background_does_not_prematurely_promote_D(self) -> None:
        self.assertIsNone(self.payload["scientific_verdict"])
        self.assertEqual(self.payload["gate_result"]["next_gate_status"], "OPEN")
        self.assertFalse(self.payload["flags"]["covariant_phase_space_D_charge_computed"])
        self.assertFalse(
            self.payload["flags"]["support_local_all_row_bv_retract_constructed"]
        )


if __name__ == "__main__":
    unittest.main()
