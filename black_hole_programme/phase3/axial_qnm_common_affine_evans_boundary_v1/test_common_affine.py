"""Scoped tests for the common-affine endpoint export attempt."""
from __future__ import annotations

import unittest

from .common_affine import compute


class CommonAffineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = compute()

    def test_one_shared_generator_and_opposite_phases(self) -> None:
        row = self.document["rows"][0]
        self.assertEqual(
            row["omega_generator_id"],
            row["horizon"]["omega_generator_id"],
        )
        self.assertEqual(
            row["omega_generator_id"],
            row["outgoing"]["omega_generator_id"],
        )
        self.assertIn("+I*omega", row["horizon"]["phase_convention"])
        self.assertIn("-I*omega", row["outgoing"]["phase_convention"])

    def test_first_failure_stops_before_root_count(self) -> None:
        self.assertEqual(len(self.document["rows"]), 1)
        self.assertEqual(
            self.document["gates"]["boundary_nonvanishing"]["status"],
            "FAIL_CLOSED",
        )
        self.assertEqual(
            self.document["gates"]["argument_principle_root_count"]["status"],
            "NOT_RUN",
        )

    def test_polynomial_exports_are_not_faked_after_transport_failure(self) -> None:
        row = self.document["rows"][0]
        self.assertIsNone(row["horizon"]["q_polynomial_coefficients"])
        self.assertIsNone(row["outgoing"]["q_polynomial_coefficients"])


if __name__ == "__main__":
    unittest.main()
