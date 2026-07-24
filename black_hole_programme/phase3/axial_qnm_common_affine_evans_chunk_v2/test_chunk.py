"""Scoped tests for common-affine panels 16--31."""
from __future__ import annotations

import json
import unittest

from flint import arb

from .chunk import RUN


class EvansChunkV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(RUN.read_text())

    def test_requested_range_and_order(self) -> None:
        self.assertEqual(self.document["requested_panels"], [16, 31])
        self.assertEqual(
            [row["panel"] for row in self.document["rows"]],
            list(range(16, 16 + len(self.document["rows"]))),
        )

    def test_shared_generator_and_correlated_fields(self) -> None:
        for row in self.document["rows"]:
            generator = row["omega_generator_id"]
            self.assertEqual(generator, row["horizon"]["omega_generator_id"])
            self.assertEqual(generator, row["outgoing"]["omega_generator_id"])
            for endpoint in ("horizon", "outgoing"):
                export = row[endpoint]
                self.assertIsNotNone(export["q_polynomial_coefficients"])
                self.assertIsNotNone(export["q_tau_polynomial_coefficients"])
                self.assertIsNotNone(export["q_omega_polynomial_coefficients"])

    def test_passing_prefix_is_strictly_nonzero(self) -> None:
        for row in self.document["rows"]:
            if row["boundary_nonvanishing"]["status"] != "PASS":
                break
            self.assertGreater(
                arb(row["physical_mismatch"]["modulus_lower"]).lower(), 0
            )

    def test_no_argument_principle_claim(self) -> None:
        self.assertEqual(
            self.document["argument_principle"]["status"], "NOT_RUN"
        )


if __name__ == "__main__":
    unittest.main()
