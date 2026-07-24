"""Scoped tests for the projective Evans/Riccati rail."""
from __future__ import annotations

import unittest

from .rail import compute, exact_chart_identities


class ProjectiveRiccatiRailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_generic_and_specialized_equations_are_typed(self) -> None:
        identities = exact_chart_identities()
        self.assertEqual(identities["generic_chart"], "v=Y2/Y1")
        self.assertIn("-A12*v**2", identities["generic_base"])
        self.assertEqual(
            identities["implemented_chart"],
            "q=(partial_x P_out)/P_out",
        )
        self.assertIn("-calI", identities["implemented_tau"])
        self.assertIn("+2*I*q", identities["implemented_omega"])

    def test_pivot_and_one_panel_pass(self) -> None:
        self.assertTrue(self.result["passed"])
        self.assertTrue(self.result["chart_gate"]["pivot_excludes_zero"])
        self.assertTrue(
            self.result["chart_gate"]["analytic_chart_through_step"]
        )
        self.assertEqual(self.result["transport"]["to_r"], "899/20")

    def test_claim_scope_is_fail_closed(self) -> None:
        self.assertFalse(self.result["scope"]["two_sided"])
        self.assertEqual(self.result["scope"]["radial_panel_count"], 1)


if __name__ == "__main__":
    unittest.main()
