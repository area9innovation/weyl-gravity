from __future__ import annotations

import unittest

from d_quotient_classical.scalar_clock.inhomogeneous_stealth_clock import (
    InhomogeneousConformalStealthClockNoGo,
)


class InhomogeneousConformalStealthClockNoGoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = InhomogeneousConformalStealthClockNoGo.build().payload

    def test_clock_sector_justifies_reciprocal(self) -> None:
        gate = self.payload["zero_field_gate"]
        self.assertFalse(gate["clock_can_cross_T_zero"])
        self.assertTrue(gate["reciprocal_valid_on_every_clock_candidate"])

    def test_complete_inhomogeneous_family(self) -> None:
        family = self.payload["global_classification"]
        self.assertEqual(
            family["complete_denominator"],
            "sigma=A*cos(t)+B*sin(t)+C.n",
        )
        self.assertEqual(
            family["coupling_relation"],
            "kappa=2(|C|^2-A^2-B^2)",
        )
        self.assertTrue(family["classification_global_for_nowhere_zero_clock_candidates"])

    def test_global_regular_clock_is_impossible(self) -> None:
        obstruction = self.payload["global_obstruction"]
        gradient = self.payload["timelike_gradient_obstruction"]
        self.assertTrue(obstruction["every_nontrivial_denominator_has_zero"])
        self.assertFalse(obstruction["globally_regular_stealth_scalar_clock_exists"])
        self.assertFalse(gradient["time_dependent_gradient_everywhere_timelike"])

    def test_only_standard_stealth_branch_is_closed(self) -> None:
        gate = self.payload["gate_result"]
        flags = self.payload["flags"]
        self.assertEqual(
            gate["surviving_gate"],
            "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK",
        )
        self.assertEqual(gate["surviving_gate_status"], "OPEN")
        self.assertFalse(flags["nonconformally_flat_backreacted_clock_ruled_out"])
        self.assertFalse(flags["generalized_non_noetherian_or_higher_derivative_scalar_ruled_out"])


if __name__ == "__main__":
    unittest.main()
