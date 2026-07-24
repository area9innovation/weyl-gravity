from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ReducedPhaseInfinityPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = json.loads((HERE / "certificate.json").read_text())

    def test_phase_is_symbolic(self) -> None:
        self.assertTrue(self.doc["phase_factor"]["kept_symbolic"])
        self.assertFalse(
            self.doc["phase_factor"]["omega_phase_taylor_expanded"]
        )

    def test_finite_panel_and_correlation(self) -> None:
        self.assertTrue(
            self.doc["mixed_rail"]["finite_seed_and_panel_passed"]
        )
        self.assertTrue(
            self.doc["correlation_gate"]["coefficient_equal"]
        )
        self.assertTrue(
            self.doc["correlation_gate"][
                "interval_difference_contains_zero"
            ]
        )

    def test_fail_closed_boundary(self) -> None:
        flags = self.doc["claim_flags"]
        self.assertTrue(
            flags["uniform_all_order_infinity_remainder_enclosed"]
        )
        self.assertTrue(flags["outgoing_Jost_column_certified"])
        self.assertFalse(flags["T_plus_recovered"])


if __name__ == "__main__":
    unittest.main()
