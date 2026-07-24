"""Scoped tests for the bounded multi-panel projective successor."""
from __future__ import annotations

import unittest

from .rail_v3 import compute


class ProjectiveRiccatiV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_sixteen_typed_colocated_panels(self) -> None:
        self.assertEqual(len(self.result["rows"]), 16)
        for row in self.result["rows"]:
            self.assertTrue(all(row["interface_gates"].values()))
            self.assertTrue(row["delta"]["excludes_zero"])
            self.assertEqual(row["match_radius"], 32)

    def test_sensitivity_obstruction_is_explicit(self) -> None:
        summary = self.result["summary"]
        self.assertEqual(
            summary["delta_tau_excludes_zero_panel_count"], 0
        )
        self.assertEqual(
            summary["delta_omega_excludes_zero_panel_count"], 0
        )
        obstruction = self.result["local_qnm_gate"][
            "parallel_quantitative_obstruction"
        ]
        self.assertEqual(
            obstruction["code"],
            "PROJECTIVE_SENSITIVITY_BALLS_CONTAIN_ZERO",
        )

    def test_fail_closed_at_first_missing_boundary_panel(self) -> None:
        gate = self.result["local_qnm_gate"]
        self.assertEqual(gate["status"], "FAIL_CLOSED")
        self.assertEqual(
            gate["first_obstruction"]["first_missing_panel"], 16
        )
        self.assertFalse(gate["interval_newton_run"])
        self.assertFalse(gate["argument_principle_run"])


if __name__ == "__main__":
    unittest.main()
