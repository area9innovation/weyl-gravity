from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_rational_fixture_q2_d_block import verify_certificate


class BergerRationalFixtureQ2DBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_action_derived_closed_block(self) -> None:
        self.assertEqual(len(self.payload["row_layout"]), 6)
        self.assertEqual(self.payload["row_layout"][0]["row_id"], "delta_u_w0")
        self.assertGreater(len(self.payload["classical_binary_q2"]["entries"]), 0)
        self.assertTrue(self.payload["exact_checks"]["declared_mode_block_closed"])
        self.assertTrue(self.payload["exact_checks"]["all_exported_coefficients_in_Q"])

    def test_reduced_mode_boundary(self) -> None:
        self.assertEqual(self.payload["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertTrue(self.payload["scope"]["not_support_local_q2"])
        self.assertFalse(self.payload["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"])
        self.assertFalse(self.payload["flags"]["ND2_PHYSICAL_EXECUTION_AUTHORIZED"])

    def test_centered_D_action_is_explicit(self) -> None:
        self.assertEqual(self.payload["D_action_cl"]["weights"], [0] * 6)
        self.assertTrue(self.payload["exact_checks"]["q1_D_commutator_zero"])


if __name__ == "__main__":
    unittest.main()
