"""Scoped tests for common-affine panels 48--63."""
from __future__ import annotations

import json
import unittest

from flint import arb

from .chunk import RUN


class EvansChunkV4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(RUN.read_text())

    def test_ordered_prefix(self) -> None:
        rows = self.document["rows"]
        self.assertEqual(
            [row["panel"] for row in rows],
            list(range(48, 48 + len(rows))),
        )

    def test_shared_correlated_exports(self) -> None:
        for row in self.document["rows"]:
            generator = row["omega_generator_id"]
            self.assertEqual(generator, row["horizon"]["omega_generator_id"])
            self.assertEqual(generator, row["outgoing"]["omega_generator_id"])
            for endpoint in ("horizon", "outgoing"):
                self.assertIsNotNone(
                    row[endpoint]["q_tau_polynomial_coefficients"]
                )
                self.assertIsNotNone(
                    row[endpoint]["q_omega_polynomial_coefficients"]
                )

    def test_passing_rows_are_nonzero(self) -> None:
        for row in self.document["rows"]:
            if row["boundary_nonvanishing"]["status"] != "PASS":
                break
            self.assertGreater(
                arb(row["physical_mismatch"]["modulus_lower"]).lower(), 0
            )


if __name__ == "__main__":
    unittest.main()
