import unittest

from d_quotient_classical.compensator.two_phase_counterflow_unrestricted_all_hodge_health_shortfall import build


class UnrestrictedAllHodgeHealthShortfallTests(unittest.TestCase):
    def test_first_shortfall_is_harmonic_restriction(self):
        certificate, _ = build()
        self.assertEqual(certificate["terminal_verdict"]["first_undefined_block"], "retained_gravity_scalar")
        self.assertIn("pi_", certificate["terminal_verdict"]["first_undefined_operation"])

    def test_no_physical_sign_promotion(self):
        certificate, _ = build()
        terminal = certificate["terminal_verdict"]
        self.assertFalse(terminal["physical_instability_found"])
        self.assertFalse(terminal["positive_physical_carrier_certified"])
        self.assertFalse(terminal["downstream_observer_and_Hadamard_consumers_activated"])

    def test_certified_blocks_are_preserved(self):
        certificate, _ = build()
        self.assertEqual(certificate["block_statuses"]["diagonal_U1_minimal_nonminimal"], "CERTIFIED_CONTRACTIBLE_NO_PHYSICAL_COHOMOLOGY")
        self.assertEqual(certificate["block_statuses"]["homogeneous_global_relative_phase_charge"], "CERTIFIED_ACTION_ANGLE_FAMILY_TANGENT")

    def test_mutations_do_not_close_gate(self):
        _, payload = build()
        self.assertTrue(all(not row["closes_target_gate"] for row in payload["mutations"]))


if __name__ == "__main__":
    unittest.main()
