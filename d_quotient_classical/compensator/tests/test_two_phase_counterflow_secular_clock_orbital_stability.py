import unittest

from d_quotient_classical.compensator.two_phase_counterflow_secular_clock_orbital_stability import build


class SecularClockOrbitalStabilityTests(unittest.TestCase):
    def test_family_tangent_and_coupled_isolation_are_separate(self):
        certificate, payload = build()
        verdict = certificate["terminal_verdict"]
        self.assertTrue(verdict["Jordan_direction_is_reduced_family_tangent"])
        self.assertFalse(verdict["nearby_full_coupled_background_family"])
        self.assertTrue(payload["action_angle_normal_form"]["linearization"]["parameter_derivative_verified"])

    def test_stability_notions_are_not_conflated(self):
        certificate, _ = build()
        statuses = certificate["stability_statuses"]
        self.assertEqual(statuses["lifted_phase_bounded_linear_stability"], "FAIL")
        self.assertEqual(statuses["compact_S1_absolute_Lyapunov_stability"], "FAIL")
        self.assertEqual(statuses["fixed_charge_orbital_stability_under_R_rel"], "PASS")
        self.assertEqual(statuses["unrestricted_orbital_stability_under_R_rel"], "PASS")
        self.assertEqual(statuses["frequency_modulated_stability"], "PASS")

    def test_global_symmetry_is_not_gauge(self):
        _, payload = build()
        fixed = payload["stability_ledger"]["fixed_charge_orbital_stability_under_R_rel"]
        modulated = payload["stability_ledger"]["frequency_modulated_stability"]
        self.assertFalse(fixed["R_rel_is_gauge"])
        self.assertFalse(modulated["frequency_shift_is_gauge"])

    def test_mutations(self):
        _, payload = build()
        rows = {row["id"]: row for row in payload["mutations"]}
        self.assertEqual(rows["INERTIA_SIGN_REVERSAL"]["energy_Hessian_inertia_[positive,negative,zero]"], [0, 1, 1])
        self.assertTrue(all(row["passed"] for row in rows.values()))


if __name__ == "__main__":
    unittest.main()
