from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.berger_clock_charge_seed import (
    BergerClockChargeSeed,
)


class BergerClockChargeSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = BergerClockChargeSeed.build().payload

    def test_clock_momentum_and_helical_relation_are_exact(self) -> None:
        self.assertEqual(
            self.payload["exact_identities"]["helical_action"],
            "L_D(T_1,T_2)=omega R(T_1,T_2)",
        )
        self.assertTrue(
            self.payload["clock_interpretation"]["charge_nonzero_on_open_interval"]
        )

    def test_rational_fixture(self) -> None:
        fixture = self.payload["rational_fixture"]
        self.assertEqual(fixture["charge_density"], "3/4")
        self.assertEqual(fixture["integrated_charge"], "9 pi^2 sqrt(10)/5")

    def test_fixed_coupling_and_covariant_current_audits(self) -> None:
        fixed = self.payload["fixed_coupling_audit"]
        current = self.payload["covariant_current_audit"]
        helical = self.payload["helical_presymplectic_audit"]
        self.assertTrue(fixed["derivative_nonzero_on_interval"])
        self.assertEqual(fixed["stationary_fixed_coupling_consequence"], "delta q=0")
        self.assertTrue(current["derived_from_action"])
        self.assertEqual(current["presymplectic_identity"], "Omega_m(delta,R)=delta Q_R")
        self.assertIn("omega delta Q_R", helical["identity"])
        self.assertFalse(helical["allowed_delta_Q_tangent_constructed"])

    def test_total_D_verdict_remains_open(self) -> None:
        self.assertIsNone(self.payload["scientific_verdict"])
        self.assertFalse(self.payload["flags"]["total_covariant_D_charge_computed"])
        self.assertEqual(self.payload["next_gate"], "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT")


if __name__ == "__main__":
    unittest.main()
