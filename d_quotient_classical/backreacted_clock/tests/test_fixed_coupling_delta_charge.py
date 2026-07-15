from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.fixed_coupling_delta_charge import (
    BergerFixedCouplingDeltaCharge,
)


class BergerFixedCouplingDeltaChargeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = BergerFixedCouplingDeltaCharge.build().payload

    def test_lapse_constraint_is_charge_variation(self) -> None:
        constraint = self.payload["linearized_lapse_constraint"]
        self.assertEqual(
            constraint["identity"],
            "delta E_N=-(alpha_B q^(3/2)/2)(delta Q_R/Q_R)",
        )
        self.assertTrue(constraint["coefficient_nonzero_on_branch"])

    def test_rational_fixture_is_exact(self) -> None:
        fixture = self.payload["rational_fixture"]
        self.assertEqual(fixture["lambda"], "119/480")
        self.assertEqual(fixture["rho"], "1")
        self.assertEqual(fixture["omega"], "3/4")
        self.assertEqual(fixture["lapse_row"]["delta_c"], "-9/16")

    def test_compact_average_upgrades_the_result(self) -> None:
        upgrade = self.payload["full_mode_upgrade"]
        self.assertTrue(upgrade["linearized_operator_equivariant"])
        self.assertTrue(upgrade["group_average_preserves_fixed_coupling_solutions"])
        self.assertIn("complete smooth", upgrade["conclusion"])

    def test_verdict_is_scoped_and_fail_closed(self) -> None:
        self.assertEqual(self.payload["scientific_verdict"], "D_GAUGE")
        self.assertFalse(
            self.payload["flags"]["fixed_coupling_linearized_delta_Q_tangent_exists"]
        )
        self.assertFalse(
            self.payload["flags"]["support_local_all_row_BV_retract_constructed"]
        )
        self.assertEqual(
            self.payload["next_gate"], "FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT"
        )


if __name__ == "__main__":
    unittest.main()
